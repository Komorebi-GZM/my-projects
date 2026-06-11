"""pytest 共享 fixtures — 所有外部 API 调用通过 mock 隔离"""
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def mock_llm():
    """Mock 大模型调用，返回预设文本"""
    with patch("maitian_agent.agents.quick_lesson_prep.ChatOpenAI") as MockChatOpenAI:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = "这是一份测试教案内容..."
        MockChatOpenAI.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_ocr():
    """Mock OCR 识别，返回预设文本（BaseOCR 接口）"""
    mock_ocr_instance = MagicMock()
    mock_ocr_instance.recognize.return_value = "三年级数学教案\n课题：分数的认识"
    yield mock_ocr_instance


@pytest.fixture
def mock_asr():
    """Mock Whisper ASR，返回预设转写文本"""
    with patch("maitian_agent.tools.asr.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        mock_client.audio.transcriptions.create.return_value.text = "这是一段测试会议记录..."
        MockOpenAI.return_value = mock_client
        yield mock_client


@pytest.fixture
def tmp_chroma_dir(tmp_path):
    """创建临时 Chroma 持久化目录"""
    chroma_dir = tmp_path / "chroma"
    chroma_dir.mkdir()
    return str(chroma_dir)
