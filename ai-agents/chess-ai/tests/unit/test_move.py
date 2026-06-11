"""
走子类单元测试
"""

import pytest

from chess_ai.board import Board
from chess_ai.move import Move


class TestMoveInitialization:
    """测试 Move 初始化"""

    def test_create_move_with_coordinates(self) -> None:
        """使用坐标创建 Move"""
        move = Move(from_pos=(9, 4), to_pos=(8, 4), piece="K")
        assert move.from_pos == (9, 4)
        assert move.to_pos == (8, 4)
        assert move.piece == "K"
        assert move.captured_piece is None

    def test_create_move_with_captured_piece(self) -> None:
        """创建包含被吃棋子的 Move"""
        move = Move(from_pos=(9, 4), to_pos=(0, 4), piece="K", captured_piece="k")
        assert move.captured_piece == "k"
        assert move.is_capture() is True

    def test_move_is_frozen(self) -> None:
        """Move 是不可变的"""
        move = Move(from_pos=(9, 4), to_pos=(8, 4), piece="K")
        with pytest.raises(Exception):
            move.piece = "R"


class TestMoveValidation:
    """测试 Move 坐标验证"""

    def test_valid_coordinates(self) -> None:
        """有效坐标不抛出异常"""
        move = Move(from_pos=(0, 0), to_pos=(9, 8), piece="r")
        assert move.from_pos == (0, 0)
        assert move.to_pos == (9, 8)

    def test_invalid_row_raises_error(self) -> None:
        """无效的 row 抛出 ValueError"""
        with pytest.raises(ValueError, match="row must be 0-9"):
            Move(from_pos=(10, 0), to_pos=(5, 4), piece="K")
        with pytest.raises(ValueError, match="row must be 0-9"):
            Move(from_pos=(-1, 0), to_pos=(5, 4), piece="K")

    def test_invalid_col_raises_error(self) -> None:
        """无效的 col 抛出 ValueError"""
        with pytest.raises(ValueError, match="col must be 0-8"):
            Move(from_pos=(0, 9), to_pos=(5, 4), piece="K")
        with pytest.raises(ValueError, match="col must be 0-8"):
            Move(from_pos=(0, -1), to_pos=(5, 4), piece="K")


class TestMoveToUCCI:
    """测试 to_ucci 方法"""

    def test_to_ucci_red_rook_initial_position(self) -> None:
        """红车从初始位置 (9,0) -> UCCI 'a0'"""
        move = Move(from_pos=(9, 0), to_pos=(5, 0), piece="R")
        assert move.to_ucci() == "a0a4"

    def test_to_ucci_black_rook_initial_position(self) -> None:
        """黑车从初始位置 (0,8) -> UCCI 'i9'"""
        move = Move(from_pos=(0, 8), to_pos=(4, 8), piece="r")
        assert move.to_ucci() == "i9i5"

    def test_to_ucci_center_position(self) -> None:
        """中心位置 (4, 4) -> UCCI 'e5'"""
        move = Move(from_pos=(4, 4), to_pos=(3, 4), piece="P")
        assert move.to_ucci() == "e5e6"

    def test_to_ucci_corner_positions(self) -> None:
        """角落位置测试"""
        move = Move(from_pos=(0, 0), to_pos=(9, 8), piece="r")
        assert move.to_ucci() == "a9i0"


class TestMoveFromUCCI:
    """测试 from_ucci 类方法"""

    def test_from_ucci_red_rook(self) -> None:
        """从 UCCI 解析红车走子"""
        board = Board.create_initial()
        move = Move.from_ucci("a0e0", board)
        assert move.from_pos == (9, 0)
        assert move.to_pos == (9, 4)
        assert move.piece == "R"

    def test_from_ucci_black_rook(self) -> None:
        """从 UCCI 解析黑车走子"""
        board = Board.create_initial()
        move = Move.from_ucci("i9e9", board)
        assert move.from_pos == (0, 8)
        assert move.to_pos == (0, 4)
        assert move.piece == "r"

    def test_from_ucci_with_capture(self) -> None:
        """从 UCCI 解析吃子走子"""
        board = Board.create_initial()
        move = Move.from_ucci("a0a9", board)
        assert move.piece == "R"
        assert move.captured_piece == "r"

    def test_from_ucci_invalid_format(self) -> None:
        """无效 UCCI 格式抛出 ValueError"""
        board = Board.create_initial()
        with pytest.raises(ValueError, match="Invalid UCCI format"):
            Move.from_ucci("invalid", board)
        with pytest.raises(ValueError, match="Invalid UCCI format"):
            Move.from_ucci("h2e", board)
        with pytest.raises(ValueError, match="Invalid UCCI format"):
            Move.from_ucci("h2e2extra", board)

    def test_from_ucci_no_piece_at_position(self) -> None:
        """起始位置无棋子抛出 ValueError"""
        board = Board.create_initial()
        with pytest.raises(ValueError, match="No piece at"):
            Move.from_ucci("a4a5", board)


class TestIsCapture:
    """测试 is_capture 方法"""

    def test_is_capture_true(self) -> None:
        """有被吃棋子时返回 True"""
        move = Move(from_pos=(9, 4), to_pos=(0, 4), piece="K", captured_piece="k")
        assert move.is_capture() is True

    def test_is_capture_false(self) -> None:
        """无被吃棋子时返回 False"""
        move = Move(from_pos=(9, 4), to_pos=(8, 4), piece="K")
        assert move.is_capture() is False


class TestMoveRepr:
    """测试 __repr__ 方法"""

    def test_repr_format(self) -> None:
        """__repr__ 返回正确的格式"""
        move = Move(from_pos=(9, 4), to_pos=(8, 4), piece="K", captured_piece=None)
        result = repr(move)
        assert "Move(" in result
        assert "from=(9, 4)" in result
        assert "to=(8, 4)" in result
        assert "piece='K'" in result
        assert "captured=None" in result
