"""参数校验模块。"""

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class ValidationError(Exception):
    """参数校验错误。"""

    code: int = 1001
    message: str = "参数校验失败"


def validate_enum(value: Any, allowed_values: List[Any]) -> Any:
    """校验枚举值是否在允许的范围内。

    Args:
        value: 要校验的值
        allowed_values: 允许的值列表

    Returns:
        原始值（如果有效）

    Raises:
        ValidationError: 如果值不在允许范围内
    """
    if value not in allowed_values:
        raise ValidationError(
            message=f"无效的枚举值: {value}，允许值: {allowed_values}"
        )
    return value


def validate_required(value: Any, field_name: str) -> Any:
    """校验必填参数。

    Args:
        value: 要校验的值
        field_name: 参数名称（用于错误信息）

    Returns:
        原始值（如果有效）

    Raises:
        ValidationError: 如果值为 None 或空字符串
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(message=f"{field_name}不能为空")
    return value