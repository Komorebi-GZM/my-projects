"""CORS 中间件 — 允许小程序开发者工具访问。"""

from flask import Flask


def setup_cors(app: Flask) -> None:
    """配置 CORS 头。"""

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, X-Open-Id, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        return response
