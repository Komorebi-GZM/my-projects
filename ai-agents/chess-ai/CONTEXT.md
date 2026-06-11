# Project Context

## Domain

中国象棋 AI 对弈工具是本地桌面应用。人类执红，LLM Agent 执黑，Pygame GUI 负责交互，规则引擎负责合法性与终局，Agent 编排回合，LLM 模块只根据结构化请求产出走子。

## Core Terms

- **Board**：10x9 棋盘状态。`row=0` 是黑方底线，`row=9` 是红方底线。
- **Move**：一次 UCCI 走子，包含起点与终点。
- **Rule Engine**：纯规则 Module，校验走法、生成合法走子、执行走子、检测将军。
- **Termination Checker**：终局判定 Module，判断将死、困毙、重复局面。
- **Agent Orchestrator**：GUI 使用的主要 Interface。隐藏规则与 LLM 编排细节。
- **LLM Client**：具体模型 Adapter。DeepSeek、OpenAI、Ollama 都满足同一 BaseLLMClient Interface。
- **Prompt Builder**：把棋盘 FEN、合法走子、历史、难度合成 LLM 请求上下文。
- **Game Recorder**：棋谱持久化 Module，保存、加载、导出对局。

## Architecture Seams

- **GUI -> Agent Orchestrator**：GUI 不直接调用 Rule Engine 或 LLM。合法目标、将军位置、棋盘恢复都通过 Agent Orchestrator。
- **Agent -> Rule Engine**：Agent 负责回合编排；Rule Engine 负责棋规。
- **Agent -> LLM**：Agent 构造 MoveRequest；LLM 模块返回 MoveResponse 或解析后的走子。
- **LLM Base -> LLM Adapters**：BaseLLMClient 定义共享 Interface；client.py 只保留 LLMClientFactory。
- **Renderer Cache**：主题切换通过 renderer Interface 失效缓存，controller 不触碰 renderer 私有状态。

## Current Quality Focus

- 收紧层 seam，避免 GUI 跳过 Agent。
- 清理 lazy import 与外部私有方法调用。
- 用集成测试覆盖 Agent、LLM、GUI 的真实交互路径。
