# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- 订单评价功能
- 优惠券系统
- 消息推送通知

## [1.0.0] - 2026-05-10

### Added
- **核心功能**
  - 用户微信登录获取openid
  - 创建暂存订单（选择仓库、物品类型、预估时长）
  - 订单列表查询（支持状态筛选、分页）
  - 订单详情查看（状态历史时间轴）
  - 发起配送服务（填写配送地址、联系人）
  - 管理员订单状态更新（PENDING → COLLECTED → STORED → DELIVERING → COMPLETED）

- **系统功能**
  - 订单状态机（6状态，严格流转控制）
  - 定时任务：PENDING订单超时自动取消（默认7天）
  - 定时任务：DELIVERING订单超时自动完结（默认24小时）
  - 暂存费用自动计算

- **技术实现**
  - Flask后端API（本地开发环境）
  - CloudBase云函数（生产环境）
  - 数据库适配器模式（SQLite ↔ CloudBase NoSQL）
  - 微信小程序前端
  - H5运营端管理面板

- **开发工具**
  - 数据迁移脚本（SQLite → CloudBase NoSQL）
  - 云函数部署脚本
  - 一键部署脚本
  - 完整的测试套件（56个测试用例）

- **文档**
  - 产品需求文档（PRD）
  - 系统设计说明书（SDD）
  - API接口文档
  - 数据库设计文档
  - 部署与运维说明
  - 生产部署检查清单
  - 架构决策记录（ADRs）

### Technical Details

#### Backend
- Python 3.12+
- Flask web framework
- SQLite（本地）/ CloudBase NoSQL（生产）
- APScheduler（本地定时任务）

#### Frontend
- 微信小程序原生开发
- H5运营端（纯HTML/CSS/JS）

#### Infrastructure
- 腾讯云CloudBase云开发
- 7个云函数
- 2个定时触发器

#### Testing
- pytest测试框架
- 56个测试用例
- 92.9%通过率（52/56）

### Security
- JWT-less认证（X-OpenId Header）
- 管理员权限校验
- 用户只能访问自己的订单数据

## [0.9.0] - 2026-05-08

### Added
- Phase 6: 集成测试
  - 完整流程测试用例
  - 前后端联调测试指南

## [0.8.0] - 2026-05-07

### Added
- Phase 5: 运营端
  - H5订单管理页面
  - 订单状态更新功能

## [0.7.0] - 2026-05-06

### Added
- Phase 4: 前端小程序
  - 小程序基础框架
  - 首页、下单页、订单列表页、订单详情页、配送发起页

## [0.6.0] - 2026-05-05

### Added
- Phase 3: 定时任务
  - pendingTimeoutChecker
  - deliveringTimeoutChecker
  - APScheduler调度配置

## [0.5.0] - 2026-05-04

### Added
- Phase 2: Flask路由
  - 登录接口
  - 订单CRUD接口
  - 状态更新接口

## [0.4.0] - 2026-05-03

### Added
- Phase 1: 数据库适配器
  - SQLite适配器实现
  - CloudBase适配器实现
  - 适配器工厂

## [0.3.0] - 2026-05-02

### Added
- Phase 0: 基础设施
  - 项目结构搭建
  - 错误处理框架
  - 权限控制模块
  - 输入验证模块

## [0.2.0] - 2026-05-01

### Added
- 项目初始化
- 需求分析文档
- 系统设计文档

## [0.1.0] - 2026-04-30

### Added
- 项目立项
- 技术选型确定
- 开发计划制定

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-05-10 | 首个完整版本，包含所有7个Phase |
| 0.9.0 | 2026-05-08 | 集成测试完成 |
| 0.8.0 | 2026-05-07 | 运营端完成 |
| 0.7.0 | 2026-05-06 | 前端小程序完成 |
| 0.6.0 | 2026-05-05 | 定时任务完成 |
| 0.5.0 | 2026-05-04 | Flask路由完成 |
| 0.4.0 | 2026-05-03 | 数据库适配器完成 |
| 0.3.0 | 2026-05-02 | 基础设施完成 |
| 0.2.0 | 2026-05-01 | 项目初始化 |
| 0.1.0 | 2026-04-30 | 项目立项 |
