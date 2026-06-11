"""订单服务单元测试。"""

import pytest
from pathlib import Path
from src.core.order_service import (
    OrderService,
    OrderCreateError,
    OrderNotFoundError,
    OrderPermissionError,
    OrderStateError,
    OrderLockError,
    OrderUpdateError,
)
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


def test_order_service_create_order(db: SQLiteAdapter, init_tables):
    """测试创建订单。"""
    service = OrderService(db)

    order_data = {
        "city": "广州",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_gz_uc_north",
    }

    order = service.create_order(order_data)

    assert order is not None
    assert order["_id"] is not None
    assert order["status"] == "PENDING"
    assert order["warehouseId"] == "wh_gz_uc_north"
    assert order["city"] == "广州"
    assert order["itemType"] == "LUGGAGE"
    assert order["isPaid"] is False


def test_order_service_create_order_missing_required_fields(db: SQLiteAdapter, init_tables):
    """测试创建订单缺少必填字段。"""
    service = OrderService(db)

    with pytest.raises(OrderCreateError) as exc_info:
        service.create_order({})

    assert exc_info.value.code == ErrorCode.PARAM_ERROR
    assert "city" in str(exc_info.value.message)


def test_order_service_create_order_invalid_item_type(db: SQLiteAdapter, init_tables):
    """测试创建订单无效物品类型。"""
    service = OrderService(db)

    with pytest.raises(OrderCreateError) as exc_info:
        service.create_order({
            "city": "广州",
            "itemType": "INVALID_TYPE",
            "warehouseId": "wh_gz_uc_north",
        })

    assert exc_info.value.code == ErrorCode.PARAM_ERROR
    assert "无效的枚举值" in str(exc_info.value.message)


def test_order_service_create_order_valid_item_types(db: SQLiteAdapter, init_tables):
    """测试创建订单有效的物品类型。"""
    service = OrderService(db)

    for item_type in ["LUGGAGE", "DOCUMENT", "PACKAGE"]:
        order = service.create_order({
            "city": "北京",
            "itemType": item_type,
            "warehouseId": "wh_bj_central",
        })
        assert order["itemType"] == item_type


def test_order_service_create_order_alls_required_fields(db: SQLiteAdapter, init_tables):
    """测试创建订单所有必填字段都提供。"""
    service = OrderService(db)

    order_data = {
        "city": "上海",
        "itemType": "PACKAGE",
        "warehouseId": "wh_sh_south",
    }

    order = service.create_order(order_data)

    assert order["userId"] == "test_user"
    assert "_openid" in order
    assert "amount" in order
    assert order["amount"]["totalFee"] == 0
    assert "statusHistory" in order
    assert len(order["statusHistory"]) == 0


# ========== get_order 测试 ==========

def test_get_order_success(db: SQLiteAdapter, init_tables):
    """测试获取订单详情成功。"""
    service = OrderService(db)
    order = service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    result = service.get_order(order["_id"], "user_001")
    assert result["_id"] == order["_id"]
    assert result["status"] == "PENDING"


def test_get_order_not_found(db: SQLiteAdapter, init_tables):
    """测试获取不存在的订单。"""
    service = OrderService(db)

    with pytest.raises(OrderNotFoundError) as exc_info:
        service.get_order("nonexistent_id", "user_001")

    assert exc_info.value.code == ErrorCode.NOT_FOUND


def test_get_order_permission_denied(db: SQLiteAdapter, init_tables):
    """测试无权访问他人订单。"""
    service = OrderService(db)
    order = service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    with pytest.raises(OrderPermissionError) as exc_info:
        service.get_order(order["_id"], "user_002")

    assert exc_info.value.code == ErrorCode.FORBIDDEN


# ========== get_orders_by_user 测试 ==========

def test_get_orders_by_user_success(db: SQLiteAdapter, init_tables):
    """测试获取用户订单列表。"""
    service = OrderService(db)

    # 创建多个订单
    for i in range(3):
        service.create_order({
            "city": "北京",
            "itemType": "LUGGAGE",
            "warehouseId": "wh_bj_001",
            "userId": "user_001",
        })

    result = service.get_orders_by_user("user_001")
    assert len(result["list"]) == 3
    assert result["total"] == 3
    assert result["page"] == 1
    assert result["pageSize"] == 10


def test_get_orders_by_user_with_status_filter(db: SQLiteAdapter, init_tables):
    """测试按状态筛选订单。"""
    service = OrderService(db)

    # 创建多个订单
    order1 = service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })
    service.create_order({
        "city": "上海",
        "itemType": "DOCUMENT",
        "warehouseId": "wh_sh_001",
        "userId": "user_001",
    })

    # 更新第一个订单状态
    service.update_order_status(order1["_id"], "COLLECTED", "user_001", "USER", "test")

    result = service.get_orders_by_user("user_001", status="PENDING")
    assert result["total"] == 1
    assert result["list"][0]["status"] == "PENDING"


def test_get_orders_by_user_pagination(db: SQLiteAdapter, init_tables):
    """测试分页查询。"""
    service = OrderService(db)

    # 创建15个订单
    for i in range(15):
        service.create_order({
            "city": "北京",
            "itemType": "LUGGAGE",
            "warehouseId": "wh_bj_001",
            "userId": "user_001",
        })

    # 第一页
    result = service.get_orders_by_user("user_001", page=1, page_size=10)
    assert len(result["list"]) == 10
    assert result["total"] == 15

    # 第二页
    result = service.get_orders_by_user("user_001", page=2, page_size=10)
    assert len(result["list"]) == 5


def test_get_orders_by_admin(db: SQLiteAdapter, init_tables):
    """测试管理员获取所有订单。"""
    service = OrderService(db)

    # 不同用户的订单
    service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })
    service.create_order({
        "city": "上海",
        "itemType": "DOCUMENT",
        "warehouseId": "wh_sh_001",
        "userId": "user_002",
    })

    result = service.get_orders_by_user("admin_001", is_admin=True)
    assert result["total"] == 2


# ========== update_order_status 测试 ==========

def test_update_order_status_success(db: SQLiteAdapter, init_tables):
    """测试更新订单状态成功。"""
    service = OrderService(db)
    order = service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    result = service.update_order_status(order["_id"], "COLLECTED", "user_001", "USER", "取件完成")
    assert result["status"] == "COLLECTED"
    assert len(result["statusHistory"]) == 1
    assert result["statusHistory"][0]["from"] == "PENDING"
    assert result["statusHistory"][0]["to"] == "COLLECTED"


def test_update_order_status_invalid_transition(db: SQLiteAdapter, init_tables):
    """测试无效状态转换。"""
    service = OrderService(db)
    order = service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    with pytest.raises(OrderStateError) as exc_info:
        service.update_order_status(order["_id"], "COMPLETED", "user_001", "USER", "skip")

    assert exc_info.value.code == ErrorCode.INVALID_TRANSITION


def test_update_order_status_permission_denied(db: SQLiteAdapter, init_tables):
    """测试无权更新他人订单状态。"""
    service = OrderService(db)
    order = service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    with pytest.raises(OrderPermissionError):
        service.update_order_status(order["_id"], "COLLECTED", "user_002", "USER", "hack")


def test_update_order_status_admin_can_update_any(db: SQLiteAdapter, init_tables):
    """测试管理员可以更新任何订单状态。"""
    service = OrderService(db)
    order = service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    result = service.update_order_status(order["_id"], "COLLECTED", "admin_001", "ADMIN", "管理员操作")
    assert result["status"] == "COLLECTED"


# ========== cancel_order 测试 ==========

def test_cancel_order_success(db: SQLiteAdapter, init_tables):
    """测试取消订单成功。"""
    service = OrderService(db)
    order = service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    result = service.cancel_order(order["_id"], "user_001", "不想要了")
    assert result["status"] == "CANCELLED"
    assert result["statusHistory"][0]["reason"] == "不想要了"


def test_cancel_order_terminal_state_fails(db: SQLiteAdapter, init_tables):
    """测试终止状态无法取消。"""
    service = OrderService(db)
    order = service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    # 先取消
    service.cancel_order(order["_id"], "user_001")

    # 再次尝试取消
    with pytest.raises(OrderStateError):
        service.cancel_order(order["_id"], "user_001")


# ========== update_order 测试 ==========

def test_update_order_success(db: SQLiteAdapter, init_tables):
    """测试更新订单信息成功。"""
    service = OrderService(db)
    order = service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    result = service.update_order(order["_id"], {"volume": "大件", "declaredValue": 500}, "user_001")
    assert result["volume"] == "大件"
    assert result["declaredValue"] == 500


def test_update_order_cannot_update_status(db: SQLiteAdapter, init_tables):
    """测试不能通过 update_order 更新状态。"""
    service = OrderService(db)
    order = service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    with pytest.raises(OrderUpdateError) as exc_info:
        service.update_order(order["_id"], {"status": "COMPLETED"}, "user_001")

    assert exc_info.value.code == ErrorCode.PARAM_ERROR


def test_update_order_permission_denied(db: SQLiteAdapter, init_tables):
    """测试无权更新他人订单。"""
    service = OrderService(db)
    order = service.create_order({
        "city": "北京",
        "itemType": "LUGGAGE",
        "warehouseId": "wh_bj_001",
        "userId": "user_001",
    })

    with pytest.raises(OrderPermissionError):
        service.update_order(order["_id"], {"volume": "大件"}, "user_002")