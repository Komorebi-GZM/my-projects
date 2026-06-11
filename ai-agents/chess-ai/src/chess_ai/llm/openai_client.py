"""
OpenAI LLM 客户端实现
"""

from __future__ import annotations

from typing import Any

from .base import BaseLLMClient
from .models import MoveRequest
from .prompt import PromptBuilder


class OpenAIClient(BaseLLMClient):
    """
    OpenAI API 客户端

    使用 OpenAI 的 Chat Completions API
    官方文档: https://platform.openai.com/docs/api-reference/chat
    """

    def _build_request_payload(self, request: MoveRequest) -> dict[str, Any]:
        """构建 OpenAI 请求负载"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self._build_system_prompt(request),
                },
                {
                    "role": "user",
                    "content": self._build_user_prompt(request),
                },
            ],
            "temperature": self.temperature,
            "max_tokens": 512,
            "stream": False,
        }
        return payload

    def _build_system_prompt(self, request: MoveRequest) -> str:
        """构建系统 Prompt"""
        return PromptBuilder.build_system_prompt(request.prompt_version)

    def _build_user_prompt(self, request: MoveRequest) -> str:
        """构建用户 Prompt"""
        return PromptBuilder.build(request)

    def _parse_response(self, response_data: dict[str, Any]) -> str:
        """解析 OpenAI 响应数据"""
        choices = response_data.get("choices", [])
        if not choices:
            raise ValueError("API 响应中没有 choices")

        message = choices[0].get("message", {})
        content = message.get("content", "")
        if not content:
            raise ValueError("API 响应中没有 content")

        return content  # type: ignore[no-any-return]

    def _get_completion_endpoint(self) -> str:
        """获取补全 API 端点"""
        base = self.base_url.rstrip("/") if self.base_url else "https://api.openai.com"
        # 如果 base_url 已包含 /v1，避免重复拼接
        if base.endswith("/v1"):
            return f"{base}/chat/completions"
        return f"{base}/v1/chat/completions"

    def _get_health_endpoint(self) -> str:
        """获取健康检查端点"""
        base = self.base_url.rstrip("/") if self.base_url else "https://api.openai.com"
        if base.endswith("/v1"):
            return f"{base}/models"
        return f"{base}/v1/models"
