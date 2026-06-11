from agents.path_skill.resource_retriever import retrieve_resources
from utils.knowledge_loader import knowledge


def test_retrieve_resources_returns_skill_with_resources():
    """retrieve_resources returns a list of skills with resource info from KB."""
    kb = knowledge.get_skill_resource_map()
    skills = [
        {"技能名": "SQL"},
        {"技能名": "Python"},
        {"技能名": "LangGraph"},
        {"技能名": "不存在的技能"}
    ]
    result = retrieve_resources(skills)

    assert isinstance(result, list)
    assert len(result) == 4
    assert result[0]["技能名"] == "SQL"
    assert isinstance(result[0]["资源"], list)
    assert result[0]["资源"] == kb["SQL"]
    assert result[1]["技能名"] == "Python"
    assert result[1]["资源"] == kb["Python"]
    assert result[2]["技能名"] == "LangGraph"
    assert result[2]["资源"] == kb["LangGraph"]
    assert result[3]["技能名"] == "不存在的技能"
    assert result[3]["资源"] == []


def test_retrieve_resources_preserves_response_shape_and_uses_skill_aliases():
    """retrieve_resources keeps the public shape while resolving known aliases."""
    kb = knowledge.get_skill_resource_map()
    result = retrieve_resources(["sql", {"技能名": "prompt"}])

    assert result == [
        {"技能名": "sql", "资源": kb["SQL"]},
        {"技能名": "prompt", "资源": kb["Prompt工程"]},
    ]
