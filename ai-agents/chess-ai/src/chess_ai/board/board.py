"""
棋盘类 - 象棋状态的不可变数据载体
"""

from __future__ import annotations

from .exceptions import OutOfBoundError
from .pieces import INITIAL_BOARD
from .types import RED, BoardGrid, PieceChar, Position, Side


class Board:
    """
    象棋棋盘状态 - 不可变数据载体

    属性:
        grid: 10×9 二维数组，存储棋子字符或 None
        current_turn: 当前走子方 ('red' 或 'black')
        half_move_clock: 半回合计数器
        full_move_number: 完整回合数
        fen_history: 历史 FEN 列表
        move_history: 走子历史记录
    """

    __slots__ = (
        "_current_turn",
        "_fen_history",
        "_full_move_number",
        "_grid",
        "_half_move_clock",
        "_move_history",
    )

    def __init__(
        self,
        grid: BoardGrid | None = None,
        current_turn: Side = RED,
        half_move_clock: int = 0,
        full_move_number: int = 1,
        fen_history: list[str] | None = None,
        move_history: list[tuple[Position, Position, PieceChar, PieceChar | None]] | None = None,
    ) -> None:
        """
        初始化棋盘

        Args:
            grid: 棋盘状态 (10×9)，None 表示使用空棋盘
            current_turn: 当前走子方
            half_move_clock: 半回合计数器
            full_move_number: 完整回合数
            fen_history: 历史 FEN 列表
            move_history: 走子历史记录
        """
        if grid is None:
            # 创建空棋盘
            self._grid: BoardGrid = [[None for _ in range(9)] for _ in range(10)]
        else:
            # 深拷贝以确保不可变性
            self._grid = [row[:] for row in grid]

        self._current_turn: Side = current_turn
        self._half_move_clock: int = half_move_clock
        self._full_move_number: int = full_move_number
        self._fen_history: list[str] = fen_history[:] if fen_history else []
        self._move_history: list[tuple[Position, Position, PieceChar, PieceChar | None]] = (
            move_history[:] if move_history else []
        )

    @classmethod
    def create_initial(cls) -> Board:
        """
        创建标准初始布局的棋盘

        Returns:
            新的 Board 实例，包含标准开局布局
        """
        # 初始状态下，红方先走
        return cls(
            grid=INITIAL_BOARD, current_turn=RED, half_move_clock=0, full_move_number=1, fen_history=[], move_history=[]
        )

    def reset(self) -> Board:
        """
        重置为标准初始布局

        Returns:
            新的 Board 实例，处于初始状态
        """
        return self.create_initial()

    def get_piece(self, pos: Position) -> PieceChar | None:
        """
        获取指定位置的棋子

        Args:
            pos: (row, col) 坐标，0 <= row <= 9, 0 <= col <= 8

        Returns:
            位置上的棋子字符，若为空则返回 None

        Raises:
            OutOfBoundError: 当坐标超出棋盘范围时
        """
        row, col = pos
        if not (0 <= row <= 9 and 0 <= col <= 8):
            raise OutOfBoundError(row, col)
        return self._grid[row][col]

    def set_piece(self, pos: Position, piece: PieceChar | None) -> Board:
        """
        在指定位置放置棋子（返回新棋盘）

        Args:
            pos: (row, col) 坐标
            piece: 要放置的棋子字符，None 表示清空该位置

        Returns:
            新的 Board 实例（原棋盘不变）

        Raises:
            OutOfBoundError: 当坐标超出棋盘范围时
        """
        row, col = pos
        if not (0 <= row <= 9 and 0 <= col <= 8):
            raise OutOfBoundError(row, col)

        # 创建新网格的深拷贝
        new_grid = [r[:] for r in self._grid]
        new_grid[row][col] = piece

        return Board(
            grid=new_grid,
            current_turn=self._current_turn,
            half_move_clock=self._half_move_clock,
            full_move_number=self._full_move_number,
            fen_history=self._fen_history,
            move_history=self._move_history,
        )

    def remove_piece(self, pos: Position) -> Board:
        """
        从指定位置移除棋子（返回新棋盘）

        Args:
            pos: (row, col) 坐标

        Returns:
            新的 Board 实例（原棋盘不变）

        Raises:
            OutOfBoundError: 当坐标超出棋盘范围时
        """
        return self.set_piece(pos, None)

    def is_empty(self, pos: Position) -> bool:
        """
        检查指定位置是否为空

        Args:
            pos: (row, col) 坐标

        Returns:
            位置为空时返回 True，否则返回 False

        Raises:
            OutOfBoundError: 当坐标超出棋盘范围时
        """
        return self.get_piece(pos) is None

    def get_king_position(self, color: Side) -> Position:
        """
        查找指定方的王（帅/将）位置

        Args:
            color: 要查找的方 ('red' 或 'black')

        Returns:
            国王的位置 (row, col)

        Raises:
            ValueError: 当找不到指定方的国王时（理论上不应发生）
        """
        king_piece = "K" if color == RED else "k"
        for row in range(10):
            for col in range(9):
                if self._grid[row][col] == king_piece:
                    return (row, col)
        raise ValueError(f"找不到 {color} 方的国王")

    def copy(self) -> Board:
        """
        创建棋盘的深拷贝

        Returns:
            新的 Board 实例，包含与当前棋盘相同的状态
        """
        return Board(
            grid=[row[:] for row in self._grid],
            current_turn=self._current_turn,
            half_move_clock=self._half_move_clock,
            full_move_number=self._full_move_number,
            fen_history=self._fen_history[:],
            move_history=self._move_history[:],
        )

    # 属性访问器（便于调试和内部使用）
    @property
    def grid(self) -> BoardGrid:
        """棋盘网格（只读）"""
        return [row[:] for row in self._grid]  # 返回拷贝以保持不可变性

    @property
    def current_turn(self) -> Side:
        """当前走子方"""
        return self._current_turn

    @property
    def half_move_clock(self) -> int:
        """半回合计数器"""
        return self._half_move_clock

    @property
    def full_move_number(self) -> int:
        """完整回合数"""
        return self._full_move_number

    @property
    def fen_history(self) -> list[str]:
        """历史 FEN 列表"""
        return self._fen_history[:]

    @property
    def move_history(self) -> list[tuple[Position, Position, PieceChar, PieceChar | None]]:
        """走子历史记录"""
        return self._move_history[:]

    def __eq__(self, other: object) -> bool:
        """检查两个棋盘是否状态相等"""
        if not isinstance(other, Board):
            return False
        return (
            self._grid == other._grid
            and self._current_turn == other._current_turn
            and self._half_move_clock == other._half_move_clock
            and self._full_move_number == other._full_move_number
            and self._fen_history == other._fen_history
            and self._move_history == other._move_history
        )

    def __repr__(self) -> str:
        """调试用字符串表示"""
        return (
            f"Board(turn={self._current_turn}, half_move={self._half_move_clock}, full_move={self._full_move_number})"
        )
