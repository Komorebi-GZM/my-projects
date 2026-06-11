"""数据库初始化脚本 — 建表 + 索引 + 种子数据。

用法：
    conda run -n py312 python scripts/init_db.py                    # 默认 data/dev.db
    conda run -n py312 python scripts/init_db.py /path/to/custom.db
"""

import sqlite3
import sys
from pathlib import Path

# Ensure project root is on sys.path for sibling imports (seed_data)
sys.path.insert(0, str(Path(__file__).parent.parent))


DB_DIR = Path("data")
DEFAULT_DB_PATH = DB_DIR / "dev.db"

SCHEMA_PATH = Path(__file__).parent.parent / "src" / "db" / "schema.sql"


def init_db(db_path: str | Path) -> None:
    """用 schema.sql 初始化指定 SQLite 文件。"""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")

    try:
        sql = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(sql)
        print(f"[OK] Schema applied to {db_path}")

        # Seed warehouses
        from scripts.seed_data import seed_warehouses
        seed_warehouses(conn)

        conn.commit()
        print("[OK] Initialization complete.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_DB_PATH)
    init_db(db)
