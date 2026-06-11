"""集成测试 - 完整业务流程测试。

测试覆盖完整的用户旅程：
1. 用户注册/登录
2. 创建订单
3. 订单状态流转（PENDING -> COLLECTED -> TRANSIT -> STORED -> DELIVERING -> COMPLETED）
4. 运营端状态变更
5. 定时任务超时处理
"""

import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.app import create_app
from src.db.sqlite_adapter import SQLiteAdapter
from src.tasks.timeout_checker import check_pending_timeout, check_delivering_timeout


@pytest.fixture
def client():
    """创建测试客户端（每个测试独立）。"""
    app = create_app("testing")
    app.config["TESTING"] = True

    # 设置内存数据库
    with app.app_context():
        from src.db import factory
        adapter = SQLiteAdapter(":memory:")
        adapter._get_connection().execute("PRAGMA journal_mode=MEMORY;")
        schema_sql = Path(__file__).parent.parent / "src" / "db" / "schema.sql"
        if schema_sql.exists():
            adapter.conn.executescript(schema_sql.read_text(encoding="utf-8"))
        factory._db_adapter = adapter

    with app.test_client() as client:
        yield client

    # 清理
    with app.app_context():
        from src.db import factory
        if hasattr(factory, '_db_adapter'):
            factory._db_adapter.close()
            delattr(factory, '_db_adapter')


class TestCompleteUserJourney:
    """完整用户旅程测试。"""

    def test_user_registration_and_login(self, client):
        """测试用户注册和登录流程。"""
        # 新用户登录（自动注册）
        response = client.post("/api/login", headers={"X-OpenId": "new_user_001"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["code"] == 0
        assert data["data"]["openId"] == "new_user_001"
        assert data["data"]["role"] == "USER"

        # 再次登录（已存在用户）
        response = client.post("/api/login", headers={"X-OpenId": "new_user_001"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["code"] == 0

    def test_create_order_flow(self, client):
        """测试创建订单流程。"""
        # 先登录
        client.post("/api/login", headers={"X-OpenId": "test_user_001"})

        # 创建订单
        response = client.post(
            "/api/orders",
            headers={"X-OpenId": "test_user_001"},
            json={
                "city": "北京",
                "itemType": "LUGGAGE",
                "warehouseId": "wh_bj_central"
            }
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["code"] == 0
        assert data["data"]["status"] == "PENDING"
        assert data["data"]["city"] == "北京"
        assert data["data"]["itemType"] == "LUGGAGE"
        assert "_id" in data["data"]
        assert "orderNo" in data["data"]

    def test_order_status_workflow(self, client):
        """测试订单状态流转流程。"""
        # 登录并创建订单
        client.post("/api/login", headers={"X-OpenId": "test_user_002"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "test_user_002"},
            json={
                "city": "上海",
                "itemType": "LUGGAGE",
                "warehouseId": "wh_sh_pudong"
            }
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 1. PENDING -> COLLECTED (运营端操作)
        response = client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={
                "newStatus": "COLLECTED",
                "operatorType": "ADMIN",
                "reason": "物品已揽收"
            }
        )
        assert response.status_code == 200
        assert response.get_json()["data"]["status"] == "COLLECTED"

        # 2. COLLECTED -> TRANSIT (运营端操作)
        response = client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={
                "newStatus": "TRANSIT",
                "operatorType": "ADMIN",
                "reason": "物品运输中"
            }
        )
        assert response.status_code == 200
        assert response.get_json()["data"]["status"] == "TRANSIT"

        # 3. TRANSIT -> STORED (运营端操作)
        response = client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={
                "newStatus": "STORED",
                "operatorType": "ADMIN",
                "reason": "物品已入库"
            }
        )
        assert response.status_code == 200
        assert response.get_json()["data"]["status"] == "STORED"

        # 4. STORED -> DELIVERING (用户发起配送)
        response = client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "test_user_002"},
            json={
                "newStatus": "DELIVERING",
                "operatorType": "USER",
                "reason": "用户发起配送"
            }
        )
        assert response.status_code == 200
        assert response.get_json()["data"]["status"] == "DELIVERING"

        # 5. DELIVERING -> COMPLETED (用户确认收货)
        response = client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "test_user_002"},
            json={
                "newStatus": "COMPLETED",
                "operatorType": "USER",
                "reason": "用户确认收货"
            }
        )
        assert response.status_code == 200
        assert response.get_json()["data"]["status"] == "COMPLETED"

        # 验证状态历史记录
        detail_response = client.get(
            f"/api/orders/{order_id}",
            headers={"X-OpenId": "test_user_002"}
        )
        status_history = detail_response.get_json()["data"]["statusHistory"]
        assert len(status_history) == 5  # 5次状态变更

    def test_invalid_status_transition(self, client):
        """测试无效状态流转被拒绝。"""
        # 登录并创建订单
        client.post("/api/login", headers={"X-OpenId": "test_user_003"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "test_user_003"},
            json={
                "city": "广州",
                "itemType": "PACKAGE",
                "warehouseId": "wh_gz_uc_north"
            }
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 尝试 PENDING -> COMPLETED (跳过中间状态)
        response = client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "test_user_003"},
            json={
                "newStatus": "COMPLETED",
                "operatorType": "USER"
            }
        )
        assert response.status_code == 400
        assert response.get_json()["code"] == 2002  # INVALID_TRANSITION

    def test_order_list_and_pagination(self, client):
        """测试订单列表和分页功能。"""
        # 登录
        client.post("/api/login", headers={"X-OpenId": "test_user_004"})

        # 创建多个订单
        for i in range(5):
            client.post(
                "/api/orders",
                headers={"X-OpenId": "test_user_004"},
                json={
                    "city": "深圳",
                    "itemType": "LUGGAGE",
                    "warehouseId": "wh_sz_nanshan"
                }
            )

        # 获取订单列表（第一页）
        response = client.get(
            "/api/orders?page=1&pageSize=3",
            headers={"X-OpenId": "test_user_004"}
        )
        assert response.status_code == 200
        data = response.get_json()["data"]
        assert len(data["list"]) == 3
        assert data["total"] >= 5
        assert data["page"] == 1

        # 获取第二页
        response = client.get(
            "/api/orders?page=2&pageSize=3",
            headers={"X-OpenId": "test_user_004"}
        )
        data = response.get_json()["data"]
        assert data["page"] == 2

    def test_order_filter_by_status(self, client):
        """测试按状态筛选订单。"""
        # 登录
        client.post("/api/login", headers={"X-OpenId": "test_user_005"})

        # 创建订单
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "test_user_005"},
            json={
                "city": "杭州",
                "itemType": "DOCUMENT",
                "warehouseId": "wh_hz_xihu"
            }
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 变更状态为 COLLECTED
        client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={
                "newStatus": "COLLECTED",
                "operatorType": "ADMIN"
            }
        )

        # 筛选 COLLECTED 状态的订单
        response = client.get(
            "/api/orders?status=COLLECTED",
            headers={"X-OpenId": "test_user_005"}
        )
        assert response.status_code == 200
        orders = response.get_json()["data"]["list"]
        assert all(o["status"] == "COLLECTED" for o in orders)


class TestTimeoutTasks:
    """定时任务超时处理测试。"""

    def test_pending_timeout_cancels_expired_orders(self, client):
        """测试PENDING超时自动取消。"""
        # 登录并创建订单
        client.post("/api/login", headers={"X-OpenId": "test_user_006"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "test_user_006"},
            json={
                "city": "成都",
                "itemType": "LUGGAGE",
                "warehouseId": "wh_cd_wuhou"
            }
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 修改订单创建时间为8天前
        from src.db import factory
        old_time = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
        factory._db_adapter.update_one("orders", {"_id": order_id}, {"createTime": old_time})

        # 执行超时检查
        result = check_pending_timeout(factory._db_adapter, timeout_days=7)

        # 验证订单已被取消
        assert result["total"] == 1
        assert result["success"] == 1

        # 验证订单状态
        detail_response = client.get(
            f"/api/orders/{order_id}",
            headers={"X-OpenId": "test_user_006"}
        )
        assert detail_response.get_json()["data"]["status"] == "CANCELLED"

    def test_delivering_timeout_completes_expired_orders(self, client):
        """测试DELIVERING超时自动完结。"""
        # 登录并创建订单
        client.post("/api/login", headers={"X-OpenId": "test_user_007"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "test_user_007"},
            json={
                "city": "武汉",
                "itemType": "LUGGAGE",
                "warehouseId": "wh_wh_wuchang"
            }
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 将订单状态更新为 DELIVERING，并设置8天前的状态时间
        from src.db import factory
        delivering_time = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
        factory._db_adapter.update_one("orders", {"_id": order_id}, {
            "status": "DELIVERING",
            "statusHistory": [{
                "from": "STORED",
                "to": "DELIVERING",
                "operatorType": "USER",
                "operatorId": "test_user_007",
                "time": delivering_time
            }]
        })

        # 执行超时检查
        result = check_delivering_timeout(factory._db_adapter, timeout_days=7)

        # 验证订单已完结
        assert result["total"] == 1
        assert result["success"] == 1

        # 验证订单状态
        detail_response = client.get(
            f"/api/orders/{order_id}",
            headers={"X-OpenId": "test_user_007"}
        )
        assert detail_response.get_json()["data"]["status"] == "COMPLETED"


class TestPermissionControl:
    """权限控制测试。"""

    def test_user_cannot_access_others_order(self, client):
        """测试用户不能访问他人订单。"""
        # 用户A创建订单
        client.post("/api/login", headers={"X-OpenId": "user_a"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "user_a"},
            json={
                "city": "西安",
                "itemType": "PACKAGE",
                "warehouseId": "wh_wa_yanta"
            }
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 用户B尝试访问
        response = client.get(
            f"/api/orders/{order_id}",
            headers={"X-OpenId": "user_b"}
        )
        assert response.status_code == 403
        assert response.get_json()["code"] == 1003  # FORBIDDEN

    def test_unauthorized_access_rejected(self, client):
        """测试未授权访问被拒绝。"""
        response = client.get("/api/orders")
        assert response.status_code == 401
        assert response.get_json()["code"] == 1002  # UNAUTHORIZED


class TestAdminOperations:
    """运营端操作测试。"""

    def test_admin_can_view_all_orders(self, client):
        """测试运营端可以查看所有订单。"""
        # 创建多个用户的订单
        for i in range(3):
            client.post("/api/login", headers={"X-OpenId": f"user_{i}"})
            client.post(
                "/api/orders",
                headers={"X-OpenId": f"user_{i}"},
                json={
                    "city": "北京",
                    "itemType": "LUGGAGE",
                    "warehouseId": "wh_bj_central"
                }
            )

        # 运营端查看所有订单
        response = client.get(
            "/api/orders?page=1&pageSize=10",
            headers={"X-OpenId": "admin"}
        )
        assert response.status_code == 200
        data = response.get_json()["data"]
        assert data["total"] >= 3

    def test_admin_can_change_any_order_status(self, client):
        """测试运营端可以变更任意订单状态。"""
        # 用户创建订单
        client.post("/api/login", headers={"X-OpenId": "regular_user"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "regular_user"},
            json={
                "city": "上海",
                "itemType": "LUGGAGE",
                "warehouseId": "wh_sh_pudong"
            }
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 运营端变更状态
        response = client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={
                "newStatus": "COLLECTED",
                "operatorType": "ADMIN",
                "reason": "运营端操作"
            }
        )
        assert response.status_code == 200
        assert response.get_json()["data"]["status"] == "COLLECTED"


class TestPaymentFlow:
    """支付流程集成测试。"""

    def test_complete_payment_flow(self, client):
        """测试完整支付流程。"""
        # 登录并创建订单
        client.post("/api/login", headers={"X-OpenId": "pay_user_001"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "pay_user_001"},
            json={"city": "北京", "itemType": "LUGGAGE", "warehouseId": "wh_bj_central"}
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 1. 创建支付单
        payment_response = client.post(
            f"/api/orders/{order_id}/payment",
            headers={"X-OpenId": "pay_user_001"},
            json={
                "amount": {
                    "storageFee": 100,
                    "deliveryFee": 50,
                    "totalFee": 150
                }
            }
        )
        assert payment_response.status_code == 201
        payment_data = payment_response.get_json()["data"]
        payment_id = payment_data["_id"]
        assert payment_data["orderId"] == order_id
        assert payment_data["status"] == "PENDING"

        # 2. 查询支付状态（待支付）
        status_response = client.get(
            f"/api/orders/{order_id}/payment/status",
            headers={"X-OpenId": "pay_user_001"}
        )
        status_data = status_response.get_json()["data"]
        assert status_data["isPaid"] is False

        # 3. 执行支付
        pay_response = client.post(
            f"/api/orders/{order_id}/pay",
            headers={"X-OpenId": "pay_user_001"},
            json={"paymentId": payment_id, "paymentMethod": "WECHAT"}
        )
        assert pay_response.status_code == 200
        pay_data = pay_response.get_json()["data"]
        assert pay_data["status"] == "SUCCESS"
        assert "transactionId" in pay_data

        # 4. 查询支付状态（已支付）
        status_response = client.get(
            f"/api/orders/{order_id}/payment/status",
            headers={"X-OpenId": "pay_user_001"}
        )
        status_data = status_response.get_json()["data"]
        assert status_data["isPaid"] is True

    def test_reject_double_payment(self, client):
        """测试重复支付被拒绝。"""
        # 登录并创建订单
        client.post("/api/login", headers={"X-OpenId": "pay_user_002"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "pay_user_002"},
            json={"city": "上海", "itemType": "PACKAGE", "warehouseId": "wh_sh_central"}
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 创建并完成支付
        payment_response = client.post(
            f"/api/orders/{order_id}/payment",
            headers={"X-OpenId": "pay_user_002"},
            json={"amount": {"totalFee": 100}}
        )
        payment_id = payment_response.get_json()["data"]["_id"]
        client.post(
            f"/api/orders/{order_id}/pay",
            headers={"X-OpenId": "pay_user_002"},
            json={"paymentId": payment_id, "paymentMethod": "WECHAT"}
        )

        # 再次支付应失败
        second_pay = client.post(
            f"/api/orders/{order_id}/pay",
            headers={"X-OpenId": "pay_user_002"},
            json={"paymentId": payment_id, "paymentMethod": "WECHAT"}
        )
        assert second_pay.status_code == 400


class TestAddressManagement:
    """地址管理集成测试。"""

    def test_create_and_manage_addresses(self, client):
        """测试创建和管理地址。"""
        # 登录
        client.post("/api/login", headers={"X-OpenId": "addr_user_001"})

        # 1. 创建第一个地址（设为默认）
        resp1 = client.post(
            "/api/addresses",
            headers={"X-OpenId": "addr_user_001"},
            json={
                "name": "家",
                "phone": "13800138001",
                "province": "北京市",
                "city": "北京市",
                "district": "朝阳区",
                "detail": "XX路XX号",
                "isDefault": True
            }
        )
        assert resp1.status_code == 201
        addr1_id = resp1.get_json()["data"]["_id"]

        # 2. 创建第二个地址
        resp2 = client.post(
            "/api/addresses",
            headers={"X-OpenId": "addr_user_001"},
            json={
                "name": "公司",
                "phone": "13800138002",
                "province": "北京市",
                "city": "北京市",
                "district": "海淀区",
                "detail": "YY路YY号"
            }
        )
        assert resp2.status_code == 201
        addr2_id = resp2.get_json()["data"]["_id"]

        # 3. 获取默认地址
        default_resp = client.get(
            "/api/addresses/default",
            headers={"X-OpenId": "addr_user_001"}
        )
        assert default_resp.get_json()["data"]["name"] == "家"

        # 4. 设置公司为默认
        set_default_resp = client.post(
            f"/api/addresses/{addr2_id}/default",
            headers={"X-OpenId": "addr_user_001"}
        )
        assert set_default_resp.get_json()["data"]["isDefault"] is True

        # 5. 验证原来的默认已被取消
        addr1_resp = client.get(
            f"/api/addresses/{addr1_id}",
            headers={"X-OpenId": "addr_user_001"}
        )
        assert addr1_resp.get_json()["data"]["isDefault"] is False

    def test_address_max_limit(self, client):
        """测试地址数量上限。"""
        client.post("/api/login", headers={"X-OpenId": "addr_user_002"})

        # 创建10个地址应该成功
        for i in range(10):
            resp = client.post(
                "/api/addresses",
                headers={"X-OpenId": "addr_user_002"},
                json={
                    "name": f"地址{i}",
                    "phone": f"138{str(i).zfill(8)}",
                    "province": "省",
                    "city": "市",
                    "detail": f"详情{i}"
                }
            )
            assert resp.status_code == 201

        # 第11个应该失败
        resp = client.post(
            "/api/addresses",
            headers={"X-OpenId": "addr_user_002"},
            json={
                "name": "超限",
                "phone": "13800139111",
                "province": "省",
                "city": "市",
                "detail": "超限详情"
            }
        )
        assert resp.status_code == 400

    def test_address_permission_isolation(self, client):
        """测试地址权限隔离。"""
        # 用户A创建地址
        client.post("/api/login", headers={"X-OpenId": "addr_user_a"})
        resp = client.post(
            "/api/addresses",
            headers={"X-OpenId": "addr_user_a"},
            json={"name": "用户A地址", "phone": "13800138010", "province": "A", "city": "A", "detail": "a"}
        )
        addr_id = resp.get_json()["data"]["_id"]

        # 用户B不能访问
        client.post("/api/login", headers={"X-OpenId": "addr_user_b"})
        access_resp = client.get(
            f"/api/addresses/{addr_id}",
            headers={"X-OpenId": "addr_user_b"}
        )
        assert access_resp.status_code == 403

        # 用户B不能编辑
        edit_resp = client.patch(
            f"/api/addresses/{addr_id}",
            headers={"X-OpenId": "addr_user_b"},
            json={"name": "被篡改"}
        )
        assert edit_resp.status_code == 403

        # 用户B不能删除
        delete_resp = client.delete(
            f"/api/addresses/{addr_id}",
            headers={"X-OpenId": "addr_user_b"}
        )
        assert delete_resp.status_code == 403


class TestOrderCancelFlow:
    """订单取消流程测试。"""

    def test_user_can_cancel_pending_order(self, client):
        """测试用户可以取消待处理订单。"""
        # 登录并创建订单
        client.post("/api/login", headers={"X-OpenId": "cancel_user_001"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "cancel_user_001"},
            json={"city": "广州", "itemType": "LUGGAGE", "warehouseId": "wh_gz_central"}
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 取消订单
        cancel_response = client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "cancel_user_001"},
            json={
                "newStatus": "CANCELLED",
                "operatorType": "USER",
                "reason": "用户主动取消"
            }
        )
        assert cancel_response.status_code == 200
        assert cancel_response.get_json()["data"]["status"] == "CANCELLED"

    def test_cannot_cancel_stored_order(self, client):
        """测试不能取消已入库订单。"""
        # 登录并创建订单
        client.post("/api/login", headers={"X-OpenId": "cancel_user_002"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "cancel_user_002"},
            json={"city": "深圳", "itemType": "PACKAGE", "warehouseId": "wh_sz_central"}
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 将订单状态更新为 STORED
        client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={"newStatus": "COLLECTED", "operatorType": "ADMIN"}
        )
        client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={"newStatus": "TRANSIT", "operatorType": "ADMIN"}
        )
        client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={"newStatus": "STORED", "operatorType": "ADMIN"}
        )

        # 尝试取消已入库订单应失败
        cancel_response = client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "cancel_user_002"},
            json={
                "newStatus": "CANCELLED",
                "operatorType": "USER"
            }
        )
        assert cancel_response.status_code == 400


class TestExceptionHandling:
    """异常处理流程测试。"""

    def test_exception_status_and_recovery(self, client):
        """测试异常状态及恢复。"""
        # 登录并创建订单
        client.post("/api/login", headers={"X-OpenId": "exc_user_001"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "exc_user_001"},
            json={"city": "成都", "itemType": "LUGGAGE", "warehouseId": "wh_cd_central"}
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 状态流转到 COLLECTED
        client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={"newStatus": "COLLECTED", "operatorType": "ADMIN"}
        )

        # 标记为异常
        client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={"newStatus": "EXCEPTION", "operatorType": "ADMIN", "reason": "物品损坏"}
        )

        # 验证异常状态
        detail_resp = client.get(
            f"/api/orders/{order_id}",
            headers={"X-OpenId": "exc_user_001"}
        )
        assert detail_resp.get_json()["data"]["status"] == "EXCEPTION"

        # 从异常恢复到 COMPLETED
        client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={"newStatus": "COMPLETED", "operatorType": "ADMIN"}
        )

        # 验证终态
        final_resp = client.get(
            f"/api/orders/{order_id}",
            headers={"X-OpenId": "exc_user_001"}
        )
        assert final_resp.get_json()["data"]["status"] == "COMPLETED"


class TestWarehouseOperations:
    """仓库操作测试。"""

    def test_get_warehouses_by_city(self, client):
        """测试按城市获取仓库。"""
        # 登录
        client.post("/api/login", headers={"X-OpenId": "wh_user_001"})

        # 获取北京的仓库
        response = client.get(
            "/api/warehouses?city=北京",
            headers={"X-OpenId": "wh_user_001"}
        )
        assert response.status_code == 200
        data = response.get_json()["data"]
        assert isinstance(data, list)
        # 如果有数据，验证城市
        if data:
            assert all(w["city"] == "北京" for w in data)

    def test_warehouse_list_excludes_inactive(self, client):
        """测试仓库列表排除停用状态。"""
        client.post("/api/login", headers={"X-OpenId": "wh_user_002"})

        response = client.get(
            "/api/warehouses",
            headers={"X-OpenId": "wh_user_002"}
        )
        assert response.status_code == 200
        data = response.get_json()["data"]
        # 验证所有仓库都是 ACTIVE 状态
        if isinstance(data, list):
            for wh in data:
                assert wh.get("status") != "INACTIVE"


class TestPaymentFlow:
    """支付流程集成测试。"""

    def test_complete_payment_flow(self, client):
        """测试完整支付流程。"""
        # 登录并创建订单
        client.post("/api/login", headers={"X-OpenId": "pay_user_001"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "pay_user_001"},
            json={"city": "北京", "itemType": "LUGGAGE", "warehouseId": "wh_bj_central"}
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 1. 创建支付单
        payment_response = client.post(
            f"/api/orders/{order_id}/payment",
            headers={"X-OpenId": "pay_user_001"},
            json={
                "amount": {
                    "storageFee": 100,
                    "deliveryFee": 50,
                    "totalFee": 150
                }
            }
        )
        assert payment_response.status_code == 201
        payment_data = payment_response.get_json()["data"]
        payment_id = payment_data["_id"]
        assert payment_data["orderId"] == order_id
        assert payment_data["status"] == "PENDING"

        # 2. 查询支付状态（待支付）
        status_response = client.get(
            f"/api/orders/{order_id}/payment/status",
            headers={"X-OpenId": "pay_user_001"}
        )
        status_data = status_response.get_json()["data"]
        assert status_data["isPaid"] is False

        # 3. 执行支付
        pay_response = client.post(
            f"/api/orders/{order_id}/pay",
            headers={"X-OpenId": "pay_user_001"},
            json={"paymentId": payment_id, "paymentMethod": "WECHAT"}
        )
        assert pay_response.status_code == 200
        pay_data = pay_response.get_json()["data"]
        assert pay_data["status"] == "SUCCESS"
        assert "transactionId" in pay_data

        # 4. 查询支付状态（已支付）
        status_response = client.get(
            f"/api/orders/{order_id}/payment/status",
            headers={"X-OpenId": "pay_user_001"}
        )
        status_data = status_response.get_json()["data"]
        assert status_data["isPaid"] is True

    def test_reject_double_payment(self, client):
        """测试重复支付被拒绝。"""
        # 登录并创建订单
        client.post("/api/login", headers={"X-OpenId": "pay_user_002"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "pay_user_002"},
            json={"city": "上海", "itemType": "PACKAGE", "warehouseId": "wh_sh_central"}
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 创建并完成支付
        payment_response = client.post(
            f"/api/orders/{order_id}/payment",
            headers={"X-OpenId": "pay_user_002"},
            json={"amount": {"totalFee": 100}}
        )
        payment_id = payment_response.get_json()["data"]["_id"]
        client.post(
            f"/api/orders/{order_id}/pay",
            headers={"X-OpenId": "pay_user_002"},
            json={"paymentId": payment_id, "paymentMethod": "WECHAT"}
        )

        # 再次支付应失败
        second_pay = client.post(
            f"/api/orders/{order_id}/pay",
            headers={"X-OpenId": "pay_user_002"},
            json={"paymentId": payment_id, "paymentMethod": "WECHAT"}
        )
        assert second_pay.status_code == 400


class TestAddressManagement:
    """地址管理集成测试。"""

    def test_create_and_manage_addresses(self, client):
        """测试创建和管理地址。"""
        # 登录
        client.post("/api/login", headers={"X-OpenId": "addr_user_001"})

        # 1. 创建第一个地址（设为默认）
        resp1 = client.post(
            "/api/addresses",
            headers={"X-OpenId": "addr_user_001"},
            json={
                "name": "家",
                "phone": "13800138001",
                "province": "北京市",
                "city": "北京市",
                "district": "朝阳区",
                "detail": "XX路XX号",
                "isDefault": True
            }
        )
        assert resp1.status_code == 201
        addr1_id = resp1.get_json()["data"]["_id"]

        # 2. 创建第二个地址
        resp2 = client.post(
            "/api/addresses",
            headers={"X-OpenId": "addr_user_001"},
            json={
                "name": "公司",
                "phone": "13800138002",
                "province": "北京市",
                "city": "北京市",
                "district": "海淀区",
                "detail": "YY路YY号"
            }
        )
        assert resp2.status_code == 201
        addr2_id = resp2.get_json()["data"]["_id"]

        # 3. 获取默认地址
        default_resp = client.get(
            "/api/addresses/default",
            headers={"X-OpenId": "addr_user_001"}
        )
        assert default_resp.get_json()["data"]["name"] == "家"

        # 4. 设置公司为默认
        set_default_resp = client.post(
            f"/api/addresses/{addr2_id}/default",
            headers={"X-OpenId": "addr_user_001"}
        )
        assert set_default_resp.get_json()["data"]["isDefault"] is True

        # 5. 验证原来的默认已被取消
        addr1_resp = client.get(
            f"/api/addresses/{addr1_id}",
            headers={"X-OpenId": "addr_user_001"}
        )
        assert addr1_resp.get_json()["data"]["isDefault"] is False

    def test_address_max_limit(self, client):
        """测试地址数量上限。"""
        client.post("/api/login", headers={"X-OpenId": "addr_user_002"})

        # 创建10个地址应该成功
        for i in range(10):
            resp = client.post(
                "/api/addresses",
                headers={"X-OpenId": "addr_user_002"},
                json={
                    "name": f"地址{i}",
                    "phone": f"138{str(i).zfill(8)}",
                    "province": "省",
                    "city": "市",
                    "detail": f"详情{i}"
                }
            )
            assert resp.status_code == 201

        # 第11个应该失败
        resp = client.post(
            "/api/addresses",
            headers={"X-OpenId": "addr_user_002"},
            json={
                "name": "超限",
                "phone": "13800139111",
                "province": "省",
                "city": "市",
                "detail": "超限详情"
            }
        )
        assert resp.status_code == 400

    def test_address_permission_isolation(self, client):
        """测试地址权限隔离。"""
        # 用户A创建地址
        client.post("/api/login", headers={"X-OpenId": "addr_user_a"})
        resp = client.post(
            "/api/addresses",
            headers={"X-OpenId": "addr_user_a"},
            json={"name": "用户A地址", "phone": "13800138010", "province": "A", "city": "A", "detail": "a"}
        )
        addr_id = resp.get_json()["data"]["_id"]

        # 用户B不能访问
        client.post("/api/login", headers={"X-OpenId": "addr_user_b"})
        access_resp = client.get(
            f"/api/addresses/{addr_id}",
            headers={"X-OpenId": "addr_user_b"}
        )
        assert access_resp.status_code == 403

        # 用户B不能编辑
        edit_resp = client.patch(
            f"/api/addresses/{addr_id}",
            headers={"X-OpenId": "addr_user_b"},
            json={"name": "被篡改"}
        )
        assert edit_resp.status_code == 403

        # 用户B不能删除
        delete_resp = client.delete(
            f"/api/addresses/{addr_id}",
            headers={"X-OpenId": "addr_user_b"}
        )
        assert delete_resp.status_code == 403


class TestOrderCancelFlow:
    """订单取消流程测试。"""

    def test_user_can_cancel_pending_order(self, client):
        """测试用户可以取消待处理订单。"""
        # 登录并创建订单
        client.post("/api/login", headers={"X-OpenId": "cancel_user_001"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "cancel_user_001"},
            json={"city": "广州", "itemType": "LUGGAGE", "warehouseId": "wh_gz_central"}
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 取消订单
        cancel_response = client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "cancel_user_001"},
            json={
                "newStatus": "CANCELLED",
                "operatorType": "USER",
                "reason": "用户主动取消"
            }
        )
        assert cancel_response.status_code == 200
        assert cancel_response.get_json()["data"]["status"] == "CANCELLED"

    def test_cannot_cancel_stored_order(self, client):
        """测试不能取消已入库订单。"""
        # 登录并创建订单
        client.post("/api/login", headers={"X-OpenId": "cancel_user_002"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "cancel_user_002"},
            json={"city": "深圳", "itemType": "PACKAGE", "warehouseId": "wh_sz_central"}
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 将订单状态更新为 STORED
        client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={"newStatus": "COLLECTED", "operatorType": "ADMIN"}
        )
        client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={"newStatus": "TRANSIT", "operatorType": "ADMIN"}
        )
        client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={"newStatus": "STORED", "operatorType": "ADMIN"}
        )

        # 尝试取消已入库订单应失败
        cancel_response = client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "cancel_user_002"},
            json={
                "newStatus": "CANCELLED",
                "operatorType": "USER"
            }
        )
        assert cancel_response.status_code == 400


class TestExceptionHandling:
    """异常处理流程测试。"""

    def test_exception_status_and_recovery(self, client):
        """测试异常状态及恢复。"""
        # 登录并创建订单
        client.post("/api/login", headers={"X-OpenId": "exc_user_001"})
        create_response = client.post(
            "/api/orders",
            headers={"X-OpenId": "exc_user_001"},
            json={"city": "成都", "itemType": "LUGGAGE", "warehouseId": "wh_cd_central"}
        )
        order_id = create_response.get_json()["data"]["_id"]

        # 状态流转到 COLLECTED
        client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={"newStatus": "COLLECTED", "operatorType": "ADMIN"}
        )

        # 标记为异常
        client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={"newStatus": "EXCEPTION", "operatorType": "ADMIN", "reason": "物品损坏"}
        )

        # 验证异常状态
        detail_resp = client.get(
            f"/api/orders/{order_id}",
            headers={"X-OpenId": "exc_user_001"}
        )
        assert detail_resp.get_json()["data"]["status"] == "EXCEPTION"

        # 从异常恢复到 COMPLETED
        client.patch(
            f"/api/orders/{order_id}/status",
            headers={"X-OpenId": "admin"},
            json={"newStatus": "COMPLETED", "operatorType": "ADMIN"}
        )

        # 验证终态
        final_resp = client.get(
            f"/api/orders/{order_id}",
            headers={"X-OpenId": "exc_user_001"}
        )
        assert final_resp.get_json()["data"]["status"] == "COMPLETED"


class TestWarehouseOperations:
    """仓库操作测试。"""

    def test_get_warehouses_by_city(self, client):
        """测试按城市获取仓库。"""
        # 登录
        client.post("/api/login", headers={"X-OpenId": "wh_user_001"})

        # 获取北京的仓库
        response = client.get(
            "/api/warehouses?city=北京",
            headers={"X-OpenId": "wh_user_001"}
        )
        assert response.status_code == 200
        data = response.get_json()["data"]
        assert isinstance(data, list)
        # 如果有数据，验证城市
        if data:
            assert all(w["city"] == "北京" for w in data)

    def test_warehouse_list_excludes_inactive(self, client):
        """测试仓库列表排除停用状态。"""
        client.post("/api/login", headers={"X-OpenId": "wh_user_002"})

        response = client.get(
            "/api/warehouses",
            headers={"X-OpenId": "wh_user_002"}
        )
        assert response.status_code == 200
        data = response.get_json()["data"]
        # 验证所有仓库都是 ACTIVE 状态
        if isinstance(data, list):
            for wh in data:
                assert wh.get("status") != "INACTIVE"
