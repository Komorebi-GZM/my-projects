"""
自定义异常类 - 中国象棋规则引擎
"""


class ChessEngineError(Exception):
    """象棋引擎基类异常"""

    pass


class OutOfBoundError(ChessEngineError):
    """坐标超出棋盘范围异常"""

    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        super().__init__(f"坐标 ({row}, {col}) 超出棋盘范围")


class IllegalMoveError(ChessEngineError):
    """非法走子异常"""

    def __init__(self, message: str = "非法走子") -> None:
        super().__init__(message)


class InvalidFENError(ChessEngineError):
    """FEN 格式错误异常"""

    def __init__(self, fen: str, message: str = "无效的 FEN 字符串") -> None:
        self.fen = fen
        super().__init__(f"{message}: {fen}")
