# 版本变更记录 Changelog

本文档记录项目所有功能、修复、变更历史。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## 规范总则

### 变更分类定义

| 分类 | 说明 |
|-----|------|
| **Added** | 新增功能 |
| **Changed** | 现有功能变更 |
| **Deprecated** | 即将废弃的功能 |
| **Removed** | 已移除的功能 |
| **Fixed** | 缺陷修复 |
| **Security** | 安全相关修复 |

### 版本号规则

| 版本类型 | 格式 | 触发条件 |
|---------|------|---------|
| 主版本 | X.0.0 | 不兼容的API变更 |
| 次版本 | 0.X.0 | 向后兼容的功能新增 |
| 修订版本 | 0.0.X | 向后兼容的Bug修复 |

---

## [Unreleased]

### Added
- `CONTEXT.md` — 新增项目域词与关键 seam，方便后续架构审查与 AI 导航
- Agent/LLM/GUI 集成测试覆盖真实跨层工作流
- GUI 主题令牌扩展为 classic/modern/dark 三套视觉风格

### Changed
- GUI 主题切换改为调用 renderer Interface，controller 不再直接修改 renderer 私有缓存
- Pygame 前端视觉升级：棋盘纹理、棋子层次、工具栏、状态条、设置/复盘/棋谱面板统一成游戏化 UI
- LLM 包导出从 `llm/base.py` 获取 Base Interface，`llm/client.py` 聚焦工厂职责
- 架构文档更新为当前实际调用关系：GUI → Agent → Rule Engine / LLM

### Deprecated
- （预留：即将废弃的功能）

### Removed
- 清理测试与类型检查缓存目录

### Fixed
- 清理 lazy import 与外部私有方法调用造成的层 seam 泄漏
- 难度选择按钮的绘制区域与点击命中区域不一致，且启动流程会跳过难度选择页

### Security
- （预留：待发布的安全修复）

---

## [0.2.1] - 2026-05-16

### Fixed
- 工具栏按钮映射不一致 — `renderer.py` 第4个按钮 tooltip/handler 对齐为 "棋谱"/`show_game_list`
- undo/redo 不对称 — `controller.py` `redo()` 现在成对重做 2 步，与 `undo()` 对称
- 主题切换缓存未失效 — `controller.py` 切换主题后清空 `_board_surface` 和 `_piece_surfaces`

### Changed
- UP042 代码规范 — `Difficulty(str, Enum)` 迁移至 `Difficulty(StrEnum)`（Python 3.12 最佳实践）
- 困毙检测测试 — 重构为确定性局面（9 黑士填满九宫），消除条件竞争

### Added
- `test_move_parser.py` — 新增 13 个单元测试，parser 覆盖率 25%→82%
- 总测试数 187→201，整体覆盖率 52%→53%

---

## [0.0.1] - 2026-05-14

### Added
- 初始可运行版本，包含完整棋盘引擎、GUI界面、AI Agent、基础设施
- 标准10x9棋盘，7种棋子走法验证
- Pygame棋盘渲染，中文字体支持
- LangGraph状态机AI Agent，支持OpenAI兼容/DeepSeek/Ollama
- YAML+环境变量双层配置，dotenv自动加载
- SQLite数据库（对局/走子/检查点）
- 单元测试覆盖 board/move/rules 模块

---

## [0.1.0] - 2026-05-13

### Added
- 项目初始化：Python 3.12 + Pygame 2.6 + LangChain 1.2+ + LangGraph 1.0+ 技术栈搭建
- 棋盘规则引擎：完整中国象棋规则实现（棋子走法、特殊规则、FEN编解码、胜负判定）
- GUI界面：Pygame桌面应用（棋盘渲染、棋子交互、走子高亮、状态提示）
- LangGraph Agent：AI代理状态机工作流（走子生成、检查点恢复、人机交互）
- LLM集成：多模型支持（DeepSeek/GPT/通义千问/Ollama本地模型）
- Prompt工程：三套实测有效模板（极简工业版、Few-shot轻量版、结构化极简版）
- 输出解析器：多级清洗策略，适配模型输出乱象（废话、换行、JSON错误）
- 数据持久化：SQLite数据库（对局记录、走子历史、配置管理、LangGraph检查点）
- 对局管理：新建/悔棋/重置/保存/恢复/导出棋谱
- 配置系统：YAML配置文件 + 环境变量 + GUI设置三层配置
- 外部接口：RESTful API + WebSocket实时通信（扩展预留）
- 全套项目文档：架构设计、4份详细设计、数据库设计、接口文档、测试计划、部署运维、用户手册、贡献指南

---

## 版本链接映射

| 版本 | 对比链接 |
|-----|---------|
| [Unreleased] | `main...HEAD` |
| [0.2.1] | `v0.2.1` 标签（功能增强与代码质量优化） |
| [0.0.1] | `v0.0.1` 标签（初始可运行版本） |
| [0.1.0] | `v0.1.0` 标签（首次发布） |

---

## 格式规范附录

### 变更条目撰写规范

| 规则 | 说明 |
|-----|------|
| **粒度** | 功能级变更，不写细碎代码调整 |
| **语言** | 中文描述，技术术语保留英文 |
| **关联** | 重要变更关联Issue编号，如 `(#XX)` |
| **排序** | 同分类内按模块排序（核心→AI→GUI→文档） |

### 版本发布规则

| 规则 | 说明 |
|-----|------|
| **合并** | Unreleased中的变更在发布时合并到对应版本 |
| **清空** | 发布后Unreleased区块清空，保留分类标题 |
| **标签** | 发布时创建Git标签 `vX.X.X` |
| **更新** | 同步更新版本链接映射区 |
