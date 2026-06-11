# Step 03: LLM 客户端支持难度参数注入

## 目标
改造 `BaseLLMClient` 和 `LLMClientFactory.create()`，根据难度等级动态注入 `temperature`/`top_p`/`max_tokens` 参数。

## 前置条件
- Step 01 完成（难度参数表 `DIFFICULTY_PARAMS` 已定义）
- Step 02 完成（`AgentState` 包含 `difficulty` 字段）

## 涉及文件
- `src/chess_ai/llm/client.py` — 修改 `LLMClientFactory.create()`
- `src/chess_ai/agent/nodes.py` — 修改 `call_llm_node` 读取难度参数

## 详细步骤

### 3.1 修改 `LLMClientFactory.create()`

在工厂方法中增加 `difficulty` 参数：

```python
@classmethod
def create(
    cls,
    provider: str = "deepseek",
    model: str = "deepseek-chat",
    api_key: str | None = None,
    base_url: str | None = None,
    timeout: int = 15,
    temperature: float = 0.1,
    top_p: float = 0.9,
    max_tokens: int = 512,
    max_retries: int = 3,
    difficulty: DifficultyLevel | None = None,
) -> BaseLLMClient:
    # 如果传入了 difficulty，优先使用难度参数表覆盖
    if difficulty is not None:
        params = DIFFICULTY_PARAMS[difficulty]
        temperature = params.get("temperature", temperature)
        top_p = params.get("top_p", top_p)
        max_tokens = params.get("max_tokens", max_tokens)

    # ... 其余逻辑保持不变 ...
```

### 3.2 修改 `call_llm_node` 读取难度

在 `src/chess_ai/agent/nodes.py` 中：

```python
from ..llm.models import DifficultyLevel

def call_llm_node(state: AgentState) -> AgentState:
    # ... 获取配置 ...
    difficulty: DifficultyLevel | None = state.get("difficulty")  # 获取难度
    # ... 调用工厂方法时传入 difficulty ...
    client = LLMClientFactory.create(
        provider=provider,
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        timeout=config.get("model.timeout", 15),
        difficulty=difficulty,  # 新增
    )
```

### 3.3 导入 `DIFFICULTY_PARAMS`（如需直接访问）

```python
from ..llm.models import DIFFICULTY_PARAMS, DifficultyLevel
```

## 验收标准
- `LLMClientFactory.create(difficulty=DifficultyLevel.EASY)` 时，`temperature` 自动变为 0.9
- `call_llm_node` 读取 `state["difficulty"]` 正确传递给工厂
- `ruff check src/` 无新增错误