import os
from dotenv import load_dotenv
from agents.llm_config import get_llm_settings

load_dotenv()
llm_settings = get_llm_settings()


class Config:
    LLM_API_KEY: str = llm_settings.api_key
    LLM_MODEL: str = llm_settings.model
    LLM_BASE_URL: str = llm_settings.base_url
    LLM_MAX_TOKENS: int = llm_settings.max_tokens
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    TRACE_LEVEL: str = os.getenv("TRACE_LEVEL", "basic")
    MOCK_HIGH_PRIORITY_RATE: float = float(os.getenv("MOCK_HIGH_PRIORITY_RATE", "0.95"))
    MOCK_LOW_PRIORITY_RATE: float = float(os.getenv("MOCK_LOW_PRIORITY_RATE", "0.80"))
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    USE_REAL_APIS: bool = os.getenv("USE_REAL_APIS", "true").lower() == "true"
    REAL_API_TIMEOUT: int = int(os.getenv("REAL_API_TIMEOUT", "5"))
    REAL_API_RETRIES: int = int(os.getenv("REAL_API_RETRIES", "1"))
    NOMINATIM_USER_AGENT: str = os.getenv("NOMINATIM_USER_AGENT", "LocalLifeAgent/1.0")


config = Config()
