"""CloudBase 适配器 — 生产环境使用。

依赖: cloudbase (tencent cloud base python sdk)
安装: pip install cloudbase

参考: https://docs.cloudbase.net/api-reference/python/database
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from src.db.adapter import DBAdapter


class CloudBaseAdapter(DBAdapter):
    """CloudBase NoSQL 数据库适配器。"""

    def __init__(self, env_id: str):
        self.env_id = env_id
        self._db = None
        self._initialized = False

    def _ensure_initialized(self):
        """延迟初始化 CloudBase SDK。"""
        if self._initialized:
            return
        try:
            from cloudbase import initialize
            from cloudbase.database import Db
        except ImportError:
            raise RuntimeError(
                "CloudBase SDK 未安装，请执行: pip install cloudbase"
            )

        app = initialize({
            "env": self.env_id,
        })
        self._db = app.database()
        self._initialized = True

    def _collection(self, name: str):
        """获取集合引用。"""
        self._ensure_initialized()
        return self._db.collection(name)

    def _prepare_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """准备文档数据：规范化字段名。

        CloudBase NoSQL 使用驼峰命名，与我们的业务代码一致。
        """
        now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        result = dict(doc)
        result.setdefault("createTime", now)
        result.setdefault("updateTime", now)
        result.setdefault("version", 1)
        return result

    def insert(self, collection: str, doc: Dict[str, Any]) -> str:
        prepared = self._prepare_doc(doc)

        if "_id" in prepared and prepared["_id"] is not None:
            doc_id = prepared["_id"]
            # 指定 ID 写入
            self._collection(collection).doc(doc_id).set(prepared)
        else:
            # 自动生成 ID
            result = self._collection(collection).add(prepared)
            doc_id = result.get("id") or result.get("ids", [None])[0]

        return doc_id

    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        coll = self._collection(collection)

        # 如果是 _id 查询，使用 doc() 方法
        if "_id" in query:
            doc_id = query.pop("_id")
            ref = coll.doc(doc_id)
            if query:
                ref = ref.where(query)
            result = ref.get()
        else:
            ref = coll.where(query)
            result = ref.limit(1).get()

        docs = result.get("data", [])
        return _normalize_doc(docs[0]) if docs else None

    def find_many(
        self,
        collection: str,
        query: Dict[str, Any],
        sort: Optional[List[tuple]] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        coll = self._collection(collection)

        ref = coll
        for k, v in query.items():
            if v is not None:
                ref = ref.where(k, "==", v)

        if sort:
            for field, direction in sort:
                order = "desc" if direction == -1 else "asc"
                ref = ref.order_by(field, order)

        if skip > 0:
            ref = ref.skip(skip)
        ref = ref.limit(limit)

        result = ref.get()
        docs = result.get("data", [])
        return [_normalize_doc(d) for d in docs]

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
        prepared = dict(update)
        prepared["updateTime"] = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        # 乐观锁：版本号自动 +1
        if version is not None:
            prepared["version"] = version + 1

        doc_id = query.get("_id")
        if doc_id:
            ref = self._collection(collection).doc(doc_id)
            # 乐观锁：添加版本校验
            if version is not None:
                ref = ref.where("version", "==", version)
            result = ref.update(prepared)
        else:
            ref = self._collection(collection)
            for k, v in query.items():
                if v is not None:
                    ref = ref.where(k, "==", v)
            # 乐观锁：添加版本校验
            if version is not None:
                ref = ref.where("version", "==", version)
            result = ref.update(prepared)

        updated = result.get("updated", 0)
        return updated > 0

    def count(self, collection: str, query: Dict[str, Any]) -> int:
        ref = self._collection(collection)
        for k, v in query.items():
            if v is not None:
                ref = ref.where(k, "==", v)

        result = ref.count()
        return result.get("total", 0)

    def begin_transaction(self):
        # CloudBase NoSQL 不支持显式事务控制
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        self._db = None
        self._initialized = False


def _normalize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """规范化文档：确保 _id 字段存在。

    CloudBase 返回的文档可能使用 _id 或 id 字段，
    也可能是嵌套的 _openid 结构，统一为平铺的 _id 格式。
    """
    if not doc:
        return doc

    result = dict(doc)
    # CloudBase 的 _id 可能在根或嵌套结构中
    if "_id" not in result:
        doc_id = result.get("id")
        if doc_id:
            result["_id"] = doc_id
    return result
