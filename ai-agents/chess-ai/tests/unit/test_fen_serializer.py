"""
FEN序列化器单元测试
"""

import pytest

from chess_ai.board import Board
from chess_ai.rules import FENSerializer


class TestFENSerializer:
    """测试FEN序列化与反序列化"""

    def test_to_fen_empty_board(self) -> None:
        """空棋盘生成正确FEN"""
        board = Board()
        fen = FENSerializer.to_fen(board)
        assert fen == "9/9/9/9/9/9/9/9/9/9 w -"

    def test_to_fen_initial_board(self) -> None:
        """初始棋盘生成正确FEN"""
        board = Board.create_initial()
        fen = FENSerializer.to_fen(board)
        assert fen == "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w -"

    def test_to_fen_with_piece(self) -> None:
        """单棋子棋盘生成正确FEN"""
        board = Board()
        board = board.set_piece((0, 0), "r")
        fen = FENSerializer.to_fen(board)
        assert fen == "r8/9/9/9/9/9/9/9/9/9 w -"

    def test_to_fen_multiple_rows(self) -> None:
        """多行棋子生成正确FEN"""
        board = Board()
        board = board.set_piece((0, 0), "r")
        board = board.set_piece((0, 8), "R")
        board = board.set_piece((9, 0), "b")
        board = board.set_piece((9, 8), "B")
        fen = FENSerializer.to_fen(board)
        assert fen == "r7R/9/9/9/9/9/9/9/9/b7B w -"

    def test_roundtrip_empty_board(self) -> None:
        """空棋盘往返序列化"""
        original = Board()
        fen = FENSerializer.to_fen(original)
        restored = FENSerializer.from_fen(fen)
        assert FENSerializer.to_fen(restored) == fen

    def test_roundtrip_initial_board(self) -> None:
        """初始棋盘往返序列化"""
        original = Board.create_initial()
        fen = FENSerializer.to_fen(original)
        restored = FENSerializer.from_fen(fen)
        assert FENSerializer.to_fen(restored) == fen

    def test_roundtrip_custom_board(self) -> None:
        """自定义棋盘往返序列化"""
        original = Board()
        original = original.set_piece((5, 4), "R")
        original = original.set_piece((4, 4), "r")
        original = original.set_piece((0, 0), "k")
        original = original.set_piece((9, 0), "K")
        fen = FENSerializer.to_fen(original)
        restored = FENSerializer.from_fen(fen)
        assert FENSerializer.to_fen(restored) == fen

    def test_from_fen_empty_board(self) -> None:
        """从空棋盘FEN重建"""
        fen = "9/9/9/9/9/9/9/9/9/9 w"
        board = FENSerializer.from_fen(fen)
        for row in range(10):
            for col in range(9):
                assert board.get_piece((row, col)) is None

    def test_from_fen_initial_position(self) -> None:
        """从初始位置FEN重建"""
        fen = "rnbakabnr/1c5c1/9/p1p1p1p1p/9/9/P1P1P1P1P/9/1C5C1/RNBAKABNR w"
        board = FENSerializer.from_fen(fen)
        assert board.get_piece((0, 0)) == "r"
        assert board.get_piece((9, 0)) == "R"
        assert board.get_piece((0, 4)) == "k"
        assert board.get_piece((9, 4)) == "K"

    def test_from_fen_with_piece(self) -> None:
        """从单棋子FEN重建"""
        fen = "r8/9/9/9/9/9/9/9/9/9 w"
        board = FENSerializer.from_fen(fen)
        assert board.get_piece((0, 0)) == "r"
        assert board.get_piece((0, 1)) is None

    def test_from_fen_invalid_format_raises(self) -> None:
        """非法FEN格式抛出异常"""
        with pytest.raises(ValueError):
            FENSerializer.from_fen("invalid")

    def test_from_fen_wrong_row_count_raises(self) -> None:
        """行数错误FEN抛出异常"""
        with pytest.raises(ValueError):
            FENSerializer.from_fen("r9/9/9/9/9")

    def test_from_fen_piece_count_raises(self) -> None:
        """每行列数错误FEN抛出异常"""
        with pytest.raises(ValueError):
            FENSerializer.from_fen("r10/9/9/9/9/9/9/9/9/9")

    def test_to_fen_row_order(self) -> None:
        """FEN行顺序正确(黑方在左上方)"""
        board = Board()
        board = board.set_piece((0, 0), "r")
        board = board.set_piece((9, 8), "R")
        fen = FENSerializer.to_fen(board)
        rows = fen.split()[0].split("/")
        assert rows[0].startswith("r")
        assert rows[9].endswith("R")

    def test_from_fen_with_half_move(self) -> None:
        """从带步数计数器的FEN重建"""
        fen = "r8/9/9/9/9/9/9/9/9/9 w - 5 12"
        board = FENSerializer.from_fen(fen)
        assert board.half_move_clock == 5
        assert board.full_move_number == 12
