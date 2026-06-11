from utils.knowledge_retriever import KnowledgeRetriever
from utils.knowledge_types import KnowledgeDoc, KnowledgeHit


def _docs():
    return [
        KnowledgeDoc(
            id="skill_resource_map:SQL",
            domain="skill_resource_map",
            title="SQL",
            content="SQL 数据库 查询 教程",
            metadata={"skill": "SQL"},
        ),
        KnowledgeDoc(
            id="jargon_map:common_jargons:抗压能力强",
            domain="jargon_map",
            title="抗压能力强",
            content="抗压能力强 经常加班",
            metadata={"phrase": "抗压能力强", "meaning": "经常加班"},
        ),
        KnowledgeDoc(
            id="interview_questions:Agent",
            domain="interview_questions",
            title="Agent 面试",
            content="请解释 Agent 的工作原理",
            metadata={"position": "Agent"},
        ),
    ]


def test_retrieve_returns_ranked_explainable_hits():
    retriever = KnowledgeRetriever(docs=_docs())
    hits = retriever.retrieve("SQL", top_k=2)

    assert [hit.id for hit in hits] == ["skill_resource_map:SQL"]
    assert hits[0].score > 0
    assert hits[0].match_reasons


def test_retrieve_filters_domains_before_scoring():
    retriever = KnowledgeRetriever(docs=_docs())
    hits = retriever.retrieve("Agent", domains=["skill_resource_map"])

    assert hits == []


def test_retrieve_handles_empty_query_and_top_k():
    retriever = KnowledgeRetriever(docs=_docs())

    assert retriever.retrieve("") == []
    assert retriever.retrieve("SQL", top_k=0) == []


def test_retrieve_uses_chinese_grams():
    retriever = KnowledgeRetriever(docs=_docs())
    hits = retriever.retrieve("抗压", domains=["jargon_map"])

    assert [hit.id for hit in hits] == ["jargon_map:common_jargons:抗压能力强"]


def test_semantic_backend_is_limited_to_filtered_docs():
    class Backend:
        def search(self, query, docs, top_k):
            return [
                KnowledgeHit(docs[0], 1.0, ["semantic"]),
                KnowledgeHit(_docs()[1], 99.0, ["semantic_leak"]),
            ]

    retriever = KnowledgeRetriever(docs=_docs(), semantic_backend=Backend())
    hits = retriever.retrieve("anything", domains=["skill_resource_map"])

    assert [hit.id for hit in hits] == ["skill_resource_map:SQL"]
    assert hits[0].match_reasons == ["semantic"]
