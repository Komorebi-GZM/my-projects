import json
from agents.interview.answer_analyst import analyze_answer


def test_analyze_answer_returns_three_scores_and_total():
    """analyze_answer returns 3 independent scores + total score."""
    mock_response = json.dumps({
        "内容分": 85,
        "逻辑分": 70,
        "匹配分": 80,
        "总分": 79
    })

    class MockClient:
        def chat_with_system(self, system: str, user: str) -> str:
            return mock_response

    question = "请做一个自我介绍"
    answer = "我是张三，计算机科学专业..."
    key_points = ["教育背景", "项目经历", "技能特长"]

    result = analyze_answer(question, answer, key_points, llm_client=MockClient())

    assert isinstance(result, dict)
    assert "内容分" in result
    assert "逻辑分" in result
    assert "匹配分" in result
    assert "总分" in result
    assert isinstance(result["内容分"], (int, float))
    assert isinstance(result["逻辑分"], (int, float))
    assert isinstance(result["匹配分"], (int, float))
    assert isinstance(result["总分"], (int, float))
    assert 0 <= result["总分"] <= 100