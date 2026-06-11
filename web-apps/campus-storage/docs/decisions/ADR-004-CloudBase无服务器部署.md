# ADR-004: CloudBase无服务器部署

## Status
Accepted

## Date
2026-05-10

## Context

项目需要选择生产环境托管方案，考虑因素：
- Demo阶段，预算有限
- 团队规模小，无专职运维
- 需要快速上线和迭代
- 与微信小程序生态集成

可选方案：
- 传统云服务器（CVM/ECS）
- 容器服务（TKE/K8s）
- 云函数（CloudBase/SCF）

## Decision

采用**腾讯云CloudBase云开发**作为生产部署方案，使用云函数（Serverless）+ NoSQL数据库 + 定时触发器。

### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      微信小程序                              │
│                   (WXML/WXSS/JS)                            │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTPS
              ┌───────────────▼───────────────┐
              │      CloudBase 云开发         │
              │  ┌─────────────────────────┐  │
              │  │      HTTP 访问服务       │  │
              │  │   (云函数HTTP触发)       │  │
              │  └─────────────────────────┘  │
              │              │                │
              │  ┌───────────┼───────────┐    │
              │  ▼           ▼           ▼    │
              │ ┌─────┐  ┌─────┐  ┌─────┐    │
              │ │login│  │order│  │admin│    │
              │ └─────┘  └─────┘  └─────┘    │
              │                              │
              │  ┌─────────────────────────┐  │
              │  │    CloudBase NoSQL      │  │
              │  │    (文档数据库)          │  │
              │  └─────────────────────────┘  │
              │                              │
              │  ┌─────────────────────────┐  │
              │  │      定时触发器          │  │
              │  │  pendingTimeoutChecker  │  │
              │  │ deliveringTimeoutChecker│  │
              │  └─────────────────────────┘  │
              └──────────────────────────────┘
```

### 云函数清单

| 云函数 | 类型 | 触发方式 | 说明 |
|--------|------|----------|------|
| login | HTTP | HTTP请求 | 用户登录获取openid |
| createOrder | HTTP | HTTP请求 | 创建订单 |
| getOrderList | HTTP | HTTP请求 | 获取订单列表 |
| getOrderDetail | HTTP | HTTP请求 | 获取订单详情 |
| updateOrderStatus | HTTP | HTTP请求 | 更新订单状态（管理员） |
| pendingTimeoutChecker | Timer | 每30分钟 | PENDING订单超时检查 |
| deliveringTimeoutChecker | Timer | 每30分钟 | DELIVERING订单超时检查 |

### 技术选型理由

1. **CloudBase vs 传统服务器**
   - 免运维：自动扩缩容，无需管理服务器
   - 成本低：按调用次数计费，Demo阶段接近免费
   - 集成好：与微信小程序深度集成

2. **NoSQL vs 关系型数据库**
   - CloudBase原生支持
   - 文档模型与JSON API匹配
   - 自动备份和恢复

3. **云函数 vs 单体应用**
   - 函数级部署，更新不影响全局
   - 自动弹性伸缩
   - 与定时触发器原生集成

## Alternatives Considered

### 方案A：腾讯云CVM + MySQL
- **Pros**: 成熟稳定，完全可控
- **Cons**: 需要运维，成本高，配置复杂
- **Rejected**: 无运维资源，过度配置

### 方案B：Docker + K8s
- **Pros**: 现代化部署，可移植性好
- **Cons**: 学习成本高，运维复杂
- **Rejected**: 团队规模小，不需要这么重的方案

### 方案C：Vercel/Netlify + Supabase
- **Pros**: 国际知名，生态丰富
- **Cons**: 国内访问慢，与微信小程序集成差
- **Rejected**: 国内项目，需要更好的微信生态支持

## Consequences

### Positive
- 零运维成本，专注业务开发
- 与微信小程序无缝集成
- 自动弹性伸缩，应对流量高峰
- 免费额度足够Demo阶段使用

### Negative
- 云厂商锁定，迁移成本高
- 本地开发需要适配层
- 冷启动延迟（几百毫秒）
- 调试和日志查看不如本地方便

### Mitigations
- 适配器模式设计，降低迁移成本
- 完善的日志记录和监控
- 预热策略减少冷启动影响
- 本地开发环境完整模拟

## Costs

### CloudBase免费额度
- 云函数调用：500万次/月
- NoSQL读操作：500万次/月
- NoSQL写操作：300万次/月
- 存储空间：2GB

Demo阶段预计完全在免费额度内。

## Related

- `cloudfunctions/` - 云函数源码
- `docs/06_云函数设计文档.md` - 云函数详细设计
- `docs/09_部署与运维说明.md` - 部署指南
- `scripts/deploy_cloudfunctions.py` - 部署脚本
