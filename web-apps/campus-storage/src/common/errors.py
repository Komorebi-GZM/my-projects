"""统一错误处理模块。"""

from enum import IntEnum
from typing import Any, Dict, Optional


class ErrorCode(IntEnum):
    """统一错误码枚举。"""

    # 1xxx - 请求错误
    PARAM_ERROR = 1001  # 参数错误
    UNAUTHORIZED = 1002  # 未授权
    FORBIDDEN = 1003  # 禁止访问

    # 2xxx - 业务错误
    NOT_FOUND = 2001  # 资源不存在
    INVALID_TRANSITION = 2002  # 无效状态转换
    LOCK_CONFLICT = 2003  # 版本锁冲突
    TERMINAL_STATE = 2004  # 终止状态不可修改

    # 3xxx - 支付错误
    PAYMENT_ERROR = 3001  # 支付错误

    # 5xxx - 系统错误
    SYSTEM_ERROR = 5001  # 系统错误


def success_response(data: Optional[Any] = None) -> Dict[str, Any]:
    """成功响应格式。"""
    return {"code": 0, "message": "success", "data": data}


def error_response(code: ErrorCode, message: str) -> Dict[str, Any]:
    """错误响应格式。"""
    return {"code": code.value, "message": message}
