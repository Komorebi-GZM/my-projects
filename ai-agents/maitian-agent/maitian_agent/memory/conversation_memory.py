"""
对话记忆管理
短期记忆实现 — 支持文件锁并发安全
"""

import fcntl
import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

logger = logging.getLogger(__name__)


class _FileLock:
    """跨进程文件锁上下文管理器

    基于 fcntl.flock 实现，支持超时自动降级。
    超时后返回 acquired=False，不阻塞主流程。
    """

    def __init__(self, lock_path: str, timeout: float = 2.0):
        self._lock_path = lock_path
        self._timeout = timeout
        self._fd: Optional[int] = None
        self._acquired = False

    def __enter__(self) -> bool:
        try:
            self._fd = os.open(self._lock_path, os.O_CREAT | os.O_WRONLY)
            deadline = time.monotonic() + self._timeout
            while time.monotonic() < deadline:
                try:
                    fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self._acquired = True
                    logger.debug(
                        "文件锁已获取: %s (等待 %.3fs)",
                        self._lock_path,
                        max(0, time.monotonic() - (deadline - self._timeout)),
                    )
                    return True
                except (IOError, OSError):
                    # 锁被占用，短暂等待后重试
                    time.sleep(0.01)
            # 超时
            logger.warning(
                "文件锁获取超时 (%.1fs)，自动降级: %s",
                self._timeout,
                self._lock_path,
            )
            return False
        except Exception as e:
            logger.warning("文件锁获取异常，自动降级: %s — %s", self._lock_path, e)
            return False

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._fd is not None:
            if self._acquired:
                try:
                    fcntl.flock(self._fd, fcntl.LOCK_UN)
                    logger.debug("文件锁已释放: %s", self._lock_path)
                except Exception:
                    pass
            try:
                os.close(self._fd)
            except Exception:
                pass
            self._fd = None
            self._acquired = False


class ConversationMemory:
    """对话记忆管理器

    短期记忆：保留最近N轮对话的滑动窗口。
    支持文件锁并发安全，锁超时自动降级。
    """

    def __init__(
        self,
        memory_type: str = "buffer",
        conversation_window: int = 5,
        session_id: str = "default",
        persist_directory: str = "./data/memory",
        lock_timeout: float = 2.0,
    ):
        self.memory_type = memory_type
        self.conversation_window = conversation_window
        self.session_id = session_id
        self.persist_directory = persist_directory
        self._lock_timeout = lock_timeout

        os.makedirs(persist_directory, exist_ok=True)

        self.chat_memory = InMemoryChatMessageHistory()
        loaded = self._load_chat_history()
        for msg in loaded:
            self.chat_memory.add_message(msg)

    def _get_lock_path(self) -> str:
        """获取当前 session 的锁文件路径"""
        return os.path.join(
            self.persist_directory,
            f"chat_history_{self.session_id}.json.lock",
        )

    def _get_history_file(self) -> str:
        """获取当前 session 的历史文件路径"""
        return os.path.join(
            self.persist_directory,
            f"chat_history_{self.session_id}.json",
        )

    def _load_chat_history(self) -> List[BaseMessage]:
        """加载聊天历史（带文件锁保护）"""
        history_file = self._get_history_file()

        if not os.path.exists(history_file):
            return []

        with _FileLock(history_file + ".lock", timeout=self._lock_timeout) as acquired:
            if not acquired:
                logger.warning("加载聊天历史锁超时，跳过加载: %s", history_file)
                return []
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    messages = json.load(f)
                    return self._messages_to_objects(messages)
            except Exception:
                pass
        return []

    def _messages_to_objects(self, messages: List[Dict]) -> List[BaseMessage]:
        """将字典转换为消息对象"""
        result = []
        for msg in messages:
            if msg.get("type") == "human":
                result.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("type") == "ai":
                result.append(AIMessage(content=msg.get("content", "")))
        return result

    def _objects_to_dict(self, messages: List[BaseMessage]) -> List[Dict]:
        """将消息对象转换为字典"""
        result = []
        for msg in messages:
            msg_dict = {"type": msg.type, "content": msg.content}
            if hasattr(msg, "additional_kwargs"):
                msg_dict["additional_kwargs"] = msg.additional_kwargs
            result.append(msg_dict)
        return result

    def _apply_window(self) -> None:
        """保留最近 N 轮对话，超出部分丢弃"""
        while len(self.chat_memory.messages) > self.conversation_window * 2:
            self.chat_memory.messages.pop(0)

    def save_context(self, input_data: Dict[str, Any], output_data: Dict[str, Any]) -> None:
        """保存对话上下文

        Args:
            input_data: 输入数据
            output_data: 输出数据
        """
        human_message = input_data.get("human_input", "")
        ai_message = output_data.get("response", "")

        if human_message:
            self.chat_memory.add_user_message(human_message)
        if ai_message:
            self.chat_memory.add_ai_message(ai_message)

        self._apply_window()
        self._persist_history()

    def _persist_history(self) -> None:
        """持久化聊天历史（带文件锁保护）"""
        history_file = self._get_history_file()
        lock_path = history_file + ".lock"

        with _FileLock(lock_path, timeout=self._lock_timeout) as acquired:
            if not acquired:
                logger.warning(
                    "持久化聊天历史锁超时，跳过写入: %s",
                    history_file,
                )
                return
            try:
                messages = self._objects_to_dict(self.chat_memory.messages)
                with open(history_file, "w", encoding="utf-8") as f:
                    json.dump(messages, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error("持久化聊天历史失败 (%s): %e", history_file, e)

    def load_memory_variables(self) -> Dict[str, Any]:
        """加载记忆变量"""
        return {"history": self.chat_memory.messages}

    def clear(self) -> None:
        """清除记忆"""
        self.chat_memory.clear()
        self._persist_history()

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """获取对话历史

        Returns:
            对话历史列表
        """
        messages = self.chat_memory.messages
        return [
            {
                "type": msg.type,
                "content": msg.content,
                "timestamp": datetime.now().isoformat(),
            }
            for msg in messages
        ]
