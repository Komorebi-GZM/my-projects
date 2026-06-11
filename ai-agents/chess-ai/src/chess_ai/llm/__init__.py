# chess_ai.llm package - LLM 接入模块

from .base import BaseLLMClient, LLMClientError
from .client import LLMClientFactory

# 注册具体客户端到工厂
from .deepseek_client import DeepSeekClient
from .models import (
    ERROR_HANDLING,
    HealthStatus,
    LLMError,
    LLMErrorType,
    MoveRequest,
    MoveRequest_Side,
    MoveResponse,
    MoveResponse_Source,
)
from .ollama_client import OllamaClient
from .openai_client import OpenAIClient
from .parser import MoveOutputParser
from .prompt import PROMPT_TEMPLATES, PromptBuilder, select_prompt_version

__all__ = [
    "ERROR_HANDLING",
    "PROMPT_TEMPLATES",
    # 客户端
    "BaseLLMClient",
    "DeepSeekClient",
    "HealthStatus",
    "LLMClientError",
    "LLMClientFactory",
    "LLMError",
    "LLMErrorType",
    # 解析器
    "MoveOutputParser",
    # 数据模型
    "MoveRequest",
    "MoveRequest_Side",
    "MoveResponse",
    "MoveResponse_Source",
    "OllamaClient",
    "OpenAIClient",
    # Prompt
    "PromptBuilder",
    "select_prompt_version",
]
