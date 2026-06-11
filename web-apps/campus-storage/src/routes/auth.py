"""认证相关路由。"""

from flask import Blueprint, request, jsonify

from src.common.auth import get_current_user_id
from src.common.errors import success_response, error_response, ErrorCode
from src.db.factory import get_db_adapter

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


@auth_bp.route("/login", methods=["POST"])
def login():
    """微信登录/模拟登录。

    本地开发模式：从请求头 X-Open-Id 获取用户标识
    生产环境：从 CloudBase event 获取

    Request Headers:
        X-Open-Id: 用户标识（本地开发模式）

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": {
                "openId": "xxx",
                "role": "USER"
            }
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        db = get_db_adapter()

        # 查询或创建用户
        user = db.find_one("users", {"_openid": user_id})
        if not user:
            # 创建新用户
            user_data = {
                "_openid": user_id,
                "nickName": "",
                "avatarUrl": "",
                "role": "USER",
            }
            user_id_created = db.insert("users", user_data)
            user = db.find_one("users", {"_id": user_id_created})

        return success_response({
            "openId": user.get("_openid") or user.get("openid"),
            "nickName": user.get("nickName", ""),
            "avatarUrl": user.get("avatarUrl", ""),
            "role": user.get("role", "USER"),
        })

    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500
