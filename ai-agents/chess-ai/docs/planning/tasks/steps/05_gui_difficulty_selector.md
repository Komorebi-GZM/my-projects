# Step 05: GUI 难度选择界面

## 目标
在游戏开始界面添加难度选择功能，支持 easy/medium/hard 三个难度档位。

## 前置条件
- Step 01 完成（难度枚举和配置）
- Step 02 完成（AgentState 包含 difficulty）

## 涉及文件
- `src/chess_ai/gui/controller.py` — 修改 `GameController` 读取/传递难度
- `src/chess_ai/gui/renderer.py` — 修改渲染层支持难度显示（可选）
- `src/chess_ai/gui/theme.py` — 可选：添加难度配色

## 详细步骤

### 5.1 修改 `GameController` 初始化

```python
from ..llm.models import DifficultyLevel

class GameController:
    def __init__(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        # ... 其余现有参数 ...
    ):
        self.difficulty = difficulty
        # ... 其余初始化逻辑 ...
```

### 5.2 传递难度给 AgentOrchestrator

```python
def start_game(self) -> None:
    orchestrator = AgentOrchestrator(
        difficulty=self.difficulty,  # 新增
        # ... 其余参数 ...
    )
```

### 5.3 AgentOrchestrator 接收难度

```python
class AgentOrchestrator:
    def __init__(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        # ... 其余现有参数 ...
    ):
        self.difficulty = difficulty
        self._setup_agent()
```

### 5.4 创建难度选择按钮（GUI 渲染层）

在 `renderer.py` 中添加难度选择按钮区域：

```python
# 难度按钮配置
DIFFICULTY_BUTTONS: dict[DifficultyLevel, tuple[str, tuple[int, int, int]]] = {
    DifficultyLevel.EASY: ("简单", (0, 200, 0)),
    DifficultyLevel.MEDIUM: ("中等", (200, 150, 0)),
    DifficultyLevel.HARD: ("困难", (200, 0, 0)),
}
```

### 5.5 在主菜单渲染难度选择

在 `start_screen` 或新建 `difficulty_screen` 中渲染三个按钮。

## 验收标准
- 游戏启动时可看到 easy/medium/hard 三个难度按钮
- 点击后难度被正确传递到 AgentOrchestrator
- `ruff check src/` 无新增错误