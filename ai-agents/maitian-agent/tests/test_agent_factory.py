"""AgentFactory 测试 — 验证工厂模式创建 Agent 及依赖注入"""
from unittest.mock import MagicMock, patch, PropertyMock

import pytest


# ── 1.1: AgentFactory 可创建所有 6 种 Agent ────────────────────────

@pytest.mark.parametrize("agent_type", [
    "quick_lesson_prep",
    "wisdom_transfer",
    "classroom_companion",
    "material",
    "meeting_notes",
    "router",
])
def test_factory_creates_all_agent_types(agent_type):
    """AgentFactory.create() 能创建所有 6 种 Agent 类型"""
    from maitian_agent.agents.factory import AgentFactory

    factory = AgentFactory()
    agent = factory.create(agent_type)
    assert agent is not None
    assert hasattr(agent, "run")
    assert hasattr(agent, "name")


# ── 1.2: 创建未知 Agent 类型抛出 ValueError ────────────────────────

def test_factory_raises_on_unknown_type():
    """创建未知 Agent 类型时应抛出 ValueError"""
    from maitian_agent.agents.factory import AgentFactory

    factory = AgentFactory()
    with pytest.raises(ValueError, match="未知.*Agent"):
        factory.create("nonexistent_agent")


# ── 1.3: AgentFactory 注入 settings ────────────────────────────────

def test_factory_injects_settings():
    """AgentFactory 创建的 Agent 应携带注入的 settings"""
    from maitian_agent.config.settings import Settings
    from maitian_agent.agents.factory import AgentFactory

    settings = Settings(openai_api_key="factory-key", model_name="factory-model")
    factory = AgentFactory(settings=settings)

    with patch("langchain_openai.ChatOpenAI") as MockChatOpenAI:
        MockChatOpenAI.return_value = MagicMock()
        agent = factory.create("quick_lesson_prep")
        assert agent.settings is settings


# ── 1.4: AgentFactory 注入自定义 LLM ───────────────────────────────

def test_factory_injects_custom_llm():
    """AgentFactory 创建的 Agent 应使用注入的 LLM"""
    from maitian_agent.agents.factory import AgentFactory

    mock_llm = MagicMock()
    factory = AgentFactory(llm=mock_llm)

    agent = factory.create("quick_lesson_prep")
    assert agent.llm is mock_llm


# ── 1.5: AgentFactory 注入 KnowledgeBase ───────────────────────────

def test_factory_injects_knowledge_base():
    """AgentFactory 创建的 Agent 应能访问注入的 KnowledgeBase"""
    from maitian_agent.agents.factory import AgentFactory

    mock_kb = MagicMock()
    factory = AgentFactory(knowledge_base=mock_kb, llm=MagicMock())

    agent = factory.create("quick_lesson_prep")
    assert agent.knowledge_base is mock_kb


# ── 1.6: AgentFactory 注入 ConversationMemory ──────────────────────

def test_factory_injects_conversation_memory():
    """AgentFactory 创建的 Agent 应能访问注入的 ConversationMemory"""
    from maitian_agent.agents.factory import AgentFactory

    mock_memory = MagicMock()
    factory = AgentFactory(conversation_memory=mock_memory, llm=MagicMock())

    agent = factory.create("quick_lesson_prep")
    assert agent.conversation_memory is mock_memory


# ── 1.7: AgentFactory 注入 TeacherProfileManager ───────────────────

def test_factory_injects_teacher_profile():
    """AgentFactory 创建的 Agent 应能访问注入的 TeacherProfileManager"""
    from maitian_agent.agents.factory import AgentFactory

    mock_profile = MagicMock()
    factory = AgentFactory(teacher_profile=mock_profile, llm=MagicMock())

    agent = factory.create("quick_lesson_prep")
    assert agent.teacher_profile is mock_profile


# ── 1.8: AgentFactory 注入 OCR 工具 ───────────────────────────────

def test_factory_injects_ocr():
    """AgentFactory 创建 WisdomTransferAgent 时应注入 OCR 工具"""
    from maitian_agent.agents.factory import AgentFactory

    mock_ocr = MagicMock()
    factory = AgentFactory(ocr=mock_ocr, llm=MagicMock())

    agent = factory.create("wisdom_transfer")
    assert agent.ocr is mock_ocr


# ── 1.9: AgentFactory 注入 ASR 工具 ───────────────────────────────

def test_factory_injects_asr():
    """AgentFactory 创建 MeetingNotesAgent 时应注入 ASR 工具"""
    from maitian_agent.agents.factory import AgentFactory

    mock_asr = MagicMock()
    factory = AgentFactory(asr=mock_asr, llm=MagicMock())

    agent = factory.create("meeting_notes")
    assert agent.asr is mock_asr


# ── 1.10: 工厂创建的 Agent 保持 run(Dict)->Dict 契约 ──────────────

def test_factory_agent_run_returns_dict():
    """工厂创建的 Agent 的 run() 方法应返回 Dict"""
    from maitian_agent.agents.factory import AgentFactory

    mock_llm = MagicMock()
    factory = AgentFactory(llm=mock_llm)

    agent = factory.create("quick_lesson_prep")
    result = agent.run({
        "subject": "数学",
        "grade": "三年级",
        "topic": "分数",
    })
    assert isinstance(result, dict)
    assert "success" in result


# ── 1.11: 工厂创建的 RouterAgent 正常路由 ─────────────────────────

def test_factory_router_agent_routes():
    """工厂创建的 RouterAgent 应能正常路由"""
    from maitian_agent.agents.factory import AgentFactory

    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = "quick_lesson_prep"
    factory = AgentFactory(llm=mock_llm)

    agent = factory.create("router")
    result = agent.run({"user_input": "帮我备一节数学课"})
    assert result["success"] is True
    assert "intent" in result["result"]


# ── 1.12: AgentFactory.create_all() 创建所有 Agent ────────────────

def test_factory_create_all_returns_dict():
    """AgentFactory.create_all() 应返回包含所有 Agent 的字典"""
    from maitian_agent.agents.factory import AgentFactory

    factory = AgentFactory(llm=MagicMock())
    agents = factory.create_all()

    assert isinstance(agents, dict)
    assert len(agents) == 6
    expected_keys = {
        "quick_lesson_prep", "wisdom_transfer",
        "classroom_companion", "material",
        "meeting_notes", "router",
    }
    assert set(agents.keys()) == expected_keys


# ── 1.13: 无 LLM 时 AgentFactory 自动创建默认 LLM ────────────────

def test_factory_auto_creates_llm_when_none():
    """不传 llm 时，AgentFactory 应自动通过 settings 创建默认 LLM"""
    from maitian_agent.agents.factory import AgentFactory

    factory = AgentFactory()

    with patch("langchain_openai.ChatOpenAI") as MockChatOpenAI, \
         patch("maitian_agent.config.settings.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.model_name = "deepseek-v2"
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_api_base = "https://api.deepseek.com"
        mock_get_settings.return_value = mock_settings

        MockChatOpenAI.return_value = MagicMock()
        agent = factory.create("quick_lesson_prep")
        assert agent.llm is not None


# ── 1.14: 各 Agent 使用正确的温度 ─────────────────────────────────

@pytest.mark.parametrize("agent_type,expected_temp", [
    ("quick_lesson_prep", 0.7),
    ("wisdom_transfer", 0.3),
    ("classroom_companion", 0.5),
    ("material", 0.7),
    ("meeting_notes", 0.3),
    ("router", 0.1),
])
def test_factory_agent_temperatures(agent_type, expected_temp):
    """工厂创建的各 Agent 应使用正确的默认温度"""
    from maitian_agent.agents.factory import AgentFactory

    factory = AgentFactory()

    with patch("langchain_openai.ChatOpenAI") as MockChatOpenAI, \
         patch("maitian_agent.config.settings.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.model_name = "deepseek-v2"
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_api_base = "https://api.deepseek.com"
        mock_get_settings.return_value = mock_settings

        MockChatOpenAI.return_value = MagicMock()
        factory.create(agent_type)

        call_kwargs = MockChatOpenAI.call_args[1]
        assert call_kwargs["temperature"] == expected_temp, \
            f"{agent_type} expected {expected_temp}, got {call_kwargs['temperature']}"
