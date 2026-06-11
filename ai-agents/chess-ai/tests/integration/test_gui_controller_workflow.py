"""
GUI 控制器集成测试。
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from chess_ai.board import Board
from chess_ai.gui.config import GUIConfig
from chess_ai.gui.controller import GameController, GameState
from chess_ai.rules import RuleValidator


class BoardPositionRenderer:
    """把测试坐标直接映射到棋盘格。"""

    def screen_to_board(self, x: int, y: int) -> tuple[int, int]:
        """将屏幕坐标映射到棋盘坐标。"""
        return (y // 60, x // 60)


class FakeAgent:
    """测试用 Agent。"""

    def __init__(self, board: Board) -> None:
        """初始化 Agent。"""
        self._current_board = board
        self.is_game_over = False
        self.game_result: str | None = None

    @property
    def current_board(self) -> Board:
        """返回当前棋盘。"""
        return self._current_board

    def process_user_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> tuple[bool, str]:
        """通过真实规则引擎应用用户走子。"""
        validator = RuleValidator()
        legal_moves = validator.get_legal_moves(self._current_board, "red")
        move = next((item for item in legal_moves if item.from_pos == from_pos and item.to_pos == to_pos), None)
        if move is None:
            return False, "非法走子"

        self._current_board = validator.apply_move(self._current_board, move)
        return True, ""

    def get_piece_legal_targets(self, position: tuple[int, int]) -> list[tuple[int, int]]:
        """返回指定棋子的合法目标。"""
        row, col = position
        validator = RuleValidator()
        legal_moves = validator.get_piece_legal_moves(self._current_board, row, col)
        return [move.to_pos for move in legal_moves]

    def get_check_position(self, side: str) -> tuple[int, int] | None:
        """返回被将军方的将帅位置。"""
        validator = RuleValidator()
        if not validator.is_in_check(self._current_board, side):
            return None
        return self._current_board.get_king_position(side)


@pytest.fixture
def controller() -> GameController:
    """创建隔离外设后的控制器。"""
    config = GUIConfig()
    renderer = BoardPositionRenderer()
    game_controller = GameController(config, renderer)  # type: ignore[arg-type]
    game_controller.state = GameState.WAITING
    game_controller.agent = FakeAgent(game_controller.board)  # type: ignore[assignment]
    game_controller._recorder = Mock()
    game_controller._start_ai_thread = Mock()  # type: ignore[method-assign]
    return game_controller


def test_clicking_legal_user_move_updates_board_and_starts_ai_turn(controller: GameController) -> None:
    """点击己方棋子再点击合法目标后，控制器推进到 AI 回合。"""
    controller.handle_click(0, 360)
    assert controller.state == GameState.PIECE_SELECTED
    assert controller.selected_pos == (6, 0)

    controller.handle_click(0, 300)

    assert controller.board.get_piece((6, 0)) is None
    assert controller.board.get_piece((5, 0)) == "P"
    assert controller.last_move == ((6, 0), (5, 0))
    assert controller.state == GameState.AI_THINKING
    assert controller.message == "AI 思考中..."
    controller._start_ai_thread.assert_called_once()
