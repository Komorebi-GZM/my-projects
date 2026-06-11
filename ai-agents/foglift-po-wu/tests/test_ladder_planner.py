import json
from agents.path_skill.ladder_planner import plan_ladder


def test_plan_ladder_returns_four_steps():
    """plan_ladder returns a dict with 4 step keys based on template."""
    mock_response = json.dumps({
        "step1_校园项目": "参加数学建模竞赛",
        "step2_实习title": "数据分析师实习",
        "step3_实习积累关键词": "SQL取数、Tableau可视化",
        "step4_秋招目标岗位": "数据分析师"
    })
    captured = {}

    class MockClient:
        def chat_with_system(self, system: str, user: str) -> str:
            captured["system"] = system
            return mock_response

    ability_dims = ["SQL", "Python", "Tableau"]
    result = plan_ladder("字节跳动-Data AML数据分析实习生", ability_dims, llm_client=MockClient())

    assert isinstance(result, dict)
    assert "step1_校园项目" in result
    assert "step2_实习title" in result
    assert "step3_实习积累关键词" in result
    assert "step4_秋招目标岗位" in result
    assert "知识库证据" in captured["system"]
    assert "ladder_templates:" in captured["system"]
