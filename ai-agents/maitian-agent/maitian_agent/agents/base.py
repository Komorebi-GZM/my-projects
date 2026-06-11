"""
Agent基类
定义所有Agent的公共接口和方法
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

from langchain_core.language_models import BaseChatModel

if TYPE_CHECKING:
    from maitian_agent.config.settings import Settings
    from maitian_agent.memory.conversation_memory import ConversationMemory
    from maitian_agent.memory.teacher_profile import TeacherProfileManager
    from maitian_agent.rag.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Agent基类"""

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        name: str = "BaseAgent",
        description: str = "基础Agent",
        settings: Optional[Settings] = None,
        default_temperature: float = 0.7,
        knowledge_base: Optional[KnowledgeBase] = None,
        conversation_memory: Optional[ConversationMemory] = None,
        teacher_profile: Optional[TeacherProfileManager] = None,
    ):
        self.llm = llm
        self.name = name
        self.description = description
        self.settings = settings
        self.default_temperature = default_temperature
        self.knowledge_base = knowledge_base
        self.conversation_memory = conversation_memory
        self.teacher_profile = teacher_profile
        self._chain = None
        logger.info(f"初始化Agent: {name}")

    def _create_default_llm(self, temperature: Optional[float] = None) -> BaseChatModel:
        """使用 settings 创建默认 LLM 实例

        优先使用注入的 settings，否则回退到 get_settings() 全局实例。
        temperature 优先使用参数值，否则使用 self.default_temperature。
        """
        from langchain_openai import ChatOpenAI
        from pydantic import SecretStr

        from maitian_agent.config.settings import get_settings

        s = self.settings or get_settings()
        temp = temperature if temperature is not None else self.default_temperature
        api_key: SecretStr | str | None = s.openai_api_key
        if isinstance(api_key, str):
            api_key = SecretStr(api_key)
        return ChatOpenAI(
            model=s.model_name,
            api_key=api_key,
            base_url=s.openai_api_base,
            temperature=temp,
        )

    def _retrieve_context(self, query: str, k: int = 4) -> str:
        """从 knowledge_base 检索相关上下文。

        如果未注入 knowledge_base，返回空字符串（向后兼容）。
        子类可在 run() 中调用此方法获取 RAG 检索结果。

        Args:
            query: 检索查询文本
            k: 返回结果数量

        Returns:
            格式化的检索结果文本，无 KB 时返回空字符串
        """
        kb = self.knowledge_base
        if kb is None:
            return ""

        try:
            results = kb.search(query, k=k)
            if not results:
                return ""

            context_parts = []
            for i, doc in enumerate(results, 1):
                text = getattr(doc, "page_content", str(doc))
                context_parts.append(f"[参考{i}] {text}")
            return "\n\n".join(context_parts)
        except Exception as e:
            logger.warning(f"RAG 检索失败，跳过: {e}")
            return ""

    def _save_to_memory(
        self,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
    ) -> None:
        """将对话上下文保存到 ConversationMemory。

        如果未注入 conversation_memory，静默跳过（向后兼容）。
        子类可在 run() 成功后调用此方法。

        Args:
            input_data: 用户输入数据
            output_data: Agent 输出数据
        """
        memory = self.conversation_memory
        if memory is None:
            return

        try:
            # ConversationMemory.save_context 期望 human_input 和 response 键
            human_input = str(input_data)
            response = output_data.get("result", str(output_data))
            memory.save_context(
                {"human_input": human_input},
                {"response": response},
            )
        except Exception as e:
            logger.warning(f"保存对话上下文失败，跳过: {e}")

    def _load_teacher_profile(self, teacher_id: str):
        """从 TeacherProfileManager 加载教师画像。

        如果未注入 teacher_profile 或 teacher_id 为空，返回 None。

        Args:
            teacher_id: 教师ID

        Returns:
            TeacherProfile 对象或 None
        """
        if not teacher_id:
            return None

        manager = self.teacher_profile
        if manager is None:
            return None

        try:
            return manager.load_profile(teacher_id)
        except Exception as e:
            logger.warning(f"加载教师画像失败，跳过: {e}")
            return None

    def _format_teacher_profile_section(self, profile) -> str:
        """将教师画像格式化为 Prompt 可用的文本段落。

        Args:
            profile: TeacherProfile 对象

        Returns:
            格式化的教师画像文本
        """
        if profile is None:
            return ""

        parts = [f"教师信息：{profile.name}"]

        if profile.school:
            parts.append(f"所在学校：{profile.school}")
        if profile.teaching_years:
            parts.append(f"教龄：{profile.teaching_years}年")
        if profile.subjects:
            parts.append(f"教授科目：{'、'.join(profile.subjects)}")
        if profile.grades:
            parts.append(f"教授年级：{'、'.join(profile.grades)}")

        if profile.teaching_styles:
            style_lines = []
            for style in profile.teaching_styles:
                style_lines.append(f"  - {style.style_name}：{style.description}")
            if style_lines:
                parts.append("教学风格：\n" + "\n".join(style_lines))

        if profile.rural_experience:
            parts.append(f"乡村教学经验：{profile.rural_experience}")

        return "\n".join(parts)

    @abstractmethod
    def build_chain(self) -> Any:
        """构建Agent链"""
        pass

    @abstractmethod
    def run(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """执行Agent"""
        pass

    def _validate_input(self, input_data: Dict[str, Any], required_keys: list) -> None:
        """验证输入数据"""
        missing_keys = [key for key in required_keys if key not in input_data]
        if missing_keys:
            raise ValueError(f"缺少必需参数: {', '.join(missing_keys)}")

    def _format_output(self, result: Any, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """格式化输出"""
        return {"success": True, "result": result, "agent": self.name, "metadata": metadata or {}}

    def _handle_error(self, error: Exception) -> Dict[str, Any]:
        """处理错误"""
        logger.error(f"{self.name}执行错误: {str(error)}")
        return {"success": False, "error": str(error), "agent": self.name}
