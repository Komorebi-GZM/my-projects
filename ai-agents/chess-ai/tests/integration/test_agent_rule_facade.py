"""
Agent 规则门面集成测试。
"""

from __future__ import annotations

from chess_ai.agent import AgentOrchestrator
from chess_ai.board import Board


def test_agent_exposes_piece_targets_for_gui_selection() -> None:
    """Agent 能为 GUI 暴露指定棋子的合法目标。"""
    agent = AgentOrchestrator()

    targets = agent.get_piece_legal_targets((6, 0))

    assert (5, 0) in targets


def test_agent_exposes_check_position_after_user_move() -> None:
    """Agent 能为 GUI 暴露被将军方的将帅位置。"""
    agent = AgentOrchestrator()
    board = Board()
    board = board.set_piece((0, 4), "k")
    board = board.set_piece((9, 4), "K")
    board = board.set_piece((2, 4), "R")
    agent.restore_board(board)

    assert agent.get_check_position("black") == (0, 4)
