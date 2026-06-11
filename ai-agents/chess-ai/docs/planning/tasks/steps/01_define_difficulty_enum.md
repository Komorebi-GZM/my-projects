# Step 01: 定义难度枚举与参数配置

## 目标
在 `src/chess_ai/llm/models.py` 中添加 `DifficultyLevel` 枚举，并在 `src/chess_ai/infra/config.py` 中添加难度参数映射。

## 前置条件
- 无

## 涉及文件
- `src/chess_ai/llm/models.py` — 新增 `DifficultyLevel` 枚举
- `src/chess_ai/infra/config.py` — 新增难度相关配置项

## 详细步骤

### 1.1 在 `llm/models.py` 添加枚举

```python
class DifficultyLevel(StrEnum):
    """AI 难度等级"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
```

### 1.2 定义难度参数表

在 `llm/models.py` 添加难度与 LLM 参数的映射：

```python
# 难度参数配置
DIFFICULTY_PARAMS: dict[DifficultyLevel, dict[str, Any]] = {
    DifficultyLevel.EASY: {
        "temperature": 0.9,
        "top_p": 0.95,
        "max_tokens": 256,
    },
    DifficultyLevel.MEDIUM: {
        "temperature": 0.3,
        "top_p": 0.9,
        "max_tokens": 512,
    },
    DifficultyLevel.HARD: {
        "temperature": 0.05,
        "top_p": 0.85,
        "max_tokens": 1024,
    },
}
```

### 1.3 在 config.yaml 添加难度配置项

```yaml
model:
  difficulty: medium  # easy | medium | hard
```

### 1.4 ConfigManager 添加 difficulty 读取

```python
def get_difficulty(self) -> DifficultyLevel:
    """获取 AI 难度等级"""
    raw = self.get("model.difficulty", "medium").lower()
    try:
        return DifficultyLevel(raw)
    except ValueError:
        return DifficultyLevel.MEDIUM
```

## 验收标准
- `DifficultyLevel` 枚举可正常导入
- `config.get_difficulty()` 返回正确枚举值
- 配置项支持 `easy`/`medium`/`hard` 三值