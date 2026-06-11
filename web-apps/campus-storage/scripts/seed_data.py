"""Warehouses 预置种子数据。"""

from datetime import datetime, timezone


WAREHOUSES = [
    {
        "id": "wh_gz_uc_north",
        "name": "广州大学城·北仓",
        "city": "广州",
        "address": "广州市番禺区大学城北一路 XX 号",
        "capacity": 200,
        "status": "ACTIVE",
    },
    {
        "id": "wh_gz_uc_south",
        "name": "广州大学城·南仓",
        "city": "广州",
        "address": "广州市番禺区大学城南二路 XX 号",
        "capacity": 150,
        "status": "ACTIVE",
    },
    {
        "id": "wh_gz_zhujiang",
        "name": "广州·珠江新城仓",
        "city": "广州",
        "address": "广州市天河区珠江新城花城大道 XX 号",
        "capacity": 300,
        "status": "ACTIVE",
    },
    {
        "id": "wh_sz_tsinghua",
        "name": "深圳·清华研究院仓",
        "city": "深圳",
        "address": "深圳市南山区西丽深圳国际研究生院 XX 号",
        "capacity": 100,
        "status": "ACTIVE",
    },
    {
        "id": "wh_sh_pudong",
        "name": "上海·浦东仓",
        "city": "上海",
        "address": "上海市浦东新区张江高科技园区 XX 号",
        "capacity": 250,
        "status": "ACTIVE",
    },
]


def seed_warehouses(conn) -> None:
    """向 warehouses 表写入预置数据，幂等执行。"""
    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    for wh in WAREHOUSES:
        conn.execute(
            """
            INSERT OR IGNORE INTO warehouses (id, name, city, address, capacity, used_capacity, status, create_time)
            VALUES (?, ?, ?, ?, ?, 0, 'ACTIVE', ?)
            """,
            (wh["id"], wh["name"], wh["city"], wh["address"], wh["capacity"], now),
        )

    count = conn.execute("SELECT COUNT(*) FROM warehouses").fetchone()[0]
    print(f"[OK] Warehouses seeded: {count} rows")
