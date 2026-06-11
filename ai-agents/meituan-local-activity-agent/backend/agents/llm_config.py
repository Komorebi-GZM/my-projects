import os
from dataclasses import dataclass
from typing import Mapping, Optional


@dataclass(frozen=True)
class LLMSettings:
    api_key: str
    model: str
    base_url: str = ""
    max_tokens: int = 2048
    force_temperature: Optional[float] = None

    @property
    def provider(self) -> str:
        return "openai_compatible"

    def normalize_temperature(self, temperature: float) -> float:
        if self.force_temperature is not None:
            return self.force_temperature
        return temperature

    def validate_for_runtime(self) -> None:
        if not self.api_key.strip():
            raise ValueError(
                "LLM_API_KEY is required. Copy backend/.env.example to "
                "backend/.env and fill in your model platform API key."
            )
        if not self.base_url.strip():
            raise ValueError(
                "LLM_BASE_URL is required. Fill in the OpenAI-compatible /v1 "
                "endpoint from your model platform in backend/.env."
            )
        if not self.model.strip():
            raise ValueError("LLM_MODEL is required.")


def get_llm_settings(env: Mapping[str, str] = os.environ) -> LLMSettings:
    """Build isolated OpenAI-compatible LLM settings from environment variables."""
    model = env.get("LLM_MODEL", "qwen-plus").strip() or "qwen-plus"
    base_url = env.get("LLM_BASE_URL", "").strip()
    max_tokens = _parse_int(env.get("LLM_MAX_TOKENS"), default=2048)
    force_temperature = _parse_force_temperature(env, model)

    return LLMSettings(
        api_key=env.get("LLM_API_KEY", ""),
        model=model,
        base_url=base_url,
        max_tokens=max_tokens,
        force_temperature=force_temperature,
    )


def _parse_int(value: Optional[str], default: int) -> int:
    if value is None or value.strip() == "":
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"LLM_MAX_TOKENS must be an integer (got {value!r})") from exc
    if parsed <= 0:
        raise ValueError("LLM_MAX_TOKENS must be greater than 0")
    return parsed


def _parse_force_temperature(env: Mapping[str, str], model: str) -> Optional[float]:
    raw_value = env.get("LLM_FORCE_TEMPERATURE", "").strip()
    if raw_value:
        try:
            return float(raw_value)
        except ValueError as exc:
            raise ValueError(
                f"LLM_FORCE_TEMPERATURE must be a number (got {raw_value!r})"
            ) from exc

    # Some OpenAI-compatible providers reject arbitrary temperatures.
    if "kimi" in model.lower():
        return 1.0
    return None
