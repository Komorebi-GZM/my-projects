"""
棋子类型与颜色定义
"""

from typing import Literal

# 类型别名
type PieceChar = Literal["K", "A", "B", "N", "R", "C", "P", "k", "a", "b", "n", "r", "c", "p"]
type Side = Literal["red", "black"]
type Position = tuple[int, int]  # (row, col)
type BoardGrid = list[list[PieceChar | None]]  # 10行 × 9列

# 颜色常量
RED: Side = "red"
BLACK: Side = "black"

# 棋子字符映射（红方大写，黑方小写）
PIECE_NAMES: dict[str, str] = {
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
}

# 颜色判定


def is_red(piece: PieceChar) -> bool:
    """判断棋子是否为红方"""
    return piece.isupper()


def is_black(piece: PieceChar) -> bool:
    """判断棋子是否为黑方"""
    return piece.islower()


def get_side(piece: PieceChar) -> Side:
    """获取棋子所属方"""
    return RED if is_red(piece) else BLACK


def opposite_side(side: Side) -> Side:
    """获取对方"""
    return BLACK if side == RED else RED
