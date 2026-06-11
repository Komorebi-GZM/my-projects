"""
Agent工厂
统一管理所有Agent的依赖注入（LLM、RAG、记忆、工具）
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from .base import BaseAgent
from .classroom_companion import ClassroomCompanionAgent
from .material_agent import MaterialAgent
from .meeting_notes import MeetingNotesAgent
from .quick_lesson_prep import QuickLessonPrepAgent
from .router import RouterAgent
from .wisdom_transfer import WisdomTransferAgent

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

    from maitian_agent.config.settings import Settings
    from maitian_agent.memory.conversation_memory import ConversationMemory
    from maitian_agent.memory.teacher_profile import TeacherProfileManager
    from maitian_agent.rag.knowledge_base import KnowledgeBase
    from maitian_agent.tools.asr import BaseASR
    from maitian_agent.tools.ocr import BaseOCR

logger = logging.getLogger(__name__)

# Agent 类型 → Agent 类的注册表
_AGENT_REGISTRY: Dict[str, type] = {
    "quick_lesson_prep": QuickLessonPrepAgent,
    "wisdom_transfer": WisdomTransferAgent,
    "classroom_companion": ClassroomCompanionAgent,
    "material": MaterialAgent,
    "meeting_notes": MeetingNotesAgent,
    "router": RouterAgent,
}


class AgentFactory:
    """Agent 工厂 — 统一管理依赖注入

    集中管理 LLM、RAG（KnowledgeBase）、记忆（ConversationMemory /
    TeacherProfileManager）、工具（OCR / ASR）的创建与注入，
    使所有 Agent 通过工厂统一创建，不再单独初始化。

    用法::

        factory = AgentFactory(settings=settings)
        agent = factory.create("quick_lesson_prep")
        result = agent.run({"subject": "数学", "grade": "三年级", "topic": "分数"})

        # 一次性创建所有 Agent
        agents = factory.create_all()
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        settings: Optional[Settings] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
        conversation_memory: Optional[ConversationMemory] = None,
        teacher_profile: Optional[TeacherProfileManager] = None,
        ocr: Optional[BaseOCR] = None,
        asr: Optional[BaseASR] = None,
    ):
        self._llm = llm
        self._settings = settings
        self._knowledge_base = knowledge_base
        self._conversation_memory = conversation_memory
        self._teacher_profile = teacher_profile
        self._ocr = ocr
        self._asr = asr

    # ── 公开接口 ──────────────────────────────────────────────────

    def create(self, agent_type: str) -> BaseAgent:
        """创建指定类型的 Agent，注入所有已注册的依赖。

        所有 7 种依赖（llm / settings / knowledge_base / conversation_memory /
        teacher_profile / ocr / asr）均通过构造函数 kwargs 注入，无属性赋值。

        Args:
            agent_type: Agent 类型标识，对应 _AGENT_REGISTRY 的 key。

        Returns:
            配置好依赖的 Agent 实例。

        Raises:
            ValueError: agent_type 不在注册表中。
        """
        if agent_type not in _AGENT_REGISTRY:
            raise ValueError(
                f"未知的 Agent 类型: '{agent_type}'，可用类型: {list(_AGENT_REGISTRY.keys())}"
            )

        cls = _AGENT_REGISTRY[agent_type]
        kwargs = self._build_kwargs(agent_type)
        agent = cls(**kwargs)

        logger.info(f"AgentFactory 创建 {agent_type}: {cls.__name__}")
        return agent

    def create_all(self) -> Dict[str, BaseAgent]:
        """创建所有已注册的 Agent。

        Returns:
            Dict[agent_type, BaseAgent]
        """
        return {agent_type: self.create(agent_type) for agent_type in _AGENT_REGISTRY}

    # ── 内部方法 ──────────────────────────────────────────────────

    def _build_kwargs(self, agent_type: str) -> Dict[str, Any]:
        """根据 Agent 类型构建构造函数关键字参数。

        所有依赖均通过 kwargs 传入 Agent 构造函数，与 llm/settings 保持一致。
        """
        kwargs: Dict[str, Any] = {}

        # 所有 Agent 共享的参数
        if self._llm is not None:
            kwargs["llm"] = self._llm
        if self._settings is not None:
            kwargs["settings"] = self._settings

        # 所有 Agent 共享的 RAG / 记忆依赖
        if self._knowledge_base is not None:
            kwargs["knowledge_base"] = self._knowledge_base
        if self._conversation_memory is not None:
            kwargs["conversation_memory"] = self._conversation_memory
        if self._teacher_profile is not None:
            kwargs["teacher_profile"] = self._teacher_profile

        # WisdomTransferAgent 特有：注入 OCR
        if agent_type == "wisdom_transfer" and self._ocr is not None:
            kwargs["ocr_reader"] = self._ocr

        # MeetingNotesAgent 特有：注入 ASR
        if agent_type == "meeting_notes" and self._asr is not None:
            kwargs["asr"] = self._asr

        return kwargs
