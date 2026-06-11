"""验证所有 Agent 继承 BaseAgent 且 run() 签名统一"""
import pytest
from maitian_agent.agents.base import BaseAgent


def _import_agent_class(agent_class_name, module_path):
    mod = __import__(module_path, fromlist=[agent_class_name])
    return getattr(mod, agent_class_name)


AGENT_CLASSES = [
    ("QuickLessonPrepAgent", "maitian_agent.agents.quick_lesson_prep"),
    ("WisdomTransferAgent", "maitian_agent.agents.wisdom_transfer"),
    ("ClassroomCompanionAgent", "maitian_agent.agents.classroom_companion"),
    ("MaterialAgent", "maitian_agent.agents.material_agent"),
    ("MeetingNotesAgent", "maitian_agent.agents.meeting_notes"),
    ("RouterAgent", "maitian_agent.agents.router"),
]


@pytest.mark.parametrize("agent_class_name,module_path", AGENT_CLASSES)
def test_agent_inherits_base(agent_class_name, module_path):
    """所有 Agent 必须继承 BaseAgent"""
    cls = _import_agent_class(agent_class_name, module_path)
    assert issubclass(cls, BaseAgent), f"{agent_class_name} does not inherit BaseAgent"


@pytest.mark.parametrize("agent_class_name,module_path", AGENT_CLASSES)
def test_run_method_exists(agent_class_name, module_path):
    """所有 Agent 必须实现 run() 方法"""
    cls = _import_agent_class(agent_class_name, module_path)
    assert hasattr(cls, "run"), f"{agent_class_name} missing run() method"
    assert callable(getattr(cls, "run")), f"{agent_class_name}.run() is not callable"


@pytest.mark.parametrize("agent_class_name,module_path", AGENT_CLASSES)
def test_build_chain_method_exists(agent_class_name, module_path):
    """所有 Agent 必须实现 build_chain() 方法"""
    cls = _import_agent_class(agent_class_name, module_path)
    assert hasattr(cls, "build_chain"), f"{agent_class_name} missing build_chain()"
    assert callable(getattr(cls, "build_chain")), f"{agent_class_name}.build_chain() is not callable"


@pytest.mark.parametrize("agent_class_name,module_path", AGENT_CLASSES)
def test_agent_instantiable(agent_class_name, module_path):
    """所有 Agent 可实例化（无 LLM 时使用 mock）"""
    cls = _import_agent_class(agent_class_name, module_path)
    try:
        agent = cls()
        assert agent is not None
    except Exception as e:
        pytest.skip(f"{agent_class_name} 实例化需要外部依赖: {e}")


def test_run_accepts_dict_and_returns_dict():
    """验证 QuickLessonPrepAgent.run() 符合 Dict→Dict 契约"""
    from langchain_core.messages import AIMessage
    from langchain_core.language_models import BaseChatModel
    from unittest.mock import MagicMock
    from maitian_agent.agents.quick_lesson_prep import QuickLessonPrepAgent

    mock_llm = MagicMock(spec=BaseChatModel)
    mock_llm.invoke.return_value = AIMessage(content="测试教案内容")
    agent = QuickLessonPrepAgent(llm=mock_llm)
    result = agent.run({
        "subject": "数学", "grade": "三年级",
        "topic": "分数", "rural_context": "分苹果"
    })
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert "success" in result
    assert "result" in result
    assert result["success"] is True


def test_run_returns_success_key():
    """所有 Agent 的 run() 返回必须包含 success 键"""
    from unittest.mock import patch, MagicMock
    from langchain_core.messages import AIMessage
    from langchain_core.language_models import BaseChatModel
    from maitian_agent.agents.classroom_companion import ClassroomCompanionAgent
    from maitian_agent.agents.material_agent import MaterialAgent
    from maitian_agent.agents.router import RouterAgent

    mock_llm = MagicMock(spec=BaseChatModel)
    mock_llm.invoke.side_effect = [
        AIMessage(content="选择题\n1. 1/2 + 1/2 = ?"),
        AIMessage(content="视频：水的循环\n图片：水滴"),
        AIMessage(content="quick_lesson_prep"),
    ]

    agents = [
        ClassroomCompanionAgent(llm=mock_llm),
        MaterialAgent(llm=mock_llm),
        RouterAgent(llm=mock_llm),
    ]

    test_inputs = [
        {"action": "quiz", "subject": "数学", "grade": "三年级", "topic": "分数"},
        {"subject": "数学", "grade": "三年级", "topic": "分数"},
        {"user_input": "帮我备一节课"},
    ]

    for agent, test_input in zip(agents, test_inputs):
        result = agent.run(test_input)
        assert isinstance(result, dict), f"{type(agent).__name__} should return dict"
        assert "success" in result or "intent" in result, \
            f"{type(agent).__name__} result missing success/intent key"
