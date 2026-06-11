"""CloudBase NoSQL 简化封装 - 同createOrder"""
import json
import os


class CloudBase:
    def __init__(self, env_id=None):
        self.env_id = env_id or os.environ.get('TCB_ENV_ID')

    def server_date(self):
        from datetime import datetime
        return datetime.now().isoformat()

    def collection(self, name):
        return Collection(name)


class Collection:
    def __init__(self, name):
        self.name = name

    def add(self, data):
        import time
        return {'id': f'{self.name}_{int(time.time() * 1000)}'}

    def doc(self, doc_id):
        return Document(self.name, doc_id)

    def where(self, condition):
        return Query(self.name, condition)

    def count(self):
        return {'total': 0}


class Document:
    def __init__(self, collection_name, doc_id):
        self.collection_name = collection_name
        self.doc_id = doc_id

    def get(self):
        return {'data': []}

    def update(self, data):
        return {'updated': 1}


class Query:
    def __init__(self, collection_name, condition=None):
        self.collection_name = collection_name
        self.condition = condition or {}
        self._order_by = None
        self._limit = None
        self._skip = None

    def order_by(self, field, direction='asc'):
        self._order_by = (field, direction)
        return self

    def limit(self, n):
        self._limit = n
        return self

    def skip(self, n):
        self._skip = n
        return self

    def get(self):
        return {'data': []}
