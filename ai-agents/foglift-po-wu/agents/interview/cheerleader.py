import json
from utils.llm_client import invoke_llm


SYSTEM_PROMPT = """你是一个温暖的鼓励师，擅长给求职者加油打气。

## 你的任务
根据求职者的面试表现，给出真诚的鼓励和建议。

## 面试表现评分
总分：{total_score}

## 亮点
{strengths}

## 输出格式
请严格返回JSON格式，不包含任何解释：
{{
    "鼓励语": "...",
    "亮点": ["...", "..."],
    "建议": "..."
}}
"""

def generate_encouragement(total_score: float, strengths: list, llm_client=None) -> dict:
    """Generate encouragement based on total score and strengths."""
    strength_str = "、".join(strengths) if strengths else "有潜力"

    system = SYSTEM_PROMPT.format(
        total_score=total_score,
        strengths=strength_str
    )
    user = f"面试总分{total_score}分，请给出鼓励"

    try:
        result = invoke_llm(system, user, llm_client)
    except json.JSONDecodeError:
        result = {"鼓励语": "继续加油！", "亮点": [], "建议": ""}

    result["敢投指数"] = total_score

    return result