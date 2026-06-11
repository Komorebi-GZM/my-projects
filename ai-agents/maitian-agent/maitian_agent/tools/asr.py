"""
语音识别工具
基于Whisper API
"""

import os
from abc import ABC, abstractmethod
from typing import Optional


class BaseASR(ABC):
    """语音识别基类"""

    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        """转写音频"""
        pass


class WhisperASR(BaseASR):
    """Whisper语音识别

    支持OpenAI Whisper API和本地Whisper模型
    """

    def __init__(
        self,
        model: str = "base",
        api_key: Optional[str] = None,
        api_base: str = "https://api.openai.com/v1",
        language: str = "zh",
    ):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_base = api_base
        self.language = language
        self._client = None

    @property
    def client(self):
        """获取OpenAI客户端"""
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key, base_url=self.api_base)
        return self._client

    def transcribe(self, audio_path: str) -> str:
        """转写音频文件

        Args:
            audio_path: 音频文件路径

        Returns:
            转写文本
        """
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=self.model, file=audio_file, language=self.language
                )
            return transcript.text
        except Exception as e:
            raise RuntimeError(f"音频转写失败: {str(e)}")

    def transcribe_with_srt(self, audio_path: str) -> str:
        """转写音频并生成SRT字幕

        Args:
            audio_path: 音频文件路径

        Returns:
            SRT格式字幕
        """
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=self.model, file=audio_file, language=self.language, response_format="srt"
                )
            return transcript
        except Exception as e:
            raise RuntimeError(f"字幕生成失败: {str(e)}")


class LocalWhisperASR(BaseASR):
    """本地 Whisper 模型语音识别

    基于 openai-whisper 实现离线音频转写，无需网络连接。
    模型按需加载（lazy loading），首次调用 transcribe() 时才加载模型。

    用法::

        asr = LocalWhisperASR(model_name="base", device="cpu", language="zh")
        text = asr.transcribe("/path/to/audio.wav")

    通过 AgentFactory 注入::

        factory = AgentFactory(asr=LocalWhisperASR(model_name="base"))
        agent = factory.create("meeting_notes")
    """

    def __init__(
        self,
        model_name: str = "base",
        device: str = "cpu",
        language: Optional[str] = "zh",
    ):
        self.model_name = model_name
        self.device = device
        self.language = language
        self._model = None

    def _load_model(self):
        """按需加载 Whisper 模型（首次调用时触发）"""
        if self._model is not None:
            return

        import whisper

        logger_info = f"加载本地 Whisper 模型: {self.model_name} (device={self.device})"
        import logging

        logging.getLogger(__name__).info(logger_info)

        self._model = whisper.load_model(self.model_name, device=self.device)

    def transcribe(self, audio_path: str) -> str:
        """转写音频文件（离线）

        Args:
            audio_path: 音频文件路径

        Returns:
            转写文本

        Raises:
            RuntimeError: 音频文件不存在或转写失败
        """
        self._load_model()

        try:
            kwargs = {}
            if self.language:
                kwargs["language"] = self.language

            result = self._model.transcribe(audio_path, **kwargs)
            return result["text"].strip()
        except Exception as e:
            raise RuntimeError(f"音频转写失败: {str(e)}")

    def transcribe_with_srt(self, audio_path: str) -> str:
        """转写音频并生成 SRT 字幕

        Args:
            audio_path: 音频文件路径

        Returns:
            SRT 格式字幕文本

        Raises:
            RuntimeError: 音频转写失败
        """
        self._load_model()

        try:
            kwargs = {}
            if self.language:
                kwargs["language"] = self.language

            result = self._model.transcribe(audio_path, **kwargs)

            # 从 whisper 结果构建 SRT 格式
            segments = result.get("segments", [])
            if not segments:
                return ""

            srt_lines = []
            for i, seg in enumerate(segments, 1):
                start = self._format_timestamp(seg["start"])
                end = self._format_timestamp(seg["end"])
                srt_lines.append(f"{i}")
                srt_lines.append(f"{start} --> {end}")
                srt_lines.append(seg["text"].strip())
                srt_lines.append("")

            return "\n".join(srt_lines)
        except Exception as e:
            raise RuntimeError(f"字幕生成失败: {str(e)}")

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """将秒数格式化为 SRT 时间戳 HH:MM:SS,mmm"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
