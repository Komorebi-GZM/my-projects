"""
悔棋/重做功能单元测试
"""

from unittest.mock import Mock

import pytest

from chess_ai.gui.config import GUIConfig
from chess_ai.gui.controller import GameController, GameState


class MockRenderer:
    def __init__(self, config, theme=None):
        self.config = config
        self.theme = theme

    def screen_to_board(self, x, y):
        return (y // 60, x // 60)

    def board_to_screen(self, row, col):
        return (col * 60 + 30, row * 60 + 30)


@pytest.fixture
def controller():
    config = GUIConfig()
    renderer = MockRenderer(config)
    controller = GameController(config, renderer)
    controller.state = GameState.WAITING
    return controller


class TestUndoRedoBasics:
    """基础撤销/重做功能测试"""

    def test_initial_undo_stack_empty(self, controller):
        """初始状态下撤销栈为空"""
        assert len(controller._undo_stack) == 0
        assert len(controller._redo_stack) == 0

    def test_can_undo_initially_false(self, controller):
        """初始状态下不能撤销"""
        assert controller.can_undo is False

    def test_can_redo_initially_false(self, controller):
        """初始状态下不能重做"""
        assert controller.can_redo is False

    def test_undo_empty_stack_returns_false(self, controller):
        """撤销空栈返回 False"""
        result = controller.undo()
        assert result is False

    def test_redo_empty_stack_returns_false(self, controller):
        """重做空栈返回 False"""
        result = controller.redo()
        assert result is False


class TestUndoStack:
    """撤销栈记录测试"""

    def test_record_state_adds_to_undo_stack(self, controller):
        """记录状态后添加到撤销栈"""
        initial_undo_len = len(controller._undo_stack)
        controller._record_state()
        assert len(controller._undo_stack) == initial_undo_len + 1

    def test_record_state_clears_redo_stack(self, controller):
        """记录新状态后清空重做栈"""
        controller._redo_stack.append(("test", None, None))
        assert len(controller._redo_stack) == 1
        controller._record_state()
        assert len(controller._redo_stack) == 0

    def test_multiple_record_states(self, controller):
        """连续记录多个状态"""
        for i in range(5):
            controller._record_state()
        assert len(controller._undo_stack) == 5


class TestUndo:
    """撤销功能测试"""

    def test_undo_single_step(self, controller):
        """撤销一步"""
        controller._record_state()
        initial_undo_len = len(controller._undo_stack)

        result = controller.undo()

        assert result is True
        assert len(controller._undo_stack) == initial_undo_len - 1
        assert len(controller._redo_stack) == 1

    def test_undo_pair_step(self, controller):
        """成对撤销（人类+AI各一步）"""
        # 记录两步
        controller._record_state()
        controller._record_state()
        initial_undo_len = len(controller._undo_stack)

        result = controller.undo()

        assert result is True
        # 成对撤销应该移除2步
        assert len(controller._undo_stack) == max(0, initial_undo_len - 2)
        assert len(controller._redo_stack) == 2

    def test_undo_only_one_step_when_insufficient(self, controller):
        """撤销栈不足时只撤销一步"""
        controller._record_state()
        initial_undo_len = len(controller._undo_stack)

        result = controller.undo()

        assert result is True
        assert len(controller._undo_stack) == initial_undo_len - 1

    def test_undo_updates_state_after_pair(self, controller):
        """成对撤销后状态正确"""
        # 记录新状态
        controller._record_state()

        # 撤销
        controller.undo()

        # 检查状态重置
        assert controller.state == GameState.WAITING
        assert controller.selected_pos is None
        assert controller.legal_moves == []
        assert controller.message == "已撤销"


class TestRedo:
    """重做功能测试"""

    def test_redo_after_undo(self, controller):
        """撤销后重做"""
        controller._record_state()
        controller.undo()
        initial_redo_len = len(controller._redo_stack)

        result = controller.redo()

        assert result is True
        assert len(controller._redo_stack) == initial_redo_len - 1
        assert len(controller._undo_stack) == 1

    def test_redo_clears_undo_stack(self, controller):
        """重做后清空撤销栈中对应项"""
        controller._record_state()
        controller.undo()
        initial_undo_len = len(controller._undo_stack)

        controller.redo()

        # 重做会添加当前状态到撤销栈
        assert len(controller._undo_stack) == initial_undo_len + 1


class TestUndoRedoWithGameReset:
    """游戏重置时撤销/重做栈清空"""

    def test_reset_clears_undo_stack(self, controller):
        """重置游戏清空撤销栈"""
        controller._record_state()
        controller._record_state()
        assert len(controller._undo_stack) == 2

        controller.reset_game()

        assert len(controller._undo_stack) == 0

    def test_reset_clears_redo_stack(self, controller):
        """重置游戏清空重做栈"""
        controller._record_state()
        controller.undo()
        assert len(controller._redo_stack) == 1

        controller.reset_game()

        assert len(controller._redo_stack) == 0


class TestUndoWithAIThread:
    """撤销时 AI 线程处理测试"""

    def test_undo_waits_for_ai_thread(self, controller):
        """撤销时等待 AI 线程结束"""
        # 模拟 AI 线程
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        mock_thread.join.return_value = None
        controller._ai_thread = mock_thread

        controller._record_state()
        result = controller.undo()

        assert result is True
        mock_thread.join.assert_called_once_with(timeout=1.0)


class TestCanUndoRedo:
    """can_undo/can_redo 属性测试"""

    def test_can_undo_after_record(self, controller):
        """记录状态后可以撤销"""
        controller._record_state()
        assert controller.can_undo is True

    def test_cannot_undo_after_undo_all(self, controller):
        """撤销所有后不能继续撤销"""
        controller._record_state()
        controller.undo()
        assert controller.can_undo is False

    def test_can_redo_after_undo(self, controller):
        """撤销后可以重做"""
        controller._record_state()
        controller.undo()
        assert controller.can_redo is True

    def test_cannot_redo_after_redo_all(self, controller):
        """重做所有后不能继续重做"""
        controller._record_state()
        controller.undo()
        controller.redo()
        assert controller.can_redo is False

    def test_redo_clears_redo_stack(self, controller):
        """重做后清空重做栈"""
        controller._record_state()
        controller.undo()
        controller.redo()
        assert len(controller._redo_stack) == 0
