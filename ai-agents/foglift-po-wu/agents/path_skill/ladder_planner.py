import json
from utils.knowledge_formatter import format_evidence_blocks
from utils.knowledge_retriever import KnowledgeRetriever
from utils.llm_client import invoke_llm


_LADDER_RETRIEVER = KnowledgeRetriever()


SYSTEM_PROMPT = """你是一个专业的阶梯规划师，擅长为求职者规划从校园到秋招的成长路径。

## 知识库证据
以下证据来自阶梯路径模板知识库，请优先依据证据中的路径结构和岗位方向规划：
{evidence_blocks}

## 你的任务
基于模板，结合岗位的目标能力维度（{ability_dims}），生成个性化的四步阶梯路径。

## 输出格式
请严格返回JSON格式，不包含任何解释：
{{
    "step1_校园项目": "...",
    "step2_实习title": "...",
    "step3_实习积累关键词": "...",
    "step4_秋招目标岗位": "..."
}}

## 要求
- 保持模板的4步结构
- 根据能力维度做适当个性化调整
- 路径要实际可执行
"""

def plan_ladder(target_position: str, ability_dims: list, llm_client=None) -> dict:
    """Plan a 4-step career ladder for the target position."""
    hits = _LADDER_RETRIEVER.retrieve(
        target_position,
        domains=["ladder_templates"],
        top_k=3,
    )
    template = hits[0].metadata.get("template", {}) if hits else {}
    if not template:
        template = {
            "step1_校园项目": "",
            "step2_实习title": "",
            "step3_实习积累关键词": "",
            "step4_秋招目标岗位": "",
        }

    dims_str = "、".join(ability_dims) if ability_dims else "核心技能"

    system = SYSTEM_PROMPT.format(
        evidence_blocks=format_evidence_blocks(hits),
        ability_dims=dims_str
    )
    user = f"请为{dims_str}能力维度的求职者，规划{target_position}岗位的成长路径"

    try:
        result = invoke_llm(system, user, llm_client)
    except json.JSONDecodeError:
        result = template.copy()

    return result
