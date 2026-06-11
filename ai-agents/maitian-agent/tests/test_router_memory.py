"""RouterAgent 记忆保存测试 — 验证路由决策记录到对话上下文

核心断言：
1. RouterAgent.run() 成功路由后调用 _save_to_memory()
2. 保存的记忆中 human_input 为用户原始输入
3. 保存的记忆中 response 包含路由决策信息
4. 无 conversation_memory 时静默降级，不报错
5. 缺少 user_input 时（错误路径）不保存记忆
6. run() 返回值使用 _format_output() 统一格式
7. 端到端：Factory + Memory → 路由决策可持久化
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, call
from langchain_core.messages import AIMessage

import pytest


# ── 辅助 ──────────────────────────────────────────────────────────

def _make_mock_llm(response_text: str = "quick_lesson_prep"):
    """创建 mock LLM，返回指定意图名称"""
    from langchain_core.language_models import BaseChatModel
    llm = MagicMock(spec=BaseChatModel)
    llm.invoke.return_value = AIMessage(content=response_text)
    return llm


def _make_real_memory(tmp_dir: str):
    """创建真实的 ConversationMemory（使用临时目录）"""
    from maitian_agent.memory.conversation_memory import ConversationMemory
    return ConversationMemory(
        session_id="test-router",
        persist_directory=tmp_dir,
    )


_STANDARD_INPUT = {"user_input": "帮我备一节数学课"}


# ══════════════════════════════════════════════════════════════════
# 1. run() 成功路由后调用 _save_to_memory()
# ══════════════════════════════════════════════════════════════════

class TestRouterSavesMemory:
    """验证 RouterAgent.run() 在成功路由后保存对话上下文"""

    def test_run_calls_save_to_memory_with_mock_memory(self):
        """有 conversation_memory 时，run() 应调用 _save_to_memory()"""
        from maitian_agent.agents.router import RouterAgent

        mock_memory = MagicMock()
        agent = RouterAgent(llm=_make_mock_llm())
        agent.conversation_memory = mock_memory

        agent.run(_STANDARD_INPUT)

        mock_memory.save_context.assert_called_once()

    def test_run_saves_human_input(self):
        """保存的记忆中 human_input 应为用户原始输入"""
        from maitian_agent.agents.router import RouterAgent

        mock_memory = MagicMock()
        agent = RouterAgent(llm=_make_mock_llm())
        agent.conversation_memory = mock_memory

        agent.run(_STANDARD_INPUT)

        call_args = mock_memory.save_context.call_args[0]
        human_input = call_args[0].get("human_input", "")
        assert "帮我备一节数学课" in human_input

    def test_run_saves_response_with_intent(self):
        """保存的记忆中 response 应包含路由决策"""
        from maitian_agent.agents.router import RouterAgent

        mock_memory = MagicMock()
        agent = RouterAgent(llm=_make_mock_llm())
        agent.conversation_memory = mock_memory

        agent.run(_STANDARD_INPUT)

        call_args = mock_memory.save_context.call_args[0]
        response = call_args[1].get("response", "")
        assert "quick_lesson_prep" in response


# ══════════════════════════════════════════════════════════════════
# 2. 静默降级 — 无 conversation_memory 时不报错
# ══════════════════════════════════════════════════════════════════

class TestRouterSilentDegradation:
    """验证无 conversation_memory 时，RouterAgent 静默降级"""

    def test_no_memory_run_still_works(self):
        """无 conversation_memory 时，run() 应正常返回"""
        from maitian_agent.agents.router import RouterAgent

        agent = RouterAgent(llm=_make_mock_llm())
        result = agent.run(_STANDARD_INPUT)

        assert result["success"] is True

    def test_no_memory_no_error(self):
        """无 conversation_memory 时，run() 不应抛异常"""
        from maitian_agent.agents.router import RouterAgent

        agent = RouterAgent(llm=_make_mock_llm())
        # 不设置 conversation_memory，不应抛异常
        result = agent.run(_STANDARD_INPUT)
        assert result is not None


# ══════════════════════════════════════════════════════════════════
# 3. 错误路径不保存记忆
# ══════════════════════════════════════════════════════════════════

class TestRouterErrorPathNoMemory:
    """验证错误路径（缺少 user_input）不保存记忆"""

    def test_missing_user_input_no_save(self):
        """缺少 user_input 时，不应调用 _save_to_memory()"""
        from maitian_agent.agents.router import RouterAgent

        mock_memory = MagicMock()
        agent = RouterAgent(llm=_make_mock_llm())
        agent.conversation_memory = mock_memory

        agent.run({})

        mock_memory.save_context.assert_not_called()

    def test_empty_user_input_no_save(self):
        """user_input 为空字符串时，不应调用 _save_to_memory()"""
        from maitian_agent.agents.router import RouterAgent

        mock_memory = MagicMock()
        agent = RouterAgent(llm=_make_mock_llm())
        agent.conversation_memory = mock_memory

        agent.run({"user_input": ""})

        mock_memory.save_context.assert_not_called()


# ══════════════════════════════════════════════════════════════════
# 4. run() 返回值使用 _format_output() 统一格式
# ══════════════════════════════════════════════════════════════════

class TestRouterOutputFormat:
    """验证 run() 返回值使用 _format_output() 统一格式"""

    def test_run_returns_format_output_keys(self):
        """run() 返回值应包含 _format_output() 的标准键"""
        from maitian_agent.agents.router import RouterAgent

        agent = RouterAgent(llm=_make_mock_llm())
        result = agent.run(_STANDARD_INPUT)

        # _format_output 返回的标准键
        assert "success" in result
        assert "result" in result
        assert "agent" in result
        assert "metadata" in result
        assert result["agent"] == "RouterAgent"

    def test_run_returns_intent_in_result(self):
        """run() 返回值中 result 或 metadata 应包含 intent"""
        from maitian_agent.agents.router import RouterAgent

        agent = RouterAgent(llm=_make_mock_llm())
        result = agent.run(_STANDARD_INPUT)

        # intent 信息应在 result 或 metadata 中可找到
        assert result["success"] is True
        # result 字段应包含路由决策信息
        assert "quick_lesson_prep" in str(result["result"])

    def test_run_missing_input_returns_error_dict(self):
        """缺少 user_input 时，应返回错误格式的 Dict"""
        from maitian_agent.agents.router import RouterAgent

        agent = RouterAgent(llm=_make_mock_llm())
        result = agent.run({})

        assert result["success"] is False
        assert "error" in result


# ══════════════════════════════════════════════════════════════════
# 5. 端到端：Factory + Memory → 路由决策持久化
# ══════════════════════════════════════════════════════════════════

class TestEndToEndRouterMemory:
    """端到端验证：AgentFactory + ConversationMemory → 路由决策持久化"""

    def test_factory_router_saves_to_real_memory(self, tmp_path):
        """通过 Factory 创建的 RouterAgent 应将路由决策保存到真实记忆"""
        from maitian_agent.agents.factory import AgentFactory

        memory = _make_real_memory(str(tmp_path))
        factory = AgentFactory(
            llm=_make_mock_llm(),
            conversation_memory=memory,
        )

        agent = factory.create("router")
        agent.run(_STANDARD_INPUT)

        history = memory.get_conversation_history()
        assert len(history) >= 1

        # 验证历史中包含用户输入和路由决策
        contents = [msg["content"] for msg in history]
        all_text = " ".join(contents)
        assert "帮我备一节数学课" in all_text
        assert "quick_lesson_prep" in all_text

    def test_factory_router_memory_persists_across_sessions(self, tmp_path):
        """路由决策应持久化到磁盘，跨会话可复用"""
        from maitian_agent.agents.factory import AgentFactory

        # 第一次运行：保存路由决策
        memory1 = _make_real_memory(str(tmp_path))
        factory1 = AgentFactory(
            llm=_make_mock_llm(),
            conversation_memory=memory1,
        )
        agent1 = factory1.create("router")
        agent1.run(_STANDARD_INPUT)

        # 第二次运行：加载历史
        memory2 = _make_real_memory(str(tmp_path))
        history = memory2.get_conversation_history()
        assert len(history) >= 1

        contents = [msg["content"] for msg in history]
        all_text = " ".join(contents)
        assert "quick_lesson_prep" in all_text

    def test_factory_router_no_memory_still_routes(self):
        """通过 Factory 创建的 RouterAgent 无记忆时应正常路由"""
        from maitian_agent.agents.factory import AgentFactory

        factory = AgentFactory(llm=_make_mock_llm())
        agent = factory.create("router")
        result = agent.run(_STANDARD_INPUT)

        assert result["success"] is True
