"""校园物品暂存平台 — Flask 应用入口"""

import os
from flask import Flask, jsonify

from src.config import config
from src.middleware.cors import setup_cors
from src.middleware.error_handler import register_error_handlers
from src.middleware.request_logger import setup_request_logger
from src.routes.auth import auth_bp
from src.routes.orders import orders_bp
from src.routes.warehouses import warehouses_bp
from src.routes.addresses import addresses_bp
from src.tasks.scheduler import init_scheduler, shutdown_scheduler, get_scheduler_status


def create_app(config_name=None):
    """创建 Flask 应用实例。"""
    config_name = config_name or os.getenv("FLASK_ENV", "development")
    app = Flask(__name__)

    app.config.from_object(config[config_name])

    setup_cors(app)
    setup_request_logger(app)
    register_error_handlers(app)

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(warehouses_bp)
    app.register_blueprint(addresses_bp)

    # 初始化定时任务调度器（仅在非测试环境）
    if config_name != "testing":
        init_scheduler(app)

        # 注册关闭钩子
        import atexit
        atexit.register(lambda: shutdown_scheduler(app))

    @app.route("/api/health")
    def health():
        """健康检查端点。"""
        scheduler_status = get_scheduler_status(app)
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "status": "ok",
                "env": config_name,
                "scheduler": scheduler_status if config_name != "testing" else None
            }
        })

    # 开发环境调试端点：手动触发定时任务
    if config_name == "development":
        @app.route("/api/debug/trigger/<task_name>", methods=["POST"])
        def debug_trigger_task(task_name):
            """手动触发定时任务（仅开发环境）。"""
            from src.tasks.timeout_checker import check_pending_timeout, check_delivering_timeout
            from src.db.factory import get_db_adapter

            TASK_MAP = {
                "pending_timeout_checker": check_pending_timeout,
                "delivering_timeout_checker": check_delivering_timeout,
            }

            if task_name not in TASK_MAP:
                return jsonify({"code": 404, "message": "未知任务", "data": None}), 404

            db = get_db_adapter()
            try:
                result = TASK_MAP[task_name](db)
                return jsonify({"code": 0, "message": "success", "data": result})
            finally:
                db.close()

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("FLASK_PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
