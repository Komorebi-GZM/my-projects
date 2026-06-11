import os
import re
import json
import ast
import time
import structlog
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from agents.llm_config import get_llm_settings

load_dotenv()

logger = structlog.get_logger()

MOCK_LLM = os.getenv("MOCK_LLM", "false").lower() == "true"
LLM_SETTINGS = get_llm_settings()
DEFAULT_MODEL = LLM_SETTINGS.model
LLM_BASE_URL = LLM_SETTINGS.base_url
_openai_client = None


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        LLM_SETTINGS.validate_for_runtime()
        from openai import OpenAI
        _openai_kwargs = {"api_key": LLM_SETTINGS.api_key}
        if LLM_SETTINGS.base_url:
            _openai_kwargs["base_url"] = LLM_SETTINGS.base_url
        _openai_client = OpenAI(**_openai_kwargs)
    return _openai_client


# ── Mock LLM 响应库 ──────────────────────────────────────────────
_MOCK_INTENT = """{
    "location": {"city": "北京", "district": "朝阳区", "area": "三里屯"},
    "time": {"range": "周末下午", "flexibility": "±2h"},
    "group": {"type": "friends", "count": 4, "children": []},
    "scene": "friends",
    "activity_type": "dining",
    "constraints": {"max_distance_km": 10, "budget": 800, "duration_hours": 2},
    "preferences": {"food": "烤肉", "activity": "无偏好"},
    "missing_fields": []
}"""

_MOCK_PLANNER = """[
    {
        "id": "plan_001",
        "name": "三里屯炭火烤肉·四人套餐",
        "restaurant": "望京小腰烤肉店（三里屯店）",
        "address": "北京市朝阳区三里屯路19号院",
        "cuisine": "炭火烤肉",
        "price_per_person": 180,
        "total_budget": 720,
        "rating": 4.6,
        "duration_hours": 2,
        "poi_id": "POI_001"
    },
    {
        "id": "plan_002",
        "name": "合生汇·韩式烤肉畅吃",
        "restaurant": "姜虎东白丁烤肉（合生汇店）",
        "address": "北京市朝阳区西大望路甲22号",
        "cuisine": "韩式烤肉",
        "price_per_person": 195,
        "total_budget": 780,
        "rating": 4.5,
        "duration_hours": 2,
        "poi_id": "POI_002"
    },
    {
        "id": "plan_003",
        "name": "朝阳大悦城·和牛烧肉",
        "restaurant": "赤坂亭·和牛烧肉（大悦城店）",
        "address": "北京市朝阳区朝阳北路101号",
        "cuisine": "日式和牛烧肉",
        "price_per_person": 210,
        "total_budget": 840,
        "rating": 4.8,
        "duration_hours": 2,
        "poi_id": "POI_003"
    }
]"""

_MOCK_REVIEW = """{
    "candidate_id": "plan_001",
    "score": 7.5,
    "veto": false,
    "comment": "烤肉品质不错，位置在三里屯核心区域，交通便利。"
}"""

_MOCK_REVISE = """[
    {
        "id": "plan_001",
        "name": "三里屯炭火烤肉·四人套餐（优化版）",
        "restaurant": "望京小腰烤肉店（三里屯店）",
        "address": "北京市朝阳区三里屯路19号院",
        "cuisine": "炭火烤肉",
        "price_per_person": 170,
        "total_budget": 680,
        "rating": 4.6,
        "duration_hours": 2,
        "poi_id": "POI_001",
        "revisions": "根据评审反馈，调整价格优惠方案"
    },
    {
        "id": "plan_002",
        "name": "合生汇·韩式烤肉畅吃",
        "restaurant": "姜虎东白丁烤肉（合生汇店）",
        "address": "北京市朝阳区西大望路甲22号",
        "cuisine": "韩式烤肉",
        "price_per_person": 195,
        "total_budget": 780,
        "rating": 4.5,
        "duration_hours": 2,
        "poi_id": "POI_002",
        "revisions": "保持原方案"
    }
]"""

_MOCK_REGENERATE = """[
    {
        "id": "plan_004",
        "name": "国贸·黑毛和牛烤肉体验",
        "restaurant": "烧肉达人（国贸商城店）",
        "address": "北京市朝阳区建国门外大街1号",
        "cuisine": "日式和牛烤肉",
        "price_per_person": 185,
        "total_budget": 740,
        "rating": 4.7,
        "duration_hours": 2,
        "poi_id": "POI_004"
    }
]"""


def _mock_llm_response(prompt: str, system_prompt: Optional[str] = None) -> str:
    """根据 system_prompt 中的 Agent 身份关键词返回对应的 mock 响应。

    使用更精确的关键词匹配，避免误判（如 planner prompt 含"意图"触发 intent mock）。
    """
    sp = (system_prompt or "").lower()
    p = prompt.lower()

    # Intent Agent：prompt 含"解析专家" + "意图信息"
    if "解析专家" in sp and ("意图信息" in sp or "结构化" in sp):
        return _MOCK_INTENT

    # Planner Agent：prompt 含"规划专家" 或 "候选活动方案"
    if "规划专家" in sp or "候选活动方案" in sp:
        # 根据 user_prompt 判断是 revise 还是 regenerate
        if "反馈" in p or "revise" in p or "修改" in p:
            return _MOCK_REVISE
        if "regenerate" in p or "重新生成" in p or "exclude" in p:
            return _MOCK_REGENERATE
        return _MOCK_PLANNER

    # 评审 Agent：prompt 含"评审" 或特定 Agent 名称
    if "评审" in sp or "体验" in sp or "安全" in sp or "效率" in sp or "预算" in sp:
        return _MOCK_REVIEW

    # 兜底：默认返回评审响应
    return _MOCK_REVIEW


def _safe_eval(response: str) -> Dict[str, Any]:
    """安全解析 LLM 返回的 Dict 内容。

    三级 fallback 策略：
    1. ast.literal_eval — 只允许字面量（{}、[]、str、int、float、bool、None）
    2. json.loads — 标准 JSON 解析
    3. 受限 eval — 通过 AST 白名单校验后执行（仅允许字面量表达式）

    Raises:
        ValueError: 三种方式均无法解析时抛出
    """
    response = response.strip()

    # 提取 markdown 代码块内容
    if response.startswith("```"):
        match = re.search(r"```(?:\w+)?\n?(.*?)```", response, re.DOTALL)
        if match:
            response = match.group(1).strip()

    # 响应长度安全限制（防止超大 payload）
    if len(response) > 10_240:
        raise ValueError(f"响应内容过长（{len(response)} 字符），拒绝解析")

    # 级别 1: ast.literal_eval（最安全，但不支持单/双引号混用等 Python 特有语法）
    try:
        result = ast.literal_eval(response)
        if isinstance(result, dict):
            return result
    except (ValueError, SyntaxError):
        pass

    # 级别 2: json.loads（标准 JSON）
    try:
        result = json.loads(response)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, ValueError):
        pass

    # 级别 3: AST 白名单校验后 eval（允许 True/False/None 等 Python 字面量）
    try:
        tree = ast.parse(response, mode="eval")
        if _is_safe_ast(tree.body):
            result = eval(response)  # noqa: S307 — 已通过 AST 白名单校验
            if isinstance(result, dict):
                return result
    except (ValueError, SyntaxError):
        pass

    raise ValueError(f"无法解析响应为 Dict（三种方式均失败）：{response[:200]}")


def _safe_eval_any(response: str) -> Any:
    """安全解析 LLM 返回的任意字面量（Dict/List/str/int 等）。

    与 _safe_eval 相同的三级 fallback，但接受 Dict 和 List 两种类型。
    用于 Planner 等需要返回 List 的场景。
    """
    response = response.strip()

    if response.startswith("```"):
        match = re.search(r"```(?:\w+)?\n?(.*?)```", response, re.DOTALL)
        if match:
            response = match.group(1).strip()

    if len(response) > 10_240:
        raise ValueError(f"响应内容过长（{len(response)} 字符），拒绝解析")

    # 级别 1: ast.literal_eval
    try:
        result = ast.literal_eval(response)
        if isinstance(result, (dict, list)):
            return result
    except (ValueError, SyntaxError):
        pass

    # 级别 2: json.loads
    try:
        result = json.loads(response)
        if isinstance(result, (dict, list)):
            return result
    except (json.JSONDecodeError, ValueError):
        pass

    # 级别 3: AST 白名单校验后 eval
    try:
        tree = ast.parse(response, mode="eval")
        if _is_safe_ast(tree.body):
            result = eval(response)  # noqa: S307
            if isinstance(result, (dict, list)):
                return result
    except (ValueError, SyntaxError):
        pass

    raise ValueError(f"无法解析响应为 Dict/List（三种方式均失败）：{response[:200]}")


def _is_safe_ast(node: ast.AST) -> bool:
    """AST 白名单校验：仅允许字面量表达式（Dict/List/str/int/float/bool/None）。

    拒绝任何函数调用、属性访问、导入等操作。
    """
    if isinstance(node, ast.Dict):
        return all(_is_safe_ast(k) and _is_safe_ast(v) for k, v in zip(node.keys, node.values))
    if isinstance(node, ast.List) or isinstance(node, ast.Tuple) or isinstance(node, ast.Set):
        return all(_is_safe_ast(elt) for elt in node.elts)
    if isinstance(node, ast.Constant):
        return True
    return False


def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_retries: int = 2,
    trace_id: Optional[str] = None
) -> str:
    """调用 LLM 生成文本响应，支持重试和 structlog 日志。

    Args:
        prompt: 用户 Prompt
        system_prompt: 系统 Prompt
        temperature: 采样温度（可通过 LLM_FORCE_TEMPERATURE 强制覆盖）
        max_retries: 最大重试次数
        trace_id: 链路追踪 ID

    Returns:
        LLM 返回的文本内容

    Raises:
        RuntimeError: 所有重试耗尽后抛出
    """
    temperature = LLM_SETTINGS.normalize_temperature(temperature)
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    log_kwargs = {
        "trace_id": trace_id,
        "model": LLM_SETTINGS.model,
        "provider": LLM_SETTINGS.provider,
        "temperature": temperature,
    }
    logger.info("llm_call_start", **log_kwargs, prompt_length=len(prompt), mock=MOCK_LLM)

    # ── Mock LLM 模式 ──
    if MOCK_LLM:
        time.sleep(0.1)  # 模拟延迟
        mock_response = _mock_llm_response(prompt, system_prompt)
        logger.info("llm_call_success", **log_kwargs, attempt=1, latency_ms=100, response_length=len(mock_response), mock=True)
        return mock_response

    # ── 真实 LLM 调用 ──
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            start_time = time.time()

            response = _get_openai_client().chat.completions.create(
                model=LLM_SETTINGS.model,
                messages=messages,
                temperature=temperature,
                max_tokens=LLM_SETTINGS.max_tokens,
            )
            latency_ms = int((time.time() - start_time) * 1000)
            content = response.choices[0].message.content

            logger.info(
                "llm_call_success",
                **log_kwargs,
                attempt=attempt + 1,
                latency_ms=latency_ms,
                response_length=len(content)
            )
            return content
        except RuntimeError:
            raise
        except Exception as e:
            last_error = str(e)
            logger.warning(
                "llm_call_exception",
                **log_kwargs,
                attempt=attempt + 1,
                error=last_error
            )
            if attempt == max_retries:
                raise RuntimeError(f"LLM 调用异常：{e}")

    raise RuntimeError("LLM 调用达到最大重试次数")


def call_llm_dict(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    trace_id: Optional[str] = None
) -> Dict[str, Any]:
    """调用 LLM 并将响应解析为 Dict。"""
    response_text = call_llm(prompt, system_prompt, temperature, trace_id=trace_id)
    return parse_dict_from_response(response_text, trace_id=trace_id)


def parse_dict_from_response(response: str, trace_id: Optional[str] = None) -> Dict[str, Any]:
    """安全解析 LLM 响应为 Dict。"""
    try:
        return _safe_eval(response)
    except ValueError as e:
        logger.error("llm_parse_failed", trace_id=trace_id, error=str(e), response_preview=response[:200])
        raise
