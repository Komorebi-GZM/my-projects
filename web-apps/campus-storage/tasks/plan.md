# Implementation Plan: 校园物品暂存平台优化

> 版本：v1.0
> 创建日期：2026-05-12
> 状态：待审核

---

## 概述

基于对项目当前状态的全面分析，本计划聚焦于**补全核心功能、提升代码质量、完善测试覆盖**三个维度。项目已完成 Phase 0-3 的后端核心开发（56 个测试全部通过），但存在功能缺失、乐观锁未启用、前端页面待完善等问题。

---

## 当前状态快照

| 模块 | 状态 | 完成度 |
|------|------|--------|
| **后端核心** | ✅ 已完成 | 90% |
| **数据库适配层** | ✅ 已完成 | 100% |
| **状态机** | ✅ 已完成 | 100% |
| **定时任务** | ✅ 已完成 | 100% |
| **测试覆盖** | ✅ 已完成 | 56 tests passing |
| **云函数** | ⚠️ 部分完成 | 框架存在，需验证 |
| **小程序前端** | ⚠️ 部分完成 | 页面结构存在，内容待完善 |
| **管理后台** | ⚠️ 仅骨架 | index.html 存在，无实际功能 |
| **乐观锁** | ❌ 未启用 | version 字段存在但未使用 |
| **支付模块** | ❌ 未实现 | 仅有错误码定义 |
| **仓库管理** | ❌ 未实现 | 仅有表结构 |

---

## 架构决策

| 决策 | 选择 | 理由 |
|------|------|------|
| **乐观锁实现** | 在 update_one 中启用 version 校验 | 数据库已有 version 字段，只需激活校验逻辑 |
| **支付流程** | 模拟支付 + 状态标记 | Demo 阶段无需真实对接，isPaid 字段已存在 |
| **仓库管理** | 仅实现查询 API | 运营端展示用，暂不实现容量管理 |
| **前端完善** | 优先核心页面 | 下单页、订单列表、订单详情优先 |
| **管理后台** | H5 单页应用 | 嵌入小程序，复用 API |

---

## 任务清单

### Phase 1: 核心功能补全（Foundation）

---

#### Task 1: 启用乐观锁并发控制

**Description:** 在 SQLiteAdapter 和 CloudBaseAdapter 的 update_one 方法中启用 version 字段校验，防止并发更新冲突。

**Acceptance criteria:**
- [ ] update_one 方法检查 version 字段
- [ ] 版本不匹配时返回 False（不抛异常）
- [ ] 更新成功时 version 自动 +1
- [ ] 单元测试覆盖并发冲突场景

**Verification:**
- [ ] `pytest tests/test_optimistic_lock.py -v` 通过
- [ ] 并发更新测试：两个请求同时更新同一订单，只有一个成功

**Dependencies:** None

**Files likely touched:**
- `src/db/sqlite_adapter.py`
- `src/db/cloudbase_adapter.py`
- `tests/test_optimistic_lock.py`（新建）

**Estimated scope:** S

---

#### Task 2: 订单服务方法补全

**Description:** 为 OrderService 类补充缺失的方法：get_order、update_order、cancel_order、get_orders_by_user。

**Acceptance criteria:**
- [ ] `get_order(order_id)` 方法实现
- [ ] `update_order(order_id, updates)` 方法实现
- [ ] `cancel_order(order_id, reason)` 方法实现（调用状态机）
- [ ] `get_orders_by_user(user_id, filters)` 方法实现
- [ ] 单元测试覆盖所有新方法

**Verification:**
- [ ] `pytest tests/test_order_service.py -v` 通过
- [ ] 所有方法有对应的测试用例

**Dependencies:** Task 1

**Files likely touched:**
- `src/core/order_service.py`
- `tests/test_order_service.py`

**Estimated scope:** M

---

#### Task 3: 支付模拟流程实现

**Description:** 实现模拟支付流程，用户确认支付后标记 isPaid = true，记录支付时间。

**Acceptance criteria:**
- [ ] POST /api/orders/<id>/pay 端点实现
- [ ] 仅 PENDING 状态订单可支付
- [ ] 支付后 isPaid = true，记录 paidAt 时间
- [ ] 状态变更为 PAID（新增状态）或保持 PENDING
- [ ] 单元测试覆盖支付流程

**Verification:**
- [ ] `pytest tests/test_payment.py -v` 通过
- [ ] 支付后订单状态正确

**Dependencies:** Task 2

**Files likely touched:**
- `src/routes/orders.py`
- `src/core/order_service.py`
- `tests/test_payment.py`（新建）

**Estimated scope:** S

---

### Checkpoint 1-3: 核心功能补全完成

- [ ] 乐观锁启用并测试通过
- [ ] 订单服务方法完整
- [ ] 支付流程可运行
- [ ] 所有测试通过：`pytest tests/ -v`

---

### Phase 2: 仓库与配送功能

---

#### Task 4: 仓库查询 API

**Description:** 实现仓库列表查询 API，供用户下单时选择暂存城市/仓库。

**Acceptance criteria:**
- [ ] GET /api/warehouses 端点实现
- [ ] 返回仓库列表（id, name, city, capacity）
- [ ] 支持按城市筛选：GET /api/warehouses?city=北京
- [ ] 预置 3-5 个模拟仓库数据

**Verification:**
- [ ] `pytest tests/test_warehouses.py -v` 通过
- [ ] 本地调试：`curl http://localhost:5000/api/warehouses` 返回数据

**Dependencies:** None

**Files likely touched:**
- `src/routes/warehouses.py`（新建）
- `src/app.py`（注册蓝图）
- `tests/test_warehouses.py`（新建）

**Estimated scope:** S

---

#### Task 5: 配送地址管理

**Description:** 实现配送地址填写和存储，用户可在 STORED 状态发起配送。

**Acceptance criteria:**
- [ ] PATCH /api/orders/<id>/delivery 端点实现
- [ ] 仅 STORED 状态订单可发起配送
- [ ] 接收 deliveryAddress、deliveryTime、receiverName、receiverPhone
- [ ] 状态变更为 DELIVERING
- [ ] 记录配送信息到订单

**Verification:**
- [ ] `pytest tests/test_delivery.py -v` 通过
- [ ] 配送流程集成测试通过

**Dependencies:** Task 2

**Files likely touched:**
- `src/routes/orders.py`
- `src/core/order_service.py`
- `tests/test_delivery.py`（新建）

**Estimated scope:** M

---

### Checkpoint 4-5: 仓库与配送完成

- [ ] 仓库查询 API 可用
- [ ] 配送流程可运行
- [ ] 相关测试通过

---

### Phase 3: 前端页面完善

---

#### Task 6: 下单页完善

**Description:** 完善小程序下单页面，支持城市选择、仓库选择、物品信息填写、费用预估。

**Acceptance criteria:**
- [ ] 城市选择器（调用 /api/warehouses）
- [ ] 仓库选择器（根据城市筛选）
- [ ] 物品类型选择（行李/文件/包裹）
- [ ] 体积选择（小/中/大/超大）
- [ ] 服务方式选择（上门取件/自送到仓）
- [ ] 暂存天数选择
- [ ] 费用预估展示
- [ ] 提交订单按钮

**Verification:**
- [ ] 微信开发者工具预览正常
- [ ] 完整下单流程可跑通

**Dependencies:** Task 4

**Files likely touched:**
- `miniprogram/pages/order/create.wxml`
- `miniprogram/pages/order/create.wxss`
- `miniprogram/pages/order/create.js`

**Estimated scope:** M

---

#### Task 7: 订单列表页完善

**Description:** 完善订单列表页面，支持 Tab 切换、下拉刷新、订单卡片展示。

**Acceptance criteria:**
- [ ] Tab 切换（全部/进行中/已完成/已取消）
- [ ] 订单卡片展示（订单号、状态、城市、创建时间）
- [ ] 下拉刷新
- [ ] 上拉加载更多
- [ ] 点击卡片跳转详情页

**Verification:**
- [ ] 微信开发者工具预览正常
- [ ] 列表数据正确展示

**Dependencies:** None（后端 API 已完成）

**Files likely touched:**
- `miniprogram/pages/order/list.wxml`
- `miniprogram/pages/order/list.wxss`
- `miniprogram/pages/order/list.js`

**Estimated scope:** M

---

#### Task 8: 订单详情页完善

**Description:** 完善订单详情页面，展示状态时间轴、物品信息、费用明细、操作按钮。

**Acceptance criteria:**
- [ ] 状态时间轴（纵向步骤条）
- [ ] 物品信息卡片
- [ ] 费用明细展示
- [ ] 操作按钮（根据状态动态显示：取消、支付、发起配送）
- [ ] 确认收货按钮

**Verification:**
- [ ] 微信开发者工具预览正常
- [ ] 操作按钮功能正确

**Dependencies:** Task 5

**Files likely touched:**
- `miniprogram/pages/order/detail.wxml`
- `miniprogram/pages/order/detail.wxss`
- `miniprogram/pages/order/detail.js`

**Estimated scope:** M

---

### Checkpoint 6-8: 前端核心页面完成

- [ ] 下单流程可跑通
- [ ] 订单列表正确展示
- [ ] 订单详情操作正确
- [ ] **Review with human:** 前端交互确认

---

### Phase 4: 管理后台实现

---

#### Task 9: 管理后台 - 订单管理页

**Description:** 实现管理后台订单管理页面，支持查看所有订单、状态操作、异常处理。

**Acceptance criteria:**
- [ ] 订单列表表格（分页、筛选）
- [ ] 状态操作按钮（确认取件、发运、入库、派送、完成）
- [ ] 异常标记功能
- [ ] 订单详情弹窗
- [ ] 管理员身份校验

**Verification:**
- [ ] 浏览器访问管理后台正常
- [ ] 订单操作功能正确

**Dependencies:** Task 2

**Files likely touched:**
- `admin/index.html`
- `admin/static/app.js`
- `admin/static/style.css`

**Estimated scope:** M

---

#### Task 10: 管理后台 - 仓库管理页

**Description:** 实现仓库管理页面，展示仓库信息、库存状态。

**Acceptance criteria:**
- [ ] 仓库列表展示
- [ ] 仓库容量状态展示
- [ ] 仓库信息编辑（可选）

**Verification:**
- [ ] 仓库数据正确展示

**Dependencies:** Task 4

**Files likely touched:**
- `admin/index.html`
- `admin/static/app.js`

**Estimated scope:** S

---

### Checkpoint 9-10: 管理后台完成

- [ ] 订单管理功能正常
- [ ] 仓库管理功能正常
- [ ] 管理员权限隔离生效

---

### Phase 5: 代码质量与测试

---

#### Task 11: 测试覆盖率提升

**Description:** 提升测试覆盖率至 80% 以上，补充边界条件测试。

**Acceptance criteria:**
- [ ] 当前覆盖率检查：`pytest --cov=src --cov-report=term`
- [ ] 补充缺失的测试用例
- [ ] 覆盖率达到 80%

**Verification:**
- [ ] `pytest --cov=src --cov-report=html` 报告确认

**Dependencies:** Task 1-10

**Files likely touched:**
- `tests/*.py`（补充测试）

**Estimated scope:** M

---

#### Task 12: 集成测试完善

**Description:** 完善集成测试，覆盖完整用户流程和管理员流程。

**Acceptance criteria:**
- [ ] 用户完整流程测试（注册→下单→支付→配送→收货）
- [ ] 管理员流程测试（查看订单→状态操作→异常处理）
- [ ] 超时任务测试已存在，验证通过

**Verification:**
- [ ] `pytest tests/test_integration.py -v` 全部通过

**Dependencies:** Task 1-10

**Files likely touched:**
- `tests/test_integration.py`

**Estimated scope:** S

---

### Checkpoint 11-12: 质量达标

- [ ] 测试覆盖率 ≥ 80%
- [ ] 所有测试通过
- [ ] 集成测试覆盖核心流程

---

### Phase 6: 生产部署准备

---

#### Task 13: 云函数验证与更新

**Description:** 验证云函数目录下的代码是否与本地 Flask 路由同步，更新过时代码。

**Acceptance criteria:**
- [ ] 检查 7 个云函数与本地路由的一致性
- [ ] 更新不一致的云函数代码
- [ ] 更新依赖包列表

**Verification:**
- [ ] 代码 diff 确认同步

**Dependencies:** Task 1-12

**Files likely touched:**
- `cloudfunctions/*/index.py`
- `cloudfunctions/*/requirements.txt`

**Estimated scope:** S

---

#### Task 14: 部署文档更新

**Description:** 更新部署文档，确保部署流程清晰可执行。

**Acceptance criteria:**
- [ ] `docs/14_生产部署检查清单.md` 更新
- [ ] 部署脚本验证
- [ ] 环境变量清单确认

**Verification:**
- [ ] 文档审核通过

**Dependencies:** Task 13

**Files likely touched:**
- `docs/14_生产部署检查清单.md`
- `scripts/deploy_cloudfunctions.py`

**Estimated scope:** S

---

### Checkpoint 13-14: 部署就绪

- [ ] 云函数代码同步
- [ ] 部署文档完整
- [ ] **Review with human:** 部署前最终确认

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 乐观锁实现影响现有功能 | 高 | 先写测试，增量修改，保持向后兼容 |
| 前端页面与 API 不匹配 | 中 | 先确认 API 契约，再开发前端 |
| 管理后台权限绕过 | 高 | 复用 permission.py 模块，后端校验 |
| 云函数部署失败 | 中 | 保留部署脚本，支持 dry-run 验证 |

---

## 任务汇总

| Phase | 任务数 | 预估工作量 | 关键产出 |
|-------|--------|-----------|---------|
| Phase 1: 核心功能补全 | 3 | 1天 | 乐观锁 + 订单服务完善 + 支付流程 |
| Phase 2: 仓库与配送 | 2 | 0.5天 | 仓库 API + 配送流程 |
| Phase 3: 前端页面完善 | 3 | 2天 | 下单页 + 列表页 + 详情页 |
| Phase 4: 管理后台 | 2 | 1天 | 订单管理 + 仓库管理 |
| Phase 5: 代码质量 | 2 | 0.5天 | 测试覆盖率 80%+ |
| Phase 6: 部署准备 | 2 | 0.5天 | 云函数同步 + 文档更新 |
| **总计** | **14** | **5.5天** | - |

---

## 并行化机会

| 可并行任务 | 说明 |
|-----------|------|
| Task 1, Task 4 | 乐观锁与仓库 API 无依赖关系 |
| Task 6, Task 7, Task 8 | 前端页面可并行开发（确认 API 后） |
| Task 9, Task 10 | 管理后台两个页面可并行 |

---

## 开放问题

| 问题 | 状态 | 决策点 |
|------|------|--------|
| 支付后是否新增 PAID 状态？ | 待确认 | 简化流程可保持 PENDING，由运营确认收款 |
| 仓库容量管理是否需要？ | 待确认 | Demo 阶段可暂不实现 |
| 目的地调整功能是否实现？ | 待确认 | PRD 中 P0 功能，但需要跨仓库转运逻辑 |

---

*计划完成，等待审核后执行*
