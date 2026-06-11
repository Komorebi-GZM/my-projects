"""数据访问层抽象基类。"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class DBAdapter(ABC):
    """统一数据访问接口。"""

    @abstractmethod
    def insert(self, collection: str, doc: Dict[str, Any]) -> str:
        """插入文档，返回文档 ID。"""

    @abstractmethod
    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """查询单个文档。"""

    @abstractmethod
    def find_many(
        self,
        collection: str,
        query: Dict[str, Any],
        sort: Optional[List[tuple]] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        """查询多个文档，支持排序、分页。"""

    @abstractmethod
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

    @abstractmethod
    def count(self, collection: str, query: Dict[str, Any]) -> int:
        """统计文档数量。"""

    @abstractmethod
    def begin_transaction(self):
        """开始事务。"""

    @abstractmethod
    def commit(self):
        """提交事务。"""

    @abstractmethod
    def rollback(self):
        """回滚事务。"""

    @abstractmethod
    def close(self):
        """关闭连接。"""
