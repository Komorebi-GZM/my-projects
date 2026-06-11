"""
DeepSeek LLM 客户端实现
"""

from __future__ import annotations

from typing import Any

from .base import BaseLLMClient
from .models import MoveRequest
from .prompt import PromptBuilder


class DeepSeekClient(BaseLLMClient):
    """
    DeepSeek API 客户端

    使用 DeepSeek 的 Chat Completions API
    官方文档: https://platform.deepseek.com/api-docs/
    """

    def _build_request_payload(self, request: MoveRequest) -> dict[str, Any]:
        """构建 DeepSeek 请求负载"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": self._build_prompt(request),
                }
            ],
            "temperature": self.temperature,
            "max_tokens": 512,  # 我们只需要少量 token
            "stream": False,
        }
        return payload

    def _build_prompt(self, request: MoveRequest) -> str:
        """构建 Prompt（此处可委托给 PromptBuilder）"""
        # 为了简化，这里直接调用外部 PromptBuilder
        # 实际项目中可以通过依赖注入或全局实例获取
        return PromptBuilder.build(request)

    def _parse_response(self, response_data: dict[str, Any]) -> str:
        """解析 DeepSeek 响应数据"""
        # DeepSeek API 响应格式与 OpenAI 兼容
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
        base = self.base_url.rstrip("/") if self.base_url else "https://api.deepseek.com"
        return f"{base}/v1/chat/completions"

    def _get_health_endpoint(self) -> str:
        """获取健康检查端点（使用 models 端点）"""
        base = self.base_url.rstrip("/") if self.base_url else "https://api.deepseek.com"
        return f"{base}/v1/models"
