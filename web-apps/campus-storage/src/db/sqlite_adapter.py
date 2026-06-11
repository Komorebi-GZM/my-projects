"""SQLite 适配器。"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.db.adapter import DBAdapter


class SQLiteAdapter(DBAdapter):
    """SQLite 数据库适配器。"""

    TABLE_MAP = {
        "users": "users",
        "orders": "orders",
        "warehouses": "warehouses",
        "tickets": "tickets",
        "addresses": "addresses",
    }

    FIELD_MAP = {
        "users": {
            "_id": "id",
            "_openid": "openid",
            "_version": "version",
            "nickName": "nick_name",
            "avatarUrl": "avatar_url",
            "createTime": "create_time",
            "updateTime": "update_time",
        },
        "orders": {
            "_id": "id",
            "_openid": "openid",
            "_version": "version",
            "orderNo": "order_no",
            "isPaid": "is_paid",
            "userId": "user_id",
            "warehouseId": "warehouse_id",
            "warehouseName": "warehouse_name",
            "itemType": "item_type",
            "volume": "volume",
            "estimatedWeight": "estimated_weight",
            "serviceType": "service_type",
            "storageDays": "storage_days",
            "deliveryAddress": "delivery_address",
            "deliveryTime": "delivery_time",
            "declaredValue": "declared_value",
            "storagePhotoUrl": "storage_photo_url",
            "statusHistory": "status_history",
            "createTime": "create_time",
            "updateTime": "update_time",
        },
        "warehouses": {
            "_id": "id",
            "usedCapacity": "used_capacity",
            "createTime": "create_time",
        },
        "tickets": {
            "_id": "id",
            "orderId": "order_id",
            "userId": "user_id",
            "imageUrl": "image_url",
            "createTime": "create_time",
        },
        "addresses": {
            "_id": "id",
            "userId": "user_id",
            "isDefault": "is_default",
            "createTime": "create_time",
            "updateTime": "update_time",
        },
    }

    def __init__(self, db_path: str | Path = "data/dev.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self._in_transaction = False

    def _get_connection(self) -> sqlite3.Connection:
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys=ON;")
        return self.conn

    def _to_snake_fields(self, collection: str, doc: Dict[str, Any]) -> Dict[str, Any]:
        """将驼峰字段转换为下划线字段。"""
        field_map = self.FIELD_MAP.get(collection, {})
        result = {}
        for k, v in doc.items():
            # 跳过值为 None 的字段（让数据库或默认值处理）
            if v is None:
                continue
            snake_key = field_map.get(k, k)
            if isinstance(v, (dict, list)):
                result[snake_key] = json.dumps(v, ensure_ascii=False)
            elif isinstance(v, bool):
                result[snake_key] = 1 if v else 0
            else:
                result[snake_key] = v
        return result

    def _to_camel_fields(self, collection: str, row: sqlite3.Row) -> Dict[str, Any]:
        """将下划线字段转换为驼峰字段。"""
        field_map_rev = {v: k for k, v in self.FIELD_MAP.get(collection, {}).items()}
        result = {}
        for k, v in dict(row).items():
            camel_key = field_map_rev.get(k, k)
            if k in ("amount", "status_history"):
                result[camel_key] = json.loads(v) if v else ({} if k == "amount" else [])
            elif k == "is_paid":
                result[camel_key] = bool(v)
            elif k == "is_default":
                result[camel_key] = bool(v)
            else:
                result[camel_key] = v
        return result

    def insert(self, collection: str, doc: Dict[str, Any]) -> str:
        table = self.TABLE_MAP.get(collection, collection)
        snake_doc = self._to_snake_fields(collection, doc)

        now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        snake_doc.setdefault("create_time", now)
        snake_doc.setdefault("update_time", now)
        snake_doc.setdefault("version", 1)

        # 优先使用 doc 中提供的 _id（如果存在且不为 None）
        if "id" not in snake_doc and "_id" in doc and doc["_id"] is not None:
            snake_doc["id"] = doc["_id"]
        if "id" not in snake_doc:
            import uuid
            snake_doc["id"] = str(uuid.uuid4())

        conn = self._get_connection()
        placeholders = ", ".join(["?"] * len(snake_doc))
        columns = ", ".join(snake_doc.keys())
        values = list(snake_doc.values())

        conn.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
        if not self._in_transaction:
            conn.commit()
        return snake_doc["id"]

    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        table = self.TABLE_MAP.get(collection, collection)
        snake_query = self._to_snake_fields(collection, query)

        where_clauses = []
        params = []
        for k, v in snake_query.items():
            if v is None:
                where_clauses.append(f"{k} IS NULL")
            else:
                where_clauses.append(f"{k} = ?")
                params.append(v)

        sql = f"SELECT * FROM {table}"
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        conn = self._get_connection()
        row = conn.execute(sql, params).fetchone()
        if row is None:
            return None
        return self._to_camel_fields(collection, row)

    def find_many(
        self,
        collection: str,
        query: Dict[str, Any],
        sort: Optional[List[tuple]] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        table = self.TABLE_MAP.get(collection, collection)
        snake_query = self._to_snake_fields(collection, query)

        where_clauses = []
        params = []
        for k, v in snake_query.items():
            if v is None:
                where_clauses.append(f"{k} IS NULL")
            else:
                where_clauses.append(f"{k} = ?")
                params.append(v)

        sql = f"SELECT * FROM {table}"
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        if sort:
            order_clauses = []
            for field, direction in sort:
                snake_field = self.FIELD_MAP.get(collection, {}).get(field, field)
                dir_str = "DESC" if direction == -1 else "ASC"
                order_clauses.append(f"{snake_field} {dir_str}")
            sql += " ORDER BY " + ", ".join(order_clauses)

        sql += " LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        conn = self._get_connection()
        rows = conn.execute(sql, params).fetchall()
        return [self._to_camel_fields(collection, row) for row in rows]

    def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any], version: Optional[int] = None) -> bool:
        """更新单个文档。

        Args:
            collection: 集合名称
            query: 查询条件
            update: 更新字段
            version: 可选的版本号，用于乐观锁校验

        Returns:
            bool: 更新成功返回 True，版本不匹配或记录不存在返回 False
        """
        table = self.TABLE_MAP.get(collection, collection)
        snake_query = self._to_snake_fields(collection, query)
        snake_update = self._to_snake_fields(collection, update)

        now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        snake_update["update_time"] = now
        # 乐观锁：版本号自动 +1（仅在提供 version 参数时）
        if version is not None:
            snake_update["version"] = version + 1

        # 构建 SET 子句
        set_clauses = ", ".join([f"{k} = ?" for k in snake_update.keys()])
        where_clauses = []
        params = list(snake_update.values())

        for k, v in snake_query.items():
            where_clauses.append(f"{k} = ?")
            params.append(v)

        # 乐观锁：如果提供了 version，添加版本校验
        if version is not None:
            where_clauses.append("version = ?")
            params.append(version)

        sql = f"UPDATE {table} SET {set_clauses} WHERE " + " AND ".join(where_clauses)

        conn = self._get_connection()
        cursor = conn.execute(sql, params)
        if not self._in_transaction:
            conn.commit()
        return cursor.rowcount > 0

    def count(self, collection: str, query: Dict[str, Any]) -> int:
        table = self.TABLE_MAP.get(collection, collection)
        snake_query = self._to_snake_fields(collection, query)

        where_clauses = []
        params = []
        for k, v in snake_query.items():
            if v is None:
                where_clauses.append(f"{k} IS NULL")
            else:
                where_clauses.append(f"{k} = ?")
                params.append(v)

        sql = f"SELECT COUNT(*) FROM {table}"
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        conn = self._get_connection()
        return conn.execute(sql, params).fetchone()[0]

    def begin_transaction(self):
        self._in_transaction = True
        self._get_connection().execute("BEGIN")

    def commit(self):
        if self.conn and self._in_transaction:
            self.conn.commit()
            self._in_transaction = False

    def rollback(self):
        if self.conn and self._in_transaction:
            self.conn.rollback()
            self._in_transaction = False

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
