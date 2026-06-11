import json
from utils.knowledge_formatter import format_evidence_blocks
from utils.knowledge_retriever import KnowledgeRetriever
from utils.llm_client import invoke_llm


_SKILL_RETRIEVER = KnowledgeRetriever()


SYSTEM_PROMPT = """你是一个专业的技能推荐官，擅长为求职者推荐岗位相关的核心技能。

## 知识库证据
以下证据来自技能-资源映射知识库，请优先使用证据中的技能标准名称：
{evidence_blocks}

## 可用技能标准名称
{skill_keys}

## 你的任务
基于目标能力维度，给出推荐技能列表。

## 输入能力维度
{ability_dims}

## 输出格式
请严格返回JSON数组，不包含任何解释：
[
    {{"技能名": "SQL", "优先级": "高", "说明": "..."}},
    ...
]

## 要求
- 技能名尽量使用知识库中的标准键名
- 优先级分为：高、中、低
- 推荐3-6个技能
- 按优先级从高到低排列
"""

def recommend_skills(ability_dims: list, llm_client=None) -> list:
    """Recommend skills based on ability dimensions."""
    dims_str = "、".join(ability_dims) if ability_dims else "核心技能"
    hits = _SKILL_RETRIEVER.retrieve(
        dims_str,
        domains=["skill_resource_map"],
        top_k=10,
    )
    skill_keys = [
        doc.title
        for doc in _SKILL_RETRIEVER.docs
        if doc.domain == "skill_resource_map"
    ]
    keys_str = "、".join(skill_keys)

    system = SYSTEM_PROMPT.format(
        evidence_blocks=format_evidence_blocks(hits),
        skill_keys=keys_str,
        ability_dims=dims_str
    )
    user = f"请为具备以下能力维度的人推荐技能：{dims_str}"

    try:
        result = invoke_llm(system, user, llm_client)
    except json.JSONDecodeError:
        result = []

    return result
