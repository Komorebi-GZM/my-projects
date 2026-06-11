"""
棋子枚举与工具函数
"""

from enum import StrEnum

from .types import PieceChar


class PieceType(StrEnum):
    """棋子类型枚举"""

    KING = "K"
    ADVISOR = "A"
    BISHOP = "B"
    KNIGHT = "N"
    ROOK = "R"
    CANNON = "C"
    PAWN = "P"


# 棋子字符映射
PIECE_CHARS: dict[PieceType, str] = {
    PieceType.KING: "K",
    PieceType.ADVISOR: "A",
    PieceType.BISHOP: "B",
    PieceType.KNIGHT: "N",
    PieceType.ROOK: "R",
    PieceType.CANNON: "C",
    PieceType.PAWN: "P",
}

# 初始布局 - 每行9列，从上到下 (row=0 为黑方底线)
# 标准中国象棋初始位置（从底线开始数）：
# 第1行 (row 0): 黑底线 - 车 马 象 士 将 士 象 马 车
# 第2行 (row 1): 空
# 第3行 (row 2): 黑炮 - 空 炮 空 空 空 空 空 炮 空
# 第4行 (row 3): 黑卒 - 卒 空 卒 空 卒 空 卒 空 卒
# 第5行 (row 4): 楚河
# 第6行 (row 5): 汉界
# 第7行 (row 6): 红兵 - 兵 空 兵 空 兵 空 兵 空 兵
# 第8行 (row 7): 红炮 - 空 炮 空 空 空 空 空 炮 空
# 第9行 (row 8): 空
# 第10行 (row 9): 红底线 - 车 马 相 仕 帅 仕 相 马 车
INITIAL_BOARD: list[list[PieceChar | None]] = [
    ["r", "n", "b", "a", "k", "a", "b", "n", "r"],  # row 0: 黑方底线
    [None, None, None, None, None, None, None, None, None],  # row 1: 空
    [None, "c", None, None, None, None, None, "c", None],  # row 2: 黑方炮 (第3行)
    ["p", None, "p", None, "p", None, "p", None, "p"],  # row 3: 黑方卒 (第4行)
    [None, None, None, None, None, None, None, None, None],  # row 4: 楚河
    [None, None, None, None, None, None, None, None, None],  # row 5: 汉界
    ["P", None, "P", None, "P", None, "P", None, "P"],  # row 6: 红方兵 (第7行)
    [None, "C", None, None, None, None, None, "C", None],  # row 7: 红方炮 (第8行)
    [None, None, None, None, None, None, None, None, None],  # row 8: 空
    ["R", "N", "B", "A", "K", "A", "B", "N", "R"],  # row 9: 红方底线
]
