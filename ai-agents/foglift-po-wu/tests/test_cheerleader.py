import json
from agents.interview.cheerleader import generate_encouragement


def test_generate_encouragement_uses_total_score():
    """cheerleader uses total_score directly for 敢投指数."""
    mock_response = json.dumps({
        "鼓励语": "你回答得很棒！继续加油！",
        "亮点": ["逻辑清晰", "表达流畅"],
        "建议": "可以再丰富一下项目经历的描述"
    })

    class MockClient:
        def chat_with_system(self, system: str, user: str) -> str:
            return mock_response

    total_score = 75
    strengths = ["逻辑清晰", "表达流畅"]

    result = generate_encouragement(total_score, strengths, llm_client=MockClient())

    assert isinstance(result, dict)
    assert "敢投指数" in result
    assert "鼓励语" in result
    assert isinstance(result["敢投指数"], (int, float))
    assert 0 <= result["敢投指数"] <= 100
    assert result["敢投指数"] == 75