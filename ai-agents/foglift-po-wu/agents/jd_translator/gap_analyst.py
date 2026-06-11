import json
from utils.knowledge_formatter import format_evidence_blocks
from utils.knowledge_retriever import KnowledgeRetriever
from utils.llm_client import invoke_llm


_PROFILE_RETRIEVER = KnowledgeRetriever()


SYSTEM_PROMPT = """你是差距分析师，负责分析求职者与目标职位之间的差距。

## 你的任务
基于JD要求分析求职者差距，输出固定2个差距项，以及弥补时间估计。

## 知识库证据
以下证据来自默认用户画像知识库，用于补足用户未提供画像时的分析依据：
{evidence_blocks}

## 用户画像参考
{profile_str}

请直接返回JSON，格式：
{{
    "差距项": [{{"技能": "xxx", "差距描述": "xxx"}}, ...],
    "弥补时间估计": "约X个月/年"
}}
差距项固定为2项。"""


def build_gap_analyst_prompt(
    jd_parsed: dict,
    user_profile: dict,
    evidence_blocks: str,
) -> tuple[str, str]:
    """Build the gap analyst prompt with resolved user profile context."""
    profile_str = "\n".join([f"- {k}: {v}" for k, v in user_profile.items()])

    system = SYSTEM_PROMPT.format(
        evidence_blocks=evidence_blocks,
        profile_str=profile_str,
    )
    user = f"JD要求：\n硬技能: {', '.join(jd_parsed.get('硬技能', []))}\n软技能: {', '.join(jd_parsed.get('软技能', []))}\n经验要求: {jd_parsed.get('经验要求', '')}\n学历要求: {jd_parsed.get('学历要求', '')}"
    return system, user


def analyze_gap(jd_parsed: dict, user_profile: dict = None, llm_client=None, kb=None) -> dict:
    """Analyze gaps between candidate profile and JD requirements."""
    hits = _PROFILE_RETRIEVER.retrieve(
        "默认用户画像",
        domains=["user_profile_default"],
        top_k=1,
    )
    if user_profile is None:
        user_profile = hits[0].metadata if hits else {}

    system, user = build_gap_analyst_prompt(
        jd_parsed,
        user_profile,
        format_evidence_blocks(hits),
    )

    try:
        result = invoke_llm(system, user, llm_client)
    except json.JSONDecodeError:
        result = {"差距项": [], "弥补时间估计": "无法估计"}

    return result
