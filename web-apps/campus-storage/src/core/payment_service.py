"""支付服务模块。

Demo 阶段：模拟支付流程，不接入真实支付网关。
生产环境：替换为微信支付 API 调用。
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from src.db.adapter import DBAdapter
from src.common.errors import ErrorCode


@dataclass
class PaymentError(Exception):
    """支付错误。"""
    code: int = ErrorCode.PAYMENT_ERROR
    message: str = "支付失败"


@dataclass
class PaymentNotFoundError(Exception):
    """支付记录不存在。"""
    code: int = ErrorCode.NOT_FOUND
    message: str = "支付记录不存在"


class PaymentService:
    """支付服务（Demo 模拟实现）。"""

    # 模拟支付成功率（用于测试）
    SUCCESS_RATE = 1.0

    def __init__(self, db: DBAdapter):
        self.db = db

    def create_payment(
        self,
        order_id: str,
        user_id: str,
        amount: Dict[str, Any],
    ) -> Dict[str, Any]:
        """创建支付单。

        Args:
            order_id: 订单ID
            user_id: 用户ID
            amount: 费用明细 {"storageFee": 0, "deliveryFee": 0, "insuranceFee": 0, "totalFee": 0}

        Returns:
            支付单信息

        Raises:
            PaymentError: 订单不存在或状态不允许支付
        """
        # 查询订单
        order = self.db.find_one("orders", {"_id": order_id})
        if not order:
            raise PaymentError(code=ErrorCode.NOT_FOUND, message="订单不存在")

        # 校验订单归属
        if order.get("userId") != user_id:
            raise PaymentError(code=ErrorCode.FORBIDDEN, message="无权操作该订单")

        # 校验订单状态：只有 PENDING 状态可支付
        if order.get("status") != "PENDING":
            raise PaymentError(code=ErrorCode.INVALID_TRANSITION, message="订单状态不允许支付")

        # 校验是否已支付
        if order.get("isPaid"):
            raise PaymentError(code=ErrorCode.PARAM_ERROR, message="订单已支付")

        # 计算总金额（Demo阶段允许零金额支付用于测试）
        total_fee = amount.get("totalFee", 0)

        # 创建支付单
        payment_id = f"pay_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")

        payment = {
            "_id": payment_id,
            "orderId": order_id,
            "userId": user_id,
            "amount": amount,
            "totalFee": total_fee,
            "status": "PENDING",
            "createTime": now,
            "updateTime": now,
        }

        # 存储支付单（Demo 阶段存入 orders 表的 statusHistory，生产环境应独立表）
        # 这里简化处理：直接返回支付单信息，前端调用 execute_payment 完成支付

        return payment

    def execute_payment(
        self,
        payment_id: str,
        order_id: str,
        user_id: str,
        payment_method: str = "WECHAT",
    ) -> Dict[str, Any]:
        """执行支付（模拟）。

        Demo 阶段：直接标记支付成功，不调用真实支付网关。
        生产环境：调用微信支付统一下单 API。

        Args:
            payment_id: 支付单ID（Demo 阶段可忽略）
            order_id: 订单ID
            user_id: 用户ID
            payment_method: 支付方式（WECHAT/ALIPAY/MOCK）

        Returns:
            支付结果

        Raises:
            PaymentError: 支付失败
        """
        # 查询订单
        order = self.db.find_one("orders", {"_id": order_id})
        if not order:
            raise PaymentError(code=ErrorCode.NOT_FOUND, message="订单不存在")

        # 校验订单归属
        if order.get("userId") != user_id:
            raise PaymentError(code=ErrorCode.FORBIDDEN, message="无权操作该订单")

        # 校验订单状态
        if order.get("status") != "PENDING":
            raise PaymentError(code=ErrorCode.INVALID_TRANSITION, message="订单状态不允许支付")

        # 校验是否已支付
        if order.get("isPaid"):
            raise PaymentError(code=ErrorCode.PARAM_ERROR, message="订单已支付")

        # 模拟支付处理
        now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        transaction_id = f"txn_{uuid.uuid4().hex[:16]}"

        # Demo: 模拟支付成功（生产环境调用真实支付 API）
        payment_result = {
            "transactionId": transaction_id,
            "paymentId": payment_id,
            "orderId": order_id,
            "status": "SUCCESS",
            "totalFee": order.get("amount", {}).get("totalFee", 0),
            "paymentMethod": payment_method,
            "paidAt": now,
        }

        # 更新订单支付状态
        status_history = order.get("statusHistory", [])
        status_history.append({
            "from": "PENDING",
            "to": "PENDING",  # 支付不改变订单状态，仍是 PENDING
            "operatorType": "USER",
            "operatorId": user_id,
            "time": now,
            "reason": "PAYMENT_SUCCESS",
            "metadata": {"transactionId": transaction_id},
        })

        # 更新订单
        current_version = order.get("_version", 1)
        updated = self.db.update_one(
            "orders",
            {"_id": order_id},
            {
                "isPaid": True,
                "statusHistory": status_history,
            },
            version=current_version,
        )

        if not updated:
            raise PaymentError(code=ErrorCode.LOCK_CONFLICT, message="订单状态已变更，请重试")

        return payment_result

    def refund_payment(
        self,
        order_id: str,
        reason: str = "用户取消",
        operator_id: str = "system",
    ) -> Dict[str, Any]:
        """退款（模拟）。

        Demo 阶段：记录退款日志，不调用真实退款 API。
        生产环境：调用微信支付退款 API。

        Args:
            order_id: 订单ID
            reason: 退款原因
            operator_id: 操作者ID

        Returns:
            退款结果

        Raises:
            PaymentError: 退款失败
        """
        # 查询订单
        order = self.db.find_one("orders", {"_id": order_id})
        if not order:
            raise PaymentError(code=ErrorCode.NOT_FOUND, message="订单不存在")

        # 校验是否已支付
        if not order.get("isPaid"):
            raise PaymentError(code=ErrorCode.PARAM_ERROR, message="订单未支付，无需退款")

        # 生成退款单号
        refund_id = f"ref_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")

        # Demo: 模拟退款成功
        refund_result = {
            "refundId": refund_id,
            "orderId": order_id,
            "status": "SUCCESS",
            "totalFee": order.get("amount", {}).get("totalFee", 0),
            "reason": reason,
            "refundedAt": now,
        }

        # 记录退款到状态历史
        status_history = order.get("statusHistory", [])
        status_history.append({
            "from": order.get("status"),
            "to": order.get("status"),
            "operatorType": "SYSTEM",
            "operatorId": operator_id,
            "time": now,
            "reason": f"REFUND: {reason}",
            "metadata": {"refundId": refund_id},
        })

        # 更新订单（标记为已退款）
        self.db.update_one(
            "orders",
            {"_id": order_id},
            {
                "statusHistory": status_history,
            },
        )

        return refund_result

    def get_payment_status(self, order_id: str) -> Dict[str, Any]:
        """查询支付状态。

        Args:
            order_id: 订单ID

        Returns:
            支付状态信息
        """
        order = self.db.find_one("orders", {"_id": order_id})
        if not order:
            raise PaymentNotFoundError(code=ErrorCode.NOT_FOUND, message="订单不存在")

        return {
            "orderId": order_id,
            "isPaid": order.get("isPaid", False),
            "amount": order.get("amount", {}),
            "status": order.get("status"),
        }
