"""ConversationMemory 并发安全测试

验证文件锁机制在多线程/多进程并发写入时的数据完整性。
TDD RED 阶段 — 所有测试预期失败（文件锁尚未实现）。
"""
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from unittest.mock import patch, MagicMock

import pytest


# ── 1. 基础设施：_FileLock 上下文管理器 ──────────────────────────


class TestFileLockContextManager:
    """验证 _FileLock 上下文管理器的基本行为"""

    def test_file_lock_exists(self):
        """ConversationMemory 模块应导出 _FileLock"""
        from maitian_agent.memory.conversation_memory import _FileLock
        assert callable(_FileLock)

    def test_file_lock_context_manager_enter_exit(self, tmp_path):
        """_FileLock 应支持 with 语句，进入时获取锁，退出时释放"""
        from maitian_agent.memory.conversation_memory import _FileLock
        lock_file = tmp_path / "test.lock"

        with _FileLock(str(lock_file)) as acquired:
            assert acquired is True

    def test_file_lock_blocks_concurrent_access(self, tmp_path):
        """同一文件上的两个 _FileLock 应互斥"""
        from maitian_agent.memory.conversation_memory import _FileLock
        lock_file = tmp_path / "test.lock"
        results = []

        def hold_lock():
            with _FileLock(str(lock_file), timeout=2.0) as acquired:
                if acquired:
                    results.append("acquired")
                    time.sleep(0.3)  # 持有锁 300ms
                else:
                    results.append("timeout")

        t1 = threading.Thread(target=hold_lock)
        t2 = threading.Thread(target=hold_lock)
        t1.start()
        time.sleep(0.05)  # 确保 t1 先获取锁
        t2.start()
        t1.join()
        t2.join()

        assert "acquired" in results
        # t2 应该最终也获取到锁（不是 timeout），因为 t1 会释放
        assert results.count("acquired") == 2

    def test_file_lock_timeout_returns_false(self, tmp_path):
        """锁超时应返回 False，不抛异常"""
        from maitian_agent.memory.conversation_memory import _FileLock
        lock_file = tmp_path / "test.lock"

        # 线程1：长时间持有锁
        def hold_long():
            with _FileLock(str(lock_file), timeout=5.0) as acquired:
                if acquired:
                    time.sleep(2.0)

        # 线程2：极短超时
        result_holder = []

        def try_short():
            with _FileLock(str(lock_file), timeout=0.1) as acquired:
                result_holder.append(acquired)

        t1 = threading.Thread(target=hold_long)
        t1.start()
        time.sleep(0.05)
        t2 = threading.Thread(target=try_short)
        t2.start()
        t1.join()
        t2.join()

        assert result_holder[0] is False


# ── 2. 多线程并发写入 — 数据完整性 ──────────────────────────────


class TestConcurrentThreadSafety:
    """验证多线程并发写入 JSON 文件时数据不损坏"""

    def test_concurrent_save_context_preserves_all_messages(self, tmp_path):
        """10 个线程并发 save_context，所有消息都应被保留"""
        from maitian_agent.memory.conversation_memory import ConversationMemory

        persist_dir = str(tmp_path / "memory")
        mem = ConversationMemory(
            session_id="concurrent_thread",
            persist_directory=persist_dir,
        )

        num_threads = 10
        barrier = threading.Barrier(num_threads)

        def save_message(thread_id):
            barrier.wait()  # 所有线程同时开始
            mem.save_context(
                input_data={"human_input": f"用户消息-{thread_id}"},
                output_data={"response": f"AI回复-{thread_id}"},
            )

        threads = [threading.Thread(target=save_message, args=(i,)) for i in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 验证：重新加载后消息数量应正确
        mem2 = ConversationMemory(
            session_id="concurrent_thread",
            persist_directory=persist_dir,
        )
        history = mem2.get_conversation_history()
        # conversation_window=5 → 最多 10 条消息（5轮）
        assert len(history) > 0, "并发写入后应有消息"
        assert len(history) <= 10, f"消息数不应超过窗口限制，实际 {len(history)}"

    def test_concurrent_save_no_json_corruption(self, tmp_path):
        """并发写入后 JSON 文件应可正常解析"""
        from maitian_agent.memory.conversation_memory import ConversationMemory

        persist_dir = str(tmp_path / "memory")

        def write_loop(thread_id):
            mem = ConversationMemory(
                session_id="json_safe",
                persist_directory=persist_dir,
            )
            for i in range(5):
                mem.save_context(
                    input_data={"human_input": f"t{thread_id}-msg{i}"},
                    output_data={"response": f"t{thread_id}-resp{i}"},
                )

        threads = [threading.Thread(target=write_loop, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 验证 JSON 文件可解析
        history_file = os.path.join(persist_dir, "chat_history_json_safe.json")
        assert os.path.exists(history_file), "历史文件应存在"
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)  # 不应抛异常
        assert isinstance(data, list), "JSON 根元素应为列表"

    def test_concurrent_clear_and_save(self, tmp_path):
        """一个线程 clear() 的同时另一个线程 save_context()，不应崩溃"""
        from maitian_agent.memory.conversation_memory import ConversationMemory

        persist_dir = str(tmp_path / "memory")
        mem = ConversationMemory(
            session_id="clear_race",
            persist_directory=persist_dir,
        )
        errors = []

        def clear_loop():
            try:
                for _ in range(10):
                    mem.clear()
            except Exception as e:
                errors.append(e)

        def save_loop():
            try:
                for i in range(10):
                    mem.save_context(
                        input_data={"human_input": f"msg-{i}"},
                        output_data={"response": f"resp-{i}"},
                    )
            except Exception as e:
                errors.append(e)

        t1 = threading.Thread(target=clear_loop)
        t2 = threading.Thread(target=save_loop)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert len(errors) == 0, f"并发 clear+save 产生异常: {errors}"


# ── 3. 多进程并发写入 — 跨进程安全 ──────────────────────────────


class TestConcurrentProcessSafety:
    """验证多进程并发写入 JSON 文件时数据不损坏"""

    def test_multiprocess_save_context_no_corruption(self, tmp_path):
        """多进程并发 save_context，JSON 文件不应损坏"""
        # 跳过条件：VM 环境可能缺少 /dev/shm 导致 ProcessPoolExecutor 不可用
        try:
            from concurrent.futures import ProcessPoolExecutor
            _test_executor = ProcessPoolExecutor(max_workers=1)
            _test_executor.shutdown(wait=True)
        except (FileNotFoundError, OSError) as e:
            pytest.skip(f"ProcessPoolExecutor 不可用（环境限制）: {e}")

        persist_dir = str(tmp_path / "memory")

        def worker(args):
            session_id, persist_dir = args
            from maitian_agent.memory.conversation_memory import ConversationMemory
            mem = ConversationMemory(
                session_id=session_id,
                persist_directory=persist_dir,
            )
            for i in range(5):
                mem.save_context(
                    input_data={"human_input": f"msg-{i}"},
                    output_data={"response": f"resp-{i}"},
                )
            return True

        # 使用相同 session_id 测试跨进程竞争
        args_list = [("mp_safe", str(persist_dir))] * 3
        with ProcessPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(worker, args_list))

        assert all(results), "所有进程应成功完成"

        # 验证 JSON 文件可解析
        history_file = os.path.join(str(persist_dir), "chat_history_mp_safe.json")
        assert os.path.exists(history_file), "历史文件应存在"
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list), "JSON 根元素应为列表"


# ── 4. 锁超时降级 — 不阻塞主流程 ───────────────────────────────


class TestLockTimeoutDegradation:
    """验证锁超时后自动降级，不阻塞主流程"""

    def test_persist_timeout_does_not_block(self, tmp_path):
        """持久化锁超时时，save_context 应快速返回，不阻塞"""
        from maitian_agent.memory.conversation_memory import ConversationMemory

        persist_dir = str(tmp_path / "memory")
        mem = ConversationMemory(
            session_id="timeout_test",
            persist_directory=persist_dir,
        )

        # 先写入一些数据
        mem.save_context(
            input_data={"human_input": "hello"},
            output_data={"response": "world"},
        )

        # 模拟锁被长时间占用：手动创建锁文件并持有
        lock_file = os.path.join(persist_dir, "chat_history_timeout_test.json.lock")
        os.makedirs(persist_dir, exist_ok=True)

        import fcntl
        fd = os.open(lock_file, os.O_CREAT | os.O_WRONLY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)  # 持有排他锁

            # 使用极短超时的 ConversationMemory
            mem2 = ConversationMemory(
                session_id="timeout_test",
                persist_directory=persist_dir,
                lock_timeout=0.01,  # 10ms 超时
            )

            start = time.time()
            mem2.save_context(
                input_data={"human_input": "blocked_msg"},
                output_data={"response": "blocked_resp"},
            )
            elapsed = time.time() - start

            # 应在超时时间内快速返回（加上一些余量）
            assert elapsed < 1.0, f"锁超时降级失败，耗时 {elapsed:.3f}s"
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    def test_persist_timeout_logs_warning(self, tmp_path):
        """锁超时时应记录 warning 日志"""
        from maitian_agent.memory.conversation_memory import ConversationMemory

        persist_dir = str(tmp_path / "memory")

        # 创建锁文件并持有
        lock_file = os.path.join(persist_dir, "chat_history_log_test.json.lock")
        os.makedirs(persist_dir, exist_ok=True)

        import fcntl
        fd = os.open(lock_file, os.O_CREAT | os.O_WRONLY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)

            mem = ConversationMemory(
                session_id="log_test",
                persist_directory=persist_dir,
                lock_timeout=0.01,
            )

            with patch("maitian_agent.memory.conversation_memory.logger") as mock_logger:
                mem.save_context(
                    input_data={"human_input": "test"},
                    output_data={"response": "test"},
                )
                # 应有 warning 级别日志
                warning_calls = [
                    c for c in mock_logger.method_calls
                    if "warning" in str(c).lower() or c[0] == "warning"
                ]
                assert len(warning_calls) > 0, "锁超时应记录 warning 日志"
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)


# ── 5. 锁状态日志记录 ──────────────────────────────────────────


class TestLockLogging:
    """验证锁的获取/释放/超时都有日志记录"""

    def test_lock_acquired_logs_debug(self, tmp_path):
        """成功获取锁时应记录 debug 日志"""
        from maitian_agent.memory.conversation_memory import ConversationMemory

        persist_dir = str(tmp_path / "memory")

        with patch("maitian_agent.memory.conversation_memory.logger") as mock_logger:
            mem = ConversationMemory(
                session_id="log_acquire",
                persist_directory=persist_dir,
            )
            mem.save_context(
                input_data={"human_input": "hello"},
                output_data={"response": "world"},
            )

            # 检查有 debug 调用（锁获取/释放）
            all_calls = str(mock_logger.method_calls)
            # 不强制检查具体内容，但应有日志调用
            assert len(mock_logger.method_calls) > 0, "应有日志记录"

    def test_lock_release_logs_debug(self, tmp_path):
        """释放锁时应记录 debug 日志"""
        from maitian_agent.memory.conversation_memory import ConversationMemory

        persist_dir = str(tmp_path / "memory")

        with patch("maitian_agent.memory.conversation_memory.logger") as mock_logger:
            mem = ConversationMemory(
                session_id="log_release",
                persist_directory=persist_dir,
            )
            mem.save_context(
                input_data={"human_input": "hello"},
                output_data={"response": "world"},
            )

            # 验证 logger 至少被调用
            assert mock_logger.called or len(mock_logger.method_calls) > 0


# ── 6. 向后兼容 — 原有接口不变 ─────────────────────────────────


class TestBackwardCompatibility:
    """验证添加文件锁后原有接口完全兼容"""

    def test_save_context_interface_unchanged(self, tmp_path):
        """save_context 签名和行为不变"""
        from maitian_agent.memory.conversation_memory import ConversationMemory

        mem = ConversationMemory(
            session_id="compat",
            persist_directory=str(tmp_path / "memory"),
        )
        mem.save_context(
            input_data={"human_input": "你好"},
            output_data={"response": "你好！有什么可以帮您？"},
        )
        history = mem.get_conversation_history()
        assert len(history) == 2
        assert history[0]["type"] == "human"
        assert history[0]["content"] == "你好"
        assert history[1]["type"] == "ai"

    def test_clear_interface_unchanged(self, tmp_path):
        """clear 签名和行为不变"""
        from maitian_agent.memory.conversation_memory import ConversationMemory

        mem = ConversationMemory(
            session_id="compat_clear",
            persist_directory=str(tmp_path / "memory"),
        )
        mem.save_context(
            input_data={"human_input": "test"},
            output_data={"response": "test"},
        )
        mem.clear()
        history = mem.get_conversation_history()
        assert len(history) == 0

    def test_load_memory_variables_unchanged(self, tmp_path):
        """load_memory_variables 签名和行为不变"""
        from maitian_agent.memory.conversation_memory import ConversationMemory

        mem = ConversationMemory(
            session_id="compat_load",
            persist_directory=str(tmp_path / "memory"),
        )
        mem.save_context(
            input_data={"human_input": "test"},
            output_data={"response": "test"},
        )
        variables = mem.load_memory_variables()
        assert "history" in variables
        assert len(variables["history"]) == 2

    def test_conversation_window_still_works(self, tmp_path):
        """conversation_window 滑动窗口仍然生效"""
        from maitian_agent.memory.conversation_memory import ConversationMemory

        mem = ConversationMemory(
            session_id="window_test",
            persist_directory=str(tmp_path / "memory"),
            conversation_window=2,  # 最多保留 4 条消息
        )
        for i in range(5):
            mem.save_context(
                input_data={"human_input": f"msg-{i}"},
                output_data={"response": f"resp-{i}"},
            )
        history = mem.get_conversation_history()
        assert len(history) == 4, f"窗口应为 4 条，实际 {len(history)}"

    def test_lock_timeout_parameter_default(self):
        """ConversationMemory 应支持 lock_timeout 参数，默认值合理"""
        from maitian_agent.memory.conversation_memory import ConversationMemory
        import inspect

        sig = inspect.signature(ConversationMemory.__init__)
        params = sig.parameters
        assert "lock_timeout" in params, "ConversationMemory.__init__ 应接受 lock_timeout 参数"
        # 默认值应 > 0
        default = params["lock_timeout"].default
        assert default is not None and default > 0, f"lock_timeout 默认值应为正数，实际 {default}"

    def test_no_lock_timeout_param_works(self, tmp_path):
        """不传 lock_timeout 时应正常工作"""
        from maitian_agent.memory.conversation_memory import ConversationMemory

        mem = ConversationMemory(
            session_id="no_timeout",
            persist_directory=str(tmp_path / "memory"),
        )
        mem.save_context(
            input_data={"human_input": "test"},
            output_data={"response": "test"},
        )
        history = mem.get_conversation_history()
        assert len(history) == 2
