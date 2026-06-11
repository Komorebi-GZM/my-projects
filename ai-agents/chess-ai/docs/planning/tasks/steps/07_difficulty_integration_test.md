# Step 07: 难度分级集成测试

## 目标
编写集成测试，覆盖三个难度等级的对弈流程，验证参数注入和行为差异正确生效。

## 前置条件
- Step 01–06 全部完成

## 涉及文件
- `tests/integration/test_difficulty分级.py` — 新建集成测试文件

## 详细步骤

### 7.1 创建集成测试文件

```python
"""
难度分级集成测试 - 验证 easy/medium/hard 三档难度参数和行为差异
"""

import pytest

from chess_ai.agent import AgentOrchestrator
from chess_ai.agent.state import create_initial_state
from chess_ai.board import Board
from chess_ai.llm.models import DIFFICULTY_PARAMS, DifficultyLevel
from chess_ai.rules import FENSerializer


class TestDifficultyParams:
    """测试难度参数配置正确"""

    def test_easy_temperature_is_high(self) -> None:
        assert DIFFICULTY_PARAMS[DifficultyLevel.EASY]["temperature"] == pytest.approx(0.9)

    def test_medium_temperature_is_balanced(self) -> None:
        assert DIFFICULTY_PARAMS[DifficultyLevel.MEDIUM]["temperature"] == pytest.approx(0.3)

    def test_hard_temperature_is_low(self) -> None:
        assert DIFFICULTY_PARAMS[DifficultyLevel.HARD]["temperature"] == pytest.approx(0.05)


class TestDifficultyStatePropagation:
    """测试难度在状态机中正确传递"""

    def test_initial_state_has_difficulty(self) -> None:
        state = create_initial_state(
            fen=FENSerializer.to_fen(Board.create_initial()),
            current_turn="red",
            thread_id="test-thread",
            difficulty=DifficultyLevel.HARD,
        )
        assert state["difficulty"] == DifficultyLevel.HARD

    def test_default_difficulty_is_medium(self) -> None:
        state = create_initial_state(
            fen=FENSerializer.to_fen(Board.create_initial()),
            current_turn="red",
            thread_id="test-thread",
        )
        assert state["difficulty"] == DifficultyLevel.MEDIUM


class TestDifficultyAgentOrchestrator:
    """测试 AgentOrchestrator 接收难度参数"""

    def test_orchestrator_accepts_difficulty(self) -> None:
        orchestrator = AgentOrchestrator(
            difficulty=DifficultyLevel.HARD,
            user_side="red",
        )
        assert orchestrator.difficulty == DifficultyLevel.HARD
```

### 7.2 运行测试

```bash
pytest tests/integration/test_difficulty分级.py -v
```

### 7.3 补充：难度选择 UI 测试

在 `tests/unit/test_gui/` 添加难度选择按钮交互测试（可选，取决于 GUI 事件循环解耦程度）。

## 验收标准
- `pytest tests/integration/test_difficulty分级.py -v` → 全部通过
- `ruff check src/ tests/` → 无新增错误
- 手动测试：easy 模式下 AI 走子更"随机"，hard 模式下走子更"保守"（通过日志或输出验证）