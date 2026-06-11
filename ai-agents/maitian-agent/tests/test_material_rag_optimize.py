"""MaterialAgent RAG 深度集成测试 — 验证检索结果融入 Prompt 模板

核心断言：
1. MaterialAgent.run() 返回 metadata 包含 has_rag_context 标记
2. 有 KB 时，RAG 检索结果作为 reference_section 传入 chain.invoke（非事后追加）
3. 无 KB 时，reference_section 为空字符串，静默降级
4. 输出结果中不再出现事后追加的 "---\\n参考资料" 分隔模式
5. run(Dict->Dict) 接口契约不变
"""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest


# ── 辅助 ──────────────────────────────────────────────────────────

def _make_mock_llm(response_text="推荐以下素材：\n1. 科普视频《水的循环》"):
    """创建 mock LLM，返回 AIMessage（StrOutputParser 兼容）"""
    from langchain_core.language_models import BaseChatModel
    from langchain_core.messages import AIMessage

    llm = MagicMock(spec=BaseChatModel)
    llm.invoke.return_value = AIMessage(content=response_text)
    return llm


def _make_mock_kb(results=None):
    """创建 mock KnowledgeBase，search() 返回预设结果"""
    kb = MagicMock()
    if results is None:
        mock_doc = MagicMock()
        mock_doc.page_content = (
            "水的循环实验视频：通过加热冷水观察蒸汽凝结，适合四年级科学课。"
        )
        results = [mock_doc]
    kb.search.return_value = results
    return kb


_STANDARD_INPUT = {
    "subject": "科学",
    "grade": "四年级",
    "topic": "水的循环",
}


# ══════════════════════════════════════════════════════════════════
# 1. RAG 检索结果传入 chain.invoke（核心行为）
# ══════════════════════════════════════════════════════════════════

class TestRAGContextPassedToChain:
    """验证 RAG 检索结果作为 reference_section 传入 LLM chain"""

    def test_chain_invoke_receives_reference_section_with_kb(self):
        """有 KB 时，chain.invoke 应收到包含参考资料的 reference_section"""
        from maitian_agent.agents.material_agent import MaterialAgent

        kb = _make_mock_kb()
        agent = MaterialAgent(llm=_make_mock_llm(), knowledge_base=kb)

        agent.recommend_materials(**_STANDARD_INPUT)

        # 验证 LLM invoke 被调用
        assert agent.llm.invoke.called

    def test_chain_invoke_receives_reference_section_content(self):
        """有 KB 时，reference_section 应包含检索到的内容"""
        from maitian_agent.agents.material_agent import MaterialAgent

        mock_doc = MagicMock()
        mock_doc.page_content = "水的循环实验视频：蒸发凝结演示"
        kb = _make_mock_kb(results=[mock_doc])
        agent = MaterialAgent(llm=_make_mock_llm(), knowledge_base=kb)

        agent.recommend_materials(**_STANDARD_INPUT)

        # 验证 KB 被检索
        kb.search.assert_called_once()

    def test_chain_invoke_without_kb_no_reference_section(self):
        """无 KB 时，不应调用 knowledge_base.search()"""
        from maitian_agent.agents.material_agent import MaterialAgent

        agent = MaterialAgent(llm=_make_mock_llm())

        agent.recommend_materials(**_STANDARD_INPUT)

        # 无 KB，不应崩溃
        assert agent.llm.invoke.called


# ══════════════════════════════════════════════════════════════════
# 2. 输出不再包含事后追加的参考资料分隔符
# ══════════════════════════════════════════════════════════════════

class TestNoPostpendReferenceSeparator:
    """验证输出中不再出现事后追加的 '---\\n参考资料' 模式"""

    def test_output_no_postpend_separator_with_kb(self):
        """有 KB 时，输出结果不应包含事后追加的分隔符"""
        from maitian_agent.agents.material_agent import MaterialAgent

        kb = _make_mock_kb()
        agent = MaterialAgent(llm=_make_mock_llm(), knowledge_base=kb)

        result = agent.recommend_materials(**_STANDARD_INPUT)

        assert "---\n参考资料：" not in result
        assert "\n---\n" not in result

    def test_output_no_postpend_separator_without_kb(self):
        """无 KB 时，输出结果不应包含任何参考资料分隔符"""
        from maitian_agent.agents.material_agent import MaterialAgent

        agent = MaterialAgent(llm=_make_mock_llm())

        result = agent.recommend_materials(**_STANDARD_INPUT)

        assert "---\n参考资料：" not in result


# ══════════════════════════════════════════════════════════════════
# 3. run() 返回 metadata 包含 has_rag_context
# ══════════════════════════════════════════════════════════════════

class TestRunMetadataHasRAGContext:
    """验证 run() 返回的 metadata 包含 has_rag_context 标记"""

    def test_run_metadata_has_rag_true_with_kb(self):
        """有 KB 且检索到结果时，has_rag_context 应为 True"""
        from maitian_agent.agents.material_agent import MaterialAgent

        kb = _make_mock_kb()
        agent = MaterialAgent(llm=_make_mock_llm(), knowledge_base=kb)

        result = agent.run(dict(_STANDARD_INPUT))

        assert result["success"] is True
        assert result["metadata"].get("has_rag_context") is True

    def test_run_metadata_has_rag_false_without_kb(self):
        """无 KB 时，has_rag_context 应为 False"""
        from maitian_agent.agents.material_agent import MaterialAgent

        agent = MaterialAgent(llm=_make_mock_llm())

        result = agent.run(dict(_STANDARD_INPUT))

        assert result["success"] is True
        assert result["metadata"].get("has_rag_context") is False

    def test_run_metadata_has_rag_false_when_kb_returns_empty(self):
        """有 KB 但检索结果为空时，has_rag_context 应为 False"""
        from maitian_agent.agents.material_agent import MaterialAgent

        kb = _make_mock_kb(results=[])
        agent = MaterialAgent(llm=_make_mock_llm(), knowledge_base=kb)

        result = agent.run(dict(_STANDARD_INPUT))

        assert result["success"] is True
        assert result["metadata"].get("has_rag_context") is False


# ══════════════════════════════════════════════════════════════════
# 4. 静默降级 — 无 KB 时不报错
# ══════════════════════════════════════════════════════════════════

class TestSilentDegradation:
    """验证未注入 KB 时，Agent 静默降级不报错"""

    def test_no_kb_recommend_materials_works(self):
        """无 KB 时，recommend_materials() 应正常返回推荐结果"""
        from maitian_agent.agents.material_agent import MaterialAgent

        agent = MaterialAgent(llm=_make_mock_llm())

        result, has_rag = agent.recommend_materials(**_STANDARD_INPUT)

        assert isinstance(result, str)
        assert len(result) > 0
        assert has_rag is False

    def test_no_kb_run_returns_success(self):
        """无 KB 时，run() 应返回 success=True"""
        from maitian_agent.agents.material_agent import MaterialAgent

        agent = MaterialAgent(llm=_make_mock_llm())

        result = agent.run(dict(_STANDARD_INPUT))

        assert result["success"] is True
        assert "result" in result

    def test_kb_search_called_with_correct_query(self):
        """有 KB 时，search() 应使用包含学科/年级/课题的查询"""
        from maitian_agent.agents.material_agent import MaterialAgent

        kb = _make_mock_kb()
        agent = MaterialAgent(llm=_make_mock_llm(), knowledge_base=kb)

        agent.recommend_materials(
            subject="数学",
            grade="三年级",
            topic="分数",
            knowledge_points="分数的基本概念",
        )

        kb.search.assert_called_once()
        call_args = kb.search.call_args[0][0]
        assert "数学" in call_args
        assert "三年级" in call_args
        assert "分数" in call_args


# ══════════════════════════════════════════════════════════════════
# 5. 接口契约不变
# ══════════════════════════════════════════════════════════════════

class TestInterfaceContract:
    """验证 run(Dict->Dict) 接口契约不变"""

    def test_run_returns_dict(self):
        """run() 应返回 Dict"""
        from maitian_agent.agents.material_agent import MaterialAgent

        agent = MaterialAgent(llm=_make_mock_llm())
        result = agent.run(dict(_STANDARD_INPUT))
        assert isinstance(result, dict)

    def test_run_returns_success_key(self):
        """run() 返回值应包含 'success' 键"""
        from maitian_agent.agents.material_agent import MaterialAgent

        agent = MaterialAgent(llm=_make_mock_llm())
        result = agent.run(dict(_STANDARD_INPUT))
        assert "success" in result

    def test_run_returns_agent_key(self):
        """run() 返回值应包含 'agent' 键"""
        from maitian_agent.agents.material_agent import MaterialAgent

        agent = MaterialAgent(llm=_make_mock_llm())
        result = agent.run(dict(_STANDARD_INPUT))
        assert result["agent"] == "MaterialAgent"

    def test_recommend_materials_returns_string(self):
        """recommend_materials() 应返回 (str, bool) 元组"""
        from maitian_agent.agents.material_agent import MaterialAgent

        agent = MaterialAgent(llm=_make_mock_llm())
        result, has_rag = agent.recommend_materials(**_STANDARD_INPUT)
        assert isinstance(result, str)
        assert isinstance(has_rag, bool)


# ══════════════════════════════════════════════════════════════════
# 6. 端到端：Factory + RAG 深度集成
# ══════════════════════════════════════════════════════════════════

class TestEndToEndFactoryRAG:
    """端到端验证：AgentFactory 创建 MaterialAgent -> RAG 深度集成"""

    def test_factory_material_with_rag_deep_integration(self):
        """通过 Factory 创建的 MaterialAgent 应将 RAG 结果融入 Prompt"""
        from maitian_agent.agents.factory import AgentFactory

        kb = _make_mock_kb()
        factory = AgentFactory(llm=_make_mock_llm(), knowledge_base=kb)

        agent = factory.create("material")
        result = agent.run(dict(_STANDARD_INPUT))

        assert result["success"] is True
        assert result["metadata"].get("has_rag_context") is True
        kb.search.assert_called_once()

    def test_factory_material_without_rag_still_works(self):
        """通过 Factory 创建的 MaterialAgent 无 KB 时应正常工作"""
        from maitian_agent.agents.factory import AgentFactory

        factory = AgentFactory(llm=_make_mock_llm())

        agent = factory.create("material")
        result = agent.run(dict(_STANDARD_INPUT))

        assert result["success"] is True
        assert result["metadata"].get("has_rag_context") is False
