"""依赖注入统一性测试 — 验证所有 7 种依赖均通过构造函数 kwargs 注入

核心断言：
1. BaseAgent.__init__ 接受 knowledge_base / conversation_memory / teacher_profile 参数
2. MeetingNotesAgent.__init__ 接受 asr 参数
3. AgentFactory.create() 不使用属性赋值注入（无 agent.xxx = ... 模式）
4. 所有 6 个 Agent 通过 Factory 创建后，7 种依赖均可通过构造函数到达
5. 未注入时静默降级，不报错
6. 直接构造 Agent 时也可通过 kwargs 注入（向后兼容）
"""
from __future__ import annotations

import inspect
import ast
from unittest.mock import MagicMock, patch
from typing import Any, Dict

import pytest


# ── 辅助 ──────────────────────────────────────────────────────────

def _make_mock_llm(response_text="测试教案内容"):
    """创建 mock LLM，返回 AIMessage（StrOutputParser 兼容）"""
    from langchain_core.language_models import BaseChatModel
    from langchain_core.messages import AIMessage

    llm = MagicMock(spec=BaseChatModel)
    llm.invoke.return_value = AIMessage(content=response_text)
    return llm


def _make_mock_kb(results=None):
    """创建 mock KnowledgeBase"""
    kb = MagicMock()
    if results is None:
        mock_doc = MagicMock()
        mock_doc.page_content = "测试参考内容"
        results = [mock_doc]
    kb.search.return_value = results
    return kb


_ALL_AGENT_TYPES = [
    "quick_lesson_prep",
    "wisdom_transfer",
    "classroom_companion",
    "material",
    "meeting_notes",
    "router",
]


# ══════════════════════════════════════════════════════════════════
# 1. BaseAgent 构造函数签名验证
# ══════════════════════════════════════════════════════════════════

class TestBaseAgentConstructorSignature:
    """验证 BaseAgent.__init__ 接受所有 3 个新依赖参数"""

    def test_base_agent_accepts_knowledge_base_param(self):
        """BaseAgent.__init__ 应接受 knowledge_base 参数"""
        from maitian_agent.agents.base import BaseAgent

        sig = inspect.signature(BaseAgent.__init__)
        assert "knowledge_base" in sig.parameters, \
            "BaseAgent.__init__ 缺少 knowledge_base 参数"

    def test_base_agent_accepts_conversation_memory_param(self):
        """BaseAgent.__init__ 应接受 conversation_memory 参数"""
        from maitian_agent.agents.base import BaseAgent

        sig = inspect.signature(BaseAgent.__init__)
        assert "conversation_memory" in sig.parameters, \
            "BaseAgent.__init__ 缺少 conversation_memory 参数"

    def test_base_agent_accepts_teacher_profile_param(self):
        """BaseAgent.__init__ 应接受 teacher_profile 参数"""
        from maitian_agent.agents.base import BaseAgent

        sig = inspect.signature(BaseAgent.__init__)
        assert "teacher_profile" in sig.parameters, \
            "BaseAgent.__init__ 缺少 teacher_profile 参数"

    def test_base_agent_stores_knowledge_base(self):
        """传入 knowledge_base 后，self.knowledge_base 应为该值"""
        from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

        mock_kb = _make_mock_kb()
        agent = QuickLessonPrepAgent(
            llm=_make_mock_llm(),
            knowledge_base=mock_kb,
        )
        assert agent.knowledge_base is mock_kb

    def test_base_agent_stores_conversation_memory(self):
        """传入 conversation_memory 后，self.conversation_memory 应为该值"""
        from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

        mock_memory = MagicMock()
        agent = QuickLessonPrepAgent(
            llm=_make_mock_llm(),
            conversation_memory=mock_memory,
        )
        assert agent.conversation_memory is mock_memory

    def test_base_agent_stores_teacher_profile(self):
        """传入 teacher_profile 后，self.teacher_profile 应为该值"""
        from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

        mock_profile = MagicMock()
        agent = QuickLessonPrepAgent(
            llm=_make_mock_llm(),
            teacher_profile=mock_profile,
        )
        assert agent.teacher_profile is mock_profile

    def test_base_agent_defaults_none_without_injection(self):
        """不传 knowledge_base/conversation_memory/teacher_profile 时，默认为 None"""
        from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

        agent = QuickLessonPrepAgent(llm=_make_mock_llm())
        assert agent.knowledge_base is None
        assert agent.conversation_memory is None
        assert agent.teacher_profile is None


# ══════════════════════════════════════════════════════════════════
# 2. MeetingNotesAgent 构造函数接受 asr 参数
# ══════════════════════════════════════════════════════════════════

class TestMeetingNotesASRInjection:
    """验证 MeetingNotesAgent.asr 通过构造函数注入"""

    def test_meeting_notes_accepts_asr_param(self):
        """MeetingNotesAgent.__init__ 应接受 asr 参数"""
        from maitian_agent.agents.meeting_notes import MeetingNotesAgent

        sig = inspect.signature(MeetingNotesAgent.__init__)
        assert "asr" in sig.parameters, \
            "MeetingNotesAgent.__init__ 缺少 asr 参数"

    def test_meeting_notes_stores_asr(self):
        """传入 asr 后，self.asr 应为该值"""
        from maitian_agent.agents.meeting_notes import MeetingNotesAgent

        mock_asr = MagicMock()
        agent = MeetingNotesAgent(
            llm=_make_mock_llm("教研报告"),
            asr=mock_asr,
        )
        assert agent.asr is mock_asr

    def test_meeting_notes_asr_defaults_none(self):
        """不传 asr 时，self.asr 应为 None"""
        from maitian_agent.agents.meeting_notes import MeetingNotesAgent

        agent = MeetingNotesAgent(llm=_make_mock_llm("教研报告"))
        assert agent.asr is None


# ══════════════════════════════════════════════════════════════════
# 3. AgentFactory.create() 无属性赋值（源码静态分析）
# ══════════════════════════════════════════════════════════════════

class TestFactoryNoAttributeAssignment:
    """验证 AgentFactory.create() 不使用 agent.xxx = ... 属性赋值"""

    def test_factory_create_no_attribute_assignment(self):
        """factory.py 的 create() 方法中不应有 agent.xxx = ... 赋值模式"""
        import maitian_agent.agents.factory as factory_module

        source = inspect.getsource(factory_module)
        tree = ast.parse(source)

        # 找到 create 方法
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "create":
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            # 检查是否有 agent.xxx = ... 模式
                            if isinstance(target, ast.Attribute):
                                if isinstance(target.value, ast.Name) and target.value.id == "agent":
                                    attr_name = target.attr
                                    # 这些属性不应通过赋值注入
                                    forbidden_attrs = {
                                        "knowledge_base",
                                        "conversation_memory",
                                        "teacher_profile",
                                        "asr",
                                    }
                                    assert attr_name not in forbidden_attrs, (
                                        f"AgentFactory.create() 不应使用属性赋值注入 '{attr_name}'，"
                                        f"应通过构造函数 kwargs 注入"
                                    )
                return  # 找到 create 方法后即返回

        pytest.fail("未找到 AgentFactory.create() 方法")


# ══════════════════════════════════════════════════════════════════
# 4. AgentFactory 统一注入 — 7 种依赖全部通过构造函数到达 Agent
# ══════════════════════════════════════════════════════════════════

class TestFactoryUnifiedInjection:
    """验证 AgentFactory 创建的 Agent 通过构造函数接收所有依赖"""

    @pytest.mark.parametrize("agent_type", _ALL_AGENT_TYPES)
    def test_factory_injects_knowledge_base_via_constructor(self, agent_type):
        """AgentFactory 注入的 knowledge_base 应通过构造函数到达 Agent"""
        from maitian_agent.agents.factory import AgentFactory

        mock_kb = _make_mock_kb()
        factory = AgentFactory(llm=_make_mock_llm(), knowledge_base=mock_kb)
        agent = factory.create(agent_type)
        assert agent.knowledge_base is mock_kb, \
            f"Agent '{agent_type}' 未通过构造函数接收到 knowledge_base"

    @pytest.mark.parametrize("agent_type", _ALL_AGENT_TYPES)
    def test_factory_injects_conversation_memory_via_constructor(self, agent_type):
        """AgentFactory 注入的 conversation_memory 应通过构造函数到达 Agent"""
        from maitian_agent.agents.factory import AgentFactory

        mock_memory = MagicMock()
        factory = AgentFactory(llm=_make_mock_llm(), conversation_memory=mock_memory)
        agent = factory.create(agent_type)
        assert agent.conversation_memory is mock_memory, \
            f"Agent '{agent_type}' 未通过构造函数接收到 conversation_memory"

    @pytest.mark.parametrize("agent_type", _ALL_AGENT_TYPES)
    def test_factory_injects_teacher_profile_via_constructor(self, agent_type):
        """AgentFactory 注入的 teacher_profile 应通过构造函数到达 Agent"""
        from maitian_agent.agents.factory import AgentFactory

        mock_profile = MagicMock()
        factory = AgentFactory(llm=_make_mock_llm(), teacher_profile=mock_profile)
        agent = factory.create(agent_type)
        assert agent.teacher_profile is mock_profile, \
            f"Agent '{agent_type}' 未通过构造函数接收到 teacher_profile"

    def test_factory_injects_asr_via_constructor(self):
        """AgentFactory 注入的 asr 应通过构造函数到达 MeetingNotesAgent"""
        from maitian_agent.agents.factory import AgentFactory

        mock_asr = MagicMock()
        factory = AgentFactory(llm=_make_mock_llm("教研报告"), asr=mock_asr)
        agent = factory.create("meeting_notes")
        assert agent.asr is mock_asr, \
            "MeetingNotesAgent 未通过构造函数接收到 asr"

    def test_factory_injects_ocr_via_constructor(self):
        """AgentFactory 注入的 ocr 应通过构造函数到达 WisdomTransferAgent（已有行为）"""
        from maitian_agent.agents.factory import AgentFactory

        mock_ocr = MagicMock()
        factory = AgentFactory(llm=_make_mock_llm("结构化结果"), ocr=mock_ocr)
        agent = factory.create("wisdom_transfer")
        assert agent.ocr is mock_ocr

    def test_factory_injects_llm_via_constructor(self):
        """AgentFactory 注入的 llm 应通过构造函数到达 Agent（已有行为）"""
        from maitian_agent.agents.factory import AgentFactory

        mock_llm = _make_mock_llm()
        factory = AgentFactory(llm=mock_llm)
        agent = factory.create("quick_lesson_prep")
        assert agent.llm is mock_llm

    def test_factory_injects_settings_via_constructor(self):
        """AgentFactory 注入的 settings 应通过构造函数到达 Agent（已有行为）"""
        from maitian_agent.config.settings import Settings
        from maitian_agent.agents.factory import AgentFactory

        settings = Settings(openai_api_key="test-key", model_name="test-model")
        factory = AgentFactory(settings=settings)

        with patch("langchain_openai.ChatOpenAI") as MockChatOpenAI:
            MockChatOpenAI.return_value = MagicMock()
            agent = factory.create("quick_lesson_prep")
            assert agent.settings is settings


# ══════════════════════════════════════════════════════════════════
# 5. 静默降级 — 未注入时不报错
# ══════════════════════════════════════════════════════════════════

class TestSilentDegradation:
    """验证未注入依赖时，Agent 静默降级不报错"""

    @pytest.mark.parametrize("agent_type", _ALL_AGENT_TYPES)
    def test_no_injection_no_error(self, agent_type):
        """不注入任何依赖时，Agent 创建和运行不报错"""
        from maitian_agent.agents.factory import AgentFactory

        factory = AgentFactory(llm=_make_mock_llm())
        agent = factory.create(agent_type)
        assert agent is not None
        assert agent.knowledge_base is None
        assert agent.conversation_memory is None
        assert agent.teacher_profile is None

    def test_retrieve_context_returns_empty_without_kb(self):
        """无 knowledge_base 时，_retrieve_context() 应返回空字符串"""
        from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

        agent = QuickLessonPrepAgent(llm=_make_mock_llm())
        ctx = agent._retrieve_context("测试查询")
        assert ctx == ""

    def test_save_to_memory_skips_without_memory(self):
        """无 conversation_memory 时，_save_to_memory() 应静默跳过"""
        from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

        agent = QuickLessonPrepAgent(llm=_make_mock_llm())
        # 不应抛异常
        agent._save_to_memory({"key": "val"}, {"result": "ok"})

    def test_load_teacher_profile_returns_none_without_manager(self):
        """无 teacher_profile 时，_load_teacher_profile() 应返回 None"""
        from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

        agent = QuickLessonPrepAgent(llm=_make_mock_llm())
        profile = agent._load_teacher_profile("teacher_001")
        assert profile is None

    def test_transcribe_audio_raises_without_asr(self):
        """无 asr 时，transcribe_audio() 应抛出 RuntimeError（已有行为）"""
        from maitian_agent.agents.meeting_notes import MeetingNotesAgent

        agent = MeetingNotesAgent(llm=_make_mock_llm("教研报告"))
        with pytest.raises(RuntimeError, match="ASR.*未注入"):
            agent.transcribe_audio("/fake/audio.wav")


# ══════════════════════════════════════════════════════════════════
# 6. 直接构造 Agent 也可注入（向后兼容）
# ══════════════════════════════════════════════════════════════════

class TestDirectConstructionBackwardCompat:
    """验证直接构造 Agent 时也可通过 kwargs 注入依赖（向后兼容）"""

    def test_quick_lesson_prep_direct_construction_with_all_deps(self):
        """QuickLessonPrepAgent 直接构造时可注入所有依赖"""
        from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

        mock_kb = _make_mock_kb()
        mock_memory = MagicMock()
        mock_profile = MagicMock()

        agent = QuickLessonPrepAgent(
            llm=_make_mock_llm(),
            knowledge_base=mock_kb,
            conversation_memory=mock_memory,
            teacher_profile=mock_profile,
        )

        assert agent.knowledge_base is mock_kb
        assert agent.conversation_memory is mock_memory
        assert agent.teacher_profile is mock_profile

    def test_wisdom_transfer_direct_construction_with_all_deps(self):
        """WisdomTransferAgent 直接构造时可注入所有依赖"""
        from maitian_agent.agents.wisdom_transfer import WisdomTransferAgent

        mock_kb = _make_mock_kb()
        mock_memory = MagicMock()
        mock_ocr = MagicMock()

        agent = WisdomTransferAgent(
            llm=_make_mock_llm("结构化结果"),
            ocr_reader=mock_ocr,
            knowledge_base=mock_kb,
            conversation_memory=mock_memory,
        )

        assert agent.knowledge_base is mock_kb
        assert agent.conversation_memory is mock_memory
        assert agent.ocr is mock_ocr

    def test_meeting_notes_direct_construction_with_asr(self):
        """MeetingNotesAgent 直接构造时可注入 asr"""
        from maitian_agent.agents.meeting_notes import MeetingNotesAgent

        mock_asr = MagicMock()
        mock_memory = MagicMock()

        agent = MeetingNotesAgent(
            llm=_make_mock_llm("教研报告"),
            asr=mock_asr,
            conversation_memory=mock_memory,
        )

        assert agent.asr is mock_asr
        assert agent.conversation_memory is mock_memory

    def test_direct_construction_without_deps_still_works(self):
        """直接构造 Agent 不传任何依赖时，应正常工作"""
        from maitian_agent.agents.classroom_companion import ClassroomCompanionAgent

        agent = ClassroomCompanionAgent(llm=_make_mock_llm())
        assert agent.knowledge_base is None
        assert agent.conversation_memory is None
        assert agent.teacher_profile is None


# ══════════════════════════════════════════════════════════════════
# 7. 端到端：Factory 全依赖注入 + Agent 运行
# ══════════════════════════════════════════════════════════════════

class TestEndToEndUnifiedInjection:
    """端到端验证：Factory 注入所有依赖 → Agent 正常运行"""

    def test_factory_full_injection_quick_lesson_prep(self):
        """QuickLessonPrepAgent 通过 Factory 注入全部依赖后正常运行"""
        from maitian_agent.agents.factory import AgentFactory

        mock_kb = _make_mock_kb()
        mock_memory = MagicMock()
        mock_profile = MagicMock()
        mock_profile.load_profile.return_value = None

        factory = AgentFactory(
            llm=_make_mock_llm(),
            knowledge_base=mock_kb,
            conversation_memory=mock_memory,
            teacher_profile=mock_profile,
        )

        agent = factory.create("quick_lesson_prep")
        result = agent.run({
            "subject": "数学",
            "grade": "三年级",
            "topic": "分数",
            "teacher_id": "T001",
        })

        assert result["success"] is True
        assert result["metadata"].get("has_rag_context") is True
        mock_kb.search.assert_called_once()
        mock_memory.save_context.assert_called_once()

    def test_factory_full_injection_meeting_notes(self):
        """MeetingNotesAgent 通过 Factory 注入全部依赖后正常运行"""
        from maitian_agent.agents.factory import AgentFactory

        mock_asr = MagicMock()
        mock_asr.transcribe.return_value = "会议转写文本"
        mock_memory = MagicMock()

        factory = AgentFactory(
            llm=_make_mock_llm("教研报告"),
            asr=mock_asr,
            conversation_memory=mock_memory,
        )

        agent = factory.create("meeting_notes")
        result = agent.run({"audio_path": "/fake/meeting.wav"})

        assert result["success"] is True
        mock_asr.transcribe.assert_called_once_with("/fake/meeting.wav")

    def test_factory_create_all_with_all_deps(self):
        """AgentFactory.create_all() 注入所有依赖后，每个 Agent 都能访问"""
        from maitian_agent.agents.factory import AgentFactory

        mock_kb = _make_mock_kb()
        mock_memory = MagicMock()
        mock_profile = MagicMock()
        mock_asr = MagicMock()

        factory = AgentFactory(
            llm=_make_mock_llm(),
            knowledge_base=mock_kb,
            conversation_memory=mock_memory,
            teacher_profile=mock_profile,
            asr=mock_asr,
        )

        agents = factory.create_all()

        for agent_type, agent in agents.items():
            assert agent.knowledge_base is mock_kb, \
                f"Agent '{agent_type}' 未接收到 knowledge_base"
            assert agent.conversation_memory is mock_memory, \
                f"Agent '{agent_type}' 未接收到 conversation_memory"
            assert agent.teacher_profile is mock_profile, \
                f"Agent '{agent_type}' 未接收到 teacher_profile"

        # meeting_notes 特有 asr
        assert agents["meeting_notes"].asr is mock_asr


# ══════════════════════════════════════════════════════════════════
# 8. 注入方式一致性审计 — 所有 7 种依赖均为构造函数注入
# ══════════════════════════════════════════════════════════════════

class TestInjectionConsistencyAudit:
    """审计所有 7 种依赖的注入方式一致性"""

    def test_all_seven_deps_use_constructor_injection(self):
        """7 种依赖全部通过构造函数 kwargs 注入，无属性赋值"""
        from maitian_agent.agents.factory import AgentFactory

        mock_llm = _make_mock_llm()
        mock_kb = _make_mock_kb()
        mock_memory = MagicMock()
        mock_profile = MagicMock()
        mock_ocr = MagicMock()
        mock_asr = MagicMock()

        factory = AgentFactory(
            llm=mock_llm,
            settings=None,
            knowledge_base=mock_kb,
            conversation_memory=mock_memory,
            teacher_profile=mock_profile,
            ocr=mock_ocr,
            asr=mock_asr,
        )

        # 创建 quick_lesson_prep 验证 5 种共享依赖
        agent = factory.create("quick_lesson_prep")
        assert agent.llm is mock_llm, "llm 未通过构造函数注入"
        assert agent.settings is None, "settings 未通过构造函数注入"
        assert agent.knowledge_base is mock_kb, "knowledge_base 未通过构造函数注入"
        assert agent.conversation_memory is mock_memory, "conversation_memory 未通过构造函数注入"
        assert agent.teacher_profile is mock_profile, "teacher_profile 未通过构造函数注入"

        # 创建 wisdom_transfer 验证 ocr
        agent_wt = factory.create("wisdom_transfer")
        assert agent_wt.ocr is mock_ocr, "ocr 未通过构造函数注入"

        # 创建 meeting_notes 验证 asr
        agent_mn = factory.create("meeting_notes")
        assert agent_mn.asr is mock_asr, "asr 未通过构造函数注入"
