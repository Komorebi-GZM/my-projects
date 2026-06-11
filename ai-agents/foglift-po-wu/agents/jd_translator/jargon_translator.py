import json
from utils.knowledge_formatter import format_evidence_blocks
from utils.knowledge_retriever import KnowledgeRetriever
from utils.llm_client import invoke_llm


_JARGON_RETRIEVER = KnowledgeRetriever()


SYSTEM_PROMPT = """你是黑话翻译官，负责将JD中的HR术语翻译成真实含义。

## 你的任务
将用户提供的HR黑话列表翻译成真实含义。

## 知识库证据
以下证据来自黑话映射知识库，请优先依据证据中的术语和真实含义翻译：
{evidence_blocks}

请直接返回JSON格式，key为黑话，value为真实含义。"""


def build_jargon_translator_prompt(jargon_list: list) -> tuple[str, str]:
    """Build the jargon translator prompt with jargon-map evidence blocks."""
    query = " ".join(jargon_list)
    hits = _JARGON_RETRIEVER.retrieve(query, domains=["jargon_map"], top_k=8)

    return (
        SYSTEM_PROMPT.format(evidence_blocks=format_evidence_blocks(hits)),
        f"请翻译以下黑话：\n{', '.join(jargon_list)}",
    )


def translate_jargon(jargon_list: list, llm_client=None, kb=None) -> dict:
    """Translate HR jargon to plain meanings."""
    system, user = build_jargon_translator_prompt(jargon_list)

    try:
        result = invoke_llm(system, user, llm_client)
    except json.JSONDecodeError:
        result = {term: "未识别黑话" for term in jargon_list}

    return result
