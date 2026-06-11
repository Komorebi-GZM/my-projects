# Step 02: AgentState 添加难度字段

## 目标
在 `AgentState` 中添加 `difficulty` 字段，使状态机能够感知当前难度设置。

## 前置条件
- Step 01 完成（`DifficultyLevel` 枚举已定义）

## 涉及文件
- `src/chess_ai/agent/state.py` — 修改 `AgentState` 和 `create_initial_state`

## 详细步骤

### 2.1 修改 `AgentState`（TypedDict）

在 `AgentState` 中新增字段：

```python
from ..llm.models import DifficultyLevel

class AgentState(TypedDict, total=False):
    # ... 现有字段保持不变 ...
    difficulty: NotRequired[DifficultyLevel]
```

### 2.2 修改 `create_initial_state` 函数签名

```python
def create_initial_state(
    fen: str,
    current_turn: Side,
    thread_id: str,
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,  # 新增参数
) -> AgentState:
    return AgentState(
        # ... 现有字段保持不变 ...
        difficulty=difficulty,
    )
```

### 2.3 添加 `DifficultyLevel` 导入

在 `src/chess_ai/agent/__init__.py` 中，确保 `DifficultyLevel` 已导出：

```python
from ..llm.models import DifficultyLevel
```

## 验收标准
- `AgentState` 包含 `difficulty` 字段
- `create_initial_state` 支持 `difficulty` 参数（默认 MEDIUM）
- 所有 agent 模块单元测试通过（pytest tests/unit/test_agent/ -v）