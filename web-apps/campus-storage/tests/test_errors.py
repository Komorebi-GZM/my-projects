"""错误处理模块单元测试。"""

import pytest
from src.common.errors import ErrorCode, success_response, error_response


def test_error_codes_enum_exists():
    """测试 ErrorCode 枚举类存在且包含所有必需的错误码。"""
    assert ErrorCode.PARAM_ERROR.value == 1001
    assert ErrorCode.UNAUTHORIZED.value == 1002
    assert ErrorCode.FORBIDDEN.value == 1003
    assert ErrorCode.NOT_FOUND.value == 2001
    assert ErrorCode.INVALID_TRANSITION.value == 2002
    assert ErrorCode.LOCK_CONFLICT.value == 2003
    assert ErrorCode.TERMINAL_STATE.value == 2004
    assert ErrorCode.PAYMENT_ERROR.value == 3001
    assert ErrorCode.SYSTEM_ERROR.value == 5001


def test_success_response_format():
    """测试成功响应格式。"""
    result = success_response({"orderId": "123"})
    assert result["code"] == 0
    assert result["message"] == "success"
    assert result["data"]["orderId"] == "123"


def test_error_response_format():
    """测试错误响应格式。"""
    result = error_response(ErrorCode.PARAM_ERROR, "参数错误")
    assert result["code"] == 1001
    assert result["message"] == "参数错误"
    assert "data" not in result or result["data"] is None
