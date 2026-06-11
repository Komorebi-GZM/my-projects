"""参数校验模块单元测试。"""

import pytest
from src.common.validator import validate_enum, validate_required, ValidationError


def test_validate_enum_valid():
    """测试枚举值校验（有效值）。"""
    result = validate_enum("USER", ["USER", "ADMIN", "SYSTEM"])
    assert result == "USER"


def test_validate_enum_invalid():
    """测试枚举值校验（无效值）。"""
    with pytest.raises(ValidationError) as exc_info:
        validate_enum("GUEST", ["USER", "ADMIN", "SYSTEM"])
    assert exc_info.value.code == 1001
    assert "无效的枚举值" in exc_info.value.message


def test_validate_required_valid():
    """测试必填参数校验（有效值）。"""
    result = validate_required("test_value", "参数名")
    assert result == "test_value"


def test_validate_required_missing():
    """测试必填参数校验（缺失值）。"""
    with pytest.raises(ValidationError) as exc_info:
        validate_required(None, "参数名")
    assert exc_info.value.code == 1001
    assert "参数名不能为空" in exc_info.value.message