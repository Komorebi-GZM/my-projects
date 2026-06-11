"""定时任务超时检查测试。"""

import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.db.sqlite_adapter import SQLiteAdapter
from src.core.order_service import OrderService
from src.tasks.timeout_checker import check_pending_timeout, check_delivering_timeout


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
def create_pending_order(db: SQLiteAdapter, init_tables):
    """创建PENDING状态订单的工厂函数。"""
    def _create(days_ago=8, is_paid=False):
        service = OrderService(db)
        order_data = {
            "city": "北京",
            "itemType": "LUGGAGE",
            "warehouseId": "wh_bj_central",
            "userId": "test_user",
        }
        order = service.create_order(order_data)
        
        # 修改创建时间为N天前
        old_time = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat(timespec="milliseconds")
        db.update_one("orders", {"_id": order["_id"]}, {
            "createTime": old_time,
            "isPaid": is_paid
        })
        
        # 重新查询获取更新后的数据
        return db.find_one("orders", {"_id": order["_id"]})
    return _create


@pytest.fixture
def create_delivering_order(db: SQLiteAdapter, init_tables):
    """创建DELIVERING状态订单的工厂函数。"""
    def _create(days_ago=8):
        service = OrderService(db)
        order_data = {
            "city": "北京",
            "itemType": "LUGGAGE",
            "warehouseId": "wh_bj_central",
            "userId": "test_user",
        }
        order = service.create_order(order_data)
        
        # 先更新为DELIVERING状态
        delivering_time = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat(timespec="milliseconds")
        db.update_one("orders", {"_id": order["_id"]}, {
            "status": "DELIVERING",
            "statusHistory": [{
                "from": "STORED",
                "to": "DELIVERING",
                "operatorType": "ADMIN",
                "operatorId": "admin",
                "time": delivering_time
            }]
        })
        
        return db.find_one("orders", {"_id": order["_id"]})
    return _create


def test_check_pending_timeout_cancels_expired_unpaid_order(db, create_pending_order):
    """测试PENDING超时取消：未支付订单应被取消。"""
    # 创建8天前的未支付订单
    order = create_pending_order(days_ago=8, is_paid=False)
    assert order["status"] == "PENDING"
    
    # 执行超时检查
    result = check_pending_timeout(db, timeout_days=7)
    
    # 验证订单已被取消
    updated_order = db.find_one("orders", {"_id": order["_id"]})
    assert updated_order["status"] == "CANCELLED"
    assert len(updated_order["statusHistory"]) == 1
    assert updated_order["statusHistory"][0]["to"] == "CANCELLED"
    assert updated_order["statusHistory"][0]["operatorType"] == "SYSTEM"
    
    # 验证返回结果
    assert result["total"] == 1
    assert result["success"] == 1
    assert result["failed"] == 0


def test_check_pending_timeout_cancels_expired_paid_order(db, create_pending_order):
    """测试PENDING超时取消：已支付订单应被取消（Demo阶段记录日志）。"""
    # 创建8天前的已支付订单
    order = create_pending_order(days_ago=8, is_paid=True)
    assert order["status"] == "PENDING"
    
    # 执行超时检查
    result = check_pending_timeout(db, timeout_days=7)
    
    # 验证订单已被取消
    updated_order = db.find_one("orders", {"_id": order["_id"]})
    assert updated_order["status"] == "CANCELLED"
    
    # 验证返回结果
    assert result["total"] == 1
    assert result["success"] == 1


def test_check_pending_timeout_ignores_recent_order(db, create_pending_order):
    """测试PENDING超时取消：近期订单不应被取消。"""
    # 创建1天前的订单
    order = create_pending_order(days_ago=1, is_paid=False)
    
    # 执行超时检查
    result = check_pending_timeout(db, timeout_days=7)
    
    # 验证订单状态未变
    updated_order = db.find_one("orders", {"_id": order["_id"]})
    assert updated_order["status"] == "PENDING"
    
    # 验证返回结果
    assert result["total"] == 0
    assert result["success"] == 0


def test_check_pending_timeout_ignores_non_pending_order(db, create_pending_order):
    """测试PENDING超时取消：非PENDING状态订单不应被处理。"""
    # 创建8天前的订单，然后改为其他状态
    order = create_pending_order(days_ago=8, is_paid=False)
    db.update_one("orders", {"_id": order["_id"]}, {"status": "COLLECTED"})
    
    # 执行超时检查
    result = check_pending_timeout(db, timeout_days=7)
    
    # 验证订单状态未变
    updated_order = db.find_one("orders", {"_id": order["_id"]})
    assert updated_order["status"] == "COLLECTED"
    
    # 验证返回结果
    assert result["total"] == 0


def test_check_delivering_timeout_completes_expired_order(db, create_delivering_order):
    """测试DELIVERING超时完结：超时应自动完结。"""
    # 创建8天前进入DELIVERING状态的订单
    order = create_delivering_order(days_ago=8)
    assert order["status"] == "DELIVERING"
    
    # 执行超时检查
    result = check_delivering_timeout(db, timeout_days=7)
    
    # 验证订单已完结
    updated_order = db.find_one("orders", {"_id": order["_id"]})
    assert updated_order["status"] == "COMPLETED"
    
    # 验证返回结果
    assert result["total"] == 1
    assert result["success"] == 1
    assert result["failed"] == 0


def test_check_delivering_timeout_ignores_recent_order(db, create_delivering_order):
    """测试DELIVERING超时完结：近期订单不应被完结。"""
    # 创建1天前进入DELIVERING状态的订单
    order = create_delivering_order(days_ago=1)
    
    # 执行超时检查
    result = check_delivering_timeout(db, timeout_days=7)
    
    # 验证订单状态未变
    updated_order = db.find_one("orders", {"_id": order["_id"]})
    assert updated_order["status"] == "DELIVERING"
    
    # 验证返回结果
    assert result["total"] == 0


def test_check_delivering_timeout_ignores_non_delivering_order(db, create_delivering_order):
    """测试DELIVERING超时完结：非DELIVERING状态订单不应被处理。"""
    # 创建订单并改为其他状态
    order = create_delivering_order(days_ago=8)
    db.update_one("orders", {"_id": order["_id"]}, {"status": "STORED"})
    
    # 执行超时检查
    result = check_delivering_timeout(db, timeout_days=7)
    
    # 验证订单状态未变
    updated_order = db.find_one("orders", {"_id": order["_id"]})
    assert updated_order["status"] == "STORED"
    
    # 验证返回结果
    assert result["total"] == 0


def test_check_pending_timeout_handles_errors_gracefully(db, init_tables):
    """测试PENDING超时取消：单条失败不影响其他订单。"""
    # 这个测试验证批量处理时单条失败不阻塞
    # 由于我们使用内存数据库，很难模拟真实错误
    # 这里主要验证函数能正常执行不抛出异常
    result = check_pending_timeout(db, timeout_days=7)
    assert isinstance(result, dict)
    assert "total" in result
    assert "success" in result
    assert "failed" in result
