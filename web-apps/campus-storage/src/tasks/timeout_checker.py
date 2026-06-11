"""超时检查定时任务。

PENDING超时自动取消、DELIVERING超时自动完结。
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

from src.db.adapter import DBAdapter
from src.common.errors import ErrorCode


def check_pending_timeout(
    db: DBAdapter,
    timeout_days: int = 7,
    batch_size: int = 50
) -> Dict[str, Any]:
    """检查并处理PENDING超时订单。

    超时条件：当前时间 > 订单创建时间 + timeout_days
    处理动作：PENDING -> CANCELLED

    Args:
        db: 数据库适配器
        timeout_days: 超时天数（默认7天）
        batch_size: 每次处理的最大订单数

    Returns:
        {
            "total": 扫描到的订单数,
            "success": 成功处理的订单数,
            "failed": 处理失败的订单数,
            "errors": 错误信息列表
        }
    """
    # 计算超时阈值
    timeout_threshold = datetime.now(timezone.utc) - timedelta(days=timeout_days)
    threshold_iso = timeout_threshold.isoformat(timespec="milliseconds")

    # 查询超时的PENDING订单
    # 由于SQLite不支持复杂的查询条件，我们先查询所有PENDING订单再过滤
    orders = db.find_many(
        "orders",
        {"status": "PENDING"},
        limit=batch_size
    )

    # 过滤出超时的订单
    expired_orders = [
        order for order in orders
        if order.get("createTime", "") < threshold_iso
    ]

    success_count = 0
    fail_count = 0
    errors = []

    for order in expired_orders:
        try:
            order_id = order.get("_id") or order.get("id")
            if not order_id:
                raise ValueError("订单ID缺失")

            # 调用状态变更逻辑
            _cancel_order(db, order_id, order.get("isPaid", False))

            success_count += 1
            print(f"[pendingTimeoutChecker] 处理成功: {order_id}")

        except Exception as e:
            fail_count += 1
            error_msg = f"[pendingTimeoutChecker] 处理失败: {order.get('_id')}, error: {e}"
            print(error_msg)
            errors.append(error_msg)

    print(f"[pendingTimeoutChecker] 执行摘要: 总数={len(expired_orders)}, 成功={success_count}, 失败={fail_count}")

    return {
        "total": len(expired_orders),
        "success": success_count,
        "failed": fail_count,
        "errors": errors
    }


def _cancel_order(db: DBAdapter, order_id: str, is_paid: bool) -> None:
    """取消订单。

    Args:
        db: 数据库适配器
        order_id: 订单ID
        is_paid: 是否已支付
    """
    # 查询当前订单
    order = db.find_one("orders", {"_id": order_id})
    if not order:
        raise ValueError(f"订单不存在: {order_id}")

    # 状态校验：只有PENDING状态可以取消
    if order.get("status") != "PENDING":
        raise ValueError(f"订单状态不是PENDING，无法取消: {order.get('status')}")

    # 构建状态历史记录
    status_history = order.get("statusHistory", [])
    status_record = {
        "from": "PENDING",
        "to": "CANCELLED",
        "operatorType": "SYSTEM",
        "operatorId": "system",
        "time": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "reason": "TIMEOUT_CANCEL"
    }
    status_history.append(status_record)

    # 更新订单状态
    updated = db.update_one(
        "orders",
        {"_id": order_id},
        {
            "status": "CANCELLED",
            "statusHistory": status_history
        }
    )

    if not updated:
        raise RuntimeError("更新订单失败")

    # Demo阶段：已支付订单记录退款日志即可
    if is_paid:
        print(f"[pendingTimeoutChecker] 订单 {order_id} 已支付，标记待退款")


def check_delivering_timeout(
    db: DBAdapter,
    timeout_days: int = 7,
    batch_size: int = 50
) -> Dict[str, Any]:
    """检查并处理DELIVERING超时订单。

    超时条件：当前时间 > statusHistory中DELIVERING状态时间 + timeout_days
    处理动作：DELIVERING -> COMPLETED

    Args:
        db: 数据库适配器
        timeout_days: 超时天数（默认7天）
        batch_size: 每次处理的最大订单数

    Returns:
        {
            "total": 扫描到的订单数,
            "success": 成功处理的订单数,
            "failed": 处理失败的订单数,
            "errors": 错误信息列表
        }
    """
    # 计算超时阈值
    timeout_threshold = datetime.now(timezone.utc) - timedelta(days=timeout_days)

    # 查询所有DELIVERING订单
    orders = db.find_many(
        "orders",
        {"status": "DELIVERING"},
        limit=batch_size
    )

    # 过滤出超时的订单（根据statusHistory中的DELIVERING时间）
    expired_orders = []
    for order in orders:
        delivering_time = _get_delivering_time(order)
        if delivering_time and delivering_time < timeout_threshold:
            expired_orders.append(order)

    success_count = 0
    fail_count = 0
    errors = []

    for order in expired_orders:
        try:
            order_id = order.get("_id") or order.get("id")
            if not order_id:
                raise ValueError("订单ID缺失")

            # 调用状态变更逻辑
            _complete_order(db, order_id)

            success_count += 1
            print(f"[deliveringTimeoutChecker] 处理成功: {order_id}")

        except Exception as e:
            fail_count += 1
            error_msg = f"[deliveringTimeoutChecker] 处理失败: {order.get('_id')}, error: {e}"
            print(error_msg)
            errors.append(error_msg)

    print(f"[deliveringTimeoutChecker] 执行摘要: 总数={len(expired_orders)}, 成功={success_count}, 失败={fail_count}")

    return {
        "total": len(expired_orders),
        "success": success_count,
        "failed": fail_count,
        "errors": errors
    }


def _get_delivering_time(order: Dict[str, Any]) -> datetime:
    """从订单状态历史中获取进入DELIVERING状态的时间。

    Args:
        order: 订单数据

    Returns:
        进入DELIVERING状态的时间，如果不存在则返回None
    """
    status_history = order.get("statusHistory", [])

    for record in status_history:
        # 支持两种字段命名：toStatus/to 和 timestamp/time
        to_status = record.get("toStatus") or record.get("to")
        if to_status == "DELIVERING":
            time_str = record.get("timestamp") or record.get("time")
            if time_str:
                try:
                    # 处理ISO格式时间字符串
                    return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    continue

    return None


def _complete_order(db: DBAdapter, order_id: str) -> None:
    """完结订单。

    Args:
        db: 数据库适配器
        order_id: 订单ID
    """
    # 查询当前订单
    order = db.find_one("orders", {"_id": order_id})
    if not order:
        raise ValueError(f"订单不存在: {order_id}")

    # 状态校验：只有DELIVERING状态可以完结
    if order.get("status") != "DELIVERING":
        raise ValueError(f"订单状态不是DELIVERING，无法完结: {order.get('status')}")

    # 构建状态历史记录
    status_history = order.get("statusHistory", [])
    status_record = {
        "from": "DELIVERING",
        "to": "COMPLETED",
        "operatorType": "SYSTEM",
        "operatorId": "system",
        "time": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "reason": "AUTO_COMPLETE"
    }
    status_history.append(status_record)

    # 更新订单状态
    updated = db.update_one(
        "orders",
        {"_id": order_id},
        {
            "status": "COMPLETED",
            "statusHistory": status_history
        }
    )

    if not updated:
        raise RuntimeError("更新订单失败")
