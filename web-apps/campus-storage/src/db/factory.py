"""数据适配器工厂。"""

import os
from pathlib import Path

from src.db.adapter import DBAdapter
from src.db.cloudbase_adapter import CloudBaseAdapter
from src.db.sqlite_adapter import SQLiteAdapter


_db_adapter: DBAdapter = None


def get_db_adapter() -> DBAdapter:
    """根据 DB_MODE 返回对应的数据库适配器。

    测试时可通过设置 ``_db_adapter`` 覆盖默认适配器。
    """
    global _db_adapter
    if _db_adapter is not None:
        return _db_adapter

    mode = os.getenv("DB_MODE", "local").lower()

    if mode == "production":
        env_id = os.getenv("TCB_ENV_ID")
        if not env_id:
            raise ValueError("TCB_ENV_ID must be set for production mode")
        return CloudBaseAdapter(env_id)

    return SQLiteAdapter("data/dev.db")
