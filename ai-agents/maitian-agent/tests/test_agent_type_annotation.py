"""Agent LLM 类型注解统一性测试 — 验证全项目使用 BaseChatModel

核心断言：
1. 所有业务 Agent 的 __init__ llm 参数类型为 Optional[BaseChatModel]
2. 业务 Agent 文件中不包含顶层 `from langchain_openai import ChatOpenAI`
3. BaseAgent.__init__ llm 参数类型为 Optional[BaseChatModel]（已有行为）
4. 任意 BaseChatModel 子类可作为 llm 注入（多态扩展性）
5. 功能兼容：注入 BaseChatModel mock 后 Agent 正常运行
"""
from __future__ import annotations

import ast
import inspect
from unittest.mock import MagicMock

import pytest


# ── 目标 Agent 列表 ─────────────────────────────────────────────

_AGENT_CLASSES = {
    "QuickLessonPrepAgent": "maitian_agent.agents.quick_lesson_prep",
    "WisdomTransferAgent": "maitian_agent.agents.wisdom_transfer",
    "ClassroomCompanionAgent": "maitian_agent.agents.classroom_companion",
    "MaterialAgent": "maitian_agent.agents.material_agent",
    "MeetingNotesAgent": "maitian_agent.agents.meeting_notes",
    "RouterAgent": "maitian_agent.agents.router",
}

_AGENT_MODULES = [
    "maitian_agent.agents.base",
    "maitian_agent.agents.quick_lesson_prep",
    "maitian_agent.agents.wisdom_transfer",
    "maitian_agent.agents.classroom_companion",
    "maitian_agent.agents.material_agent",
    "maitian_agent.agents.meeting_notes",
    "maitian_agent.agents.router",
]


# ── 辅助 ──────────────────────────────────────────────────────────

def _make_mock_llm(response_text: str = "测试结果"):
    """创建 mock LLM（BaseChatModel spec）"""
    from langchain_core.language_models import BaseChatModel
    from langchain_core.messages import AIMessage
    llm = MagicMock(spec=BaseChatModel)
    llm.invoke.return_value = AIMessage(content=response_text)
    return llm


def _check_llm_annotation(module_path: str) -> bool:
    """AST 分析：检查模块中 Agent.__init__ 的 llm 参数是否使用 BaseChatModel

    Returns True 如果 llm 参数注解包含 'BaseChatModel'，False 如果包含 'ChatOpenAI'
    """
    import importlib
    module = importlib.import_module(module_path)
    source = inspect.getsource(module)
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            for arg in node.args.args:
                if arg.arg == "llm" and arg.annotation is not None:
                    annotation_str = ast.dump(arg.annotation)
                    if "ChatOpenAI" in annotation_str:
                        return False
                    if "BaseChatModel" in annotation_str:
                        return True
    return False


# ══════════════════════════════════════════════════════════════════
# 1. 所有 Agent 的 llm 参数使用 BaseChatModel 类型注解
# ══════════════════════════════════════════════════════════════════

class TestAgentLLMTypeAnnotation:
    """验证所有 Agent 的 llm 参数使用 BaseChatModel 类型注解"""

    @pytest.mark.parametrize("module_path", _AGENT_MODULES)
    def test_llm_annotation_uses_base_chat_model(self, module_path):
        """{module_path} 的 __init__ llm 参数应使用 BaseChatModel"""
        assert _check_llm_annotation(module_path), (
            f"{module_path} 的 llm 参数未使用 BaseChatModel 类型注解"
        )

    @pytest.mark.parametrize("module_path", _AGENT_MODULES)
    def test_llm_annotation_not_chat_openai(self, module_path):
        """{module_path} 的 __init__ llm 参数不应使用 ChatOpenAI"""
        import importlib
        module = importlib.import_module(module_path)
        source = inspect.getsource(module)
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                for arg in node.args.args:
                    if arg.arg == "llm" and arg.annotation is not None:
                        annotation_str = ast.dump(arg.annotation)
                        assert "ChatOpenAI" not in annotation_str, (
                            f"{module_path}.__init__ llm 参数仍使用 ChatOpenAI，"
                            f"应改为 BaseChatModel"
                        )


# ══════════════════════════════════════════════════════════════════
# 2. 业务 Agent 文件中不包含顶层 ChatOpenAI 导入
# ══════════════════════════════════════════════════════════════════

class TestNoTopLevelChatOpenAIImport:
    """验证业务 Agent 文件中无顶层 ChatOpenAI 导入"""

    @pytest.mark.parametrize("module_path", _AGENT_MODULES)
    def test_no_top_level_chat_openai_import(self, module_path):
        """{module_path} 不应包含顶层 `from langchain_openai import ChatOpenAI`"""
        import importlib
        module = importlib.import_module(module_path)
        source = inspect.getsource(module)
        tree = ast.parse(source)

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == "langchain_openai":
                    imported_names = {alias.name for alias in node.names}
                    assert "ChatOpenAI" not in imported_names, (
                        f"{module_path} 包含顶层 `from langchain_openai import ChatOpenAI`，"
                        f"应使用 BaseChatModel 类型注解替代"
                    )


# ══════════════════════════════════════════════════════════════════
# 3. 多态扩展性 — 任意 BaseChatModel 子类可注入
# ══════════════════════════════════════════════════════════════════

class TestPolymorphicLLMInjection:
    """验证任意 BaseChatModel 子类可作为 llm 注入"""

    @pytest.mark.parametrize("class_name,module_path", list(_AGENT_CLASSES.items()))
    def test_agent_accepts_base_chat_model_mock(self, class_name, module_path):
        """{class_name} 应接受 BaseChatModel mock 作为 llm"""
        import importlib
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)

        agent = cls(llm=_make_mock_llm())
        assert agent.llm is not None

    def test_factory_injects_base_chat_model(self):
        """AgentFactory 应接受 BaseChatModel 子类"""
        from maitian_agent.agents.factory import AgentFactory

        mock_llm = _make_mock_llm()
        factory = AgentFactory(llm=mock_llm)
        agent = factory.create("quick_lesson_prep")

        assert agent.llm is mock_llm

    def test_agent_run_with_mock_base_chat_model(self):
        """Agent 使用 BaseChatModel mock 应正常运行"""
        from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

        agent = QuickLessonPrepAgent(llm=_make_mock_llm())
        result = agent.run({
            "subject": "数学",
            "grade": "三年级",
            "topic": "分数",
        })

        assert result["success"] is True
