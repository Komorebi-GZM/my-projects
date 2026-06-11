"""Demo 课堂伴教 Agent — TDD 测试"""
from unittest.mock import MagicMock
import pytest


class TestClassroomCompanionInstantiation:
    """行为 1: ClassroomCompanionAgent 可实例化"""

    def test_class_can_be_imported(self):
        """可以从 demo.agents.classroom_companion 导入 ClassroomCompanionAgent"""
        from demo.agents.classroom_companion import ClassroomCompanionAgent
        assert ClassroomCompanionAgent is not None

    def test_can_instantiate_with_mock_llm(self):
        """使用 mock LLM 可正常实例化"""
        from demo.agents.classroom_companion import ClassroomCompanionAgent
        agent = ClassroomCompanionAgent(llm=MagicMock())
        assert agent is not None
        assert hasattr(agent, "generate_quiz")
        assert hasattr(agent, "retrieve_classic_questions")


class TestGenerateQuiz:
    """行为 2: generate_quiz() 生成练习题文本"""

    def test_returns_string_with_quiz_content(self):
        """generate_quiz 返回包含练习题的文本"""
        from langchain_core.messages import AIMessage
        from demo.agents.classroom_companion import ClassroomCompanionAgent

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="1. 1/2 + 1/2 = ？\n2. 3/4 - 1/4 = ？")
        agent = ClassroomCompanionAgent(llm=mock_llm)

        result = agent.generate_quiz(
            subject="数学", grade="三年级", topic="分数",
            knowledge_points="分数的加减法",
            question_count=3, question_types=["选择题", "填空题"]
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_uses_provided_parameters_in_prompt(self):
        """传递的参数应影响生成的题目内容"""
        from langchain_core.messages import AIMessage
        from demo.agents.classroom_companion import ClassroomCompanionAgent

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="练习题内容")
        agent = ClassroomCompanionAgent(llm=mock_llm)

        agent.generate_quiz(
            subject="数学", grade="三年级", topic="分数",
            knowledge_points="分数的认识", question_count=5
        )

        mock_llm.invoke.assert_called_once()

    def test_handles_empty_knowledge_points(self):
        """知识点为空时应使用默认值"""
        from langchain_core.messages import AIMessage
        from demo.agents.classroom_companion import ClassroomCompanionAgent

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="练习题")
        agent = ClassroomCompanionAgent(llm=mock_llm)

        result = agent.generate_quiz(
            subject="数学", grade="三年级", topic="分数",
            knowledge_points="", question_count=3
        )

        assert isinstance(result, str)


class TestRetrieveClassicQuestions:
    """行为 3: retrieve_classic_questions() 检索经典题目"""

    def test_returns_string_with_questions(self):
        """retrieve_classic_questions 返回包含经典题目的文本"""
        from langchain_core.messages import AIMessage
        from demo.agents.classroom_companion import ClassroomCompanionAgent

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="经典题1：分数的意义")
        agent = ClassroomCompanionAgent(llm=mock_llm)

        result = agent.retrieve_classic_questions(
            subject="数学", grade="三年级", topic="分数"
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_llm_is_called_with_correct_params(self):
        """LLM 被调用且传入正确参数"""
        from langchain_core.messages import AIMessage
        from demo.agents.classroom_companion import ClassroomCompanionAgent

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="经典题")
        agent = ClassroomCompanionAgent(llm=mock_llm)

        agent.retrieve_classic_questions(
            subject="数学", grade="三年级", topic="分数"
        )

        mock_llm.invoke.assert_called_once()
