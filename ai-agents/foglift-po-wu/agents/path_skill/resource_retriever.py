from utils.knowledge_retriever import KnowledgeRetriever


_RESOURCE_RETRIEVER = KnowledgeRetriever()


def _normalize_skill(skill_name: str) -> str:
    """Normalize skill name for KB lookup."""
    skill_map = {
        "sql": "SQL", "mysql": "SQL", "数据库": "SQL",
        "python": "Python", "pandas": "Python", "numpy": "Python",
        "excel": "Excel", "电子表格": "Excel",
        "tableau": "Tableau",
        "powerbi": "PowerBI", "power bi": "PowerBI",
        "axure": "Axure",
        "selenium": "Selenium",
        "appium": "Appium",
        "jmeter": "Jmeter",
        "langchain": "LangChain",
        "langgraph": "LangGraph",
        "rag": "RAG",
        "向量数据库": "向量数据库", "faiss": "向量数据库", "chroma": "向量数据库",
        "fastapi": "FastAPI",
        "prompt工程": "Prompt工程", "prompt": "Prompt工程"
    }
    normalized = skill_name.lower().strip()
    return skill_map.get(normalized, skill_name)


def retrieve_resources(skills: list, llm_client=None) -> list:
    """Retrieve resources for skills from KB. Returns list with skill name and resources."""
    result = []
    
    for skill in skills:
        skill_name = skill.get("技能名", "") if isinstance(skill, dict) else skill
        
        normalized = _normalize_skill(skill_name)
        hits = _RESOURCE_RETRIEVER.retrieve(
            normalized,
            domains=["skill_resource_map"],
            top_k=1,
        )
        resources = []
        if hits and hits[0].title == normalized:
            resources = hits[0].metadata.get("resources", [])
        
        result.append({
            "技能名": skill_name,
            "资源": resources
        })
    
    return result
