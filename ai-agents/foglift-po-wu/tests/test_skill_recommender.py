import json
from agents.path_skill.skill_recommender import recommend_skills


def test_recommend_skills_returns_skill_list_with_priority():
    """recommend_skills returns a list of skills with 技能名 and 优先级."""
    mock_response = json.dumps([
        {"技能名": "SQL", "优先级": "高", "说明": "数据分析的基础工具"},
        {"技能名": "Python", "优先级": "高", "说明": "数据处理和建模"},
        {"技能名": "Tableau", "优先级": "中", "说明": "数据可视化"}
    ])
    captured = {}

    class MockClient:
        def chat_with_system(self, system: str, user: str) -> str:
            captured["system"] = system
            return mock_response

    ability_dims = ["SQL", "Python", "Tableau", "PowerBI"]
    result = recommend_skills(ability_dims, llm_client=MockClient())

    assert isinstance(result, list)
    assert len(result) > 0
    assert "技能名" in result[0]
    assert "优先级" in result[0]
    assert result[0]["技能名"] == "SQL"
    assert "知识库证据" in captured["system"]
    assert "skill_resource_map:" in captured["system"]
