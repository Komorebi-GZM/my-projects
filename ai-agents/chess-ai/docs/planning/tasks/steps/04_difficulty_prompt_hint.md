# Step 04: Prompt 模板支持难度动态提示

## 目标
根据难度等级，在 LLM Prompt 中注入不同的策略提示（easy：鼓励新手友好；medium：平衡攻防；hard：强调深度计算）。

## 前置条件
- Step 01 完成（难度枚举和参数定义）
- Step 02 完成（AgentState 包含 difficulty）

## 涉及文件
- `src/chess_ai/llm/prompt.py` — 新增难度 Prompt 注入函数
- `src/chess_ai/agent/nodes.py` — 修改 `prepare_node` 调用难度提示注入

## 详细步骤

### 4.1 定义难度策略提示

在 `llm/prompt.py` 添加：

```python
DIFFICULTY_HINTS: dict[DifficultyLevel, str] = {
    DifficultyLevel.EASY: (
        "【策略提示】你是一个象棋初学者，思考简单直接。优先走子力交换、"
        "吃子或将军的明显好棋，不要走出过于复杂的变化。"
    ),
    DifficultyLevel.MEDIUM: (
        "【策略提示】你是一个中等水平的象棋玩家。注意棋子的协调配合，"
        "关注开局定型和中盘攻防的节奏变化，必要时可以进行兑换。"
    ),
    DifficultyLevel.HARD: (
        "【策略提示】你是一个象棋高手，追求最优走法。请深入计算各种变化，"
        "考虑对手的应招，寻找局面最优解。注意棋形弱点和潜在的战术组合。"
    ),
}
```

### 4.2 创建 Prompt 注入函数

```python
def inject_difficulty_hint(base_prompt: str, difficulty: DifficultyLevel) -> str:
    """向 Prompt 注入难度策略提示"""
    hint = DIFFICULTY_HINTS.get(difficulty, "")
    return f"{base_prompt}\n\n{hint}"
```

### 4.3 修改 `prepare_node`（或 `MoveRequest` 构建处）

在 `src/chess_ai/agent/nodes.py` 的 `prepare_node` 或 `call_llm_node` 中，
构建 Prompt 时注入难度提示：

```python
from ..llm.prompt import inject_difficulty_hint

def call_llm_node(state: AgentState) -> AgentState:
    # ... 构建 request ...
    difficulty = state.get("difficulty", DifficultyLevel.MEDIUM)
    # 在构建 Prompt 时（如有自定义 prompt 逻辑）注入难度提示
    # 若使用 MoveRequest.prompt_version，则需在 MoveRequest 或 prompt.py 中处理
```

## 验收标准
- `inject_difficulty_hint(prompt, DifficultyLevel.HARD)` 返回的字符串包含 HARD 策略提示
- `ruff check src/` 无新增错误