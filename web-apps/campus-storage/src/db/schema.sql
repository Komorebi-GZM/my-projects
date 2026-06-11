-- 校园物品暂存平台 · SQLite 建表脚本
-- 可重复执行（IF NOT EXISTS）

-- users 表
CREATE TABLE IF NOT EXISTS users (
    id            TEXT PRIMARY KEY,
    openid        TEXT NOT NULL UNIQUE,
    version       INTEGER NOT NULL DEFAULT 1,
    nick_name     TEXT NOT NULL DEFAULT '',
    avatar_url    TEXT NOT NULL DEFAULT '',
    phone         TEXT NOT NULL DEFAULT '',
    role          TEXT NOT NULL DEFAULT 'USER',
    status        TEXT NOT NULL DEFAULT 'ACTIVE',
    create_time   TEXT NOT NULL,
    update_time   TEXT NOT NULL
);

-- orders 表
CREATE TABLE IF NOT EXISTS orders (
    id                TEXT PRIMARY KEY,
    openid            TEXT NOT NULL,
    version           INTEGER NOT NULL DEFAULT 1,
    order_no          TEXT NOT NULL UNIQUE,
    status            TEXT NOT NULL DEFAULT 'PENDING',
    is_paid           INTEGER NOT NULL DEFAULT 0,
    user_id           TEXT NOT NULL,
    warehouse_id      TEXT NOT NULL,
    warehouse_name    TEXT NOT NULL DEFAULT '',
    city              TEXT NOT NULL DEFAULT '',
    item_type         TEXT NOT NULL DEFAULT '',
    volume            TEXT NOT NULL DEFAULT '',
    estimated_weight  REAL NOT NULL DEFAULT 0,
    service_type      TEXT NOT NULL DEFAULT '',
    storage_days      INTEGER NOT NULL DEFAULT 7,
    delivery_address  TEXT NOT NULL DEFAULT '',
    delivery_time     TEXT NOT NULL DEFAULT '',
    amount            TEXT NOT NULL DEFAULT '{}',
    declared_value    REAL NOT NULL DEFAULT 0,
    storage_photo_url TEXT NOT NULL DEFAULT '',
    status_history    TEXT NOT NULL DEFAULT '[]',
    create_time       TEXT NOT NULL,
    update_time       TEXT NOT NULL
);

-- warehouses 表
CREATE TABLE IF NOT EXISTS warehouses (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    city            TEXT NOT NULL DEFAULT '',
    address         TEXT NOT NULL DEFAULT '',
    capacity        INTEGER NOT NULL DEFAULT 100,
    used_capacity   INTEGER NOT NULL DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'ACTIVE',
    create_time     TEXT NOT NULL
);

-- tickets 表
CREATE TABLE IF NOT EXISTS tickets (
    id            TEXT PRIMARY KEY,
    order_id      TEXT NOT NULL,
    user_id       TEXT NOT NULL,
    type          TEXT NOT NULL DEFAULT '',
    description   TEXT NOT NULL DEFAULT '',
    image_url     TEXT NOT NULL DEFAULT '',
    status        TEXT NOT NULL DEFAULT 'PENDING',
    resolution    TEXT NOT NULL DEFAULT '',
    create_time   TEXT NOT NULL
);

-- addresses 表（用户配送地址）
CREATE TABLE IF NOT EXISTS addresses (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL,
    version       INTEGER NOT NULL DEFAULT 1,
    name          TEXT NOT NULL,          -- 收货人姓名
    phone         TEXT NOT NULL,          -- 联系电话
    province      TEXT NOT NULL DEFAULT '',  -- 省份
    city          TEXT NOT NULL DEFAULT '',  -- 城市
    district      TEXT NOT NULL DEFAULT '',  -- 区/县
    detail        TEXT NOT NULL,          -- 详细地址
    tag           TEXT NOT NULL DEFAULT '',  -- 标签（家/学校/公司等）
    is_default    INTEGER NOT NULL DEFAULT 0, -- 是否默认地址
    status        TEXT NOT NULL DEFAULT 'ACTIVE',
    create_time   TEXT NOT NULL,
    update_time   TEXT NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_orders_user_status ON orders(user_id, status);
CREATE INDEX IF NOT EXISTS idx_orders_status_createtime ON orders(status, create_time DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_orderno ON orders(order_no);
CREATE INDEX IF NOT EXISTS idx_orders_warehouse_status ON orders(warehouse_id, status);
CREATE INDEX IF NOT EXISTS idx_tickets_orderid ON tickets(order_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_openid ON users(openid);
