# 校园物品暂存平台

> 状态：开发完成，已就绪部署
> 版本：v2.0
> 最后更新：2026-05-13

一个面向校园场景的物品暂存服务小程序，支持用户下单寄存物品、查看订单状态、发起配送等核心功能。

## 项目概述

本项目采用"本地Python完整开发 → 统一部署"的Demo阶段模式：
- **本地开发**：Python 3.12 + Flask + SQLite，完整业务逻辑开发与测试
- **生产部署**：CloudBase云开发 + 微信小程序，线上发布与运营

## 快速开始

### 环境要求

| 工具 | 版本要求 |
|------|---------|
| Python | 3.12+ |
| Node.js | 18+ (小程序开发) |
| 微信开发者工具 | 最新稳定版 |

### 安装依赖

```bash
# 克隆项目
git clone <repo-url>
cd campus-storage

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 运行测试（验证环境）
pytest tests/ -v
# 预期结果: 161 passed, 覆盖率80%
```

### 本地开发

```bash
# 初始化数据库
python scripts/init_db.py

# 启动Flask开发服务器
python src/app.py

# 运行测试
pytest tests/ -v
```

### 小程序开发

1. 打开微信开发者工具
2. 导入 `miniprogram` 目录
3. 修改 `miniprogram/config.js` 中的 API 地址指向本地服务器
4. 开启"不校验合法域名"进行本地联调

## 项目结构

```
campus-storage/
├── src/                      # 后端源码
│   ├── app.py               # Flask应用入口
│   ├── config.py            # 配置文件
│   ├── routes/              # API路由
│   │   ├── auth.py          # 认证接口
│   │   └── orders.py        # 订单接口
│   ├── core/                # 核心业务逻辑
│   │   ├── order_service.py # 订单服务
│   │   └── order_state.py   # 状态机
│   ├── db/                  # 数据层
│   │   ├── adapter.py       # 适配器接口
│   │   ├── sqlite_adapter.py # SQLite实现
│   │   ├── cloudbase_adapter.py # CloudBase实现
│   │   └── factory.py       # 适配器工厂
│   └── tasks/               # 定时任务
│       ├── timeout_checker.py
│       └── scheduler.py
├── miniprogram/             # 微信小程序
│   ├── pages/               # 页面
│   │   ├── index/           # 首页
│   │   ├── order/           # 订单相关页面
│   │   └── delivery/        # 配送页面
│   ├── utils/               # 工具函数
│   ├── app.js               # 小程序入口
│   ├── app.json             # 全局配置
│   └── config.js            # 环境配置
├── admin/                   # 运营端H5
│   ├── index.html
│   └── static/
├── cloudfunctions/          # CloudBase云函数
│   ├── login/
│   ├── createOrder/
│   ├── getOrderList/
│   ├── getOrderDetail/
│   ├── updateOrderStatus/
│   ├── pendingTimeoutChecker/
│   └── deliveringTimeoutChecker/
├── scripts/                 # 工具脚本
│   ├── init_db.py           # 数据库初始化
│   ├── migrate_to_cloudbase.py # 数据迁移
│   ├── deploy_cloudfunctions.py # 云函数部署
│   └── full_deploy.py       # 一键部署
├── tests/                   # 测试用例
│   ├── test_auth.py
│   ├── test_order_service.py
│   ├── test_routes.py
│   └── test_integration.py
└── docs/                    # 项目文档
    ├── 01_产品需求文档_PRD.md
    ├── 02_系统设计说明书_SDD.md
    ├── 05_API接口文档.md
    ├── 09_部署与运维说明.md
    ├── 14_生产部署检查清单.md
    └── decisions/           # 架构决策记录(ADRs)
```

## 核心功能

### 用户端（小程序）
- 微信登录获取openid
- 创建暂存订单（选择仓库、物品类型、预估时长）
- 查看订单列表和详情
- 发起配送服务
- 查看订单状态流转

### 运营端（H5）
- 订单管理列表
- 订单状态更新（PENDING → COLLECTED → STORED → DELIVERING → COMPLETED）

### 系统功能
- 定时任务：PENDING订单超时自动取消
- 定时任务：DELIVERING订单超时自动完结
- 暂存费用自动计算

## 技术架构

### 后端架构
- **框架**: Flask + Blueprint
- **数据库**: SQLite（本地）/ CloudBase NoSQL（生产）
- **认证**: JWT-less，使用X-OpenId Header
- **定时任务**: APScheduler（本地）/ CloudBase定时触发器（生产）

### 前端架构
- **小程序**: 原生微信小程序（WXML/WXSS/JS）
- **运营端**: 纯HTML/CSS/JS

### 部署架构
```
本地开发 → pytest测试 → Flask本地联调 → 微信开发者工具预览
                                                ↓
              CloudBase环境创建 → 数据迁移 → 云函数部署 → 小程序发布
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `python src/app.py` | 启动开发服务器 |
| `pytest tests/ -v` | 运行测试 |
| `python scripts/init_db.py` | 初始化数据库 |
| `python scripts/full_deploy.py --env-id <id> --dry-run` | 预览部署 |
| `python scripts/full_deploy.py --env-id <id>` | 执行部署 |

## 文档索引

| 文档 | 说明 |
|------|------|
| [docs/01_产品需求文档_PRD.md](docs/01_产品需求文档_PRD.md) | 产品需求 |
| [docs/02_系统设计说明书_SDD.md](docs/02_系统设计说明书_SDD.md) | 系统设计 |
| [docs/04_数据库设计文档.md](docs/04_数据库设计文档.md) | 数据库设计 |
| [docs/05_API接口文档.md](docs/05_API接口文档.md) | API文档 |
| [docs/09_部署与运维说明.md](docs/09_部署与运维说明.md) | 部署指南 |
| [docs/14_生产部署检查清单.md](docs/14_生产部署检查清单.md) | 发布检查清单 |
| [docs/decisions/](docs/decisions/) | 架构决策记录(ADRs) |

## 项目状态

| 指标 | 状态 |
|------|------|
| 测试数量 | 161个 (全部通过) |
| 测试覆盖率 | 80% |
| API端点 | 16个 |
| 云函数 | 7个 |
| 文档数量 | 14份 |

## 快速验证

```bash
# 1. 启动开发服务器
python src/app.py

# 2. 在另一个终端运行测试
pytest tests/ -v

# 预期: ============================= 161 passed in 0.XXs =============================
```

## 项目状态

| 指标 | 状态 |
|------|------|
| 测试数量 | 161个 (全部通过) |
| 测试覆盖率 | 80% |
| API端点 | 16个 |
| 云函数 | 7个 |
| 文档数量 | 14份 |

## 快速验证

```bash
# 1. 启动开发服务器
python src/app.py

# 2. 在另一个终端运行测试
pytest tests/ -v

# 预期: ============================= 161 passed in 0.XXs =============================
```

## 贡献指南

1. 遵循现有代码风格
2. 提交前运行 `pytest tests/ -v` 确保测试通过
3. 重要变更需更新相关文档
4. 新功能需补充测试用例

## 许可证

MIT License
