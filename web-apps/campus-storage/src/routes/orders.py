"""订单相关路由。"""

from flask import Blueprint, request, jsonify

from src.common.auth import get_current_user_id
from src.common.errors import success_response, error_response, ErrorCode
from src.common.validator import validate_required, ValidationError
from src.core.order_service import OrderService, OrderCreateError
from src.core.order_state import OrderStateMachine, InvalidTransitionError
from src.db.factory import get_db_adapter

orders_bp = Blueprint("orders", __name__, url_prefix="/api")


@orders_bp.route("/orders", methods=["POST"])
def create_order():
    """创建新订单。

    Request Body:
        {
            "city": "北京",
            "itemType": "LUGGAGE",
            "warehouseId": "wh_bj_central"
        }

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": {
                "_id": "xxx",
                "orderNo": "ORD20260510...",
                "status": "PENDING",
                ...
            }
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        data = request.get_json()
        if not data:
            return error_response(ErrorCode.PARAM_ERROR, "请求体不能为空"), 400

        # 添加用户ID到订单数据
        data["userId"] = user_id

        db = get_db_adapter()
        service = OrderService(db)
        order = service.create_order(data)

        return success_response(order), 201

    except OrderCreateError as e:
        return error_response(e.code, e.message), 400
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500


@orders_bp.route("/orders", methods=["GET"])
def get_order_list():
    """获取订单列表。

    Query Parameters:
        page: 页码（默认1）
        pageSize: 每页数量（默认10）
        status: 状态筛选（可选）

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": {
                "list": [...],
                "total": 100,
                "page": 1,
                "pageSize": 10
            }
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        # 获取分页参数
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("pageSize", 10, type=int)
        status_filter = request.args.get("status")

        # 限制分页范围
        page = max(1, page)
        page_size = min(100, max(1, page_size))

        db = get_db_adapter()

        # 构建查询条件
        # 管理员可以看到所有订单
        from src.common.permission import is_admin
        if is_admin(user_id):
            query = {}
        else:
            query = {"userId": user_id}
        if status_filter:
            query["status"] = status_filter

        # 查询总数
        total = db.count("orders", query)

        # 查询列表
        skip = (page - 1) * page_size
        orders = db.find_many(
            "orders",
            query,
            sort=[("createTime", -1)],
            limit=page_size,
            skip=skip,
        )

        return success_response({
            "list": orders,
            "total": total,
            "page": page,
            "pageSize": page_size,
        })

    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500


@orders_bp.route("/orders/<order_id>", methods=["GET"])
def get_order_detail(order_id):
    """获取订单详情。

    Path Parameters:
        order_id: 订单ID

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": {...}
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        db = get_db_adapter()
        order = db.find_one("orders", {"_id": order_id})

        if not order:
            return error_response(ErrorCode.NOT_FOUND, "订单不存在"), 404

        # 权限检查：用户只能查看自己的订单
        if order.get("userId") != user_id:
            return error_response(ErrorCode.FORBIDDEN, "无权访问该订单"), 403

        return success_response(order)

    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500


@orders_bp.route("/orders/<order_id>/status", methods=["PATCH"])
def update_order_status(order_id):
    """更新订单状态。

    Path Parameters:
        order_id: 订单ID

    Request Body:
        {
            "newStatus": "COLLECTED",
            "operatorType": "ADMIN",
            "reason": "操作原因（可选）"
        }

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": {...}
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        data = request.get_json()
        if not data:
            return error_response(ErrorCode.PARAM_ERROR, "请求体不能为空"), 400

        new_status = data.get("newStatus")
        operator_type = data.get("operatorType", "USER")
        reason = data.get("reason", "")

        # 验证必填字段
        try:
            validate_required(new_status, "newStatus")
        except ValidationError as e:
            return error_response(ErrorCode.PARAM_ERROR, e.message), 400

        db = get_db_adapter()

        # 查询订单
        order = db.find_one("orders", {"_id": order_id})
        if not order:
            return error_response(ErrorCode.NOT_FOUND, "订单不存在"), 404

        # 权限检查
        if operator_type == "USER" and order.get("userId") != user_id:
            return error_response(ErrorCode.FORBIDDEN, "无权操作该订单"), 403

        # 状态机校验
        try:
            machine = OrderStateMachine(order.get("status", "PENDING"))
            machine.transition(new_status)
        except InvalidTransitionError as e:
            return error_response(ErrorCode.INVALID_TRANSITION, str(e)), 400

        # 更新订单状态
        current_status = order.get("status", "PENDING")
        status_history = order.get("statusHistory", [])

        # 添加状态变更记录
        from datetime import datetime, timezone
        status_record = {
            "from": current_status,
            "to": new_status,
            "operatorType": operator_type,
            "operatorId": user_id,
            "time": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        }
        if reason:
            status_record["reason"] = reason

        status_history.append(status_record)

        # 执行更新
        updated = db.update_one(
            "orders",
            {"_id": order_id},
            {
                "status": new_status,
                "statusHistory": status_history,
            }
        )

        if not updated:
            return error_response(ErrorCode.LOCK_CONFLICT, "订单状态已变更，请刷新后重试"), 409

        # 返回更新后的订单
        updated_order = db.find_one("orders", {"_id": order_id})
        return success_response(updated_order)

    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500


@orders_bp.route("/orders/<order_id>/payment", methods=["POST"])
def create_payment(order_id):
    """创建支付单。

    Path Parameters:
        order_id: 订单ID

    Request Body:
        {
            "amount": {
                "storageFee": 100,
                "deliveryFee": 50,
                "insuranceFee": 10,
                "totalFee": 160
            }
        }

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": {
                "_id": "pay_xxx",
                "orderId": "xxx",
                "totalFee": 160,
                "status": "PENDING"
            }
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        data = request.get_json() or {}
        amount = data.get("amount", {})

        db = get_db_adapter()
        from src.core.payment_service import PaymentService, PaymentError
        service = PaymentService(db)

        payment = service.create_payment(order_id, user_id, amount)
        return success_response(payment), 201

    except PaymentError as e:
        return error_response(e.code, e.message), 400
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500


@orders_bp.route("/orders/<order_id>/pay", methods=["POST"])
def execute_payment(order_id):
    """执行支付（模拟）。

    Path Parameters:
        order_id: 订单ID

    Request Body:
        {
            "paymentId": "pay_xxx",
            "paymentMethod": "WECHAT"
        }

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": {
                "transactionId": "txn_xxx",
                "orderId": "xxx",
                "status": "SUCCESS",
                "totalFee": 160,
                "paidAt": "2026-05-12T..."
            }
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        data = request.get_json() or {}
        payment_id = data.get("paymentId", f"pay_{order_id}")
        payment_method = data.get("paymentMethod", "WECHAT")

        db = get_db_adapter()
        from src.core.payment_service import PaymentService, PaymentError
        service = PaymentService(db)

        result = service.execute_payment(payment_id, order_id, user_id, payment_method)
        return success_response(result)

    except PaymentError as e:
        return error_response(e.code, e.message), 400
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500


@orders_bp.route("/orders/<order_id>/payment/status", methods=["GET"])
def get_payment_status(order_id):
    """查询支付状态。

    Path Parameters:
        order_id: 订单ID

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": {
                "orderId": "xxx",
                "isPaid": true,
                "amount": {...},
                "status": "PENDING"
            }
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        db = get_db_adapter()
        from src.core.payment_service import PaymentService, PaymentNotFoundError
        service = PaymentService(db)

        # 先验证订单归属
        order = db.find_one("orders", {"_id": order_id})
        if not order:
            return error_response(ErrorCode.NOT_FOUND, "订单不存在"), 404
        if order.get("userId") != user_id:
            return error_response(ErrorCode.FORBIDDEN, "无权访问该订单"), 403

        status = service.get_payment_status(order_id)
        return success_response(status)

    except PaymentNotFoundError as e:
        return error_response(e.code, e.message), 404
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500
