from utils.knowledge_index import DOMAIN_ORDER, build_knowledge_docs


def test_build_knowledge_docs_covers_current_domains():
    docs = build_knowledge_docs()
    domains = {doc.domain for doc in docs}

    assert set(DOMAIN_ORDER).issubset(domains)
    assert len(docs) > len(DOMAIN_ORDER)


def test_build_knowledge_docs_preserves_resource_metadata():
    docs = build_knowledge_docs()
    sql_doc = next(doc for doc in docs if doc.id == "skill_resource_map:SQL")

    assert sql_doc.domain == "skill_resource_map"
    assert sql_doc.title == "SQL"
    assert sql_doc.metadata["skill"] == "SQL"
    assert sql_doc.metadata["resources"]
    assert "w3schools.com/sql" in sql_doc.content
