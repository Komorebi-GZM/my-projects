import json
from agents.jd_translator.gap_analyst import analyze_gap


def test_analyze_gap_returns_fixed_structure():
    """analyze_gap returns gaps with fixed 2 items + time estimate."""
    mock_response = json.dumps({
        "差距项": [
            {"技能": "SQL", "差距描述": "缺乏数据库操作经验"},
            {"技能": "数据可视化", "差距描述": "未掌握Tableau/PowerBI"}
        ],
        "弥补时间估计": "约3个月系统学习"
    })

    class MockClient:
        def chat_with_system(self, system: str, user: str) -> str:
            return mock_response

    jd_parsed = {
        "硬技能": ["Python", "SQL", "Tableau"],
        "软技能": ["沟通能力", "数据分析思维"],
        "经验要求": "1-3年",
        "学历要求": "本科及以上"
    }
    user_profile = {"技能基础": ["Python基础"], "实习经验": "无"}

    result = analyze_gap(jd_parsed, user_profile, llm_client=MockClient())

    assert isinstance(result, dict)
    assert "差距项" in result
    assert "弥补时间估计" in result
    assert len(result["差距项"]) == 2
    assert isinstance(result["差距项"][0], dict)
    assert "弥补时间估计" in result


def test_analyze_gap_injects_default_user_profile_into_prompt():
    """analyze_gap includes default profile evidence when no profile is provided."""
    mock_response = json.dumps({
        "差距项": [
            {"技能": "SQL", "差距描述": "需要补齐数据库分析能力"},
            {"技能": "沟通", "差距描述": "需要加强业务表达"}
        ],
        "弥补时间估计": "约2个月"
    })

    class RecordingClient:
        system = ""

        def chat_with_system(self, system: str, user: str) -> str:
            self.system = system
            return mock_response

    client = RecordingClient()

    analyze_gap({"硬技能": ["SQL"], "软技能": []}, llm_client=client)

    assert "知识库证据" in client.system
    assert "user_profile_default:profile" in client.system
    assert "Python基础" in client.system
