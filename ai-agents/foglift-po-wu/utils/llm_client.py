import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatZhipuAI

class LLMClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _ensure_initialized(self):
        if self._initialized:
            return
        self._initialized = True
        model_provider = os.getenv("LLM_PROVIDER", "dashscope")

        if model_provider == "dashscope":
            self.client = ChatOpenAI(
                model=os.getenv("DASHSCOPE_MODEL", "qwen-plus"),
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=0.7
            )
        elif model_provider == "openai":
            self.client = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
                temperature=0.7
            )
        elif model_provider == "zhipu":
            zhipu_key = os.getenv("ZHIPUAI_API_KEY") or os.getenv("ZHIPU_API_KEY")
            self.client = ChatZhipuAI(
                model=os.getenv("ZHIPU_MODEL", "glm-4-flash"),
                zhipuai_api_key=zhipu_key,
                temperature=0.7
            )

    def chat(self, messages: list) -> str:
        self._ensure_initialized()
        response = self.client.invoke(messages)
        return response.content

    def chat_with_system(self, system: str, user: str) -> str:
        messages = [
            ("system", system),
            ("human", user)
        ]
        return self.chat(messages)

import json
from typing import Any, Optional

llm_client = LLMClient()


def invoke_llm(system: str, user: str, client: Optional[LLMClient] = None) -> Any:
    """Call LLM with system/user, parse JSON response. Returns parsed dict or raises."""
    if client is None:
        client = llm_client
    response = client.chat_with_system(system, user)
    return json.loads(response)