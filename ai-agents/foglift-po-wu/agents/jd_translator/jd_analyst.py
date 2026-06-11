import json
from utils.knowledge_formatter import format_evidence_blocks
from utils.knowledge_retriever import KnowledgeRetriever
from utils.llm_client import invoke_llm


_JD_RETRIEVER = KnowledgeRetriever()


SYSTEM_PROMPT = """你是一个专业的JD解析师，擅长从职位描述中提取关键信息。

## 你的任务
分析用户提供的JD文本，提取以下5个维度的信息：
1. 硬技能：技术能力、工具使用、编程语言等
2. 软技能：沟通、协作、领导力等
3. 经验要求：工作年限要求
4. 学历要求：学历学位要求
5. HR黑话：需要翻译的HR术语

## 知识库证据
以下证据来自岗位JD知识库，请优先参考证据中的岗位关键词、硬技能、软技能和要求字段：
{evidence_blocks}

## 输出要求
请严格返回标准JSON格式，不要包含任何markdown标记、注释或额外文字：
{{
  "硬技能": ["技能1", "技能2"],
  "软技能": ["能力1"],
  "经验要求": "年限要求",
  "学历要求": "学历要求",
  "HR黑话": ["术语1"]
}}"""


def build_jd_parser_prompt(jd_text: str) -> tuple[str, str]:
    """Build the JD parser prompt with JD-library evidence blocks."""
    hits = _JD_RETRIEVER.retrieve(jd_text, domains=["jd_library"], top_k=3)

    return (
        SYSTEM_PROMPT.format(evidence_blocks=format_evidence_blocks(hits)),
        f"请分析以下JD：\n{jd_text}",
    )


def parse_jd(jd_text: str, llm_client=None, kb=None) -> dict:
    """Parse a job description into structured fields."""
    system, user = build_jd_parser_prompt(jd_text)

    try:
        result = invoke_llm(system, user, llm_client)
    except json.JSONDecodeError as e:
        print(f"[JD解析警告] LLM返回非标准JSON，尝试修复: {e}")
        result = {"硬技能": [], "软技能": [], "经验要求": "", "学历要求": "", "HR黑话": []}
    except Exception as e:
        print(f"[JD解析错误] {type(e).__name__}: {e}")
        result = {"硬技能": [], "软技能": [], "经验要求": "", "学历要求": "", "HR黑话": []}

    return result
