"""身份认证模块。"""

from dataclasses import dataclass
from typing import Optional

from flask import request


@dataclass
class AuthContext:
    """认证上下文。"""

    user_id: Optional[str] = None
    openid: Optional[str] = None


def get_current_user_id() -> Optional[str]:
    """获取当前用户 ID。

    - 本地开发：从请求头 X-OpenId 获取
    - 生产环境：从 CloudBase event.userInfo 获取
    """
    # TODO: 支持生产环境 CloudBase event.userInfo
    return request.headers.get("X-OpenId")
