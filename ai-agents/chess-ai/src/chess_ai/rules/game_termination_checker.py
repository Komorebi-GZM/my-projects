"""
终局检测器 - 象棋游戏结束状态检测
"""

from __future__ import annotations

from collections import defaultdict

from chess_ai.board import Board
from chess_ai.rules.fen_serializer import FENSerializer
from chess_ai.rules.rule_validator import RuleValidator


class GameTerminationChecker:
    """象棋终局状态检测器"""

    def __init__(self) -> None:
        """初始化终局检测器"""
        self.rule_validator = RuleValidator()

    def is_checkmate(self, board: Board, color: str) -> bool:
        """
        检查指定方是否被将死

        Args:
            board: 当前棋盘
            color: 要检查的方 ('red' 或 'black')

        Returns:
            True 如果被将死
        """
        # 将死 = 被将军 + 没有合法走子
        return (
            self.rule_validator.is_in_check(board, color)
            and len(self.rule_validator.get_legal_moves(board, color)) == 0
        )

    def is_stalemate(self, board: Board, color: str) -> bool:
        """
        检查指定方是否困毙（无合法走子但未被将军）

        Args:
            board: 当前棋盘
            color: 要检查的方 ('red' 或 'black')

        Returns:
            True 如果困毙
        """
        # 困毙 = 未被将军 + 没有合法走子
        return (
            not self.rule_validator.is_in_check(board, color)
            and len(self.rule_validator.get_legal_moves(board, color)) == 0
        )

    def is_threefold_repetition(self, board: Board) -> bool:
        """
        检查是否出现三次重复局面（和棋）

        Args:
            board: 当前棋盘

        Returns:
            True 如果出现三次重复局面
        """
        fen_history = board.fen_history
        if len(fen_history) < 3:
            return False

        # 只考虑棋子布局和回合，不计步数
        simplified_fens = []
        for fen in fen_history:
            parts = fen.split()[:2]  # 只取棋子布局和回合
            simplified_fens.append(" ".join(parts))

        # 当前局面也要算入历史
        current_fen = FENSerializer.to_fen(board)
        current_parts = current_fen.split()[:2]
        current_simplified = " ".join(current_parts)
        all_fens = [*simplified_fens, current_simplified]

        # 计数每个局面出现的次数
        counter: dict[str, int] = defaultdict(int)
        for fen in all_fens:
            counter[fen] += 1
            if counter[fen] >= 3:
                return True

        return False

    def is_perpetual_check(self, board: Board, color: str) -> bool:
        """
        检查是否构成长将（连续将军超过3次，长将方负）

        这个检测通常需要走子历史，这里实现简化版本：
        检查当前方是否可以持续将军而对方无法避免

        Args:
            board: 当前棋盘
            color: 要检查的方 ('red' 或 'black')

        Returns:
            True 如果构成长将
        """
        enemy_color = "black" if color == "red" else "red"

        try:
            if not self.rule_validator.is_in_check(board, enemy_color):
                return False
        except ValueError:
            return False

        try:
            legal_moves = self.rule_validator.get_legal_moves(board, color)
            enemy_legal_moves = self.rule_validator.get_legal_moves(board, enemy_color)
        except ValueError:
            return False

        if not legal_moves:
            return False

        checking_moves = []
        for move in legal_moves:
            try:
                new_board = self.rule_validator.apply_move(board, move)
                if self.rule_validator.is_in_check(new_board, enemy_color):
                    checking_moves.append(move)
            except ValueError:
                continue

        if not checking_moves:
            return False

        return len(enemy_legal_moves) == 0

    def is_game_over(self, board: Board) -> tuple[bool, str | None]:
        """
        检查游戏是否结束，并返回结束原因

        Args:
            board: 当前棋盘

        Returns:
            (is_over, reason) 元组
            reason 可能为: "red_checkmate", "black_checkmate",
                         "red_stalemate", "black_stalemate",
                         "threefold_repetition", "perpetual_check"
        """
        # 检查红方将死/困毙
        if self.is_checkmate(board, "red"):
            return True, "black_checkmate"  # 红方被将死 = 黑方获胜
        if self.is_stalemate(board, "red"):
            return True, "red_stalemate"

        # 检查黑方将死/困毙
        if self.is_checkmate(board, "black"):
            return True, "red_checkmate"  # 黑方被将死 = 红方获胜
        if self.is_stalemate(board, "black"):
            return True, "black_stalemate"

        # 检查和棋情况
        if self.is_threefold_repetition(board):
            return True, "threefold_repetition"

        # 注意：长将检测通常需要指定方向，这里简化处理
        # 实际中可能需要分别检查红长将和黑长将
        if self.is_perpetual_check(board, "red") or self.is_perpetual_check(board, "black"):
            return True, "perpetual_check"

        return False, None
