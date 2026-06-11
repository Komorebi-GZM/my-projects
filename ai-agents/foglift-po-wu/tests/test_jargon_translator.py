import json
from agents.jd_translator.jargon_translator import translate_jargon


def test_translate_jargon_returns_dict():
    """translate_jargon returns a dict mapping jargon to meaning."""
    mock_response = json.dumps({
        "抗压能力强": "需要加班，处理紧急需求",
        "弹性工作": "不打卡但随时待命，下班后也要回消息"
    })

    class MockClient:
        def chat_with_system(self, system: str, user: str) -> str:
            return mock_response

    result = translate_jargon(["抗压能力强", "弹性工作"], llm_client=MockClient())

    assert isinstance(result, dict)
    assert "抗压能力强" in result
    assert "弹性工作" in result
    assert isinstance(result["抗压能力强"], str)
    assert isinstance(result["弹性工作"], str)


def test_translate_jargon_injects_jargon_map_into_prompt():
    """translate_jargon includes jargon-map evidence blocks in the LLM prompt."""
    mock_response = json.dumps({"快速成长": "岗位职责变化快，需要持续补位"})

    class RecordingClient:
        system = ""

        def chat_with_system(self, system: str, user: str) -> str:
            self.system = system
            return mock_response

    client = RecordingClient()

    translate_jargon(["快速成长"], llm_client=client)

    assert "知识库证据" in client.system
    assert "jargon_map:" in client.system
    assert "快速成长" in client.system
