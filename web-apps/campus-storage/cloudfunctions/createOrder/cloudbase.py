"""
CloudBase NoSQL 简化封装
"""
import json
import os


class CloudBase:
    """CloudBase 数据库操作类"""

    def __init__(self, env_id=None):
        self.env_id = env_id or os.environ.get('TCB_ENV_ID')

    def server_date(self):
        """获取服务器时间"""
        from datetime import datetime
        return datetime.now().isoformat()

    def collection(self, name):
        """获取集合"""
        return Collection(name)


class Collection:
    """集合操作类"""

    def __init__(self, name):
        self.name = name

    def add(self, data):
        """添加文档"""
        # 实际部署时使用 cloudbase-sdk
        # 这里返回模拟结果
        import time
        return {'id': f'{self.name}_{int(time.time() * 1000)}'}

    def doc(self, doc_id):
        """获取文档引用"""
        return Document(self.name, doc_id)

    def where(self, condition):
        """条件查询"""
        return Query(self.name, condition)

    def count(self):
        """统计数量"""
        return {'total': 0}


class Document:
    """文档操作类"""

    def __init__(self, collection_name, doc_id):
        self.collection_name = collection_name
        self.doc_id = doc_id

    def get(self):
        """获取文档"""
        return {'data': []}

    def update(self, data):
        """更新文档"""
        return {'updated': 1}


class Query:
    """查询类"""

    def __init__(self, collection_name, condition=None):
        self.collection_name = collection_name
        self.condition = condition or {}
        self._order_by = None
        self._limit = None
        self._skip = None

    def order_by(self, field, direction='asc'):
        """排序"""
        self._order_by = (field, direction)
        return self

    def limit(self, n):
        """限制数量"""
        self._limit = n
        return self

    def skip(self, n):
        """跳过数量"""
        self._skip = n
        return self

    def get(self):
        """执行查询"""
        return {'data': []}
