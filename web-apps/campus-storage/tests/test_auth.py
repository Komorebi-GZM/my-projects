"""身份认证模块单元测试。"""

import pytest
from src.common.auth import get_current_user_id, AuthContext


def test_get_current_user_id_from_flask_request():
    """测试从 Flask 请求头获取用户 ID。"""
    from flask import Flask

    app = Flask(__name__)

    with app.test_request_context(headers={"X-OpenId": "o_test_openid_123"}):
        user_id = get_current_user_id()
        assert user_id == "o_test_openid_123"


def test_get_current_user_id_missing_header():
    """测试缺少 X-OpenId 头时返回 None。"""
    from flask import Flask

    app = Flask(__name__)

    with app.test_request_context():
        user_id = get_current_user_id()
        assert user_id is None
