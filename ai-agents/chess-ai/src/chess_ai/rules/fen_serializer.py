"""
FEN序列化器 - 中国象棋棋盘状态与FEN字符串互转
"""

from __future__ import annotations

from typing import cast

from chess_ai.board import Board
from chess_ai.board.types import BoardGrid, PieceChar, Side


class FENSerializer:
    """FEN字符串与Board对象之间的序列化/反序列化"""

    @staticmethod
    def to_fen(board: Board, *, include_move_counters: bool = False) -> str:
        """
        将棋盘状态序列化为FEN字符串

        Args:
            board: 棋盘对象
            include_move_counters: 是否包含步数计数器

        Returns:
            FEN字符串 (如 "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w -")
        """
        # 1. 棋子布局
        rows: list[str] = []
        for r in range(10):
            empty_count = 0
            row_str = ""
            for c in range(9):
                piece = board.get_piece((r, c))
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += piece
            if empty_count > 0:
                row_str += str(empty_count)
            rows.append(row_str)

        fen = "/".join(rows)

        # 2. 当前回合 ('w'表示红方/'b'表示黑方)
        turn_char = "w" if board.current_turn == "red" else "b"
        fen += f" {turn_char}"

        # 3. 可用着法 (中国象棋无王车易位)
        fen += " -"

        return fen

    @staticmethod
    def from_fen(fen: str) -> Board:
        """
        从FEN字符串重建棋盘

        Args:
            fen: FEN字符串

        Returns:
            新的Board对象

        Raises:
            ValueError: FEN格式非法
        """
        fen = fen.strip()
        parts = fen.split()

        board_fen = parts[0]
        turn_fen = parts[1] if len(parts) > 1 else "w"

        half_move_clock = 0
        full_move_number = 1
        # FEN fields: position turn castling en_passant half_move full_move
        # parts[2] = castling/en passant, parts[3] = half-move clock, parts[4] = full-move
        if len(parts) >= 5:
            try:
                half_move_clock = int(parts[3])
                full_move_number = int(parts[4])
            except ValueError:
                raise ValueError(f"FEN步数计数器格式错误: {parts[3]} {parts[4]}")

        # 解析棋盘布局
        rows = board_fen.split("/")
        if len(rows) != 10:
            raise ValueError(f"FEN行数错误: 需要10行, 当前{len(rows)}行")

        grid: BoardGrid = [[None for _ in range(9)] for _ in range(10)]

        for r, row_fen in enumerate(rows):
            col = 0
            for ch in row_fen:
                if ch.isdigit():
                    count = int(ch)
                    if count < 1 or count > 9:
                        raise ValueError(f"FEN数字错误: {ch} 在第{r}行")
                    for _ in range(count):
                        if col >= 9:
                            raise ValueError(f"FEN列数溢出: 第{r}行")
                        grid[r][col] = None
                        col += 1
                else:
                    if col >= 9:
                        raise ValueError(f"FEN列数溢出: 第{r}行")
                    grid[r][col] = cast(PieceChar, ch)
                    col += 1

            if col != 9:
                raise ValueError(f"FEN第{r}行列数错误: 期望9列, 实际{col}列")

        # 解析回合
        current_turn: Side
        if turn_fen == "w":
            current_turn = "red"
        elif turn_fen == "b":
            current_turn = "black"
        else:
            raise ValueError(f"FEN回合字段错误: {turn_fen!r}")

        return Board(
            grid=grid,
            current_turn=current_turn,
            half_move_clock=half_move_clock,
            full_move_number=full_move_number,
        )
