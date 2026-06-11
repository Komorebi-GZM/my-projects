"""乐观锁并发控制测试。"""

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


def test_update_with_correct_version(db: SQLiteAdapter, init_tables):
    """测试使用正确版本号更新成功，版本号自动递增。"""
    # 插入测试数据
    db.insert("orders", {
        "_id": "order_001",
        "_openid": "o_test",
        "orderNo": "ORD001",
        "userId": "user_001",
        "warehouseId": "wh_001",
        "status": "PENDING",
    })

    # 查询当前版本
    order = db.find_one("orders", {"_id": "order_001"})
    assert order["_version"] == 1

    # 使用正确版本号更新
    result = db.update_one("orders", {"_id": "order_001"}, {"status": "COLLECTED"}, version=1)
    assert result is True

    # 验证版本号已递增
    order = db.find_one("orders", {"_id": "order_001"})
    assert order["status"] == "COLLECTED"
    assert order["_version"] == 2


def test_update_with_wrong_version_fails(db: SQLiteAdapter, init_tables):
    """测试使用错误版本号更新失败（乐观锁冲突）。"""
    # 插入测试数据
    db.insert("orders", {
        "_id": "order_001",
        "_openid": "o_test",
        "orderNo": "ORD001",
        "userId": "user_001",
        "warehouseId": "wh_001",
        "status": "PENDING",
    })

    # 尝试用错误的版本号更新（实际版本是1，传入2）
    result = db.update_one("orders", {"_id": "order_001"}, {"status": "COLLECTED"}, version=2)
    assert result is False

    # 验证数据未被修改
    order = db.find_one("orders", {"_id": "order_001"})
    assert order["status"] == "PENDING"
    assert order["_version"] == 1


def test_update_without_version_bypasses_lock(db: SQLiteAdapter, init_tables):
    """测试不传版本号时跳过乐观锁检查（向后兼容）。"""
    # 插入测试数据
    db.insert("orders", {
        "_id": "order_001",
        "_openid": "o_test",
        "orderNo": "ORD001",
        "userId": "user_001",
        "warehouseId": "wh_001",
        "status": "PENDING",
    })

    # 不传版本号更新
    result = db.update_one("orders", {"_id": "order_001"}, {"status": "COLLECTED"})
    assert result is True

    # 验证更新成功（版本号不变，因为没有传入version参数）
    order = db.find_one("orders", {"_id": "order_001"})
    assert order["status"] == "COLLECTED"
    # 注意：不传version时，version字段不会被自动更新


def test_update_nonexistent_record_fails(db: SQLiteAdapter, init_tables):
    """测试更新不存在的记录返回 False。"""
    result = db.update_one("orders", {"_id": "nonexistent"}, {"status": "COLLECTED"}, version=1)
    assert result is False


def test_concurrent_update_only_one_succeeds(db: SQLiteAdapter, init_tables):
    """测试并发更新场景：两个请求同时更新同一订单，只有一个成功。

    模拟场景：
    1. 请求A读取订单，version=1
    2. 请求B读取订单，version=1
    3. 请求A更新成功，version变为2
    4. 请求B更新失败，因为version已变
    """
    # 插入测试数据
    db.insert("orders", {
        "_id": "order_001",
        "_openid": "o_test",
        "orderNo": "ORD001",
        "userId": "user_001",
        "warehouseId": "wh_001",
        "status": "PENDING",
    })

    # 模拟两个并发请求读取到相同的版本号
    order_a = db.find_one("orders", {"_id": "order_001"})
    order_b = db.find_one("orders", {"_id": "order_001"})

    version_a = order_a["_version"]  # version = 1
    version_b = order_b["_version"]  # version = 1

    # 请求A先更新（使用version=1）
    result_a = db.update_one("orders", {"_id": "order_001"}, {"status": "COLLECTED"}, version=version_a)
    assert result_a is True, "请求A应该成功"

    # 验证版本已更新
    order = db.find_one("orders", {"_id": "order_001"})
    assert order["_version"] == 2
    assert order["status"] == "COLLECTED"

    # 请求B尝试更新（使用过期的version=1）
    result_b = db.update_one("orders", {"_id": "order_001"}, {"status": "STORED"}, version=version_b)
    assert result_b is False, "请求B应该失败（版本冲突）"

    # 验证最终状态：只有请求A的更新生效
    order = db.find_one("orders", {"_id": "order_001"})
    assert order["_version"] == 2
    assert order["status"] == "COLLECTED", "状态应保持请求A的更新"


def test_multiple_version_updates(db: SQLiteAdapter, init_tables):
    """测试连续多次版本更新。"""
    # 插入测试数据
    db.insert("orders", {
        "_id": "order_001",
        "_openid": "o_test",
        "orderNo": "ORD001",
        "userId": "user_001",
        "warehouseId": "wh_001",
        "status": "PENDING",
    })

    # 连续更新3次
    for i, (new_status, expected_version) in enumerate([
        ("COLLECTED", 2),
        ("STORED", 3),
        ("DELIVERING", 4),
    ], 1):
        order = db.find_one("orders", {"_id": "order_001"})
        result = db.update_one("orders", {"_id": "order_001"}, {"status": new_status}, version=order["_version"])
        assert result is True, f"第{i}次更新失败"

        order = db.find_one("orders", {"_id": "order_001"})
        assert order["_version"] == expected_version, f"第{i}次版本号不正确"
        assert order["status"] == new_status


def test_version_check_for_users_table(db: SQLiteAdapter, init_tables):
    """测试用户表的乐观锁。"""
    # 插入测试数据
    db.insert("users", {
        "_id": "user_001",
        "_openid": "o_test",
        "nickName": "测试用户",
        "role": "USER",
    })

    # 正确版本更新
    result = db.update_one("users", {"_id": "user_001"}, {"nickName": "新昵称"}, version=1)
    assert result is True

    user = db.find_one("users", {"_id": "user_001"})
    assert user["_version"] == 2
    assert user["nickName"] == "新昵称"

    # 错误版本更新
    result = db.update_one("users", {"_id": "user_001"}, {"nickName": "再次修改"}, version=1)
    assert result is False

    user = db.find_one("users", {"_id": "user_001"})
    assert user["_version"] == 2
    assert user["nickName"] == "新昵称"
