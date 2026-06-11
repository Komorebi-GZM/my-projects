"""LocalWhisperASR 本地语音识别测试 — 验证离线转写功能

核心断言：
1. LocalWhisperASR 继承 BaseASR 接口
2. __init__ 不加载模型（按需加载，无阻塞）
3. transcribe() 首次调用时按需加载模型
4. transcribe() 返回转写文本字符串
5. transcribe_with_srt() 返回 SRT 格式字幕
6. 无效音频路径抛出 RuntimeError
7. 与 WhisperASR 接口完全兼容（多态替换）
8. 可通过 AgentFactory 注入 MeetingNotesAgent
"""
from __future__ import annotations

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest


# ── 辅助 ──────────────────────────────────────────────────────────

def _make_mock_llm(response_text: str = "教研报告"):
    """创建 mock LLM"""
    from langchain_core.language_models import BaseChatModel
    from langchain_core.messages import AIMessage
    llm = MagicMock(spec=BaseChatModel)
    llm.invoke.return_value = AIMessage(content=response_text)
    return llm


def _make_wav_file(content: bytes = None) -> str:
    """创建临时 WAV 文件（用于测试）"""
    if content is None:
        content = (
            b"RIFF\x24\x00\x00\x00WAVE"
            b"fmt \x10\x00\x00\x00\x01\x00\x01\x00"
            b"\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00"
            b"data\x00\x00\x00\x00"
        )
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.write(fd, content)
    os.close(fd)
    return path


def _patch_whisper():
    """创建 mock whisper 模型并 patch whisper.load_model"""
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "转写结果", "segments": []}
    return patch("whisper.load_model", return_value=mock_model), mock_model


# ══════════════════════════════════════════════════════════════════
# 1. LocalWhisperASR 接口规范
# ══════════════════════════════════════════════════════════════════

class TestLocalWhisperASRInterface:
    """验证 LocalWhisperASR 遵循 BaseASR 接口"""

    def test_inherits_base_asr(self):
        """LocalWhisperASR 应继承 BaseASR"""
        from maitian_agent.tools.asr import BaseASR, LocalWhisperASR
        assert issubclass(LocalWhisperASR, BaseASR)

    def test_has_transcribe_method(self):
        """LocalWhisperASR 应有 transcribe() 方法"""
        from maitian_agent.tools.asr import LocalWhisperASR
        assert hasattr(LocalWhisperASR, "transcribe")

    def test_has_transcribe_with_srt_method(self):
        """LocalWhisperASR 应有 transcribe_with_srt() 方法"""
        from maitian_agent.tools.asr import LocalWhisperASR
        assert hasattr(LocalWhisperASR, "transcribe_with_srt")


# ══════════════════════════════════════════════════════════════════
# 2. 按需加载 — __init__ 不加载模型
# ══════════════════════════════════════════════════════════════════

class TestLazyLoading:
    """验证模型按需加载，__init__ 不阻塞"""

    def test_init_does_not_load_model(self):
        """__init__ 不应加载 Whisper 模型"""
        from maitian_agent.tools.asr import LocalWhisperASR

        with patch("whisper.load_model") as mock_load:
            asr = LocalWhisperASR(model_name="tiny", device="cpu")
            mock_load.assert_not_called()
            assert asr._model is None

    def test_init_stores_config(self):
        """__init__ 应保存模型配置"""
        from maitian_agent.tools.asr import LocalWhisperASR

        asr = LocalWhisperASR(model_name="base", device="cpu", language="zh")

        assert asr.model_name == "base"
        assert asr.device == "cpu"
        assert asr.language == "zh"

    def test_transcribe_loads_model_on_first_call(self):
        """transcribe() 首次调用时应加载模型"""
        from maitian_agent.tools.asr import LocalWhisperASR

        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "测试转写结果", "segments": []}

        with patch("whisper.load_model", return_value=mock_model) as mock_load:
            asr = LocalWhisperASR(model_name="tiny", device="cpu")
            audio_path = _make_wav_file()

            try:
                asr.transcribe(audio_path)
            finally:
                os.unlink(audio_path)

            mock_load.assert_called_once_with("tiny", device="cpu")
            assert asr._model is mock_model

    def test_transcribe_reuses_loaded_model(self):
        """transcribe() 后续调用应复用已加载的模型"""
        from maitian_agent.tools.asr import LocalWhisperASR

        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "转写结果", "segments": []}

        with patch("whisper.load_model", return_value=mock_model) as mock_load:
            asr = LocalWhisperASR(model_name="tiny", device="cpu")
            audio_path = _make_wav_file()

            try:
                asr.transcribe(audio_path)
                asr.transcribe(audio_path)
            finally:
                os.unlink(audio_path)

            mock_load.assert_called_once()


# ══════════════════════════════════════════════════════════════════
# 3. transcribe() 功能验证
# ══════════════════════════════════════════════════════════════════

class TestTranscribe:
    """验证 transcribe() 返回转写文本"""

    def test_transcribe_returns_string(self):
        """transcribe() 应返回字符串"""
        from maitian_agent.tools.asr import LocalWhisperASR

        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "教研会议记录内容", "segments": []}

        with patch("whisper.load_model", return_value=mock_model):
            asr = LocalWhisperASR(model_name="tiny", device="cpu")
            audio_path = _make_wav_file()

            try:
                result = asr.transcribe(audio_path)
            finally:
                os.unlink(audio_path)

            assert isinstance(result, str)
            assert result == "教研会议记录内容"

    def test_transcribe_passes_language(self):
        """transcribe() 应传递 language 参数"""
        from maitian_agent.tools.asr import LocalWhisperASR

        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "结果", "segments": []}

        with patch("whisper.load_model", return_value=mock_model):
            asr = LocalWhisperASR(model_name="tiny", device="cpu", language="zh")
            audio_path = _make_wav_file()

            try:
                asr.transcribe(audio_path)
            finally:
                os.unlink(audio_path)

            call_kwargs = mock_model.transcribe.call_args[1]
            assert call_kwargs.get("language") == "zh"

    def test_transcribe_invalid_path_raises(self):
        """无效音频路径应抛出 RuntimeError"""
        from maitian_agent.tools.asr import LocalWhisperASR

        mock_model = MagicMock()
        mock_model.transcribe.side_effect = FileNotFoundError("文件不存在")

        with patch("whisper.load_model", return_value=mock_model):
            asr = LocalWhisperASR(model_name="tiny", device="cpu")

            with pytest.raises(RuntimeError, match="音频转写失败"):
                asr.transcribe("/nonexistent/audio.wav")


# ══════════════════════════════════════════════════════════════════
# 4. transcribe_with_srt() 功能验证
# ══════════════════════════════════════════════════════════════════

class TestTranscribeWithSRT:
    """验证 transcribe_with_srt() 返回 SRT 字幕"""

    def test_transcribe_with_srt_returns_string(self):
        """transcribe_with_srt() 应返回 SRT 格式字符串"""
        from maitian_agent.tools.asr import LocalWhisperASR

        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "测试字幕",
            "segments": [
                {"start": 0.0, "end": 5.0, "text": "第一句话"},
                {"start": 5.5, "end": 10.0, "text": "第二句话"},
            ],
        }

        with patch("whisper.load_model", return_value=mock_model):
            asr = LocalWhisperASR(model_name="tiny", device="cpu")
            audio_path = _make_wav_file()

            try:
                result = asr.transcribe_with_srt(audio_path)
            finally:
                os.unlink(audio_path)

            assert isinstance(result, str)
            assert "00:00:00,000 --> 00:00:05,000" in result
            assert "第一句话" in result
            assert "第二句话" in result

    def test_transcribe_with_srt_empty_segments(self):
        """无 segments 时应返回空字符串"""
        from maitian_agent.tools.asr import LocalWhisperASR

        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "", "segments": []}

        with patch("whisper.load_model", return_value=mock_model):
            asr = LocalWhisperASR(model_name="tiny", device="cpu")
            audio_path = _make_wav_file()

            try:
                result = asr.transcribe_with_srt(audio_path)
            finally:
                os.unlink(audio_path)

            assert result == ""

    def test_transcribe_with_srt_calls_model(self):
        """transcribe_with_srt 应调用 whisper 模型"""
        from maitian_agent.tools.asr import LocalWhisperASR

        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "内容", "segments": []}

        with patch("whisper.load_model", return_value=mock_model):
            asr = LocalWhisperASR(model_name="tiny", device="cpu")
            audio_path = _make_wav_file()

            try:
                asr.transcribe_with_srt(audio_path)
            finally:
                os.unlink(audio_path)

            mock_model.transcribe.assert_called_once()


# ══════════════════════════════════════════════════════════════════
# 5. 接口兼容 — 与 WhisperASR 多态替换
# ══════════════════════════════════════════════════════════════════

class TestPolymorphicCompatibility:
    """验证 LocalWhisperASR 与 WhisperASR 接口兼容"""

    def test_both_have_transcribe(self):
        """两种 ASR 都应有 transcribe() 方法"""
        from maitian_agent.tools.asr import WhisperASR, LocalWhisperASR
        assert hasattr(WhisperASR, "transcribe")
        assert hasattr(LocalWhisperASR, "transcribe")

    def test_both_inherit_base_asr(self):
        """两种 ASR 都应继承 BaseASR"""
        from maitian_agent.tools.asr import BaseASR, WhisperASR, LocalWhisperASR
        assert issubclass(WhisperASR, BaseASR)
        assert issubclass(LocalWhisperASR, BaseASR)


# ══════════════════════════════════════════════════════════════════
# 6. 端到端：AgentFactory + LocalWhisperASR → MeetingNotesAgent
# ══════════════════════════════════════════════════════════════════

class TestEndToEndFactoryInjection:
    """端到端验证：AgentFactory 注入 LocalWhisperASR"""

    def test_factory_injects_local_asr(self):
        """AgentFactory 应能注入 LocalWhisperASR"""
        from maitian_agent.agents.factory import AgentFactory
        from maitian_agent.tools.asr import LocalWhisperASR

        mock_asr = MagicMock(spec=LocalWhisperASR)
        mock_asr.transcribe.return_value = "会议转写文本"

        factory = AgentFactory(llm=_make_mock_llm(), asr=mock_asr)
        agent = factory.create("meeting_notes")

        assert agent.asr is mock_asr

    def test_meeting_notes_with_local_asr(self):
        """MeetingNotesAgent 使用 LocalWhisperASR 应正常转写"""
        from maitian_agent.agents.factory import AgentFactory
        from maitian_agent.tools.asr import LocalWhisperASR

        mock_asr = MagicMock(spec=LocalWhisperASR)
        mock_asr.transcribe.return_value = "今天讨论了教学方法的改进"

        factory = AgentFactory(llm=_make_mock_llm("教研报告"), asr=mock_asr)
        agent = factory.create("meeting_notes")
        result = agent.run({"audio_path": "/fake/meeting.wav"})

        assert result["success"] is True
        mock_asr.transcribe.assert_called_once_with("/fake/meeting.wav")

    def test_factory_switch_between_online_and_local(self):
        """AgentFactory 应支持在线/本地 ASR 切换"""
        from maitian_agent.agents.factory import AgentFactory
        from maitian_agent.tools.asr import BaseASR

        online_asr = MagicMock(spec=BaseASR)
        factory_online = AgentFactory(llm=_make_mock_llm(), asr=online_asr)
        agent_online = factory_online.create("meeting_notes")
        assert agent_online.asr is online_asr

        local_asr = MagicMock(spec=BaseASR)
        factory_local = AgentFactory(llm=_make_mock_llm(), asr=local_asr)
        agent_local = factory_local.create("meeting_notes")
        assert agent_local.asr is local_asr
