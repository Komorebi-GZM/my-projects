"""记忆集成测试 — 验证 ConversationMemory 和 TeacherProfile 注入 Agent"""
import os
import json
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage


# ── 辅助 ──────────────────────────────────────────────────────────

def _make_mock_llm(response_text="测试教案内容"):
    from langchain_core.language_models import BaseChatModel
    llm = MagicMock(spec=BaseChatModel)
    llm.invoke.return_value = AIMessage(content=response_text)
    return llm


def _make_real_memory(tmp_dir):
    """创建真实的 ConversationMemory（使用临时目录）"""
    from maitian_agent.memory.conversation_memory import ConversationMemory
    return ConversationMemory(
        session_id="test-session",
        persist_directory=tmp_dir,
    )


def _make_real_profile_manager(tmp_dir):
    """创建真实的 TeacherProfileManager（使用临时目录）"""
    from maitian_agent.memory.teacher_profile import TeacherProfileManager
    return TeacherProfileManager(persist_directory=tmp_dir)


# ── 1.1: BaseAgent._save_to_memory() 方法 ─────────────────────────

def test_base_agent_has_save_to_memory():
    """BaseAgent 应有 _save_to_memory() 方法"""
    from maitian_agent.agents.base import BaseAgent
    assert hasattr(BaseAgent, "_save_to_memory")


def test_save_to_memory_skips_when_no_memory():
    """无 conversation_memory 时，_save_to_memory() 应静默跳过"""
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent
    agent = QuickLessonPrepAgent(llm=_make_mock_llm())
    # 不设置 conversation_memory，不应抛异常
    agent._save_to_memory({"subject": "数学"}, {"success": True, "result": "教案"})


def test_save_to_memory_calls_conversation_memory():
    """有 conversation_memory 时，_save_to_memory() 应调用 save_context()"""
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent
    agent = QuickLessonPrepAgent(llm=_make_mock_llm())

    mock_memory = MagicMock()
    agent.conversation_memory = mock_memory

    agent._save_to_memory(
        {"subject": "数学", "grade": "三年级", "topic": "分数"},
        {"success": True, "result": "教案内容"},
    )
    mock_memory.save_context.assert_called_once()


# ── 1.2: BaseAgent._load_teacher_profile() 方法 ──────────────────

def test_base_agent_has_load_teacher_profile():
    """BaseAgent 应有 _load_teacher_profile() 方法"""
    from maitian_agent.agents.base import BaseAgent
    assert hasattr(BaseAgent, "_load_teacher_profile")


def test_load_teacher_profile_returns_none_when_no_manager():
    """无 teacher_profile 时，_load_teacher_profile() 应返回 None"""
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent
    agent = QuickLessonPrepAgent(llm=_make_mock_llm())
    profile = agent._load_teacher_profile("teacher_001")
    assert profile is None


def test_load_teacher_profile_returns_profile():
    """有 teacher_profile 时，应返回教师画像"""
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent
    agent = QuickLessonPrepAgent(llm=_make_mock_llm())

    mock_manager = MagicMock()
    mock_profile = MagicMock()
    mock_profile.name = "张老师"
    mock_profile.teaching_styles = []
    mock_manager.load_profile.return_value = mock_profile
    agent.teacher_profile = mock_manager

    profile = agent._load_teacher_profile("teacher_001")
    assert profile is not None
    mock_manager.load_profile.assert_called_once_with("teacher_001")


# ── 2.1: QuickLessonPrepAgent 教师画像个性化备课 ────────────────

def test_quick_lesson_prep_uses_teacher_profile(tmp_path):
    """QuickLessonPrepAgent 应将教师画像信息注入 Prompt"""
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent
    from maitian_agent.memory.teacher_profile import TeacherProfileManager, TeacherProfile, TeachingStyle

    # 创建真实教师画像
    mgr = TeacherProfileManager(persist_directory=str(tmp_path))
    profile = TeacherProfile(
        teacher_id="teacher_001",
        name="张老师",
        school="麦田小学",
        subjects=["数学"],
        grades=["三年级"],
        teaching_years=15,
        teaching_styles=[
            TeachingStyle(style_name="故事导入", description="用乡村故事引入新课", examples=["分苹果"]),
        ],
        rural_experience="10年乡村教学经验",
    )
    mgr.save_profile(profile)

    # 创建 Agent 并注入
    agent = QuickLessonPrepAgent(llm=_make_mock_llm())
    agent.teacher_profile = mgr

    result = agent.run({
        "subject": "数学",
        "grade": "三年级",
        "topic": "分数",
        "teacher_id": "teacher_001",
    })

    assert result["success"] is True
    assert result["metadata"].get("has_teacher_profile") is True


def test_quick_lesson_prep_no_profile_still_works():
    """无教师画像时，QuickLessonPrepAgent 应正常工作"""
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent
    agent = QuickLessonPrepAgent(llm=_make_mock_llm())

    result = agent.run({
        "subject": "数学",
        "grade": "三年级",
        "topic": "分数",
    })

    assert result["success"] is True
    assert result["metadata"].get("has_teacher_profile") is False


# ── 2.2: 所有 Agent 自动保存对话上下文 ─────────────────────────

def test_quick_lesson_prep_saves_context(tmp_path):
    """QuickLessonPrepAgent.run() 后应自动保存对话上下文"""
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

    memory = _make_real_memory(str(tmp_path))
    agent = QuickLessonPrepAgent(llm=_make_mock_llm())
    agent.conversation_memory = memory

    agent.run({"subject": "数学", "grade": "三年级", "topic": "分数"})

    history = memory.get_conversation_history()
    assert len(history) >= 1  # 至少保存了一轮对话


def test_classroom_companion_saves_context(tmp_path):
    """ClassroomCompanionAgent.run() 后应自动保存对话上下文"""
    from maitian_agent.agents.classroom_companion import ClassroomCompanionAgent

    memory = _make_real_memory(str(tmp_path))
    agent = ClassroomCompanionAgent(llm=_make_mock_llm())
    agent.conversation_memory = memory

    agent.run({"action": "quiz", "subject": "数学", "grade": "三年级", "topic": "分数"})

    history = memory.get_conversation_history()
    assert len(history) >= 1


def test_material_saves_context(tmp_path):
    """MaterialAgent.run() 后应自动保存对话上下文"""
    from maitian_agent.agents.material_agent import MaterialAgent

    memory = _make_real_memory(str(tmp_path))
    agent = MaterialAgent(llm=_make_mock_llm("素材推荐"))
    agent.conversation_memory = memory

    agent.run({"subject": "科学", "grade": "四年级", "topic": "水的循环"})

    history = memory.get_conversation_history()
    assert len(history) >= 1


def test_meeting_notes_saves_context(tmp_path):
    """MeetingNotesAgent.run() 后应自动保存对话上下文"""
    from maitian_agent.agents.meeting_notes import MeetingNotesAgent

    memory = _make_real_memory(str(tmp_path))
    agent = MeetingNotesAgent(llm=_make_mock_llm("教研报告"))
    agent.conversation_memory = memory

    agent.run({"transcript": "今天讨论了教学方法的改进..."})

    history = memory.get_conversation_history()
    assert len(history) >= 1


def test_no_memory_no_error():
    """无 conversation_memory 时，Agent 不应报错"""
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent
    agent = QuickLessonPrepAgent(llm=_make_mock_llm())

    result = agent.run({"subject": "数学", "grade": "三年级", "topic": "分数"})
    assert result["success"] is True


# ── 3.1: 记忆持久化验证 ─────────────────────────────────────────

def test_memory_persists_to_disk(tmp_path):
    """ConversationMemory 应将对话持久化到磁盘"""
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

    # 第一次运行：保存对话
    memory1 = _make_real_memory(str(tmp_path))
    agent1 = QuickLessonPrepAgent(llm=_make_mock_llm())
    agent1.conversation_memory = memory1
    agent1.run({"subject": "数学", "grade": "三年级", "topic": "分数"})

    # 第二次运行：加载对话
    memory2 = _make_real_memory(str(tmp_path))
    history = memory2.get_conversation_history()
    assert len(history) >= 1


def test_teacher_profile_persists_to_disk(tmp_path):
    """TeacherProfileManager 应将画像持久化到磁盘"""
    from maitian_agent.memory.teacher_profile import TeacherProfileManager, TeacherProfile

    # 第一次：保存画像
    mgr1 = TeacherProfileManager(persist_directory=str(tmp_path))
    profile = TeacherProfile(
        teacher_id="teacher_001",
        name="张老师",
        subjects=["数学"],
    )
    mgr1.save_profile(profile)

    # 第二次：加载画像
    mgr2 = TeacherProfileManager(persist_directory=str(tmp_path))
    loaded = mgr2.load_profile("teacher_001")
    assert loaded is not None
    assert loaded.name == "张老师"
    assert loaded.subjects == ["数学"]


# ── 4.1: AgentFactory + 记忆端到端 ───────────────────────────────

def test_factory_agents_have_memory():
    """AgentFactory 创建的 Agent 应携带 conversation_memory"""
    from maitian_agent.agents.factory import AgentFactory

    mock_memory = MagicMock()
    factory = AgentFactory(llm=_make_mock_llm(), conversation_memory=mock_memory)

    agent = factory.create("quick_lesson_prep")
    assert agent.conversation_memory is mock_memory


def test_factory_agents_have_teacher_profile():
    """AgentFactory 创建的 Agent 应携带 teacher_profile"""
    from maitian_agent.agents.factory import AgentFactory

    mock_profile = MagicMock()
    factory = AgentFactory(llm=_make_mock_llm(), teacher_profile=mock_profile)

    agent = factory.create("quick_lesson_prep")
    assert agent.teacher_profile is mock_profile


def test_factory_end_to_end_with_memory_and_profile(tmp_path):
    """AgentFactory 端到端：创建 Agent → 运行 → 记忆保存 + 画像读取"""
    from maitian_agent.agents.factory import AgentFactory
    from maitian_agent.memory.teacher_profile import TeacherProfileManager, TeacherProfile

    # 创建教师画像
    mgr = TeacherProfileManager(persist_directory=str(tmp_path))
    profile = TeacherProfile(
        teacher_id="teacher_001",
        name="张老师",
        subjects=["数学"],
    )
    mgr.save_profile(profile)

    # 创建记忆
    memory = _make_real_memory(str(tmp_path))

    # 通过工厂创建 Agent
    factory = AgentFactory(
        llm=_make_mock_llm(),
        conversation_memory=memory,
        teacher_profile=mgr,
    )

    agent = factory.create("quick_lesson_prep")
    result = agent.run({
        "subject": "数学",
        "grade": "三年级",
        "topic": "分数",
        "teacher_id": "teacher_001",
    })

    assert result["success"] is True
    assert result["metadata"].get("has_teacher_profile") is True

    # 验证对话已保存
    history = memory.get_conversation_history()
    assert len(history) >= 1
