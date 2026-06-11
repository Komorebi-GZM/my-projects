"""地址服务模块。

用户配送地址管理：增删改查、默认地址设置。
"""

import uuid
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from src.db.adapter import DBAdapter
from src.common.errors import ErrorCode
from src.common.validator import validate_required, ValidationError


@dataclass
class AddressError(Exception):
    """地址操作错误。"""
    code: int = ErrorCode.PARAM_ERROR
    message: str = "地址操作失败"


@dataclass
class AddressNotFoundError(Exception):
    """地址不存在。"""
    code: int = ErrorCode.NOT_FOUND
    message: str = "地址不存在"


class AddressService:
    """地址服务。"""

    MAX_ADDRESSES_PER_USER = 10  # 每个用户最多10个地址

    def __init__(self, db: DBAdapter):
        self.db = db

    def create_address(
        self,
        user_id: str,
        name: str,
        phone: str,
        province: str,
        city: str,
        district: str,
        detail: str,
        tag: str = "",
        is_default: bool = False,
    ) -> Dict[str, Any]:
        """创建配送地址。

        Args:
            user_id: 用户ID
            name: 收货人姓名
            phone: 联系电话
            province: 省份
            city: 城市
            district: 区/县
            detail: 详细地址
            tag: 标签（家/学校/公司等）
            is_default: 是否设为默认地址

        Returns:
            创建的地址

        Raises:
            AddressError: 参数校验失败或地址数量超限
        """
        # 参数校验
        try:
            validate_required(name, "name")
            validate_required(phone, "phone")
            validate_required(province, "province")
            validate_required(city, "city")
            validate_required(detail, "detail")
        except ValidationError as e:
            raise AddressError(code=ErrorCode.PARAM_ERROR, message=e.message)

        # 手机号格式校验（简单校验）
        if not phone.isdigit() or len(phone) < 7:
            raise AddressError(code=ErrorCode.PARAM_ERROR, message="手机号格式不正确")

        # 检查地址数量限制
        current_count = self.db.count("addresses", {"userId": user_id, "status": "ACTIVE"})
        if current_count >= self.MAX_ADDRESSES_PER_USER:
            raise AddressError(
                code=ErrorCode.PARAM_ERROR,
                message=f"地址数量已达上限（{self.MAX_ADDRESSES_PER_USER}个）"
            )

        # 如果设为默认，先取消其他默认
        if is_default:
            self._clear_default_addresses(user_id)

        # 构建地址数据
        address = {
            "_id": f"addr_{uuid.uuid4().hex[:10]}",
            "userId": user_id,
            "name": name,
            "phone": phone,
            "province": province,
            "city": city,
            "district": district,
            "detail": detail,
            "tag": tag,
            "isDefault": is_default,
            "status": "ACTIVE",
        }

        doc_id = self.db.insert("addresses", address)
        address["_id"] = doc_id

        return address

    def get_addresses(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户所有地址。

        Args:
            user_id: 用户ID

        Returns:
            地址列表（按默认地址优先、创建时间倒序）
        """
        addresses = self.db.find_many(
            "addresses",
            {"userId": user_id, "status": "ACTIVE"},
            sort=[("isDefault", -1), ("createTime", -1)],
            limit=100,
        )
        return addresses

    def get_address(self, address_id: str, user_id: str) -> Dict[str, Any]:
        """获取单个地址。

        Args:
            address_id: 地址ID
            user_id: 当前用户ID

        Returns:
            地址详情

        Raises:
            AddressNotFoundError: 地址不存在或无权访问
        """
        address = self.db.find_one("addresses", {"_id": address_id})

        if not address or address.get("status") != "ACTIVE":
            raise AddressNotFoundError(code=ErrorCode.NOT_FOUND, message="地址不存在")

        if address.get("userId") != user_id:
            raise AddressError(code=ErrorCode.FORBIDDEN, message="无权访问该地址")

        return address

    def update_address(
        self,
        address_id: str,
        user_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """更新地址。

        Args:
            address_id: 地址ID
            user_id: 当前用户ID
            updates: 更新字段

        Returns:
            更新后的地址

        Raises:
            AddressNotFoundError: 地址不存在
            AddressError: 无权操作
        """
        # 校验地址归属
        address = self.get_address(address_id, user_id)

        # 不允许通过此方法更新 status
        if "status" in updates:
            raise AddressError(code=ErrorCode.PARAM_ERROR, message="不允许修改状态字段")

        # 如果设为默认，先取消其他默认
        if updates.get("isDefault"):
            self._clear_default_addresses(user_id)

        # 过滤有效字段
        allowed_fields = {"name", "phone", "province", "city", "district", "detail", "tag", "isDefault"}
        filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}

        if not filtered_updates:
            return address

        # 手机号格式校验
        if "phone" in filtered_updates:
            phone = filtered_updates["phone"]
            if not phone.isdigit() or len(phone) < 7:
                raise AddressError(code=ErrorCode.PARAM_ERROR, message="手机号格式不正确")

        # 执行更新
        self.db.update_one(
            "addresses",
            {"_id": address_id},
            filtered_updates,
        )

        return self.db.find_one("addresses", {"_id": address_id})

    def delete_address(self, address_id: str, user_id: str) -> bool:
        """删除地址（软删除）。

        Args:
            address_id: 地址ID
            user_id: 当前用户ID

        Returns:
            是否删除成功

        Raises:
            AddressNotFoundError: 地址不存在
            AddressError: 无权操作
        """
        # 校验地址归属
        address = self.get_address(address_id, user_id)

        # 软删除
        self.db.update_one(
            "addresses",
            {"_id": address_id},
            {"status": "INACTIVE"},
        )

        # 如果删除的是默认地址，自动设置一个新的默认地址
        if address.get("isDefault"):
            remaining = self.db.find_many(
                "addresses",
                {"userId": user_id, "status": "ACTIVE"},
                limit=1,
            )
            if remaining:
                self.db.update_one(
                    "addresses",
                    {"_id": remaining[0]["_id"]},
                    {"isDefault": True},
                )

        return True

    def set_default_address(self, address_id: str, user_id: str) -> Dict[str, Any]:
        """设置默认地址。

        Args:
            address_id: 地址ID
            user_id: 当前用户ID

        Returns:
            更新后的地址

        Raises:
            AddressNotFoundError: 地址不存在
            AddressError: 无权操作
        """
        # 校验地址归属
        address = self.get_address(address_id, user_id)

        # 取消其他默认
        self._clear_default_addresses(user_id)

        # 设置新默认
        self.db.update_one(
            "addresses",
            {"_id": address_id},
            {"isDefault": True},
        )

        return self.db.find_one("addresses", {"_id": address_id})

    def get_default_address(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户默认地址。

        Args:
            user_id: 用户ID

        Returns:
            默认地址，不存在则返回 None
        """
        address = self.db.find_one("addresses", {"userId": user_id, "isDefault": True, "status": "ACTIVE"})
        return address

    def _clear_default_addresses(self, user_id: str) -> None:
        """清除用户的所有默认地址标记。"""
        addresses = self.db.find_many(
            "addresses",
            {"userId": user_id, "isDefault": True, "status": "ACTIVE"},
        )
        for addr in addresses:
            self.db.update_one(
                "addresses",
                {"_id": addr["_id"]},
                {"isDefault": False},
            )
