"""
LLM 客户端统一工厂。
"""

from __future__ import annotations

import os
from typing import ClassVar

from .base import BaseLLMClient
from .deepseek_client import DeepSeekClient
from .ollama_client import OllamaClient
from .openai_client import OpenAIClient


class LLMClientFactory:
    """
    LLM 客户端统一工厂。

    根据配置创建合适的 LLM 客户端实例。
    """

    _clients: ClassVar[dict[str, type[BaseLLMClient]]] = {
        "deepseek": DeepSeekClient,
        "openai": OpenAIClient,
        "ollama": OllamaClient,
    }

    @classmethod
    def register(cls, provider: str, client_class: type[BaseLLMClient]) -> None:
        """注册新的客户端实现"""
        cls._clients[provider.lower()] = client_class

    @classmethod
    def create(
        cls,
        provider: str = "deepseek",
        model: str = "deepseek-chat",
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: int = 15,
        temperature: float = 0.1,
        max_retries: int = 3,
    ) -> BaseLLMClient:
        """
        创建 LLM 客户端实例。

        Args:
            provider: 服务提供商 (deepseek, openai, ollama)
            model: 模型名称
            api_key: API 密钥
            base_url: 自定义 API 地址
            timeout: 超时时间（秒）
            temperature: 生成温度
            max_retries: 最大重试次数

        Returns:
            配置好的 LLM 客户端实例

        Raises:
            ValueError: 不支持的提供商
        """
        provider_lower = provider.lower()
        client_class = cls._clients.get(provider_lower)
        if client_class is None:
            raise ValueError(f"不支持的 LLM 提供商: {provider}")

        if api_key is None:
            env_key = os.getenv("CHESS_LLM_API_KEY")
            if env_key:
                api_key = env_key

        return client_class(
            model=model,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            temperature=temperature,
            max_retries=max_retries,
        )

    @classmethod
    def list_providers(cls) -> list[str]:
        """获取所有已注册的提供商列表"""
        return list(cls._clients.keys())

    @classmethod
    def get_client_class(cls, provider: str) -> type[BaseLLMClient] | None:
        """获取指定提供商的客户端类"""
        return cls._clients.get(provider.lower())


__all__ = ["LLMClientFactory"]
