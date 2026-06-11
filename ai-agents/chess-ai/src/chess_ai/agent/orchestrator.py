"""
Agent 编排器 - 对外统一接口
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from ..board import Board
from ..board.types import RED, Side
from ..rules import FENSerializer, GameTerminationChecker, RuleValidator
from .graph import ChessAgentGraph, run_single_turn
from .state import AgentState, GameStatus, create_initial_state

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Agent 编排器 - 封装 LangGraph 状态机，对外提供统一接口

    职责:
    - 管理对局生命周期
    - 处理用户走子和 AI 响应
    - 维护棋盘状态和历史
    - 协调规则引擎和 LLM 调用
    """

    def __init__(
        self,
        max_retries: int = 3,
        checkpoint_enabled: bool = True,
    ):
        """
        初始化 Agent 编排器

        Args:
            max_retries: 最大重试次数
            checkpoint_enabled: 是否启用检查点持久化
        """
        self._max_retries = max_retries
        self._checkpoint_enabled = checkpoint_enabled

        self._current_board: Board = Board.create_initial()
        self._thread_id: str = str(uuid.uuid4())
        self._game_over: bool = False
        self._game_result: str | None = None

        # 初始化状态机
        self._graph = ChessAgentGraph(checkpoint=checkpoint_enabled)
        self._agent: Any = self._graph.compile()

    @property
    def current_board(self) -> Board:
        """获取当前棋盘状态"""
        return self._current_board

    @property
    def thread_id(self) -> str:
        """获取当前对局 ID"""
        return self._thread_id

    @property
    def is_game_over(self) -> bool:
        """是否游戏结束"""
        return self._game_over

    @property
    def game_result(self) -> str | None:
        """获取游戏结果"""
        return self._game_result

    def reset(self) -> Board:
        """
        重置游戏

        Returns:
            新的初始棋盘
        """
        self._current_board = Board.create_initial()
        self._thread_id = str(uuid.uuid4())
        self._game_over = False
        self._game_result = None

        logger.info("游戏已重置")
        return self._current_board

    def process_user_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> tuple[bool, str]:
        """
        处理用户走子

        Args:
            from_pos: 起始位置 (row, col)
            to_pos: 目标位置 (row, col)

        Returns:
            (是否成功, 消息)
        """

        if self._game_over:
            return False, "游戏已结束"

        # 获取当前方
        current_turn = self._current_board.current_turn
        if current_turn != RED:
            return False, "当前不是你的回合"

        # 验证走子
        validator = RuleValidator()
        legal_moves = validator.get_legal_moves(self._current_board, RED)

        # 找到匹配的合法走子
        target_move = None
        for move in legal_moves:
            if move.from_pos == from_pos and move.to_pos == to_pos:
                target_move = move
                break

        if target_move is None:
            return False, "非法走子"

        # 应用走子
        new_board = validator.apply_move(self._current_board, target_move)

        # 更新状态
        self._current_board = new_board

        # 检查终局
        checker = GameTerminationChecker()
        is_over, reason = checker.is_game_over(new_board)
        if is_over:
            self._game_over = True
            self._game_result = reason

        logger.info(f"用户走子: {target_move.to_ucci()}")
        return True, "走子成功"

    def generate_ai_move(self) -> tuple[str | None, str | None]:
        """
        生成 AI 走子

        Returns:
            (走子 UCCI, 错误信息)，如果成功则错误信息为 None
        """
        if self._game_over:
            return None, "游戏已结束"

        current_turn = self._current_board.current_turn

        # 创建初始状态
        initial_state = create_initial_state(
            fen=FENSerializer.to_fen(self._current_board),
            current_turn=current_turn,
            thread_id=self._thread_id,
        )

        # 配置
        config = {"configurable": {"thread_id": self._thread_id}}

        try:
            # 执行状态机
            result_state = run_single_turn(self._agent, initial_state, config)

            # 获取走子
            validated_move = result_state.get("validated_move")

            if not validated_move:
                return None, result_state.get("last_error") or "AI 未能生成有效走子"

            # 应用走子到棋盘
            board = FENSerializer.from_fen(result_state["fen"])
            self._current_board = board

            # 检查终局
            checker = GameTerminationChecker()
            is_over, reason = checker.is_game_over(board)
            if is_over:
                self._game_over = True
                self._game_result = reason

            logger.info(f"AI 走子: {validated_move}")
            return validated_move, None

        except Exception as e:
            logger.exception(f"AI 生成走子异常: {e}")
            return None, str(e)

    def undo_move(self, steps: int = 1) -> bool:
        """
        悔棋

        Args:
            steps: 回退步数

        Returns:
            是否成功悔棋
        """
        if self._checkpoint_enabled:
            try:
                config = {"configurable": {"thread_id": self._thread_id}}
                history = list(self._agent.get_state_history(config))

                if len(history) <= steps:
                    return False

                # 回退到指定检查点
                target_checkpoint = history[steps].config
                self._agent.invoke(None, config=target_checkpoint)

                # 重新获取状态
                state = self._agent.get_state(config)
                self._current_board = FENSerializer.from_fen(state["fen"])

                logger.info(f"悔棋成功，回退了 {steps} 步")
                return True

            except Exception as e:
                logger.error(f"悔棋失败: {e}")
                return False

        logger.warning("悔棋功能需要启用检查点")
        return False

    def get_legal_moves(self, side: Side | None = None) -> list[str]:
        """
        获取当前合法走子列表

        Args:
            side: 哪一方的走子，默认当前回合方

        Returns:
            合法走子 UCCI 列表
        """
        if side is None:
            side = self._current_board.current_turn

        validator = RuleValidator()
        legal_moves = validator.get_legal_moves(self._current_board, side)
        return [m.to_ucci() for m in legal_moves]

    def get_piece_legal_targets(self, position: tuple[int, int]) -> list[tuple[int, int]]:
        """
        获取指定棋子的合法目标位置。

        Args:
            position: 棋子位置 (row, col)

        Returns:
            合法目标位置列表
        """
        row, col = position
        validator = RuleValidator()
        legal_moves = validator.get_piece_legal_moves(self._current_board, row, col)
        return [move.to_pos for move in legal_moves]

    def get_check_position(self, side: Side) -> tuple[int, int] | None:
        """
        获取被将军一方的将帅位置。

        Args:
            side: 要检查的一方

        Returns:
            被将军时返回将帅位置，否则返回 None
        """
        validator = RuleValidator()
        if not validator.is_in_check(self._current_board, side):
            return None
        return self._current_board.get_king_position(side)

    def restore_board(self, board: Board) -> None:
        """
        恢复当前棋盘状态。

        Args:
            board: 要恢复的棋盘
        """
        self._current_board = board
        checker = GameTerminationChecker()
        is_over, reason = checker.is_game_over(board)
        self._game_over = is_over
        self._game_result = reason

    def get_state(self) -> dict:
        """
        获取当前游戏状态摘要

        Returns:
            状态字典
        """
        return {
            "fen": FENSerializer.to_fen(self._current_board),
            "current_turn": self._current_board.current_turn,
            "game_over": self._game_over,
            "game_result": self._game_result,
            "thread_id": self._thread_id,
            "legal_moves_count": len(self.get_legal_moves()),
        }

    def load_game(self, state: AgentState) -> None:
        """
        加载游戏状态

        Args:
            state: AgentState 状态
        """
        fen = state.get("fen", "")
        if fen:
            self._current_board = FENSerializer.from_fen(fen)

        self._thread_id = state.get("thread_id", str(uuid.uuid4()))
        self._game_over = state.get("game_status") != GameStatus.ONGOING
        self._game_result = state.get("last_error")

    def export_state(self) -> AgentState:
        """
        导出当前状态

        Returns:
            AgentState
        """
        return create_initial_state(
            fen=FENSerializer.to_fen(self._current_board),
            current_turn=self._current_board.current_turn,
            thread_id=self._thread_id,
        )
