"""仓库路由测试。"""

import pytest
from pathlib import Path

from src.app import create_app
from src.db.sqlite_adapter import SQLiteAdapter
from src.common.errors import ErrorCode


@pytest.fixture
def app():
    """创建测试应用实例。"""
    app = create_app("testing")
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """创建测试客户端。"""
    return app.test_client()


@pytest.fixture
def init_db(app):
    """初始化测试内存数据库，确保所有路由使用同一实例。"""
    with app.app_context():
        from src.db import factory
        adapter = SQLiteAdapter(":memory:")
        adapter._get_connection().execute("PRAGMA journal_mode=MEMORY;")
        schema_sql = Path(__file__).parent.parent / "src" / "db" / "schema.sql"
        if schema_sql.exists():
            adapter.conn.executescript(schema_sql.read_text(encoding="utf-8"))

        # 插入测试仓库数据（直接使用SQL，因为warehouses表没有update_time字段）
        now = "2026-05-12T00:00:00.000+00:00"
        adapter.conn.execute(
            "INSERT INTO warehouses (id, name, city, address, capacity, used_capacity, status, create_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("wh_bj_001", "北京中心仓", "北京", "朝阳区建国路88号", 100, 20, "ACTIVE", now)
        )
        adapter.conn.execute(
            "INSERT INTO warehouses (id, name, city, address, capacity, used_capacity, status, create_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("wh_bj_002", "北京通州仓", "北京", "通州区新华大街100号", 150, 50, "ACTIVE", now)
        )
        adapter.conn.execute(
            "INSERT INTO warehouses (id, name, city, address, capacity, used_capacity, status, create_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("wh_sh_001", "上海浦东仓", "上海", "浦东新区张江路66号", 200, 80, "ACTIVE", now)
        )
        adapter.conn.execute(
            "INSERT INTO warehouses (id, name, city, address, capacity, used_capacity, status, create_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("wh_inactive", "已关闭仓库", "北京", "无效地址", 50, 0, "INACTIVE", now)
        )

        factory._db_adapter = adapter
        yield
        adapter.close()
        factory._db_adapter = None


def test_get_warehouses_list(client, init_db):
    """测试获取仓库列表。"""
    response = client.get("/api/warehouses")
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 0
    assert "data" in data
    # 应该返回3个活跃仓库（排除INACTIVE状态）
    assert len(data["data"]) == 3


def test_get_warehouses_filter_by_city(client, init_db):
    """测试按城市筛选仓库。"""
    response = client.get("/api/warehouses?city=北京")
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 0
    assert len(data["data"]) == 2
    # 验证返回的都是北京的仓库
    for wh in data["data"]:
        assert wh["city"] == "北京"


def test_get_warehouses_filter_by_city_shanghai(client, init_db):
    """测试按城市筛选仓库 - 上海。"""
    response = client.get("/api/warehouses?city=上海")
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 0
    assert len(data["data"]) == 1
    assert data["data"][0]["city"] == "上海"
    assert data["data"][0]["name"] == "上海浦东仓"


def test_get_warehouses_filter_by_city_not_found(client, init_db):
    """测试按城市筛选 - 无结果。"""
    response = client.get("/api/warehouses?city=深圳")
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 0
    assert len(data["data"]) == 0


def test_warehouse_response_fields(client, init_db):
    """测试仓库返回字段。"""
    response = client.get("/api/warehouses?city=上海")
    assert response.status_code == 200
    data = response.get_json()
    wh = data["data"][0]

    # 验证必要字段存在
    assert "_id" in wh
    assert "name" in wh
    assert "city" in wh
    assert "address" in wh
    assert "capacity" in wh
    assert "usedCapacity" in wh

    # 验证字段值
    assert wh["_id"] == "wh_sh_001"
    assert wh["name"] == "上海浦东仓"
    assert wh["city"] == "上海"
    assert wh["address"] == "浦东新区张江路66号"
    assert wh["capacity"] == 200
    assert wh["usedCapacity"] == 80


def test_warehouses_exclude_inactive(client, init_db):
    """测试不返回已关闭的仓库。"""
    response = client.get("/api/warehouses?city=北京")
    assert response.status_code == 200
    data = response.get_json()

    # 确保不包含已关闭的仓库
    warehouse_ids = [wh["_id"] for wh in data["data"]]
    assert "wh_inactive" not in warehouse_ids
