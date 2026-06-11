import json
from utils.llm_client import invoke_llm


SYSTEM_PROMPT = """你是一个专业的面试答案分析师，擅长评估求职者的面试回答。

## 你的任务
根据面试题目、标准答案要点，对求职者的回答进行三维评分。

## 评分标准
- 内容分（40%）：回答内容的完整性、相关性、深度
- 逻辑分（30%）：回答的逻辑性、条理性、表达清晰度
- 匹配分（30%）：回答与岗位要求的匹配程度

## 题目
{question}

## 标准评分要点
{key_points}

## 求职者回答
{answer}

## 输出格式
请严格返回JSON格式，不包含任何解释：
{{
    "内容分": 0-100的整数,
    "逻辑分": 0-100的整数,
    "匹配分": 0-100的整数,
    "总分": 0-100的整数
}}
"""

def analyze_answer(question: str, answer: str, key_points: list, llm_client=None) -> dict:
    """Analyze interview answer and return 3 scores + total."""
    kp_str = "、".join(key_points) if key_points else "无标准要点"

    system = SYSTEM_PROMPT.format(
        question=question,
        key_points=kp_str,
        answer=answer
    )
    user = "请评估以上回答"

    try:
        result = invoke_llm(system, user, llm_client)
        if "总分" not in result:
            result["总分"] = round(0.4 * result.get("内容分", 0) + 
                                   0.3 * result.get("逻辑分", 0) + 
                                   0.3 * result.get("匹配分", 0))
    except json.JSONDecodeError:
        result = {"内容分": 0, "逻辑分": 0, "匹配分": 0, "总分": 0}

    return result