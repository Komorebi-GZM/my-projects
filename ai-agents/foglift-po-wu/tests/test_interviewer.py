from agents.interview.interviewer import get_question
from utils.session_store import SessionStore
from utils.knowledge_retriever import KnowledgeRetriever


def test_get_question_returns_session_id_and_question():
    """get_question returns a dict with session_id and question from KB."""
    store = SessionStore(ttl_minutes=30)

    class MockClient:
        def chat_with_system(self, system: str, user: str) -> str:
            raise AssertionError("known KB questions should not call the LLM")

    result = get_question("数据分析师", store, llm_client=MockClient())

    hit = KnowledgeRetriever().retrieve(
        "数据分析师",
        domains=["interview_questions"],
        top_k=1,
    )[0]
    expected_question = hit.metadata["questions"][0]["question"]

    assert isinstance(result, dict)
    assert "session_id" in result
    assert "question" in result
    assert isinstance(result["session_id"], str)
    assert isinstance(result["question"], str)
    assert result["question"] == expected_question

    saved = store.get(result["session_id"])
    assert saved is not None
    assert saved["target_position"] == "数据分析师"
    assert saved["question"] == result["question"]
    assert "key_points" in saved


def test_get_question_uses_evidence_blocks_for_llm_fallback():
    """get_question uses interview-question evidence when generating fallback questions."""
    store = SessionStore(ttl_minutes=30)

    class RecordingClient:
        system = ""

        def chat_with_system(self, system: str, user: str) -> str:
            self.system = system
            return '{"question": "mock", "key_points": ["A", "B", "C"]}'

    client = RecordingClient()
    result = get_question("zzzz_unmatched_role_123", store, llm_client=client)

    assert result["question"] == "mock"
    assert result["key_points"] == ["A", "B", "C"]
    assert "知识库证据" in client.system
    assert "interview_questions:" in client.system
