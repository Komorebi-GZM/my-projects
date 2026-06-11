import json
from utils.knowledge_formatter import format_evidence_blocks
from utils.knowledge_retriever import KnowledgeRetriever
from utils.llm_client import invoke_llm


_JD_RETRIEVER = KnowledgeRetriever()


SYSTEM_PROMPT = """你是一个专业的岗位拆解师，擅长从岗位名称中拆解出核心能力维度。

## 你的任务
针对用户提供的岗位名称，提取3-5个硬技能维度（不包含软技能）。

## 知识库证据
以下证据来自岗位JD知识库，请优先依据证据中的岗位名称、关键词和硬技能拆解能力维度：
{evidence_blocks}

## 输出格式
请严格返回JSON格式，不包含任何解释：
{{
    "岗位名称": "...",
    "能力维度": ["技能1", "技能2", "技能3", ...]
}}

## 要求
- 只输出硬技能维度
- 能力维度数量必须为3-5项
- 技能名称要贴近知识库中的标准命名
"""

def resolve_position(target_position: str, llm_client=None) -> dict:
    """Resolve a position into hard skill dimensions (3-5 items)."""
    hits = _JD_RETRIEVER.retrieve(
        target_position,
        domains=["jd_library"],
        top_k=3,
    )

    system = SYSTEM_PROMPT.format(evidence_blocks=format_evidence_blocks(hits))
    user = f"请分析以下岗位：{target_position}"

    try:
        result = invoke_llm(system, user, llm_client)
    except json.JSONDecodeError:
        result = {
            "岗位名称": target_position,
            "能力维度": []
        }

    return result
