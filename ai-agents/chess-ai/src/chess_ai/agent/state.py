"""
Agent 状态定义 - LangGraph 状态机状态模型
"""

from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

from ..board.types import Side


class AgentState(TypedDict, total=False):
    """
    LangGraph Agent 状态定义

    字段说明:
        fen: 当前棋盘 FEN 字符串
        current_turn: 当前走子方 (red/black)
        move_history: 走子历史 (UCCI 格式)
        retry_count: 当前重试次数 (0-3)
        last_error: 上次错误信息 (用于 Prompt 引导)
        game_status: 游戏状态
        llm_move: LLM 生成的原始走子 (UCCI)
        validated_move: 校验通过的 Move 对象 (内部格式)
        thread_id: 对局唯一标识 (用于检查点隔离)
        last_output: 上次的原始输出 (用于错误修正)
        fen_history: FEN 历史列表 (用于三次重复检测)
    """

    fen: str
    current_turn: Side
    move_history: NotRequired[list[str]]
    retry_count: NotRequired[int]
    last_error: NotRequired[str | None]
    game_status: NotRequired[Literal["ongoing", "checkmate", "stalemate", "draw"]]
    llm_move: NotRequired[str | None]
    validated_move: NotRequired[str | None]
    thread_id: str
    last_output: NotRequired[str | None]
    fen_history: NotRequired[list[str]]


class GameStatus:
    """游戏状态常量"""

    ONGOING = "ongoing"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"
    ILLEGAL_MOVE = "illegal_move"


def create_initial_state(
    fen: str,
    current_turn: Side,
    thread_id: str,
) -> AgentState:
    """
    创建初始 Agent 状态

    Args:
        fen: 初始 FEN 字符串
        current_turn: 初始走子方
        thread_id: 对局唯一标识

    Returns:
        初始化的 AgentState
    """
    return AgentState(
        fen=fen,
        current_turn=current_turn,
        move_history=[],
        retry_count=0,
        last_error=None,
        game_status="ongoing",
        llm_move=None,
        validated_move=None,
        thread_id=thread_id,
        last_output=None,
        fen_history=[fen],
    )
