import uuid
from typing import Dict, Any, Optional

import structlog

logger = structlog.get_logger()


def generate_trace_id() -> str:
    """生成唯一链路追踪 ID。"""
    return str(uuid.uuid4())


def inject_trace_id(state: Dict[str, Any], parent_trace_id: Optional[str] = None) -> Dict[str, Any]:
    """向状态中注入 trace_id。"""
    state["trace_id"] = generate_trace_id()
    if parent_trace_id:
        state["parent_trace_id"] = parent_trace_id
    return state


def extract_trace_from_state(state: Dict[str, Any]) -> Dict[str, str]:
    """从状态中提取链路追踪信息。"""
    return {
        "trace_id": state.get("trace_id", "unknown"),
        "parent_trace_id": state.get("parent_trace_id"),
        "session_id": state.get("session_id", "unknown")
    }


def log_with_trace(
    event: str,
    state: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None,
    level: str = "info",
    **kwargs
) -> None:
    """携带 trace_id 的结构化日志快捷方法。

    DEV_GUIDE 7.2 节定义的标准日志接口，所有模块统一使用此函数记录关键操作日志。

    Args:
        event: 事件名称（如 "intent_parsed", "plan_generated"）
        state: 可选的 BrainstormState，从中提取 trace_id
        trace_id: 可选的显式 trace_id（优先级高于 state）
        level: 日志级别（info / warning / error / debug）
        **kwargs: 附加日志字段
    """
    # trace_id 来源优先级：显式传入 > state 提取 > 默认 "unknown"
    resolved_trace_id = trace_id
    if not resolved_trace_id and state:
        resolved_trace_id = state.get("trace_id", "unknown")
    if not resolved_trace_id:
        resolved_trace_id = "unknown"

    log_method = getattr(logger, level, logger.info)
    log_method(event, trace_id=resolved_trace_id, **kwargs)
