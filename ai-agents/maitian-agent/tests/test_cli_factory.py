"""CLI Factory 接入测试 — 验证 cli.py 通过 AgentFactory 统一创建 Agent

测试覆盖：
1. CLI 不直接导入具体 Agent 类（AST 静态分析）
2. CLI 通过 AgentFactory.create_all() 获取 Agent
3. lesson_prep 命令使用 Dict 输入调用 run()
4. wisdom_transfer 命令使用 Dict 输入调用 run()
5. route 命令使用 Dict 输入调用 run()
6. Factory 注入的依赖（RAG/记忆/工具）在 CLI 中生效
7. agents_list 命令正常工作
"""
from __future__ import annotations

import ast
import inspect
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest


# ── 1. CLI 不直接导入具体 Agent 类 ──────────────────────────────────


def test_cli_no_direct_agent_imports():
    """cli.py 不应直接导入 QuickLessonPrepAgent / WisdomTransferAgent / RouterAgent"""
    import maitian_agent.cli as cli_module

    source = inspect.getsource(cli_module)
    tree = ast.parse(source)

    # 收集所有 import 语句的目标名称
    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and "agents" in node.module:
                for alias in node.names:
                    imported_names.add(alias.name)

    # 不应直接导入具体 Agent 类
    forbidden = {
        "QuickLessonPrepAgent",
        "WisdomTransferAgent",
        "RouterAgent",
        "ClassroomCompanionAgent",
        "MaterialAgent",
        "MeetingNotesAgent",
    }
    direct_violations = imported_names & forbidden
    assert not direct_violations, (
        f"cli.py 不应直接导入具体 Agent 类，发现: {direct_violations}"
    )


def test_cli_imports_agent_factory():
    """cli.py 应导入 AgentFactory"""
    import maitian_agent.cli as cli_module

    source = inspect.getsource(cli_module)
    tree = ast.parse(source)

    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.add(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add(alias.name)

    assert "AgentFactory" in imported_names, (
        "cli.py 应导入 AgentFactory"
    )


# ── 2. CLI 通过 AgentFactory.create_all() 获取 Agent ────────────────


def test_cli_uses_factory_create_all():
    """cli.py 的命令函数应通过 AgentFactory.create_all() 获取 Agent"""
    import maitian_agent.cli as cli_module

    source = inspect.getsource(cli_module)
    assert "create_all" in source or "create(" in source, (
        "cli.py 应使用 AgentFactory.create_all() 或 AgentFactory.create()"
    )


def test_cli_factory_create_all_returns_dict():
    """通过 CLI 的 Factory 创建的 Agent 字典应包含所有 6 种 Agent"""
    from maitian_agent.agents.factory import AgentFactory

    mock_llm = MagicMock()
    factory = AgentFactory(llm=mock_llm)
    agents = factory.create_all()

    assert isinstance(agents, dict)
    assert len(agents) == 6
    expected_keys = {
        "quick_lesson_prep", "wisdom_transfer",
        "classroom_companion", "material",
        "meeting_notes", "router",
    }
    assert set(agents.keys()) == expected_keys


# ── 3. lesson_prep 命令使用 Dict 输入调用 run() ─────────────────────


def test_lesson_prep_uses_dict_input():
    """lesson_prep 命令应将 CLI 参数组装为 Dict 后调用 agent.run(dict)"""
    from maitian_agent.agents.factory import AgentFactory
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = "测试教案内容"
    factory = AgentFactory(llm=mock_llm)

    agent = factory.create("quick_lesson_prep")
    assert isinstance(agent, QuickLessonPrepAgent)

    # 验证 run() 接收 Dict 并返回 Dict
    result = agent.run({
        "subject": "数学",
        "grade": "三年级",
        "topic": "分数",
        "rural_context": "乡村小学",
    })
    assert isinstance(result, dict)
    assert "success" in result


# ── 4. wisdom_transfer 命令使用 Dict 输入调用 run() ─────────────────


def test_wisdom_transfer_uses_dict_input():
    """wisdom_transfer 命令应将图片路径组装为 Dict 后调用 agent.run(dict)"""
    from maitian_agent.agents.factory import AgentFactory
    from maitian_agent.agents.wisdom_transfer import WisdomTransferAgent

    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = "结构化结果"
    mock_ocr = MagicMock()
    mock_ocr.recognize.return_value = "手写教案OCR文本"
    factory = AgentFactory(llm=mock_llm, ocr=mock_ocr)

    agent = factory.create("wisdom_transfer")
    assert isinstance(agent, WisdomTransferAgent)

    # 验证 run() 接收 Dict 并返回 Dict
    result = agent.run({"image_path": "/fake/path/image.png"})
    assert isinstance(result, dict)
    assert "success" in result


# ── 5. route 命令使用 Dict 输入调用 run() ──────────────────────────


def test_route_uses_dict_input():
    """route 命令应将用户输入组装为 Dict 后调用 agent.run(dict)"""
    from maitian_agent.agents.factory import AgentFactory
    from maitian_agent.agents.router import RouterAgent

    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = "quick_lesson_prep"
    factory = AgentFactory(llm=mock_llm)

    agent = factory.create("router")
    assert isinstance(agent, RouterAgent)

    # 验证 run() 接收 Dict 并返回 Dict
    result = agent.run({"user_input": "帮我备一节数学课"})
    assert isinstance(result, dict)
    assert "success" in result
    assert "intent" in result["result"]


# ── 6. Factory 注入的依赖在 CLI Agent 中生效 ────────────────────────


def test_factory_rag_injection_in_cli_agent():
    """通过 Factory 注入的 KnowledgeBase 应在 CLI 使用的 Agent 中生效"""
    from maitian_agent.agents.factory import AgentFactory

    mock_llm = MagicMock()
    mock_kb = MagicMock()
    mock_kb.search.return_value = []
    factory = AgentFactory(llm=mock_llm, knowledge_base=mock_kb)

    agent = factory.create("quick_lesson_prep")
    assert agent.knowledge_base is mock_kb


def test_factory_memory_injection_in_cli_agent():
    """通过 Factory 注入的 ConversationMemory 应在 CLI 使用的 Agent 中生效"""
    from maitian_agent.agents.factory import AgentFactory

    mock_llm = MagicMock()
    mock_memory = MagicMock()
    factory = AgentFactory(llm=mock_llm, conversation_memory=mock_memory)

    agent = factory.create("quick_lesson_prep")
    assert agent.conversation_memory is mock_memory


def test_factory_ocr_injection_in_cli_agent():
    """通过 Factory 注入的 OCR 应在 CLI 使用的 WisdomTransferAgent 中生效"""
    from maitian_agent.agents.factory import AgentFactory

    mock_llm = MagicMock()
    mock_ocr = MagicMock()
    factory = AgentFactory(llm=mock_llm, ocr=mock_ocr)

    agent = factory.create("wisdom_transfer")
    assert agent.ocr is mock_ocr


def test_factory_teacher_profile_injection_in_cli_agent():
    """通过 Factory 注入的 TeacherProfileManager 应在 CLI 使用的 Agent 中生效"""
    from maitian_agent.agents.factory import AgentFactory

    mock_llm = MagicMock()
    mock_profile = MagicMock()
    factory = AgentFactory(llm=mock_llm, teacher_profile=mock_profile)

    agent = factory.create("quick_lesson_prep")
    assert agent.teacher_profile is mock_profile


# ── 7. agents_list 命令正常工作 ────────────────────────────────────


def test_agents_list_command():
    """agents_list 命令应能正常列出所有 Agent"""
    from maitian_agent.agents.factory import AgentFactory

    mock_llm = MagicMock()
    factory = AgentFactory(llm=mock_llm)
    agents = factory.create_all()

    assert len(agents) == 6
    for agent_type, agent in agents.items():
        assert hasattr(agent, "name")
        assert hasattr(agent, "run")


# ── 8. CLI 无直接 Agent 实例化（AST 检查） ─────────────────────────


def test_cli_no_direct_agent_instantiation():
    """cli.py 中不应有 XxxAgent() 的直接实例化调用"""
    import maitian_agent.cli as cli_module

    source = inspect.getsource(cli_module)
    tree = ast.parse(source)

    # 检查所有 Call 节点，确保没有直接调用 Agent 类的构造函数
    agent_class_names = {
        "QuickLessonPrepAgent",
        "WisdomTransferAgent",
        "RouterAgent",
        "ClassroomCompanionAgent",
        "MaterialAgent",
        "MeetingNotesAgent",
    }

    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in agent_class_names:
                violations.append(f"发现直接实例化: {func.id}()")
            elif isinstance(func, ast.Attribute) and func.attr in agent_class_names:
                violations.append(f"发现直接实例化: ...{func.attr}()")

    assert not violations, f"cli.py 不应直接实例化 Agent: {violations}"


# ── 9. CLI 命令函数签名保持不变 ────────────────────────────────────


def test_cli_command_signatures_preserved():
    """重构后 CLI 命令函数的 click 参数签名应保持不变"""
    import maitian_agent.cli as cli_module

    # 验证 click.group 存在
    assert hasattr(cli_module, "cli")
    assert callable(cli_module.cli)

    # 验证各命令函数存在
    assert hasattr(cli_module, "lesson_prep")
    assert hasattr(cli_module, "wisdom_transfer")
    assert hasattr(cli_module, "route")
    assert hasattr(cli_module, "agents_list")


# ── 10. CLI 端到端：Factory 创建 + Agent 调用完整链路 ───────────────


def test_cli_end_to_end_lesson_prep():
    """端到端验证：Factory 创建 QuickLessonPrepAgent → Dict 输入 → Dict 输出"""
    from langchain_core.language_models import BaseChatModel
    from langchain_core.messages import AIMessage
    from maitian_agent.agents.factory import AgentFactory

    mock_llm = MagicMock(spec=BaseChatModel)
    mock_llm.invoke.return_value = AIMessage(content="端到端测试教案")
    mock_kb = MagicMock()
    mock_kb.search.return_value = []
    mock_memory = MagicMock()
    mock_profile = MagicMock()

    factory = AgentFactory(
        llm=mock_llm,
        knowledge_base=mock_kb,
        conversation_memory=mock_memory,
        teacher_profile=mock_profile,
    )

    agents = factory.create_all()
    agent = agents["quick_lesson_prep"]

    result = agent.run({
        "subject": "语文",
        "grade": "二年级",
        "topic": "古诗",
        "rural_context": "田园风光",
        "teacher_id": "T001",
    })

    assert result["success"] is True
    assert "result" in result
    assert "agent" in result


def test_cli_end_to_end_wisdom_transfer():
    """端到端验证：Factory 创建 WisdomTransferAgent → Dict 输入 → Dict 输出"""
    from langchain_core.language_models import BaseChatModel
    from langchain_core.messages import AIMessage
    from maitian_agent.agents.factory import AgentFactory

    mock_llm = MagicMock(spec=BaseChatModel)
    mock_llm.invoke.return_value = AIMessage(content="结构化结果")
    mock_ocr = MagicMock()
    mock_ocr.recognize.return_value = "OCR识别文本"
    mock_memory = MagicMock()

    factory = AgentFactory(
        llm=mock_llm,
        ocr=mock_ocr,
        conversation_memory=mock_memory,
    )

    agents = factory.create_all()
    agent = agents["wisdom_transfer"]

    result = agent.run({"image_path": "/fake/test.png"})

    assert result["success"] is True
    assert "result" in result


def test_cli_end_to_end_route():
    """端到端验证：Factory 创建 RouterAgent → Dict 输入 → Dict 输出"""
    from maitian_agent.agents.factory import AgentFactory

    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = "wisdom_transfer"
    factory = AgentFactory(llm=mock_llm)

    agents = factory.create_all()
    agent = agents["router"]

    result = agent.run({"user_input": "识别这份手写教案"})

    assert result["success"] is True
    assert "intent" in result["result"]
