"""Flask路由集成测试。"""

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
        factory._db_adapter = adapter
        yield
        adapter.close()
        factory._db_adapter = None


def test_health_endpoint(client):
    """测试健康检查端点。"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 0
    assert data["data"]["status"] == "ok"


def test_login_endpoint(client, init_db):
    """测试登录端点。"""
    response = client.post(
        "/api/login",
        headers={"X-OpenId": "test_user_123"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 0
    assert "data" in data
    assert data["data"]["openId"] == "test_user_123"
    assert data["data"]["role"] == "USER"


def test_create_order_endpoint(client, init_db):
    """测试创建订单端点。"""
    # 先登录
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    # 创建订单
    response = client.post(
        "/api/orders",
        headers={"X-OpenId": "test_user_123"},
        json={
            "city": "北京",
            "itemType": "LUGGAGE",
            "warehouseId": "wh_bj_central"
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["code"] == 0
    assert "data" in data
    assert data["data"]["status"] == "PENDING"
    assert data["data"]["city"] == "北京"
    assert data["data"]["itemType"] == "LUGGAGE"


def test_get_order_list_endpoint(client, init_db):
    """测试获取订单列表端点。"""
    # 先登录并创建订单
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})
    client.post(
        "/api/orders",
        headers={"X-OpenId": "test_user_123"},
        json={
            "city": "北京",
            "itemType": "LUGGAGE",
            "warehouseId": "wh_bj_central"
        }
    )

    # 获取订单列表
    response = client.get(
        "/api/orders",
        headers={"X-OpenId": "test_user_123"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 0
    assert "data" in data
    assert "list" in data["data"]
    assert "total" in data["data"]
    assert len(data["data"]["list"]) >= 1


def test_update_order_status_endpoint(client, init_db):
    """测试更新订单状态端点。"""
    # 先登录并创建订单
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})
    create_response = client.post(
        "/api/orders",
        headers={"X-OpenId": "test_user_123"},
        json={
            "city": "北京",
            "itemType": "LUGGAGE",
            "warehouseId": "wh_bj_central"
        }
    )
    order_id = create_response.get_json()["data"]["_id"]

    # 更新订单状态
    response = client.patch(
        f"/api/orders/{order_id}/status",
        headers={"X-OpenId": "test_user_123"},
        json={
            "newStatus": "COLLECTED",
            "operatorType": "ADMIN"
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 0
    assert data["data"]["status"] == "COLLECTED"
    assert len(data["data"]["statusHistory"]) == 1


def test_invalid_status_transition(client, init_db):
    """测试无效状态转换。"""
    # 先登录并创建订单
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})
    create_response = client.post(
        "/api/orders",
        headers={"X-OpenId": "test_user_123"},
        json={
            "city": "北京",
            "itemType": "LUGGAGE",
            "warehouseId": "wh_bj_central"
        }
    )
    order_id = create_response.get_json()["data"]["_id"]

    # 尝试无效状态转换（PENDING -> COMPLETED 直接完成）
    response = client.patch(
        f"/api/orders/{order_id}/status",
        headers={"X-OpenId": "test_user_123"},
        json={
            "newStatus": "COMPLETED",
            "operatorType": "ADMIN"
        }
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == ErrorCode.INVALID_TRANSITION


# ========== 地址路由测试 ==========

def test_get_addresses_empty(client, init_db):
    """测试获取空地址列表。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    response = client.get("/api/addresses", headers={"X-OpenId": "test_user_123"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 0
    assert data["data"] == []


def test_create_address(client, init_db):
    """测试创建地址。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    response = client.post(
        "/api/addresses",
        headers={"X-OpenId": "test_user_123"},
        json={
            "name": "张三",
            "phone": "13800138000",
            "province": "北京市",
            "city": "北京市",
            "district": "朝阳区",
            "detail": "XX路XX号",
            "tag": "家",
            "isDefault": True
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["code"] == 0
    assert data["data"]["name"] == "张三"
    assert data["data"]["isDefault"] is True


def test_create_address_minimal(client, init_db):
    """测试创建地址（最小字段）。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    response = client.post(
        "/api/addresses",
        headers={"X-OpenId": "test_user_123"},
        json={
            "name": "李四",
            "phone": "13900139000",
            "province": "上海市",
            "city": "上海市",
            "detail": "YY路YY号"
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["data"]["name"] == "李四"
    assert data["data"]["isDefault"] is False


def test_create_address_empty_body(client, init_db):
    """测试空请求体创建地址。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    response = client.post(
        "/api/addresses",
        headers={"X-OpenId": "test_user_123"},
        data="",
        content_type="application/json"
    )
    # 空请求体应返回错误（400或500都表示失败）
    assert response.status_code >= 400


def test_create_address_max_limit(client, init_db):
    """测试地址数量上限（超过10个应拒绝）。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    # 创建10个地址应该成功
    for i in range(10):
        resp = client.post(
            "/api/addresses",
            headers={"X-OpenId": "test_user_123"},
            json={
                "name": f"地址{i}",
                "phone": f"138{str(i).zfill(8)}",
                "province": "省",
                "city": "市",
                "detail": f"地址{i}"
            }
        )
        assert resp.status_code == 201

    # 第11个应该失败
    resp = client.post(
        "/api/addresses",
        headers={"X-OpenId": "test_user_123"},
        json={
            "name": "地址超限",
            "phone": "13800139011",
            "province": "省",
            "city": "市",
            "detail": "超限"
        }
    )
    assert resp.status_code == 400


def test_get_address_detail(client, init_db):
    """测试获取地址详情。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    # 先创建地址
    create_response = client.post(
        "/api/addresses",
        headers={"X-OpenId": "test_user_123"},
        json={
            "name": "王五",
            "phone": "13700137000",
            "province": "广东省",
            "city": "广州市",
            "detail": "ZZ路ZZ号"
        }
    )
    address_id = create_response.get_json()["data"]["_id"]

    # 获取详情
    response = client.get(
        f"/api/addresses/{address_id}",
        headers={"X-OpenId": "test_user_123"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["name"] == "王五"


def test_get_address_not_found(client, init_db):
    """测试获取不存在的地址。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    response = client.get(
        "/api/addresses/nonexistent_id",
        headers={"X-OpenId": "test_user_123"}
    )
    assert response.status_code == 404


def test_update_address(client, init_db):
    """测试更新地址。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    # 先创建地址
    create_response = client.post(
        "/api/addresses",
        headers={"X-OpenId": "test_user_123"},
        json={
            "name": "赵六",
            "phone": "13600136000",
            "province": "浙江省",
            "city": "杭州市",
            "detail": "AA路AA号"
        }
    )
    address_id = create_response.get_json()["data"]["_id"]

    # 更新地址
    response = client.patch(
        f"/api/addresses/{address_id}",
        headers={"X-OpenId": "test_user_123"},
        json={"name": "赵六更新", "phone": "13600136001"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["name"] == "赵六更新"
    assert data["data"]["phone"] == "13600136001"


def test_update_nonexistent_address(client, init_db):
    """测试更新不存在的地址。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    response = client.patch(
        "/api/addresses/nonexistent_id",
        headers={"X-OpenId": "test_user_123"},
        json={"name": "新名字"}
    )
    assert response.status_code == 404


def test_delete_address(client, init_db):
    """测试删除地址。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    # 先创建地址
    create_response = client.post(
        "/api/addresses",
        headers={"X-OpenId": "test_user_123"},
        json={
            "name": "孙七",
            "phone": "13500135000",
            "province": "四川省",
            "city": "成都市",
            "detail": "BB路BB号"
        }
    )
    address_id = create_response.get_json()["data"]["_id"]

    # 删除地址
    response = client.delete(
        f"/api/addresses/{address_id}",
        headers={"X-OpenId": "test_user_123"}
    )
    assert response.status_code == 200

    # 验证已删除
    get_response = client.get(
        f"/api/addresses/{address_id}",
        headers={"X-OpenId": "test_user_123"}
    )
    assert get_response.status_code == 404


def test_delete_nonexistent_address(client, init_db):
    """测试删除不存在的地址。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    response = client.delete(
        "/api/addresses/nonexistent_id",
        headers={"X-OpenId": "test_user_123"}
    )
    assert response.status_code == 404


def test_set_default_nonexistent_address(client, init_db):
    """测试设置不存在的地址为默认。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    response = client.post(
        "/api/addresses/nonexistent_id/default",
        headers={"X-OpenId": "test_user_123"}
    )
    assert response.status_code == 404


def test_set_default_address(client, init_db):
    """测试设置默认地址。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    # 创建两个地址（使用有效手机号）
    resp1 = client.post(
        "/api/addresses",
        headers={"X-OpenId": "test_user_123"},
        json={"name": "默认", "phone": "13800138011", "province": "京", "city": "京", "detail": "a"}
    )
    resp2 = client.post(
        "/api/addresses",
        headers={"X-OpenId": "test_user_123"},
        json={"name": "非默认", "phone": "13800138012", "province": "沪", "city": "沪", "detail": "b"}
    )
    addr1_id = resp1.get_json()["data"]["_id"]
    addr2_id = resp2.get_json()["data"]["_id"]

    # 设置第二个为默认
    response = client.post(
        f"/api/addresses/{addr2_id}/default",
        headers={"X-OpenId": "test_user_123"}
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["isDefault"] is True

    # 验证第一个不再是默认
    resp = client.get(f"/api/addresses/{addr1_id}", headers={"X-OpenId": "test_user_123"})
    assert resp.get_json()["data"]["isDefault"] is False


def test_get_default_address(client, init_db):
    """测试获取默认地址。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    # 创建默认地址（使用有效手机号）
    client.post(
        "/api/addresses",
        headers={"X-OpenId": "test_user_123"},
        json={"name": "默认地址", "phone": "13800138888", "province": "粤", "city": "穗", "detail": "c", "isDefault": True}
    )

    response = client.get("/api/addresses/default", headers={"X-OpenId": "test_user_123"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["name"] == "默认地址"


def test_address_unauthorized(client, init_db):
    """测试未登录访问地址接口。"""
    # 无 header 请求
    response = client.get("/api/addresses")
    assert response.status_code == 401

    response = client.post("/api/addresses", json={"name": "test"})
    assert response.status_code == 401


def test_address_forbidden(client, init_db):
    """测试访问他人地址被拒绝。"""
    # 用户1创建地址
    client.post("/api/login", headers={"X-OpenId": "user1"})
    resp1 = client.post(
        "/api/addresses",
        headers={"X-OpenId": "user1"},
        json={"name": "用户1地址", "phone": "13800138001", "province": "A", "city": "A", "detail": "a"}
    )
    addr_id = resp1.get_json()["data"]["_id"]

    # 用户2尝试访问
    client.post("/api/login", headers={"X-OpenId": "user2"})
    resp2 = client.get(f"/api/addresses/{addr_id}", headers={"X-OpenId": "user2"})
    assert resp2.status_code == 403


def test_address_permission_edit(client, init_db):
    """测试编辑他人地址被拒绝。"""
    # 用户1创建地址
    client.post("/api/login", headers={"X-OpenId": "user3"})
    resp1 = client.post(
        "/api/addresses",
        headers={"X-OpenId": "user3"},
        json={"name": "用户3地址", "phone": "13800138003", "province": "B", "city": "B", "detail": "b"}
    )
    addr_id = resp1.get_json()["data"]["_id"]

    # 用户4尝试编辑
    client.post("/api/login", headers={"X-OpenId": "user4"})
    resp2 = client.patch(
        f"/api/addresses/{addr_id}",
        headers={"X-OpenId": "user4"},
        json={"name": "被拒绝"}
    )
    assert resp2.status_code == 403


def test_address_permission_delete(client, init_db):
    """测试删除他人地址被拒绝。"""
    # 用户5创建地址
    client.post("/api/login", headers={"X-OpenId": "user5"})
    resp1 = client.post(
        "/api/addresses",
        headers={"X-OpenId": "user5"},
        json={"name": "用户5地址", "phone": "13800138005", "province": "C", "city": "C", "detail": "c"}
    )
    addr_id = resp1.get_json()["data"]["_id"]

    # 用户6尝试删除
    client.post("/api/login", headers={"X-OpenId": "user6"})
    resp2 = client.delete(f"/api/addresses/{addr_id}", headers={"X-OpenId": "user6"})
    assert resp2.status_code == 403


# ========== 订单支付路由测试 ==========

def test_create_payment(client, init_db):
    """测试创建支付单。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    # 创建订单
    create_response = client.post(
        "/api/orders",
        headers={"X-OpenId": "test_user_123"},
        json={"city": "北京", "itemType": "LUGGAGE", "warehouseId": "wh_bj_central"}
    )
    order_id = create_response.get_json()["data"]["_id"]

    # 创建支付单
    response = client.post(
        f"/api/orders/{order_id}/payment",
        headers={"X-OpenId": "test_user_123"},
        json={
            "amount": {
                "storageFee": 100,
                "deliveryFee": 50,
                "totalFee": 150
            }
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["code"] == 0
    assert data["data"]["orderId"] == order_id
    assert data["data"]["totalFee"] == 150


def test_execute_payment(client, init_db):
    """测试执行支付。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    # 创建订单和支付单
    create_response = client.post(
        "/api/orders",
        headers={"X-OpenId": "test_user_123"},
        json={"city": "北京", "itemType": "PACKAGE", "warehouseId": "wh_bj_central"}
    )
    order_id = create_response.get_json()["data"]["_id"]

    payment_response = client.post(
        f"/api/orders/{order_id}/payment",
        headers={"X-OpenId": "test_user_123"},
        json={"amount": {"totalFee": 100}}
    )
    payment_id = payment_response.get_json()["data"]["_id"]

    # 执行支付
    response = client.post(
        f"/api/orders/{order_id}/pay",
        headers={"X-OpenId": "test_user_123"},
        json={"paymentId": payment_id, "paymentMethod": "WECHAT"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 0
    assert data["data"]["status"] == "SUCCESS"


def test_get_payment_status(client, init_db):
    """测试查询支付状态。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    # 创建订单
    create_response = client.post(
        "/api/orders",
        headers={"X-OpenId": "test_user_123"},
        json={"city": "上海", "itemType": "DOCUMENT", "warehouseId": "wh_sh_central"}
    )
    order_id = create_response.get_json()["data"]["_id"]

    response = client.get(
        f"/api/orders/{order_id}/payment/status",
        headers={"X-OpenId": "test_user_123"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["code"] == 0
    assert data["data"]["orderId"] == order_id


def test_execute_payment_wrong_status(client, init_db):
    """测试对已支付订单再次支付。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    # 创建并完成支付流程
    create_response = client.post(
        "/api/orders",
        headers={"X-OpenId": "test_user_123"},
        json={"city": "深圳", "itemType": "LUGGAGE", "warehouseId": "wh_sz_central"}
    )
    order_id = create_response.get_json()["data"]["_id"]

    payment_response = client.post(
        f"/api/orders/{order_id}/payment",
        headers={"X-OpenId": "test_user_123"},
        json={"amount": {"totalFee": 80}}
    )
    payment_id = payment_response.get_json()["data"]["_id"]

    # 第一次支付成功
    client.post(
        f"/api/orders/{order_id}/pay",
        headers={"X-OpenId": "test_user_123"},
        json={"paymentId": payment_id, "paymentMethod": "WECHAT"}
    )

    # 再次支付应失败
    response = client.post(
        f"/api/orders/{order_id}/pay",
        headers={"X-OpenId": "test_user_123"},
        json={"paymentId": payment_id, "paymentMethod": "WECHAT"}
    )
    assert response.status_code == 400


def test_order_pagination(client, init_db):
    """测试订单分页。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    # 创建多个订单
    for i in range(5):
        client.post(
            "/api/orders",
            headers={"X-OpenId": "test_user_123"},
            json={"city": "广州", "itemType": "LUGGAGE", "warehouseId": "wh_gz_central"}
        )

    # 分页查询
    response = client.get(
        "/api/orders?page=1&pageSize=3",
        headers={"X-OpenId": "test_user_123"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]["list"]) == 3
    assert data["data"]["total"] >= 5
    assert data["data"]["page"] == 1
    assert data["data"]["pageSize"] == 3


def test_order_filter_by_status(client, init_db):
    """测试按状态筛选订单。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    # 创建订单
    create_response = client.post(
        "/api/orders",
        headers={"X-OpenId": "test_user_123"},
        json={"city": "成都", "itemType": "PACKAGE", "warehouseId": "wh_cd_central"}
    )
    order_id = create_response.get_json()["data"]["_id"]

    # 变更状态
    client.patch(
        f"/api/orders/{order_id}/status",
        headers={"X-OpenId": "test_user_123"},
        json={"newStatus": "COLLECTED", "operatorType": "ADMIN"}
    )

    # 按状态筛选
    response = client.get(
        "/api/orders?status=COLLECTED",
        headers={"X-OpenId": "test_user_123"}
    )
    data = response.get_json()
    assert all(o["status"] == "COLLECTED" for o in data["data"]["list"])


def test_order_unauthorized(client, init_db):
    """测试未登录访问订单接口。"""
    response = client.get("/api/orders")
    assert response.status_code == 401

    response = client.post("/api/orders", json={"city": "北京"})
    assert response.status_code == 401


def test_create_order_empty_body(client, init_db):
    """测试空请求体创建订单。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    response = client.post(
        "/api/orders",
        headers={"X-OpenId": "test_user_123"},
        data="",
        content_type="application/json"
    )
    assert response.status_code >= 400


def test_create_order_empty_body(client, init_db):
    """测试空请求体创建订单。"""
    client.post("/api/login", headers={"X-OpenId": "test_user_123"})

    response = client.post(
        "/api/orders",
        headers={"X-OpenId": "test_user_123"},
        data="",
        content_type="application/json"
    )
    assert response.status_code >= 400