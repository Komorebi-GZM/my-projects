from utils.knowledge_formatter import EMPTY_EVIDENCE_TEXT, format_evidence_blocks
from utils.knowledge_types import KnowledgeDoc, KnowledgeHit


def test_format_evidence_blocks_returns_empty_fallback():
    assert format_evidence_blocks([]) == EMPTY_EVIDENCE_TEXT


def test_format_evidence_blocks_includes_source_and_truncated_content():
    doc = KnowledgeDoc(
        id="skill_resource_map:SQL",
        domain="skill_resource_map",
        title="SQL",
        content="abcdef",
        metadata={"skill": "SQL"},
    )
    hit = KnowledgeHit(doc=doc, score=2.345, match_reasons=["exact_title"])

    result = format_evidence_blocks([hit], max_content_chars=3)

    assert "[证据 1] skill_resource_map / SQL" in result
    assert "id: skill_resource_map:SQL" in result
    assert "score: 2.35" in result
    assert "match_reasons: exact_title" in result
    assert "abc..." in result
