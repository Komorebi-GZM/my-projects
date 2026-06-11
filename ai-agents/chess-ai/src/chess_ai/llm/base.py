"""
LLM 客户端基类。
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any

import httpx

from .models import HealthStatus, LLMError, LLMErrorType, MoveRequest, MoveResponse


class LLMClientError(Exception):
    """LLM 客户端异常"""

    def __init__(
        self,
        message: str,
        error_type: str = LLMErrorType.SERVICE_ERROR,
        retryable: bool = True,
        original_error: Exception | None = None,
    ):
        super().__init__(message)
        self.error_type = error_type
        self.retryable = retryable
        self.original_error = original_error


class BaseLLMClient(ABC):
    """
    LLM 客户端抽象基类。

    所有具体模型客户端必须继承此类并实现抽象方法。
    """

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: int = 15,
        temperature: float = 0.1,
        max_retries: int = 3,
    ):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.temperature = temperature
        self.max_retries = max_retries
        self._client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.Client:
        """获取同步 HTTP 客户端（延迟初始化）"""
        if self._client is None:
            timeout = httpx.Timeout(
                connect=10.0,
                read=self.timeout,
                write=10.0,
                pool=5.0,
            )
            self._client = httpx.Client(
                base_url=self.base_url or "",
                timeout=timeout,
                headers=self._default_headers,
                verify=False,
            )
        return self._client

    @property
    def _default_headers(self) -> dict[str, str]:
        """默认请求头"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ChessAI/1.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    @abstractmethod
    def _build_request_payload(self, request: MoveRequest) -> dict:
        """构建模型特定的请求负载"""
        ...

    @abstractmethod
    def _parse_response(self, response_data: dict) -> str:
        """解析模型特定的响应数据，提取原始输出文本"""
        ...

    def invoke(self, request: MoveRequest) -> MoveResponse:
        """
        同步调用 LLM 生成走子。

        Args:
            request: 走子请求

        Returns:
            MoveResponse 包含走子结果
        """
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        start_time = time.time()
        last_error: LLMError | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                payload = self._build_request_payload(request)
                response = self.client.post(
                    self._get_completion_endpoint(),
                    json=payload,
                )
                response.raise_for_status()

                response_data = response.json()
                raw_output = self._parse_response(response_data)

                latency_ms = int((time.time() - start_time) * 1000)

                return MoveResponse(
                    move=None,
                    source="llm",
                    raw_output=raw_output,
                    provider=self.__class__.__name__.replace("Client", "").lower(),
                    latency_ms=latency_ms,
                    token_usage=response_data.get("usage", {}),
                )

            except httpx.TimeoutException as e:
                last_error = LLMError(
                    error_type=LLMErrorType.TIMEOUT,
                    message=f"请求超时 (尝试 {attempt}/{self.max_retries}): {e}",
                    retryable=attempt < self.max_retries,
                    original_error=e,
                )
                logger.warning(last_error.message)

            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                error_type = LLMErrorType.RATE_LIMIT if status == 429 else LLMErrorType.SERVICE_ERROR
                last_error = LLMError(
                    error_type=error_type,
                    message=f"HTTP {status} 错误 (尝试 {attempt}/{self.max_retries}): {e}",
                    retryable=attempt < self.max_retries and error_type == LLMErrorType.RATE_LIMIT,
                    original_error=e,
                )
                logger.error(last_error.message)

            except Exception as e:
                last_error = LLMError(
                    error_type=LLMErrorType.SERVICE_ERROR,
                    message=f"调用异常 (尝试 {attempt}/{self.max_retries}): {e}",
                    retryable=attempt < self.max_retries,
                    original_error=e,
                )
                logger.error(last_error.message)

            if last_error and last_error.retryable and attempt < self.max_retries:
                wait_time = min(2 ** (attempt - 1), 10)
                time.sleep(wait_time)

        return MoveResponse(
            move=None,
            source="error",
            raw_output=None,
            provider=self.__class__.__name__.replace("Client", "").lower(),
            latency_ms=int((time.time() - start_time) * 1000),
            error_message=str(last_error) if last_error else "未知错误",
        )

    def health_check(self) -> HealthStatus:
        """
        健康检查。

        Returns:
            HealthStatus 包含可用性和延迟信息
        """
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        try:
            start_time = time.time()
            response = self.client.get(self._get_health_endpoint())
            latency_ms = int((time.time() - start_time) * 1000)

            return HealthStatus(
                provider=self.__class__.__name__.replace("Client", "").lower(),
                available=response.status_code == 200,
                latency_ms=latency_ms,
            )
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return HealthStatus(
                provider=self.__class__.__name__.replace("Client", "").lower(),
                available=False,
                error=str(e),
            )

    @abstractmethod
    def _get_completion_endpoint(self) -> str:
        """获取补全 API 端点"""
        ...

    @abstractmethod
    def _get_health_endpoint(self) -> str:
        """获取健康检查端点"""
        ...

    def close(self) -> None:
        """关闭 HTTP 客户端连接"""
        if self._client is not None:
            self._client.close()
            self._client = None
        if self._async_client is not None:
            if asyncio.get_event_loop().is_running():
                asyncio.create_task(self._async_client.aclose())  # noqa: RUF006
            else:
                asyncio.get_event_loop().run_until_complete(self._async_client.aclose())
            self._async_client = None

    def __enter__(self) -> BaseLLMClient:
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any | None) -> None:
        self.close()
