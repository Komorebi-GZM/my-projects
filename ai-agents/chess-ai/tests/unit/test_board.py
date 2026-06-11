"""
棋盘基础功能测试
"""

import pytest

from chess_ai.board import (
    BLACK,
    RED,
    Board,
    OutOfBoundError,
)


class TestBoardInitialization:
    """测试棋盘初始化"""

    def test_create_initial_returns_board(self) -> None:
        """create_initial 方法返回 Board 实例"""
        board = Board.create_initial()
        assert isinstance(board, Board)

    def test_initial_position_has_32_pieces(self) -> None:
        """初始布局包含32个棋子"""
        board = Board.create_initial()
        piece_count = sum(1 for row in board.grid for cell in row if cell is not None)
        assert piece_count == 32

    def test_red_pieces_at_bottom(self) -> None:
        """红方棋子位于棋盘底部 (rows 6-9)"""
        board = Board.create_initial()
        red_pieces = []
        for row in range(6, 10):
            for col in range(9):
                piece = board.get_piece((row, col))
                if piece is not None and piece.isupper():
                    red_pieces.append((row, col, piece))
        assert len(red_pieces) == 16

    def test_black_pieces_at_top(self) -> None:
        """黑方棋子位于棋盘顶部 (rows 0-3)"""
        board = Board.create_initial()
        black_pieces = []
        for row in range(0, 4):
            for col in range(9):
                piece = board.get_piece((row, col))
                if piece is not None and piece.islower():
                    black_pieces.append((row, col, piece))
        assert len(black_pieces) == 16

    def test_initial_turn_is_red(self) -> None:
        """初始走子方为红方"""
        board = Board.create_initial()
        assert board.current_turn == RED


class TestGetPiece:
    """测试 get_piece 方法"""

    def test_get_piece_returns_correct_piece(self) -> None:
        """get_piece 返回正确的棋子"""
        board = Board.create_initial()
        # 黑方车在 (0, 0)
        assert board.get_piece((0, 0)) == "r"
        # 红方车在 (9, 0)
        assert board.get_piece((9, 0)) == "R"
        # 黑将在 (0, 4)
        assert board.get_piece((0, 4)) == "k"
        # 红帅在 (9, 4)
        assert board.get_piece((9, 4)) == "K"

    def test_get_piece_returns_none_for_empty(self) -> None:
        """get_piece 对空位返回 None"""
        board = Board.create_initial()
        # 中心区域应该是空的
        assert board.get_piece((4, 4)) is None

    def test_get_piece_raises_out_of_bound_error(self) -> None:
        """get_piece 对越界坐标抛出 OutOfBoundError"""
        board = Board.create_initial()
        with pytest.raises(OutOfBoundError):
            board.get_piece((10, 0))
        with pytest.raises(OutOfBoundError):
            board.get_piece((0, 9))
        with pytest.raises(OutOfBoundError):
            board.get_piece((-1, 0))


class TestSetPiece:
    """测试 set_piece 方法"""

    def test_set_piece_places_piece(self) -> None:
        """set_piece 可以在指定位置放置棋子"""
        board = Board.create_initial()
        new_board = board.set_piece((4, 4), "R")
        assert new_board.get_piece((4, 4)) == "R"
        # 原棋盘不变
        assert board.get_piece((4, 4)) is None

    def test_set_piece_returns_new_board(self) -> None:
        """set_piece 返回新的 Board 实例"""
        board = Board.create_initial()
        new_board = board.set_piece((4, 4), "R")
        assert new_board is not board
        assert board == Board.create_initial()

    def test_set_piece_with_none_clears_position(self) -> None:
        """set_piece(None) 清除指定位置"""
        board = Board.create_initial()
        new_board = board.set_piece((9, 4), None)
        assert new_board.get_piece((9, 4)) is None
        # 原棋盘红帅位置不变
        assert board.get_piece((9, 4)) == "K"

    def test_set_piece_raises_out_of_bound_error(self) -> None:
        """set_piece 对越界坐标抛出 OutOfBoundError"""
        board = Board.create_initial()
        with pytest.raises(OutOfBoundError):
            board.set_piece((10, 0), "R")


class TestRemovePiece:
    """测试 remove_piece 方法"""

    def test_remove_piece_removes_piece(self) -> None:
        """remove_piece 移除指定位置的棋子"""
        board = Board.create_initial()
        new_board = board.remove_piece((9, 4))
        assert new_board.get_piece((9, 4)) is None

    def test_remove_piece_returns_new_board(self) -> None:
        """remove_piece 返回新的 Board 实例"""
        board = Board.create_initial()
        new_board = board.remove_piece((9, 4))
        assert new_board is not board
        # 原棋盘红帅位置不变
        assert board.get_piece((9, 4)) == "K"


class TestIsEmpty:
    """测试 is_empty 方法"""

    def test_is_empty_returns_true_for_empty_cell(self) -> None:
        """is_empty 对空位返回 True"""
        board = Board.create_initial()
        assert board.is_empty((4, 4)) is True

    def test_is_empty_returns_false_for_occupied_cell(self) -> None:
        """is_empty 对有棋子的位置返回 False"""
        board = Board.create_initial()
        assert board.is_empty((9, 4)) is False

    def test_is_empty_raises_out_of_bound_error(self) -> None:
        """is_empty 对越界坐标抛出 OutOfBoundError"""
        board = Board.create_initial()
        with pytest.raises(OutOfBoundError):
            board.is_empty((10, 0))


class TestGetKingPosition:
    """测试 get_king_position 方法"""

    def test_get_king_position_finds_red_king(self) -> None:
        """get_king_position 找到红帅位置"""
        board = Board.create_initial()
        pos = board.get_king_position(RED)
        assert pos == (9, 4)

    def test_get_king_position_finds_black_king(self) -> None:
        """get_king_position 找到黑将位置"""
        board = Board.create_initial()
        pos = board.get_king_position(BLACK)
        assert pos == (0, 4)

    def test_get_king_position_raises_for_missing_king(self) -> None:
        """get_king_position 在找不到国王时抛出异常"""
        board = Board.create_initial().remove_piece((9, 4))
        with pytest.raises(ValueError):
            board.get_king_position(RED)


class TestCopy:
    """测试 copy 方法"""

    def test_copy_creates_independent_copy(self) -> None:
        """copy 创建独立的深拷贝"""
        board = Board.create_initial()
        copied = board.copy()

        # 内容相等
        assert board == copied
        assert copied is not board

        # 修改拷贝不影响原棋盘
        new_board = copied.set_piece((4, 4), "R")
        assert board.get_piece((4, 4)) is None
        assert new_board.get_piece((4, 4)) == "R"

    def test_copy_preserves_all_state(self) -> None:
        """copy 保持所有状态"""
        board = Board.create_initial()
        copied = board.copy()

        assert board.current_turn == copied.current_turn
        assert board.half_move_clock == copied.half_move_clock
        assert board.full_move_number == copied.full_move_number


class TestReset:
    """测试 reset 方法"""

    def test_reset_returns_initial_position(self) -> None:
        """reset 返回初始布局"""
        board = Board.create_initial()
        modified = board.set_piece((4, 4), "R").remove_piece((9, 4))
        reset_board = modified.reset()

        assert reset_board == Board.create_initial()

    def test_reset_returns_new_board(self) -> None:
        """reset 返回新的 Board 实例"""
        board = Board.create_initial()
        modified = board.set_piece((4, 4), "R")
        reset_board = modified.reset()

        assert reset_board is not board
        assert reset_board is not modified
