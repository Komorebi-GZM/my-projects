"""配置注入测试 — 验证所有 Agent 通过 Settings 注入获取配置"""
import importlib
import inspect
from unittest.mock import MagicMock, patch, ANY

import pytest

# 延迟导入的 patch 路径：ChatOpenAI 和 get_settings 在 _create_default_llm() 内部导入
_CHATOPENAI_PATCH = "langchain_openai.ChatOpenAI"
_GET_SETTINGS_PATCH = "maitian_agent.config.settings.get_settings"


# ── 1.1: BaseAgent 接受并存储 settings ──────────────────────────────

def test_base_agent_accepts_settings_parameter():
    """BaseAgent.__init__ 接受 settings 参数并存储为 self.settings"""
    from maitian_agent.config.settings import Settings
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

    settings = Settings(openai_api_key="test-key", model_name="test-model")
    agent = QuickLessonPrepAgent(settings=settings, llm=MagicMock())
    assert agent.settings is settings


# ── 1.2: 不传 settings 时默认 None ─────────────────────────────────

def test_base_agent_settings_default_none():
    """不传 settings 时，self.settings 应为 None（向后兼容）"""
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

    agent = QuickLessonPrepAgent(llm=MagicMock())
    assert agent.settings is None


# ── 1.3: _create_default_llm 使用注入的 settings ────────────────────

def test_create_default_llm_uses_settings():
    """传入 settings 时，_create_default_llm() 应使用 settings 中的配置创建 ChatOpenAI"""
    from maitian_agent.config.settings import Settings
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

    settings = Settings(
        openai_api_key="custom-key",
        openai_api_base="https://custom.api/v1",
        model_name="custom-model",
    )
    agent = QuickLessonPrepAgent(settings=settings, llm=MagicMock())

    with patch(_CHATOPENAI_PATCH) as MockChatOpenAI:
        mock_instance = MagicMock()
        MockChatOpenAI.return_value = mock_instance
        llm = agent._create_default_llm()

        MockChatOpenAI.assert_called_once_with(
            model="custom-model",
            api_key=ANY,  # SecretStr 包装，值在下方单独验证
            base_url="https://custom.api/v1",
            temperature=0.7,
        )
        # 验证 api_key 被 SecretStr 包装且值正确
        actual_key = MockChatOpenAI.call_args[1]["api_key"]
        assert actual_key.get_secret_value() == "custom-key"
        assert llm is mock_instance


# ── 1.4: 无 settings 时回退到 get_settings() ───────────────────────

def test_create_default_llm_without_settings_uses_get_settings():
    """不传 settings 时，_create_default_llm() 应回退到 get_settings() 全局实例"""
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

    agent = QuickLessonPrepAgent(llm=MagicMock())

    with patch(_GET_SETTINGS_PATCH) as mock_get_settings, \
         patch(_CHATOPENAI_PATCH) as MockChatOpenAI:
        mock_settings = MagicMock()
        mock_settings.model_name = "deepseek-v2"
        mock_settings.openai_api_key = "env-key"
        mock_settings.openai_api_base = "https://api.deepseek.com"
        mock_get_settings.return_value = mock_settings

        agent._create_default_llm()

        MockChatOpenAI.assert_called_once_with(
            model="deepseek-v2",
            api_key=ANY,  # SecretStr 包装，值在下方单独验证
            base_url="https://api.deepseek.com",
            temperature=0.7,
        )
        # 验证 api_key 被 SecretStr 包装且值正确
        actual_key = MockChatOpenAI.call_args[1]["api_key"]
        assert actual_key.get_secret_value() == "env-key"


# ── 1.5: temperature 参数覆盖默认值 ───────────────────────────────

def test_create_default_llm_temperature_override():
    """_create_default_llm(temperature=0.1) 应使用传入的温度而非默认温度"""
    from maitian_agent.config.settings import Settings
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

    settings = Settings(openai_api_key="key", model_name="model")
    agent = QuickLessonPrepAgent(settings=settings, llm=MagicMock())

    with patch(_CHATOPENAI_PATCH) as MockChatOpenAI:
        agent._create_default_llm(temperature=0.1)
        call_kwargs = MockChatOpenAI.call_args[1]
        assert call_kwargs["temperature"] == 0.1


# ── 1.6: 6 个 Agent 源码不含 os.getenv / load_dotenv ──────────────

@pytest.mark.parametrize("module_path", [
    "maitian_agent.agents.quick_lesson_prep",
    "maitian_agent.agents.wisdom_transfer",
    "maitian_agent.agents.classroom_companion",
    "maitian_agent.agents.material_agent",
    "maitian_agent.agents.meeting_notes",
    "maitian_agent.agents.router",
])
def test_agent_no_os_getenv_imports(module_path):
    """重构后 6 个 Agent 模块中不再有 os.getenv 和 load_dotenv 调用"""
    mod = importlib.import_module(module_path)
    source = inspect.getsource(mod)
    assert "os.getenv" not in source, f"{module_path} still contains os.getenv()"
    assert "load_dotenv" not in source, f"{module_path} still contains load_dotenv()"


# ── 1.7: 不传 llm 时通过 _create_default_llm 创建 ─────────────────

@pytest.mark.parametrize("agent_class,module_path", [
    ("QuickLessonPrepAgent", "maitian_agent.agents.quick_lesson_prep"),
    ("WisdomTransferAgent", "maitian_agent.agents.wisdom_transfer"),
    ("ClassroomCompanionAgent", "maitian_agent.agents.classroom_companion"),
    ("MaterialAgent", "maitian_agent.agents.material_agent"),
    ("MeetingNotesAgent", "maitian_agent.agents.meeting_notes"),
    ("RouterAgent", "maitian_agent.agents.router"),
])
def test_agent_uses_create_default_llm_when_no_llm(agent_class, module_path):
    """不传 llm 也不传 settings 时，Agent 应通过 _create_default_llm() 创建 LLM"""
    mod = __import__(module_path, fromlist=[agent_class])
    cls = getattr(mod, agent_class)

    with patch(_CHATOPENAI_PATCH) as MockChatOpenAI, \
         patch(_GET_SETTINGS_PATCH) as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.model_name = "deepseek-v2"
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_api_base = "https://api.deepseek.com"
        mock_get_settings.return_value = mock_settings

        mock_instance = MagicMock()
        MockChatOpenAI.return_value = mock_instance

        agent = cls()
        assert agent.llm is mock_instance


# ── 1.8: 各 Agent 使用正确的默认温度 ──────────────────────────────

@pytest.mark.parametrize("agent_class,module_path,expected_temp", [
    ("QuickLessonPrepAgent", "maitian_agent.agents.quick_lesson_prep", 0.7),
    ("WisdomTransferAgent", "maitian_agent.agents.wisdom_transfer", 0.3),
    ("ClassroomCompanionAgent", "maitian_agent.agents.classroom_companion", 0.5),
    ("MaterialAgent", "maitian_agent.agents.material_agent", 0.7),
    ("MeetingNotesAgent", "maitian_agent.agents.meeting_notes", 0.3),
    ("RouterAgent", "maitian_agent.agents.router", 0.1),
])
def test_agent_temperature_values(agent_class, module_path, expected_temp):
    """验证每个 Agent 使用正确的默认温度"""
    mod = __import__(module_path, fromlist=[agent_class])
    cls = getattr(mod, agent_class)

    with patch(_CHATOPENAI_PATCH) as MockChatOpenAI, \
         patch(_GET_SETTINGS_PATCH) as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.model_name = "deepseek-v2"
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_api_base = "https://api.deepseek.com"
        mock_get_settings.return_value = mock_settings

        cls()
        call_kwargs = MockChatOpenAI.call_args[1]
        assert call_kwargs["temperature"] == expected_temp, \
            f"{agent_class} expected temperature {expected_temp}, got {call_kwargs['temperature']}"


# ── 1.9: 注入 settings 覆盖环境变量 ───────────────────────────────

def test_settings_injection_overrides_env():
    """传入 settings 时，Agent 应使用 settings 的值而非环境变量"""
    from maitian_agent.config.settings import Settings
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

    settings = Settings(
        openai_api_key="injected-key",
        model_name="injected-model",
        openai_api_base="https://injected.api/v1",
    )

    with patch(_CHATOPENAI_PATCH) as MockChatOpenAI:
        QuickLessonPrepAgent(settings=settings)
        call_kwargs = MockChatOpenAI.call_args[1]
        assert call_kwargs["api_key"].get_secret_value() == "injected-key"
        assert call_kwargs["model"] == "injected-model"
        assert call_kwargs["base_url"] == "https://injected.api/v1"


# ── 1.10: 显式 llm 参数优先级最高 ─────────────────────────────────

def test_explicit_llm_still_takes_priority():
    """同时传入 llm 和 settings 时，llm 优先（向后兼容）"""
    from maitian_agent.config.settings import Settings
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

    mock_llm = MagicMock()
    settings = Settings(openai_api_key="injected-key")

    with patch(_CHATOPENAI_PATCH) as MockChatOpenAI:
        agent = QuickLessonPrepAgent(llm=mock_llm, settings=settings)
        assert agent.llm is mock_llm
        MockChatOpenAI.assert_not_called()
