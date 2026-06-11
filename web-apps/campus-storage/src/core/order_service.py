"""订单服务模块。"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List

from src.db.adapter import DBAdapter
from src.common.errors import ErrorCode, error_response
from src.common.validator import validate_required, validate_enum, ValidationError
from src.common.auth import get_current_user_id
from src.core.order_state import OrderStateMachine, InvalidTransitionError


def generate_order_no() -> str:
    """生成订单号。"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = uuid.uuid4().hex[:6].upper()
    return f"ORD{timestamp}{random_suffix}"


@dataclass
class OrderCreateError(Exception):
    """订单创建错误。"""
    code: int = ErrorCode.PARAM_ERROR
    message: str = "订单创建失败"


@dataclass
class OrderNotFoundError(Exception):
    """订单不存在错误。"""
    code: int = ErrorCode.NOT_FOUND
    message: str = "订单不存在"


@dataclass
class OrderPermissionError(Exception):
    """订单权限错误。"""
    code: int = ErrorCode.FORBIDDEN
    message: str = "无权访问该订单"


@dataclass
class OrderStateError(Exception):
    """订单状态错误。"""
    code: int = ErrorCode.INVALID_TRANSITION
    message: str = "无效的状态转换"


@dataclass
class OrderLockError(Exception):
    """订单锁冲突错误。"""
    code: int = ErrorCode.LOCK_CONFLICT
    message: str = "订单状态已变更"


@dataclass
class OrderUpdateError(Exception):
    """订单更新错误。"""
    code: int = ErrorCode.PARAM_ERROR
    message: str = "订单更新失败"


class OrderService:
    """订单服务。"""

    def __init__(self, db: DBAdapter):
        """初始化订单服务。"""
        self.db = db

    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新订单。

        Args:
            order_data: 订单数据，包含 city, itemType, warehouseId

        Returns:
            Dict[str, Any]: 创建的订单

        Raises:
            OrderCreateError: 如果参数验证失败
        """
        # 验证必填字段
        try:
            validate_required(order_data.get("city"), "city")
            validate_required(order_data.get("itemType"), "itemType")
            validate_required(order_data.get("warehouseId"), "warehouseId")
        except ValidationError as e:
            raise OrderCreateError(code=ErrorCode.PARAM_ERROR, message=e.message)

        # 验证枚举值
        try:
            validate_enum(order_data["itemType"], ["LUGGAGE", "DOCUMENT", "PACKAGE"])
        except ValidationError as e:
            raise OrderCreateError(code=ErrorCode.PARAM_ERROR, message=e.message)

        # 获取当前用户 ID
        try:
            user_id = get_current_user_id()
        except RuntimeError:
            # 测试环境中可能没有请求上下文，使用默认值
            user_id = order_data.get("userId", "test_user")

        if not user_id:
            raise OrderCreateError(code=ErrorCode.UNAUTHORIZED, message="用户未登录")

        # 创建订单数据
        order = {
            "_id": None,
            "_openid": user_id,
            "openid": user_id,  # SQLite 数据库需要 openid 字段
            "orderNo": generate_order_no(),
            "userId": user_id,
            "warehouseId": order_data["warehouseId"],
            "warehouseName": "",
            "city": order_data["city"],
            "status": "PENDING",
            "isPaid": False,
            "itemType": order_data["itemType"],
            "volume": "",
            "amount": {"storageFee": 0, "deliveryFee": 0, "insuranceFee": 0, "totalFee": 0},
            "statusHistory": [],
            # createTime 和 updateTime 由数据库适配器自动设置
        }

        # 插入数据库
        doc_id = self.db.insert("orders", order)
        order["_id"] = doc_id

        return order

    def get_order(self, order_id: str, user_id: str) -> Dict[str, Any]:
        """获取订单详情。

        Args:
            order_id: 订单ID
            user_id: 当前用户ID（用于权限校验）

        Returns:
            Dict[str, Any]: 订单详情

        Raises:
            OrderNotFoundError: 订单不存在
            OrderPermissionError: 无权访问
        """
        order = self.db.find_one("orders", {"_id": order_id})
        if not order:
            raise OrderNotFoundError(code=ErrorCode.NOT_FOUND, message="订单不存在")

        # 权限检查：用户只能查看自己的订单
        if order.get("userId") != user_id:
            raise OrderPermissionError(code=ErrorCode.FORBIDDEN, message="无权访问该订单")

        return order

    def get_orders_by_user(
        self,
        user_id: str,
        status: str = None,
        page: int = 1,
        page_size: int = 10,
        is_admin: bool = False,
    ) -> Dict[str, Any]:
        """获取用户订单列表。

        Args:
            user_id: 当前用户ID
            status: 状态筛选（可选）
            page: 页码
            page_size: 每页数量
            is_admin: 是否为管理员

        Returns:
            Dict[str, Any]: 包含 list, total, page, pageSize 的分页结果
        """
        # 构建查询条件
        if is_admin:
            query = {}
        else:
            query = {"userId": user_id}

        if status:
            query["status"] = status

        # 查询总数
        total = self.db.count("orders", query)

        # 查询列表
        skip = (page - 1) * page_size
        orders = self.db.find_many(
            "orders",
            query,
            sort=[("createTime", -1)],
            limit=page_size,
            skip=skip,
        )

        return {
            "list": orders,
            "total": total,
            "page": page,
            "pageSize": page_size,
        }

    def update_order_status(
        self,
        order_id: str,
        new_status: str,
        operator_id: str,
        operator_type: str = "USER",
        reason: str = "",
    ) -> Dict[str, Any]:
        """更新订单状态。

        Args:
            order_id: 订单ID
            new_status: 新状态
            operator_id: 操作者ID
            operator_type: 操作者类型 (USER/ADMIN/SYSTEM)
            reason: 操作原因（可选）

        Returns:
            Dict[str, Any]: 更新后的订单

        Raises:
            OrderNotFoundError: 订单不存在
            OrderPermissionError: 无权操作
            OrderStateError: 状态转换无效
        """
        from datetime import datetime, timezone

        # 查询订单
        order = self.db.find_one("orders", {"_id": order_id})
        if not order:
            raise OrderNotFoundError(code=ErrorCode.NOT_FOUND, message="订单不存在")

        # 权限检查
        if operator_type == "USER" and order.get("userId") != operator_id:
            raise OrderPermissionError(code=ErrorCode.FORBIDDEN, message="无权操作该订单")

        # 状态机校验
        try:
            machine = OrderStateMachine(order.get("status", "PENDING"))
            machine.transition(new_status)
        except InvalidTransitionError as e:
            raise OrderStateError(code=ErrorCode.INVALID_TRANSITION, message=str(e))

        # 更新状态历史
        current_status = order.get("status", "PENDING")
        status_history = order.get("statusHistory", [])

        status_record = {
            "from": current_status,
            "to": new_status,
            "operatorType": operator_type,
            "operatorId": operator_id,
            "time": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        }
        if reason:
            status_record["reason"] = reason

        status_history.append(status_record)

        # 执行更新（使用乐观锁）
        current_version = order.get("_version", 1)
        updated = self.db.update_one(
            "orders",
            {"_id": order_id},
            {
                "status": new_status,
                "statusHistory": status_history,
            },
            version=current_version,
        )

        if not updated:
            raise OrderLockError(code=ErrorCode.LOCK_CONFLICT, message="订单状态已变更，请刷新后重试")

        # 返回更新后的订单
        return self.db.find_one("orders", {"_id": order_id})

    def cancel_order(
        self,
        order_id: str,
        user_id: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        """取消订单。

        Args:
            order_id: 订单ID
            user_id: 当前用户ID
            reason: 取消原因（可选）

        Returns:
            Dict[str, Any]: 取消后的订单

        Raises:
            OrderNotFoundError: 订单不存在
            OrderPermissionError: 无权操作
            OrderStateError: 状态不允许取消
        """
        return self.update_order_status(
            order_id=order_id,
            new_status="CANCELLED",
            operator_id=user_id,
            operator_type="USER",
            reason=reason or "用户取消",
        )

    def update_order(
        self,
        order_id: str,
        updates: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """更新订单信息（非状态字段）。

        Args:
            order_id: 订单ID
            updates: 更新字段
            user_id: 当前用户ID

        Returns:
            Dict[str, Any]: 更新后的订单

        Raises:
            OrderNotFoundError: 订单不存在
            OrderPermissionError: 无权操作
        """
        # 查询订单
        order = self.db.find_one("orders", {"_id": order_id})
        if not order:
            raise OrderNotFoundError(code=ErrorCode.NOT_FOUND, message="订单不存在")

        # 权限检查
        if order.get("userId") != user_id:
            raise OrderPermissionError(code=ErrorCode.FORBIDDEN, message="无权操作该订单")

        # 不允许通过此方法更新状态
        if "status" in updates:
            raise OrderUpdateError(code=ErrorCode.PARAM_ERROR, message="请使用 update_order_status 更新状态")

        # 执行更新（使用乐观锁）
        current_version = order.get("_version", 1)
        updated = self.db.update_one(
            "orders",
            {"_id": order_id},
            updates,
            version=current_version,
        )

        if not updated:
            raise OrderLockError(code=ErrorCode.LOCK_CONFLICT, message="订单已变更，请刷新后重试")

        return self.db.find_one("orders", {"_id": order_id})