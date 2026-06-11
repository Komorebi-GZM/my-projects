"""
LLM 模块 - Pydantic 数据模型定义
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

MoveRequest_Side = Literal["red", "black"]
MoveResponse_Source = Literal["llm", "rule_engine_fallback", "error"]


@dataclass
class MoveRequest:
    """走子请求标准入参"""

    fen: str
    side: MoveRequest_Side
    valid_moves: list[str] = field(default_factory=list)
    history: list[str] = field(default_factory=list)
    prompt_version: Literal["minimal", "fewshot", "structured"] = "minimal"
    thread_id: str = ""
    difficulty: str = "medium"


@dataclass
class MoveResponse:
    """走子响应标准出参"""

    move: str | None
    source: MoveResponse_Source
    raw_output: str | None = None
    provider: str = "unknown"
    latency_ms: int = 0
    token_usage: dict[str, int] = field(default_factory=dict)
    error_message: str | None = None


@dataclass
class HealthStatus:
    """健康检查状态"""

    provider: str
    available: bool
    latency_ms: int = 0
    error: str | None = None


class LLMErrorType:
    """LLM 错误类型枚举"""

    FORMAT_VIOLATION = "format_violation"
    PARSE_FAILURE = "parse_failure"
    INVALID_MOVE = "invalid_move"
    TIMEOUT = "timeout"
    SERVICE_ERROR = "service_error"
    RATE_LIMIT = "rate_limit"
    CONFIG_ERROR = "config_error"


@dataclass
class LLMError:
    """LLM 错误信息"""

    error_type: str
    message: str
    retryable: bool = True
    original_error: Exception | None = None


ERROR_HANDLING = {
    LLMErrorType.FORMAT_VIOLATION: {
        "action": "log_and_retry",
        "max_retries": 1,
        "fallback": "rule_engine",
    },
    LLMErrorType.PARSE_FAILURE: {
        "action": "log_and_fallback",
        "fallback": "rule_engine",
    },
    LLMErrorType.INVALID_MOVE: {
        "action": "log_and_fallback",
        "fallback": "rule_engine",
    },
    LLMErrorType.TIMEOUT: {
        "action": "immediate_fallback",
        "fallback": "rule_engine",
    },
    LLMErrorType.SERVICE_ERROR: {
        "action": "exponential_backoff",
        "max_retries": 3,
        "fallback": "rule_engine",
    },
    LLMErrorType.RATE_LIMIT: {
        "action": "exponential_backoff",
        "max_retries": 2,
        "fallback": "rule_engine",
    },
}
