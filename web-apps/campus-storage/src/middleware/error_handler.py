"""统一错误处理中间件。"""

from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """注册全局错误处理器。"""

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """处理 HTTP 异常。"""
        response = {
            "code": e.code or 500,
            "message": e.description,
            "data": None,
        }
        return jsonify(response), e.code

    @app.errorhandler(Exception)
    def handle_exception(e):
        """处理未捕获的异常。"""
        app.logger.error(f"Unhandled exception: {e}", exc_info=True)
        response = {
            "code": 5001,
            "message": "Internal server error",
            "data": None,
        }
        return jsonify(response), 500
