import json
from agents.jd_translator.jd_analyst import parse_jd


def test_parse_jd_returns_required_keys():
    """parse_jd returns a dict with 5 required keys."""
    mock_response = json.dumps({
        "硬技能": ["Python", "SQL", "数据可视化"],
        "软技能": ["沟通能力", "团队协作"],
        "经验要求": "3-5年数据分析经验",
        "学历要求": "本科及以上",
        "HR黑话": ["弹性工作"]
    })

    class MockClient:
        def chat_with_system(self, system: str, user: str) -> str:
            return mock_response

    result = parse_jd("数据分析师 JD", llm_client=MockClient())

    assert isinstance(result, dict)
    assert set(result.keys()) == {"硬技能", "软技能", "经验要求", "学历要求", "HR黑话"}
    assert isinstance(result["硬技能"], list)
    assert isinstance(result["软技能"], list)
    assert isinstance(result["经验要求"], str)
    assert isinstance(result["学历要求"], str)
    assert isinstance(result["HR黑话"], list)


def test_parse_jd_injects_jd_library_into_prompt():
    """parse_jd includes JD-library evidence blocks in the LLM prompt."""
    mock_response = json.dumps({
        "硬技能": [],
        "软技能": [],
        "经验要求": "",
        "学历要求": "",
        "HR黑话": []
    })

    class RecordingClient:
        system = ""

        def chat_with_system(self, system: str, user: str) -> str:
            self.system = system
            return mock_response

    client = RecordingClient()

    parse_jd("AI Agent Python SQL 大模型 JD", llm_client=client)

    assert "知识库证据" in client.system
    assert "jd_library:" in client.system
    assert "Python" in client.system
