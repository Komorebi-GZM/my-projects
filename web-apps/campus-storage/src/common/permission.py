"""权限校验模块。"""

import os
from dataclasses import dataclass
from typing import List


@dataclass
class PermissionError(Exception):
    """权限错误。"""

    code: int = 1003
    message: str = "权限不足"


def check_permission(user_role: str, required_roles: List[str]) -> bool:
    """检查用户是否有权限访问指定资源。

    Args:
        user_role: 用户角色（USER/ADMIN/SYSTEM）
        required_roles: 所需角色列表

    Returns:
        bool: 是否有权限

    Raises:
        PermissionError: 如果权限不足
    """
    # SYSTEM 用户拥有所有权限
    if user_role == "SYSTEM":
        return True

    # 检查用户角色是否在所需角色列表中
    if user_role in required_roles:
        return True

    raise PermissionError(message=f"权限不足: 需要 {required_roles}，当前为 {user_role}")


# 默认管理员 openid 列表（可通过环境变量 ADMIN_OPENIDS 覆盖）
ADMIN_OPENIDS = set(
    os.environ.get("ADMIN_OPENIDS", "admin").split(",")
)


def is_admin(user_id: str) -> bool:
    """判断用户是否为管理员。"""
    return user_id in ADMIN_OPENIDS