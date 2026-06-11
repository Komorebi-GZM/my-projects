"""数据访问层单元测试。"""

import pytest
from pathlib import Path
from src.db.sqlite_adapter import SQLiteAdapter


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


def test_insert_user(db: SQLiteAdapter, init_tables):
    """测试插入用户。"""
    doc = {
        "_id": "test_user_1",
        "_openid": "o_test_openid",
        "nickName": "测试用户",
        "avatarUrl": "https://example.com/avatar.jpg",
        "role": "USER",
        "status": "ACTIVE",
    }
    doc_id = db.insert("users", doc)

    assert doc_id == "test_user_1"


def test_find_one_user(db: SQLiteAdapter, init_tables):
    """测试查询单个用户。"""
    db.insert("users", {
        "_id": "test_user_1",
        "_openid": "o_test_openid",
        "nickName": "测试用户",
        "role": "USER",
    })

    result = db.find_one("users", {"_id": "test_user_1"})
    assert result is not None
    assert result["_id"] == "test_user_1"
    assert result["nickName"] == "测试用户"


def test_find_many_users(db: SQLiteAdapter, init_tables):
    """测试查询多个用户。"""
    db.insert("users", {"_id": "u1", "_openid": "o1", "nickName": "用户1", "role": "USER"})
    db.insert("users", {"_id": "u2", "_openid": "o2", "nickName": "用户2", "role": "USER"})
    db.insert("users", {"_id": "u3", "_openid": "o3", "nickName": "用户3", "role": "ADMIN"})

    results = db.find_many("users", {"role": "USER"}, limit=10)
    assert len(results) == 2


def test_update_user(db: SQLiteAdapter, init_tables):
    """测试更新用户。"""
    db.insert("users", {"_id": "test_user_1", "_openid": "o1", "nickName": "旧昵称", "role": "USER"})

    updated = db.update_one("users", {"_id": "test_user_1"}, {"nickName": "新昵称"})
    assert updated is True

    user = db.find_one("users", {"_id": "test_user_1"})
    assert user["nickName"] == "新昵称"


def test_count_users(db: SQLiteAdapter, init_tables):
    """测试统计用户数量。"""
    db.insert("users", {"_id": "u1", "_openid": "o1", "nickName": "用户1", "role": "USER"})
    db.insert("users", {"_id": "u2", "_openid": "o2", "nickName": "用户2", "role": "USER"})
    db.insert("users", {"_id": "u3", "_openid": "o3", "nickName": "用户3", "role": "ADMIN"})

    count = db.count("users", {"role": "USER"})
    assert count == 2


def test_insert_order(db: SQLiteAdapter, init_tables):
    """测试插入订单（含 JSON 字段）。"""
    doc = {
        "_id": "order_001",
        "_openid": "o_test_openid",
        "orderNo": "ORD20260510001",
        "userId": "test_user_1",
        "warehouseId": "wh_gz_uc_north",
        "warehouseName": "广州大学城·北仓",
        "city": "广州",
        "status": "PENDING",
        "isPaid": False,
        "itemType": "LUGGAGE",
        "volume": "LARGE",
        "amount": {"storageFee": 35.0, "deliveryFee": 0, "insuranceFee": 5.0, "totalFee": 40.0},
        "statusHistory": [
            {
                "timestamp": "2026-05-10T10:00:00.000Z",
                "fromStatus": "",
                "toStatus": "PENDING",
                "operatorType": "USER",
                "operatorId": "test_user_1",
                "reason": "USER_CREATE",
                "metadata": {},
            }
        ],
    }
    doc_id = db.insert("orders", doc)

    assert doc_id == "order_001"
    result = db.find_one("orders", {"_id": "order_001"})
    assert result is not None
    assert result["amount"]["totalFee"] == 40.0
    assert len(result["statusHistory"]) == 1


def test_transaction(db: SQLiteAdapter, init_tables):
    """测试事务。"""
    db.begin_transaction()
    try:
        db.insert("users", {"_id": "u1", "_openid": "o1", "nickName": "用户1", "role": "USER"})
        db.insert("users", {"_id": "u2", "_openid": "o2", "nickName": "用户2", "role": "USER"})
        db.commit()
    except Exception:
        db.rollback()
        raise

    count = db.count("users", {})
    assert count == 2


def test_transaction_rollback(db: SQLiteAdapter, init_tables):
    """测试事务回滚。"""
    db.begin_transaction()
    try:
        db.insert("users", {"_id": "u1", "_openid": "o1", "nickName": "用户1", "role": "USER"})
        db.insert("users", {"_id": "u2", "_openid": "o2", "nickName": "用户2", "role": "USER"})
        db.rollback()
    except Exception:
        db.rollback()
        raise

    count = db.count("users", {})
    assert count == 0
