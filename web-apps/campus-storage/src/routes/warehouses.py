"""仓库相关路由。"""

from flask import Blueprint, request

from src.common.errors import success_response, error_response, ErrorCode
from src.db.factory import get_db_adapter

warehouses_bp = Blueprint("warehouses", __name__, url_prefix="/api")


@warehouses_bp.route("/warehouses", methods=["GET"])
def get_warehouses():
    """获取仓库列表。

    Query Parameters:
        city: 城市筛选（可选）

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": [
                {
                    "_id": "wh_001",
                    "name": "北京中心仓",
                    "city": "北京",
                    "address": "朝阳区xxx",
                    "capacity": 100,
                    "usedCapacity": 20
                },
                ...
            ]
        }
    """
    try:
        city = request.args.get("city")

        db = get_db_adapter()

        # 构建查询条件
        query = {}
        if city:
            query["city"] = city

        # 查询仓库列表（只返回活跃状态的仓库）
        query["status"] = "ACTIVE"
        warehouses = db.find_many(
            "warehouses",
            query,
            sort=[("createTime", -1)],
            limit=100,
            skip=0,
        )

        return success_response(warehouses)

    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500
