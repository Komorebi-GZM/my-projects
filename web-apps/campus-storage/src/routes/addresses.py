"""地址相关路由。"""

from flask import Blueprint, request, jsonify

from src.common.auth import get_current_user_id
from src.common.errors import success_response, error_response, ErrorCode
from src.core.address_service import AddressService, AddressError, AddressNotFoundError
from src.db.factory import get_db_adapter

addresses_bp = Blueprint("user_addresses", __name__, url_prefix="/api")


@addresses_bp.route("/addresses", methods=["GET"])
def get_addresses():
    """获取用户所有地址。

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": [...]
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        db = get_db_adapter()
        service = AddressService(db)
        addresses = service.get_addresses(user_id)

        return success_response(addresses)

    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500


@addresses_bp.route("/addresses", methods=["POST"])
def create_address():
    """创建配送地址。

    Request Body:
        {
            "name": "张三",
            "phone": "13800138000",
            "province": "北京市",
            "city": "北京市",
            "district": "朝阳区",
            "detail": "XX路XX号XX栋XX室",
            "tag": "家",
            "isDefault": true
        }

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": {...}
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        data = request.get_json()
        if not data:
            return error_response(ErrorCode.PARAM_ERROR, "请求体不能为空"), 400

        db = get_db_adapter()
        service = AddressService(db)

        address = service.create_address(
            user_id=user_id,
            name=data.get("name"),
            phone=data.get("phone"),
            province=data.get("province"),
            city=data.get("city"),
            district=data.get("district", ""),
            detail=data.get("detail"),
            tag=data.get("tag", ""),
            is_default=data.get("isDefault", False),
        )

        return success_response(address), 201

    except AddressError as e:
        return error_response(e.code, e.message), 400
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500


@addresses_bp.route("/addresses/<address_id>", methods=["GET"])
def get_address_detail(address_id):
    """获取地址详情。

    Path Parameters:
        address_id: 地址ID

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": {...}
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        db = get_db_adapter()
        service = AddressService(db)

        address = service.get_address(address_id, user_id)
        return success_response(address)

    except AddressNotFoundError as e:
        return error_response(e.code, e.message), 404
    except AddressError as e:
        if e.code == ErrorCode.FORBIDDEN:
            return error_response(e.code, e.message), 403
        return error_response(e.code, e.message), 400
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500


@addresses_bp.route("/addresses/<address_id>", methods=["PUT", "PATCH"])
def update_address(address_id):
    """更新地址。

    Path Parameters:
        address_id: 地址ID

    Request Body:
        {
            "name": "李四",
            "phone": "13900139000",
            "detail": "新地址..."
        }

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": {...}
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        data = request.get_json() or {}

        db = get_db_adapter()
        service = AddressService(db)

        address = service.update_address(address_id, user_id, data)
        return success_response(address)

    except AddressNotFoundError as e:
        return error_response(e.code, e.message), 404
    except AddressError as e:
        if e.code == ErrorCode.FORBIDDEN:
            return error_response(e.code, e.message), 403
        return error_response(e.code, e.message), 400
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500


@addresses_bp.route("/addresses/<address_id>", methods=["DELETE"])
def delete_address(address_id):
    """删除地址。

    Path Parameters:
        address_id: 地址ID

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": null
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        db = get_db_adapter()
        service = AddressService(db)

        service.delete_address(address_id, user_id)
        return success_response(None)

    except AddressNotFoundError as e:
        return error_response(e.code, e.message), 404
    except AddressError as e:
        if e.code == ErrorCode.FORBIDDEN:
            return error_response(e.code, e.message), 403
        return error_response(e.code, e.message), 400
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500


@addresses_bp.route("/addresses/<address_id>/default", methods=["POST"])
def set_default_address(address_id):
    """设置默认地址。

    Path Parameters:
        address_id: 地址ID

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": {...}
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        db = get_db_adapter()
        service = AddressService(db)

        address = service.set_default_address(address_id, user_id)
        return success_response(address)

    except AddressNotFoundError as e:
        return error_response(e.code, e.message), 404
    except AddressError as e:
        if e.code == ErrorCode.FORBIDDEN:
            return error_response(e.code, e.message), 403
        return error_response(e.code, e.message), 400
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500


@addresses_bp.route("/addresses/default", methods=["GET"])
def get_default_address():
    """获取默认地址。

    Returns:
        {
            "code": 0,
            "message": "success",
            "data": {...} | null
        }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return error_response(ErrorCode.UNAUTHORIZED, "用户未登录"), 401

        db = get_db_adapter()
        service = AddressService(db)

        address = service.get_default_address(user_id)
        return success_response(address)

    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e)), 500
