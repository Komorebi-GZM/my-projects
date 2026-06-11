# Step 06: Agent 难度差异化重试策略

## 目标
根据难度等级调整 Agent 的重试策略和错误处理行为（如 easy 模式更激进降级，hard 模式允许更多重试）。

## 前置条件
- Step 02 完成（AgentState 包含 difficulty）
- Step 05 完成（GUI 难度选择可工作）

## 涉及文件
- `src/chess_ai/agent/nodes.py` — 修改 `should_retry`、`retry_node`
- `src/chess_ai/agent/state.py` — 可选：调整重试上限常量

## 详细步骤

### 6.1 定义难度重试策略表

```python
# 难度重试配置
RETRY_CONFIG: dict[DifficultyLevel, dict[str, int]] = {
    DifficultyLevel.EASY: {
        "max_retries": 1,       # 1次重试失败后立即降级
        "fallback_immediately_on_auth_error": True,
    },
    DifficultyLevel.MEDIUM: {
        "max_retries": 3,
        "fallback_immediately_on_auth_error": True,
    },
    DifficultyLevel.HARD: {
        "max_retries": 5,       # 允许更多重试以获得更好走子
        "fallback_immediately_on_auth_error": False,  # 认证错误也重试
    },
}
```

### 6.2 修改 `should_retry` 条件分支

```python
def should_retry(state: AgentState) -> Literal["retry", "fallback", "apply"]:
    difficulty = state.get("difficulty", DifficultyLevel.MEDIUM)
    config = RETRY_CONFIG[difficulty]
    max_retries = config["max_retries"]

    retry_count = state.get("retry_count", 0)
    validated_move = state.get("validated_move")
    last_error = state.get("last_error")

    if validated_move:
        return "apply"

    if last_error:
        if any(code in last_error for code in ("401", "403", "Authorization")):
            if config["fallback_immediately_on_auth_error"]:
                return "fallback"

    if retry_count >= max_retries:
        return "fallback"

    return "retry"
```

### 6.3 更新 `AgentState` 文档注释

在 `state.py` 的 docstring 中说明 `difficulty` 字段对重试策略的影响。

## 验收标准
- EASY 模式下 1 次重试后降级，HARD 模式下 5 次
- `ruff check src/` 无新增错误