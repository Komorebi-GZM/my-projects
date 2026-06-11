# 📚 中国象棋AI对弈工具 - 文档中心

> 适配技术栈：Python 3.12 | LangChain 1.2+ | LangGraph 1.0+ | Pygame 2.6

---

## 快速导航

| 文档 | 说明 |
|------|------|
| [设计文档](design/) | 架构设计、技术决策 |
| [使用指南](guides/) | 部署、使用、贡献规范 |
| [项目规划](planning/) | 版本记录、任务跟踪、PRD |
| [发布总结](releases/) | 版本发布说明 |
| [参考资料](references/) | 外部规范、协议文档 |

---

## 核心文档

### 架构与设计
- [design/ARCHITECTURE.md](design/ARCHITECTURE.md) - 系统架构、模块职责、数据流
- [design/prompt_engineering_log.md](design/prompt_engineering_log.md) - Prompt迭代与模型评估

### 使用指南
- [guides/DEPLOYMENT.md](guides/DEPLOYMENT.md) - 环境要求、安装部署
- [guides/USER_GUIDE.md](guides/USER_GUIDE.md) - 对弈操作、功能说明
- [guides/CONTRIBUTING.md](guides/CONTRIBUTING.md) - 代码规范、Git规范

### 项目规划
- [planning/CHANGELOG.md](planning/CHANGELOG.md) - 版本变更记录
- [planning/PRD.docx](planning/PRD.docx) - 产品需求文档
- [planning/tasks/](planning/tasks/) - 任务跟踪与开发计划

### 版本发布
- [releases/v0.0.1_summary.md](releases/v0.0.1_summary.md) - v0.0.1 核心功能实现
- [releases/v0.1.1_summary.md](releases/v0.1.1_summary.md) - v0.1.1 代码质量优化
- [releases/v0.2.1_summary.md](releases/v0.2.1_summary.md) - v0.2.1 架构边界、集成测试与界面优化

### 参考资料
- [references/cchess_protocol.html](references/cchess_protocol.html) - UCCI通信协议
- [references/cchess_rules_2011.pdf](references/cchess_rules_2011.pdf) - 中国象棋竞赛规则
- [references/pygame_docs.html](references/pygame_docs.html) - Pygame文档

---

## 根目录重要文件

| 文件 | 说明 |
|------|------|
| [../README.md](../README.md) | 项目主 README |
| [../AGENTS.md](../AGENTS.md) | 智能体代码规范 |
| [../CONTEXT.md](../CONTEXT.md) | 领域上下文与核心术语 |
| [../PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) | 项目目录结构说明 |
