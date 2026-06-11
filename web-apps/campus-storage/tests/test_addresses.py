"""地址服务单元测试。"""

import pytest
from pathlib import Path

from src.core.address_service import (
    AddressService,
    AddressError,
    AddressNotFoundError,
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


@pytest.fixture
def service(db: SQLiteAdapter):
    """地址服务实例。"""
    return AddressService(db)


def _create_test_address(service, user_id="user_001", **kwargs):
    """创建测试地址的辅助函数。"""
    defaults = {
        "name": "张三",
        "phone": "13800138000",
        "province": "北京市",
        "city": "北京市",
        "district": "朝阳区",
        "detail": "XX路88号",
    }
    defaults.update(kwargs)
    return service.create_address(user_id=user_id, **defaults)


# ========== create_address 测试 ==========

def test_create_address_success(db: SQLiteAdapter, init_tables, service):
    """测试创建地址成功。"""
    address = _create_test_address(service)
    assert address["_id"].startswith("addr_")
    assert address["name"] == "张三"
    assert address["phone"] == "13800138000"
    assert address["isDefault"] is False


def test_create_address_with_default(db: SQLiteAdapter, init_tables, service):
    """测试创建默认地址。"""
    address = _create_test_address(service, is_default=True)
    assert address["isDefault"] is True


def test_create_address_missing_required_fields(db: SQLiteAdapter, init_tables, service):
    """测试缺少必填字段。"""
    with pytest.raises(AddressError) as exc_info:
        service.create_address(
            user_id="user_001", name=None, phone="13800138000",
            province="北京市", city="北京市", district="朝阳区", detail="XX路88号",
        )
    assert exc_info.value.code == ErrorCode.PARAM_ERROR


def test_create_address_invalid_phone(db: SQLiteAdapter, init_tables, service):
    """测试无效手机号。"""
    with pytest.raises(AddressError) as exc_info:
        _create_test_address(service, phone="123")
    assert "手机号格式不正确" in exc_info.value.message


def test_create_address_max_limit(db: SQLiteAdapter, init_tables, service):
    """测试地址数量上限。"""
    for i in range(10):
        _create_test_address(service, name=f"用户{i}", detail=f"地址{i}")
    with pytest.raises(AddressError) as exc_info:
        _create_test_address(service, name="用户11", detail="地址11")
    assert "地址数量已达上限" in exc_info.value.message


def test_create_address_multiple_defaults(db: SQLiteAdapter, init_tables, service):
    """测试多个默认地址只有最后一个生效。"""
    addr1 = _create_test_address(service, is_default=True)
    addr2 = _create_test_address(service, name="李四", phone="13900139000", is_default=True)
    addr1_updated = service.get_address(addr1["_id"], "user_001")
    addr2_updated = service.get_address(addr2["_id"], "user_001")
    assert addr1_updated["isDefault"] is False
    assert addr2_updated["isDefault"] is True


# ========== get_addresses 测试 ==========

def test_get_addresses(db: SQLiteAdapter, init_tables, service):
    """测试获取地址列表。"""
    for i in range(3):
        _create_test_address(service, name=f"用户{i}", detail=f"地址{i}")
    addresses = service.get_addresses("user_001")
    assert len(addresses) == 3


def test_get_addresses_empty(db: SQLiteAdapter, init_tables, service):
    """测试无地址时返回空列表。"""
    addresses = service.get_addresses("user_001")
    assert addresses == []


def test_get_addresses_different_users(db: SQLiteAdapter, init_tables, service):
    """测试不同用户地址隔离。"""
    _create_test_address(service, user_id="user_001")
    _create_test_address(service, user_id="user_002", name="用户2")
    user1_addresses = service.get_addresses("user_001")
    user2_addresses = service.get_addresses("user_002")
    assert len(user1_addresses) == 1
    assert len(user2_addresses) == 1


# ========== get_address 测试 ==========

def test_get_address_success(db: SQLiteAdapter, init_tables, service):
    """测试获取单个地址成功。"""
    created = _create_test_address(service)
    address = service.get_address(created["_id"], "user_001")
    assert address["_id"] == created["_id"]
    assert address["name"] == "张三"


def test_get_address_not_found(db: SQLiteAdapter, init_tables, service):
    """测试地址不存在。"""
    with pytest.raises(AddressNotFoundError):
        service.get_address("nonexistent", "user_001")


def test_get_address_permission_denied(db: SQLiteAdapter, init_tables, service):
    """测试无权访问他人地址。"""
    address = _create_test_address(service)
    with pytest.raises(AddressError) as exc_info:
        service.get_address(address["_id"], "user_002")
    assert exc_info.value.code == ErrorCode.FORBIDDEN


# ========== update_address 测试 ==========

def test_update_address_success(db: SQLiteAdapter, init_tables, service):
    """测试更新地址成功。"""
    address = _create_test_address(service)
    updated = service.update_address(address["_id"], "user_001", {"name": "李四", "detail": "新地址"})
    assert updated["name"] == "李四"
    assert updated["detail"] == "新地址"


def test_update_address_permission_denied(db: SQLiteAdapter, init_tables, service):
    """测试无权更新他人地址。"""
    address = _create_test_address(service)
    with pytest.raises(AddressError):
        service.update_address(address["_id"], "user_002", {"name": "黑客"})


def test_update_address_not_found(db: SQLiteAdapter, init_tables, service):
    """测试更新不存在的地址。"""
    with pytest.raises(AddressNotFoundError):
        service.update_address("nonexistent", "user_001", {"name": "测试"})


# ========== delete_address 测试 ==========

def test_delete_address_success(db: SQLiteAdapter, init_tables, service):
    """测试删除地址成功。"""
    address = _create_test_address(service)
    result = service.delete_address(address["_id"], "user_001")
    assert result is True
    addresses = service.get_addresses("user_001")
    assert len(addresses) == 0


def test_delete_default_address_auto_replace(db: SQLiteAdapter, init_tables, service):
    """测试删除默认地址后自动设置新默认。"""
    addr1 = _create_test_address(service, is_default=True)
    addr2 = _create_test_address(service, name="用户2", phone="13900139000")
    service.delete_address(addr1["_id"], "user_001")
    addr2_updated = service.get_address(addr2["_id"], "user_001")
    assert addr2_updated["isDefault"] is True


def test_delete_address_permission_denied(db: SQLiteAdapter, init_tables, service):
    """测试无权删除他人地址。"""
    address = _create_test_address(service)
    with pytest.raises(AddressError):
        service.delete_address(address["_id"], "user_002")


# ========== set_default_address 测试 ==========

def test_set_default_address_success(db: SQLiteAdapter, init_tables, service):
    """测试设置默认地址。"""
    addr1 = _create_test_address(service, is_default=True)
    addr2 = _create_test_address(service, name="用户2", phone="13900139000")
    service.set_default_address(addr2["_id"], "user_001")
    addr1_updated = service.get_address(addr1["_id"], "user_001")
    addr2_updated = service.get_address(addr2["_id"], "user_001")
    assert addr1_updated["isDefault"] is False
    assert addr2_updated["isDefault"] is True


# ========== get_default_address 测试 ==========

def test_get_default_address(db: SQLiteAdapter, init_tables, service):
    """测试获取默认地址。"""
    address = _create_test_address(service, is_default=True)
    default = service.get_default_address("user_001")
    assert default["_id"] == address["_id"]


def test_get_default_address_none(db: SQLiteAdapter, init_tables, service):
    """测试无默认地址时返回 None。"""
    _create_test_address(service)
    default = service.get_default_address("user_001")
    assert default is None
