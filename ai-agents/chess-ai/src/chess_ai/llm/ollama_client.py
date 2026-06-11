"""
Ollama 本地 LLM 客户端实现
"""

from __future__ import annotations

from typing import Any

from .base import BaseLLMClient
from .models import MoveRequest
from .prompt import PromptBuilder


class OllamaClient(BaseLLMClient):
    """
    Ollama 本地模型客户端

    通过 Ollama 的 HTTP API 调用本地部署的模型
    官方文档: https://github.com/ollama/ollama/blob/main/docs/api.md
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Ollama 不需要 API Key
        if "api_key" not in kwargs or not kwargs.get("api_key"):
            kwargs["api_key"] = ""  # Ollama 通常不需要 API Key
        super().__init__(*args, **kwargs)
        # Ollama 默认超时需要更长（本地模型较慢）
        if kwargs.get("timeout", 15) == 15:
            self.timeout = 30  # 本地模型给更长时间

    def _build_request_payload(self, request: MoveRequest) -> dict[str, Any]:
        """构建 Ollama 请求负载"""
        payload = {
            "model": self.model,
            "prompt": self._build_prompt(request),
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": 128,  # 限制输出长度（我们只需要少量字符）
            },
        }
        # 添加系统提示（Ollama 支持）
        payload["system"] = "你是中国象棋AI。请严格按格式输出走子坐标，仅输出4字符UCCI坐标，禁止任何其他文字。"

        return payload

    def _build_prompt(self, request: MoveRequest) -> str:
        """构建 Prompt"""
        return PromptBuilder.build(request)

    def _parse_response(self, response_data: dict[str, Any]) -> str:
        """解析 Ollama 响应数据"""
        # Ollama API 响应格式
        content = response_data.get("response", "")
        if not content:
            # 尝试备用字段
            content = response_data.get("content", "")
        if not content:
            raise ValueError("Ollama 响应中没有 response/content")

        return content  # type: ignore[no-any-return]

    def _get_completion_endpoint(self) -> str:
        """获取补全 API 端点"""
        base = self.base_url.rstrip("/") if self.base_url else "http://localhost:11434"
        return f"{base}/api/generate"

    def _get_health_endpoint(self) -> str:
        """获取健康检查端点"""
        base = self.base_url.rstrip("/") if self.base_url else "http://localhost:11434"
        return f"{base}/api/tags"

    def get_available_models(self) -> list[str]:
        """
        获取本地可用的模型列表

        Returns:
            可用模型名称列表
        """

        response = self.client.get(self._get_health_endpoint())
        response.raise_for_status()
        data = response.json()

        models = data.get("models", [])
        return [m.get("name", "") for m in models]
