"""请求日志中间件。"""

import time
from flask import Flask, g, request


def setup_request_logger(app: Flask) -> None:
    """记录请求方法、路径、耗时。"""

    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_method = request.method
        g.request_path = request.path

    @app.after_request
    def after_request(response):
        if hasattr(g, "start_time"):
            duration = time.time() - g.start_time
            app.logger.info(f"{g.request_method} {g.request_path} - {response.status_code} - {duration:.3f}s")
        return response
