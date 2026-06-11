"""差异化重试管理器。

DEV_GUIDE 6.2 节定义的标准重试策略：
- 高优 API（search_poi / book_poi）：最多重试 2 次，指数退避 (1s, 2s)
- 低优 API（get_reviews / get_poi_detail）：最多重试 1 次，固定 1s 间隔
- LLM 调用：最多重试 2 次（在 llm_client.py 内部已实现）
"""

import time
import functools
import structlog
from typing import Callable, Any, Optional

logger = structlog.get_logger()


class RetryConfig:
    """重试配置。"""

    def __init__(
        self,
        max_retries: int = 2,
        base_delay: float = 1.0,
        backoff_factor: float = 2.0,
        retryable_exceptions: tuple = (Exception,),
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor
        self.retryable_exceptions = retryable_exceptions


# 预定义的重试策略
HIGH_PRIORITY_RETRY = RetryConfig(
    max_retries=2,
    base_delay=1.0,
    backoff_factor=2.0,
)

LOW_PRIORITY_RETRY = RetryConfig(
    max_retries=1,
    base_delay=1.0,
    backoff_factor=1.0,  # 固定间隔
)

BRAINSTORM_RETRY = RetryConfig(
    max_retries=1,
    base_delay=0.5,
    backoff_factor=1.0,
)


def retry_with_strategy(
    config: RetryConfig,
    trace_id: Optional[str] = None,
    operation_name: str = "unknown"
):
    """差异化重试装饰器。

    Args:
        config: 重试配置（HIGH_PRIORITY_RETRY / LOW_PRIORITY_RETRY / 自定义）
        trace_id: 链路追踪 ID
        operation_name: 操作名称，用于日志记录

    Usage:
        @retry_with_strategy(HIGH_PRIORITY_RETRY, operation_name="search_poi")
        def call_search_poi(keyword: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error = None
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_error = e
                    if attempt < config.max_retries:
                        delay = config.base_delay * (config.backoff_factor ** attempt)
                        logger.warning(
                            "retry_attempt",
                            trace_id=trace_id,
                            operation=operation_name,
                            attempt=attempt + 1,
                            max_retries=config.max_retries,
                            delay_s=delay,
                            error=str(e),
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            "retry_exhausted",
                            trace_id=trace_id,
                            operation=operation_name,
                            max_retries=config.max_retries,
                            error=str(e),
                        )
            raise last_error  # type: ignore
        return wrapper
    return decorator
