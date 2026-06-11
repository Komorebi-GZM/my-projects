"""支付服务单元测试。"""

import pytest
from pathlib import Path

from src.core.payment_service import (
    PaymentService,
    PaymentError,
    PaymentNotFoundError,
)
from src.core.order_service import OrderService
from src.db.sqlite_adapter import SQLiteAdapter
from src.common.errors import ErrorCode


@pytest.fixture
def db():
    """使用内存数据库创建测试适配器。"""
    adapter = SQLiteAdapter(":memory:")
    adapter._get_connection().execute("PRAGMA journal_mode=MEMORY;")
    yield adapter
    adapter.close()


@pytest.fixture
def init_tables(db: SQLiteAdapter):
    """初始化测试表。"""
    schema_sql = (Path(__file__).parent.parent / "src" / "db" / "schema.sql").read_text(encoding="utf-8")
    db.conn.executescript(schema_sql)


@pytest.fixture
def order_service(db: SQLiteAdapter):
    """订单服务实例。"""
    return OrderService(db)


@pytest.fixture
def payment_service(db: SQLiteAdapter):
    """支付服务实例。"""
    return PaymentService(db)


# ========== create_payment 测试 ==========

def test_create_payment_success(db: SQLiteAdapter, init_tables, order_service, payment_service):
    """测试创建支付单成功。"""
    order = order_service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    amount = {"storageFee": 100, "deliveryFee": 50, "insuranceFee": 10, "totalFee": 160}
    payment = payment_service.create_payment(order["_id"], "user_001", amount)

    assert payment["_id"].startswith("pay_")
    assert payment["orderId"] == order["_id"]
    assert payment["totalFee"] == 160
    assert payment["status"] == "PENDING"


def test_create_payment_order_not_found(db: SQLiteAdapter, init_tables, payment_service):
    """测试订单不存在时创建支付单。"""
    with pytest.raises(PaymentError) as exc_info:
        payment_service.create_payment("nonexistent", "user_001", {"totalFee": 100})

    assert exc_info.value.code == ErrorCode.NOT_FOUND


def test_create_payment_permission_denied(db: SQLiteAdapter, init_tables, order_service, payment_service):
    """测试无权创建他人订单的支付单。"""
    order = order_service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    with pytest.raises(PaymentError) as exc_info:
        payment_service.create_payment(order["_id"], "user_002", {"totalFee": 100})

    assert exc_info.value.code == ErrorCode.FORBIDDEN


def test_create_payment_invalid_amount(db: SQLiteAdapter, init_tables, order_service, payment_service):
    """测试无效金额。"""
    order = order_service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    with pytest.raises(PaymentError) as exc_info:
        payment_service.create_payment(order["_id"], "user_001", {"totalFee": 0})

    assert exc_info.value.code == ErrorCode.PARAM_ERROR


def test_create_payment_already_paid(db: SQLiteAdapter, init_tables, order_service, payment_service):
    """测试已支付订单无法重复支付。"""
    order = order_service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    # 先支付一次
    payment_service.execute_payment("pay_001", order["_id"], "user_001")

    # 尝试再次创建支付单
    with pytest.raises(PaymentError) as exc_info:
        payment_service.create_payment(order["_id"], "user_001", {"totalFee": 100})

    assert "已支付" in exc_info.value.message


# ========== execute_payment 测试 ==========

def test_execute_payment_success(db: SQLiteAdapter, init_tables, order_service, payment_service):
    """测试执行支付成功。"""
    order = order_service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    # 先设置金额
    db.update_one("orders", {"_id": order["_id"]}, {"amount": {"totalFee": 160}})

    result = payment_service.execute_payment("pay_001", order["_id"], "user_001")

    assert result["status"] == "SUCCESS"
    assert result["orderId"] == order["_id"]
    assert result["transactionId"].startswith("txn_")

    # 验证订单已标记为已支付
    updated_order = db.find_one("orders", {"_id": order["_id"]})
    assert updated_order["isPaid"] is True


def test_execute_payment_permission_denied(db: SQLiteAdapter, init_tables, order_service, payment_service):
    """测试无权支付他人订单。"""
    order = order_service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    with pytest.raises(PaymentError) as exc_info:
        payment_service.execute_payment("pay_001", order["_id"], "user_002")

    assert exc_info.value.code == ErrorCode.FORBIDDEN


def test_execute_payment_order_not_found(db: SQLiteAdapter, init_tables, payment_service):
    """测试支付不存在的订单。"""
    with pytest.raises(PaymentError) as exc_info:
        payment_service.execute_payment("pay_001", "nonexistent", "user_001")

    assert exc_info.value.code == ErrorCode.NOT_FOUND


def test_execute_payment_already_paid(db: SQLiteAdapter, init_tables, order_service, payment_service):
    """测试重复支付。"""
    order = order_service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    # 第一次支付
    payment_service.execute_payment("pay_001", order["_id"], "user_001")

    # 尝试重复支付
    with pytest.raises(PaymentError) as exc_info:
        payment_service.execute_payment("pay_002", order["_id"], "user_001")

    assert "已支付" in exc_info.value.message


def test_execute_payment_wrong_status(db: SQLiteAdapter, init_tables, order_service, payment_service):
    """测试非 PENDING 状态订单无法支付。"""
    order = order_service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    # 更新状态为 COLLECTED
    order_service.update_order_status(order["_id"], "COLLECTED", "user_001", "USER", "test")

    # 尝试支付
    with pytest.raises(PaymentError) as exc_info:
        payment_service.execute_payment("pay_001", order["_id"], "user_001")

    assert exc_info.value.code == ErrorCode.INVALID_TRANSITION


# ========== refund_payment 测试 ==========

def test_refund_payment_success(db: SQLiteAdapter, init_tables, order_service, payment_service):
    """测试退款成功。"""
    order = order_service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    # 先支付
    db.update_one("orders", {"_id": order["_id"]}, {"amount": {"totalFee": 160}})
    payment_service.execute_payment("pay_001", order["_id"], "user_001")

    # 退款
    result = payment_service.refund_payment(order["_id"], "用户取消", "system")

    assert result["status"] == "SUCCESS"
    assert result["refundId"].startswith("ref_")
    assert result["totalFee"] == 160


def test_refund_payment_not_paid(db: SQLiteAdapter, init_tables, order_service, payment_service):
    """测试未支付订单无法退款。"""
    order = order_service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    with pytest.raises(PaymentError) as exc_info:
        payment_service.refund_payment(order["_id"])

    assert "未支付" in exc_info.value.message


def test_refund_payment_order_not_found(db: SQLiteAdapter, init_tables, payment_service):
    """测试退款不存在的订单。"""
    with pytest.raises(PaymentError) as exc_info:
        payment_service.refund_payment("nonexistent")

    assert exc_info.value.code == ErrorCode.NOT_FOUND


# ========== get_payment_status 测试 ==========

def test_get_payment_status_unpaid(db: SQLiteAdapter, init_tables, order_service, payment_service):
    """测试查询未支付订单状态。"""
    order = order_service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    status = payment_service.get_payment_status(order["_id"])

    assert status["orderId"] == order["_id"]
    assert status["isPaid"] is False
    assert status["status"] == "PENDING"


def test_get_payment_status_paid(db: SQLiteAdapter, init_tables, order_service, payment_service):
    """测试查询已支付订单状态。"""
    order = order_service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    # 支付
    db.update_one("orders", {"_id": order["_id"]}, {"amount": {"totalFee": 160}})
    payment_service.execute_payment("pay_001", order["_id"], "user_001")

    status = payment_service.get_payment_status(order["_id"])

    assert status["isPaid"] is True


def test_get_payment_status_order_not_found(db: SQLiteAdapter, init_tables, payment_service):
    """测试查询不存在订单的支付状态。"""
    with pytest.raises(PaymentNotFoundError):
        payment_service.get_payment_status("nonexistent")
