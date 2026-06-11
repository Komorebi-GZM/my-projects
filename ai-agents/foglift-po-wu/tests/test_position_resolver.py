import json
from agents.path_skill.position_resolver import resolve_position


def test_resolve_position_returns_hard_skill_dims():
    """resolve_position returns a dict with position name and 3-5 hard skill dimensions."""
    mock_response = json.dumps({
        "岗位名称": "数据分析师",
        "能力维度": ["SQL", "Python", "Excel", "Tableau"]
    })
    captured = {}

    class MockClient:
        def chat_with_system(self, system: str, user: str) -> str:
            captured["system"] = system
            return mock_response

    result = resolve_position("数据分析师", llm_client=MockClient())

    assert isinstance(result, dict)
    assert "岗位名称" in result
    assert "能力维度" in result
    assert isinstance(result["能力维度"], list)
    assert 3 <= len(result["能力维度"]) <= 5
    assert "知识库证据" in captured["system"]
    assert "jd_library:" in captured["system"]
