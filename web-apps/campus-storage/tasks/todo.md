# 校园物品暂存平台 — 任务清单

> 更新日期：2026-05-12
> 状态：待开始

---

## Phase 1: 核心功能补全

- [ ] **Task 1**: 启用乐观锁并发控制 `src/db/sqlite_adapter.py` `src/db/cloudbase_adapter.py`
- [ ] **Task 2**: 订单服务方法补全 `src/core/order_service.py`
- [ ] **Task 3**: 支付模拟流程实现 `src/routes/orders.py`

**Checkpoint 1-3**: 乐观锁启用、订单服务完整、支付流程可运行

---

## Phase 2: 仓库与配送功能

- [ ] **Task 4**: 仓库查询 API `src/routes/warehouses.py`（新建）
- [ ] **Task 5**: 配送地址管理 `src/routes/orders.py`

**Checkpoint 4-5**: 仓库 API 可用、配送流程可运行

---

## Phase 3: 前端页面完善

- [ ] **Task 6**: 下单页完善 `miniprogram/pages/order/create.*`
- [ ] **Task 7**: 订单列表页完善 `miniprogram/pages/order/list.*`
- [ ] **Task 8**: 订单详情页完善 `miniprogram/pages/order/detail.*`

**Checkpoint 6-8**: 下单流程、列表展示、详情操作正常

---

## Phase 4: 管理后台实现

- [ ] **Task 9**: 订单管理页 `admin/index.html` `admin/static/app.js`
- [ ] **Task 10**: 仓库管理页 `admin/index.html`

**Checkpoint 9-10**: 订单管理、仓库管理功能正常

---

## Phase 5: 代码质量与测试

- [ ] **Task 11**: 测试覆盖率提升至 80% `tests/*.py`
- [ ] **Task 12**: 集成测试完善 `tests/test_integration.py`

**Checkpoint 11-12**: 覆盖率 ≥ 80%、集成测试通过

---

## Phase 6: 生产部署准备

- [ ] **Task 13**: 云函数验证与更新 `cloudfunctions/*/index.py`
- [ ] **Task 14**: 部署文档更新 `docs/14_生产部署检查清单.md`

**Checkpoint 13-14**: 云函数同步、部署文档完整

---

## 快速参考

| 命令 | 说明 |
|------|------|
| `pytest tests/ -v` | 运行所有测试 |
| `pytest tests/ --cov=src --cov-report=html` | 测试覆盖率报告 |
| `python src/app.py` | 启动本地服务器 |
| `pytest tests/test_integration.py -v` | 集成测试 |

---

## 当前状态

- **已完成**: 后端核心（56 tests passing）、数据库适配层、状态机、定时任务
- **进行中**: 无
- **待开始**: Task 1-14

**下一步**: 从 Task 1（乐观锁）开始
