"""权限校验模块单元测试。"""

import pytest
from src.common.permission import check_permission, PermissionError


def test_check_permission_admin():
    """测试管理员权限校验。"""
    # 模拟管理员用户
    result = check_permission("ADMIN", ["USER", "ADMIN"])
    assert result is True


def test_check_permission_user():
    """测试普通用户权限校验。"""
    # 模拟普通用户
    result = check_permission("USER", ["USER"])
    assert result is True


def test_check_permission_no_permission():
    """测试权限不足。"""
    with pytest.raises(PermissionError) as exc_info:
        check_permission("USER", ["ADMIN"])
    assert exc_info.value.code == 1003
    assert "权限不足" in exc_info.value.message


def test_check_permission_system():
    """测试系统权限。"""
    # 系统权限可以访问所有
    result = check_permission("SYSTEM", ["USER", "ADMIN"])
    assert result is True