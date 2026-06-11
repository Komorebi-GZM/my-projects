"""
Agent模块
包含五大核心Agent链和AgentFactory
"""

from .base import BaseAgent
from .classroom_companion import ClassroomCompanionAgent
from .factory import AgentFactory
from .material_agent import MaterialAgent
from .meeting_notes import MeetingNotesAgent
from .quick_lesson_prep import QuickLessonPrepAgent
from .router import RouterAgent
from .wisdom_transfer import WisdomTransferAgent

__all__ = [
    "BaseAgent",
    "QuickLessonPrepAgent",
    "WisdomTransferAgent",
    "ClassroomCompanionAgent",
    "MaterialAgent",
    "MeetingNotesAgent",
    "RouterAgent",
    "AgentFactory",
]
