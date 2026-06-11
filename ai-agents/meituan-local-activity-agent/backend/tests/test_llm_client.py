import os
import sys
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def mock_env():
    old_base_url = os.environ.pop("LLM_BASE_URL", None)
    old_api_key = os.environ.pop("LLM_API_KEY", None)
    old_mock = os.environ.pop("MOCK_LLM", None)
    old_max_tokens = os.environ.pop("LLM_MAX_TOKENS", None)
    old_model = os.environ.pop("LLM_MODEL", None)
    os.environ["LLM_API_KEY"] = "test-key"
    os.environ["LLM_BASE_URL"] = "https://llm.example.com/v1"
    os.environ["LLM_MODEL"] = "qwen-plus"
    os.environ["MOCK_LLM"] = "false"
    yield
    _restore_env("LLM_BASE_URL", old_base_url)
    _restore_env("LLM_API_KEY", old_api_key)
    _restore_env("MOCK_LLM", old_mock)
    _restore_env("LLM_MAX_TOKENS", old_max_tokens)
    _restore_env("LLM_MODEL", old_model)


def _restore_env(name, value):
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value


def _mock_openai_module(response_text="测试响应"):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = response_text
    mock_client.chat.completions.create.return_value = mock_response

    mock_openai_module = MagicMock()
    mock_openai_module.OpenAI.return_value = mock_client
    return mock_openai_module, mock_client


def _reload_module():
    import importlib
    if "agents.llm_client" in sys.modules:
        importlib.reload(sys.modules["agents.llm_client"])
    else:
        import agents.llm_client


def test_call_llm_success():
    mock_openai_module, mock_client = _mock_openai_module("测试响应")

    with patch.dict("sys.modules", {"openai": mock_openai_module}):
        _reload_module()
        from agents.llm_client import call_llm
        result = call_llm(prompt="测试提示")

    assert result == "测试响应"
    mock_openai_module.OpenAI.assert_called_once_with(
        api_key="test-key",
        base_url="https://llm.example.com/v1",
    )
    mock_client.chat.completions.create.assert_called_once()


def test_call_llm_failure_with_retry():
    mock_openai_module, mock_client = _mock_openai_module("成功")
    mock_client.chat.completions.create.side_effect = [
        ValueError("Internal Server Error"),
        mock_client.chat.completions.create.return_value,
    ]

    with patch.dict("sys.modules", {"openai": mock_openai_module}):
        _reload_module()
        from agents.llm_client import call_llm
        result = call_llm(prompt="测试提示", max_retries=1)

    assert result == "成功"
    assert mock_client.chat.completions.create.call_count == 2


def test_llm_settings_stays_openai_compatible_without_base_url():
    from agents.llm_config import get_llm_settings

    settings = get_llm_settings({
        "LLM_API_KEY": "test-key",
        "LLM_MODEL": "qwen-plus",
        "LLM_BASE_URL": "",
    })

    assert settings.provider == "openai_compatible"
    assert settings.base_url == ""


def test_llm_settings_accept_any_openai_compatible_base_url():
    from agents.llm_config import get_llm_settings

    settings = get_llm_settings({
        "LLM_API_KEY": "test-key",
        "LLM_MODEL": "provider-model",
        "LLM_BASE_URL": "https://llm.example.com/v1",
        "LLM_MAX_TOKENS": "4096",
    })

    assert settings.provider == "openai_compatible"
    assert settings.base_url == "https://llm.example.com/v1"
    assert settings.max_tokens == 4096


def test_call_llm_openai_compatible_client():
    os.environ["LLM_BASE_URL"] = "https://llm.example.com/v1"
    os.environ["LLM_MODEL"] = "provider-model"
    os.environ["LLM_MAX_TOKENS"] = "4096"

    mock_openai_module, mock_client = _mock_openai_module("通用响应")

    with patch.dict("sys.modules", {"openai": mock_openai_module}):
        _reload_module()
        from agents.llm_client import call_llm

        result = call_llm(prompt="测试提示", temperature=0.2)

    assert result == "通用响应"
    mock_openai_module.OpenAI.assert_called_once_with(
        api_key="test-key",
        base_url="https://llm.example.com/v1",
    )
    mock_client.chat.completions.create.assert_called_once_with(
        model="provider-model",
        messages=[{"role": "user", "content": "测试提示"}],
        temperature=0.2,
        max_tokens=4096,
    )


def test_missing_api_key_has_team_onboarding_message():
    from agents.llm_config import get_llm_settings

    settings = get_llm_settings({
        "LLM_API_KEY": "",
        "LLM_MODEL": "qwen-plus",
    })

    with pytest.raises(ValueError, match="backend/.env.example"):
        settings.validate_for_runtime()


def test_missing_base_url_has_team_onboarding_message():
    from agents.llm_config import get_llm_settings

    settings = get_llm_settings({
        "LLM_API_KEY": "test-key",
        "LLM_BASE_URL": "",
        "LLM_MODEL": "qwen-plus",
    })

    with pytest.raises(ValueError, match="LLM_BASE_URL is required"):
        settings.validate_for_runtime()


def test_parse_dict_from_response():
    from agents.llm_client import parse_dict_from_response

    response = "{'key': 'value', 'num': 123}"
    result = parse_dict_from_response(response)
    assert result == {"key": "value", "num": 123}
