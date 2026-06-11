"""
走子类 - 象棋走子的不可变数据载体
"""

from __future__ import annotations

import re
from typing import ClassVar, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, field_validator

from chess_ai.board import Board
from chess_ai.board.types import Position

# Pydantic 2.9 cannot consume PEP 695 TypeAliasType for model fields.
MovePiece: TypeAlias = Literal["K", "A", "B", "N", "R", "C", "P", "k", "a", "b", "n", "r", "c", "p"]  # noqa: UP040


class Move(BaseModel):
    """
    象棋走子数据模型 - 不可变数据载体

    属性:
        from_pos: 起始位置 (row, col)，0 <= row <= 9, 0 <= col <= 8
        to_pos: 目标位置 (row, col)，同上
        piece: 被移动的棋子字符（单字符 FEN 格式）
        captured_piece: 被吃掉的棋子，若无则为空
    """

    VALID_PIECES: ClassVar[frozenset[str]] = frozenset("KABNRCPkabnrcp")

    model_config = ConfigDict(frozen=True)

    from_pos: tuple[int, int] = Field(description="起始位置 (row, col)")
    to_pos: tuple[int, int] = Field(description="目标位置 (row, col)")
    piece: MovePiece = Field(description="被移动的棋子字符")
    captured_piece: MovePiece | None = Field(
        default=None,
        description="被吃掉的棋子，无则为空",
    )

    @field_validator("from_pos", "to_pos")
    @classmethod
    def _validate_position(cls, v: Position) -> Position:
        row, col = v
        if not (0 <= row <= 9):
            raise ValueError(f"row must be 0-9, got {row}")
        if not (0 <= col <= 8):
            raise ValueError(f"col must be 0-8, got {col}")
        return v

    @field_validator("piece", "captured_piece")
    @classmethod
    def _validate_piece(cls, v: MovePiece | None) -> MovePiece | None:
        if v is None:
            return v
        if v not in cls.VALID_PIECES:
            raise ValueError(f"invalid piece: {v}")
        return v

    def is_capture(self) -> bool:
        """
        判断是否为吃子走法

        Returns:
            True 如果这个走法吃掉了对方棋子
        """
        return self.captured_piece is not None

    @staticmethod
    def _pos_to_ucci(pos: Position) -> str:
        """将内部坐标转换为 UCCI 坐标"""
        row, col = pos
        return chr(ord("a") + col) + str(9 - row)

    @staticmethod
    def _ucci_to_pos(ucci: str) -> Position:
        """将 UCCI 坐标转换为内部坐标"""
        col = ord(ucci[0]) - ord("a")
        row = 9 - int(ucci[1])
        return (row, col)

    def to_ucci(self) -> str:
        """
        转换为 UCCI 走子记谱法

        Returns:
            UCCI 格式字符串，如 "h2e2"
        """
        return self._pos_to_ucci(self.from_pos) + self._pos_to_ucci(self.to_pos)

    @classmethod
    def from_ucci(cls, ucci_str: str, board: Board) -> Move:
        """
        从 UCCI 字符串创建 Move 实例

        Args:
            ucci_str: UCCI 格式字符串，如 "h2e2"
            board: 当前棋盘状态（用于查找棋子）

        Returns:
            新的 Move 实例

        Raises:
            ValueError: 当 UCCI 格式无效或起始位置无棋子时
        """
        if not re.match(r"^[a-i][0-9][a-i][0-9]$", ucci_str):
            raise ValueError(f"Invalid UCCI format: {ucci_str}")

        from_pos = cls._ucci_to_pos(ucci_str[:2])
        to_pos = cls._ucci_to_pos(ucci_str[2:])

        piece = board.get_piece(from_pos)
        if piece is None:
            raise ValueError(f"No piece at {from_pos}")

        captured = board.get_piece(to_pos)

        return cls(from_pos=from_pos, to_pos=to_pos, piece=piece, captured_piece=captured)

    def __str__(self) -> str:
        """人类可读的走子描述"""
        piece_name = {
            "K": "帅",
            "A": "仕",
            "B": "相",
            "N": "马",
            "R": "车",
            "C": "炮",
            "P": "兵",
            "k": "将",
            "a": "士",
            "b": "象",
            "n": "马",
            "r": "车",
            "c": "炮",
            "p": "卒",
        }.get(self.piece, self.piece)

        from_col, from_row = self.from_pos[1], self.from_pos[0]
        to_col, to_row = self.to_pos[1], self.to_pos[0]

        col_names = {0: "一", 1: "二", 2: "三", 3: "四", 4: "五", 5: "六", 6: "七", 7: "八", 8: "九"}

        if self.piece.isupper():
            from_label = col_names.get(from_col, str(from_col + 1))
            to_label = col_names.get(to_col, str(to_col + 1))
        else:
            from_label = str(9 - from_col)
            to_label = str(9 - to_col)

        prefix = (
            "平"
            if from_row == to_row
            else (
                "进"
                if ((self.piece.isupper() and to_row < from_row) or (self.piece.islower() and to_row > from_row))
                else "退"
            )
        )

        capture = "吃" + piece_name if self.captured_piece else ""

        return f"{piece_name}{from_label}{prefix}{to_label}{capture}"

    def __repr__(self) -> str:
        """调试用的字符串表示"""
        return f"Move(from={self.from_pos}, to={self.to_pos}, piece={self.piece!r}, captured={self.captured_piece!r})"
