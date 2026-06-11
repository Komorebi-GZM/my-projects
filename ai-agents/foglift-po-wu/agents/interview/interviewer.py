import json
from utils.knowledge_formatter import format_evidence_blocks
from utils.knowledge_retriever import KnowledgeRetriever
from utils.llm_client import invoke_llm


_QUESTION_RETRIEVER = KnowledgeRetriever()


SYSTEM_PROMPT = """你是一个专业的面试官，擅长为特定岗位提出合适的面试问题。

## 你的任务
根据目标岗位，从题库中选择或生成一道面试题。

## 知识库证据
以下证据来自面试题库，请优先依据证据中的题目风格和评分要点生成：
{evidence_blocks}

## 输出格式
请严格返回JSON格式，不包含任何解释：
{{
    "question": "面试问题",
    "key_points": ["评分要点1", "评分要点2", ...]
}}

## 要求
- 选择题库中已有题目或基于题库风格生成
- key_points为该题的评分要点，3-5个
- 问题要贴合{target_position}岗位特点
"""

def get_question(target_position: str, session_store=None, llm_client=None) -> dict:
    """Get a random interview question for the target position and store in session."""
    if session_store is None:
        from utils.session_store import session_store as _store
        store = _store
    else:
        store = session_store

    hits = _QUESTION_RETRIEVER.retrieve(
        target_position,
        domains=["interview_questions"],
        top_k=3,
    )
    kb_questions = []
    if hits:
        kb_questions = hits[0].metadata.get("questions", [])

    if kb_questions:
        selected = kb_questions[0]
        question_text = selected.get("question", "")
        key_points = selected.get("key_points", [])
    else:
        example_hits = _QUESTION_RETRIEVER.retrieve(
            "数据分析师",
            domains=["interview_questions"],
            top_k=2,
        )
        system = SYSTEM_PROMPT.format(
            evidence_blocks=format_evidence_blocks(example_hits),
            target_position=target_position
        )
        user = f"请为{target_position}岗位生成一道面试题"
        try:
            parsed = invoke_llm(system, user, llm_client)
            question_text = parsed.get("question", "")
            key_points = parsed.get("key_points", [])
        except json.JSONDecodeError:
            question_text = f"请介绍一下你自己和{target_position}的相关经历"
            key_points = []

    session_id = store.create({
        "target_position": target_position,
        "question": question_text,
        "key_points": key_points
    })

    return {
        "session_id": session_id,
        "question": question_text,
        "key_points": key_points
    }
