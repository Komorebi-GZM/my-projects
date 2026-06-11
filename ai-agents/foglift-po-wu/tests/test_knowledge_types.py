from utils.knowledge_types import KnowledgeDoc, KnowledgeHit


def test_knowledge_hit_exposes_doc_fields():
    doc = KnowledgeDoc(
        id="skill_resource_map:SQL",
        domain="skill_resource_map",
        title="SQL",
        content="SQL resource content",
        metadata={"skill": "SQL"},
    )
    hit = KnowledgeHit(doc=doc, score=3.5, match_reasons=["exact_title"])

    assert hit.id == doc.id
    assert hit.domain == doc.domain
    assert hit.title == doc.title
    assert hit.content == doc.content
    assert hit.metadata == doc.metadata
