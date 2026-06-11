# 任务跟踪

## v0.0.1 已完成 ✅

- [x] Board Engine - 棋盘、走子、规则验证
- [x] FEN 序列化/反序列化
- [x] 终局检测（将死、困毙、三次重复）
- [x] GUI 渲染、事件循环、控制器
- [x] LLM 客户端（OpenAI/DeepSeek/Ollama）
- [x] Prompt 工程、Move 解析器
- [x] LangGraph Agent 状态机
- [x] 配置管理、日志、数据库
- [x] 单元测试（board/move/rules）

---

## v0.1.1 已完成 ✅

- [x] 代码格式统一（Ruff formatter 替代 Black）
- [x] 修复 lazy import 散落问题（统一顶层导入）
- [x] 修复 ClassVar 标注缺失（theme/client/parser）
- [x] 修正 FEN 行序测试期望值 bug
- [x] 修正炮初始位置测试 bug
- [x] 更新 AGENTS.md Code Conventions + Rules

---

## v0.1.2 已完成 ✅

### Step 01 - 定义难度枚举与参数配置
- [x] `infra/difficulty.py` 添加 `Difficulty` 枚举
- [x] 定义 `difficulty_to_temperature()` 映射（Easy→0.8, Medium→0.3, Hard→0.1）
- [x] `config.yaml` 添加 `game.difficulty: "medium"`
- [x] `ConfigManager` 添加 `get_difficulty()` / `set_difficulty()` + `save()`

### Step 02 - AgentState 添加难度字段
- [ ] ~~AgentState 新增 difficulty 字段~~（跳过，ConfigManager 直接读取更简洁）

### Step 03 - LLM 客户端支持难度参数注入
- [x] `LLMClientFactory.create()` 接受 `temperature` 参数
- [x] `call_llm_node` 读取 `ConfigManager.get_difficulty()` → `difficulty_to_temperature()` → 传给工厂
- [x] EASY/MEDIUM/HARD 对应不同 temperature 生效

### Step 04 - Prompt 模板支持难度动态提示
- [x] `llm/prompt.py` 定义 `DIFFICULTY_HINTS` 策略提示字典
- [x] 添加 `inject_difficulty_hint()` 函数
- [x] `PromptBuilder.build()` 注入难度提示到 LLM Prompt
- [x] `MoveRequest` 新增 `difficulty` 字段

### Step 05 - GUI 难度选择界面
- [x] GUI 渲染层添加 easy/medium/hard 难度选择按钮
- [x] 难度配置写入 config.yaml（支持持久化）

### Step 06 - Agent 难度差异化重试策略
- [x] 修改 `should_retry()` 使用难度对应的 `max_retries`
- [x] EASY→5次重试, MEDIUM→3次, HARD→2次

### Step 07 - 难度分级集成测试
- [x] `tests/integration/test_difficulty.py` — 5个集成测试

### 基础设施
- [x] 配置系统重构：`_defaults` 扁平→嵌套结构 + `copy.deepcopy()` + `_compute_diff()` 修正
- [x] Issue tracker 基础设施：`.scratch/` + `docs/agents/`
- [x] AGENTS.md 失效链接修复

---

## v0.2.0 已完成 ✅

### Phase 1 - 悔棋/重做功能
- [x] `controller.py` — `_undo_stack` / `_redo_stack` 双栈结构
- [x] `undo()` / `redo()` 方法，成对撤销/重做（人类+AI各一步）
- [x] `can_undo` / `can_redo` 属性
- [x] `_record_state()` 走子前状态记录
- [x] `renderer.py` — `render_toolbar()` 工具栏（7个按钮）
- [x] SVG 图标加载（new_game/undo/redo/save/settings/sound/exit）
- [x] 快捷键 Ctrl+Z / Ctrl+Y
- [x] `handle_toolbar_click()` 事件分发
- [x] `test_controller_undo_redo.py` — 22 个单元测试

### Phase 2 - 游戏设置界面
- [x] `GameState.SETTINGS` 状态
- [x] `_handle_settings_click()` — 音效/动画/主题开关
- [x] `render_settings_dialog()` — 设置对话框渲染
- [x] 三个主题选项（classic/modern/dark）
- [x] ESC 快捷键返回
- [x] `test_settings.py` — 14 个单元测试

### Phase 3 - 棋谱保存/加载/复盘
- [x] `recorder.py` — `GameRecorder` 类（新增）
- [x] `start_game()` / `record_move()` / `end_game()`
- [x] JSON 导出/导入
- [x] `GameState.GAME_LIST` / `GameState.REPLAY` 状态
- [x] `_load_game_for_replay()` / `_replay_prev()` / `_replay_next()`
- [x] `render_game_list()` / `render_replay_controls()` + 进度条
- [x] `test_recorder.py` — 15 个单元测试

### 其他
- [x] `gui/config.py` — `window_height: 750`（650→750，容纳工具栏）
- [x] pygame 2.6.1 安装

---

## v0.2.1 已完成 ✅

### Bug 修复
- [x] 工具栏按钮映射不一致 — `renderer.py:558` tooltip/handler 对齐
- [x] undo/redo 不对称 — `controller.py:159-189` redo() 成对重做 2 步
- [x] 主题切换缓存未失效 — `controller.py:256-258` 清空缓存

### 代码质量
- [x] UP042 — `Difficulty(str, Enum)` → `Difficulty(StrEnum)`
- [x] 困毙测试重构 — 确定性局面（9 黑士填满九宫）
- [x] `test_move_parser.py` — 新增 13 个测试，parser 覆盖率 25%→82%
- [x] 总测试数 187→201，整体覆盖率 52%→53%
- [x] Ruff/format clean

---

## v0.3.x 待规划 📋

### 架构收紧（进行中）
- [x] GUI → Agent seam 收紧：GUI 不直接调用 `RuleValidator` / `GameTerminationChecker`
- [x] Agent facade 补充 `get_piece_legal_targets()` / `get_check_position()` / `restore_board()`
- [x] 规则引擎公开 `RuleValidator.apply_move()`，移除外部 `_apply_move` 调用
- [x] LLM Base Interface 拆到 `llm/base.py`，`llm/client.py` 聚焦 `LLMClientFactory`
- [x] Renderer 主题切换提供 `set_theme()` Interface，controller 不再触碰 renderer 私有缓存
- [x] `CONTEXT.md` 记录项目域词与关键 seam
- [x] Agent/LLM/GUI 集成测试补齐

### 功能增强
- [x] Pygame 前端视觉升级：棋盘纹理、棋子层次、工具栏/状态条、设置/复盘/棋谱面板统一游戏化
- [x] 难度选择页入口修复：启动保留难度选择，按钮点击区域与渲染区域共用布局
- [x] classic/modern/dark 三套主题使用真实差异化色板
- [ ] 音效系统完整实现（播放 WAV）
- [ ] 工具栏 settings/sound/exit 按钮实现
- [ ] 开局库/残局库集成
- [ ] 本地模型优化（Ollama）
- [ ] 联网对战模式

### 测试补充
- [ ] GUI renderer 单元测试
- [x] Agent/Rule facade 集成测试
- [x] Agent/LLM workflow 集成测试
- [x] GUI controller workflow 集成测试
- [x] LLM prompt/parser 集成测试
- [ ] Agent 模块单元测试
- [ ] LLM 模块单元测试
- [ ] 测试覆盖率 53% → 70%

### 代码质量
- [x] 生产与测试代码 lazy import 清零
- [x] GUI 外部私有缓存访问清零
- [ ] mypy 严格模式全通过

---

## 未来方向 🚀

- AI 自我对弈训练数据收集
- 棋力评估系统
- 多语言支持
