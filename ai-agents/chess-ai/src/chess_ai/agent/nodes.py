"""
Agent 工作流节点定义 - LangGraph 状态机节点

包含以下节点:
- prepare: 准备 Prompt 上下文
- call_llm: 调用 LLM 生成走子
- parse: 解析 LLM 输出为 UCCI
- validate: 校验走子合法性
- apply_move: 应用走子到棋盘
- check_termination: 检查终局状态
- retry: 重试准备
- fallback: 降级为随机合法走子
"""

from __future__ import annotations

import logging
import os
import random
from typing import Literal

from ..board import Board
from ..board.types import opposite_side
from ..infra import ConfigManager
from ..infra.difficulty import Difficulty, difficulty_to_temperature
from ..llm import (
    LLMClientFactory,
    MoveOutputParser,
    MoveRequest,
)
from ..rules import FENSerializer, GameTerminationChecker, RuleValidator
from .state import AgentState, GameStatus

logger = logging.getLogger(__name__)


def prepare_node(state: AgentState) -> AgentState:
    """
    准备阶段节点 - 准备 Prompt 上下文

    输入: AgentState (包含 fen, current_turn)
    输出: 更新后的 AgentState

    主要职责:
    - 从 Board 生成 FEN (如果还没有)
    - 注入状态到状态机
    """
    if not state.get("fen"):
        board = Board.create_initial()
        state["fen"] = FENSerializer.to_fen(board)

    state.setdefault("move_history", [])
    state.setdefault("retry_count", 0)
    state.setdefault("last_error", None)
    state.setdefault("game_status", "ongoing")
    state.setdefault("fen_history", [state["fen"]])
    state.setdefault("llm_move", None)
    state.setdefault("validated_move", None)
    state.setdefault("last_output", None)

    logger.debug(f"prepare: fen={state['fen'][:50]}..., turn={state['current_turn']}")

    return state


def call_llm_node(state: AgentState) -> AgentState:
    """
    调用 LLM 节点 - 调用大模型生成走子

    输入: AgentState (包含 fen, current_turn, retry_count, last_error)
    输出: 更新后的 AgentState (添加 llm_move, last_output)

    主要职责:
    - 构建 Prompt
    - 调用 LLM API
    - 记录原始输出
    """
    fen = state["fen"]
    side = state["current_turn"]

    config = ConfigManager()
    model_name = config.get("model.name", "deepseek-chat")
    provider = config.get("model.provider", "openai")

    base_url = config.get("model.base_url") or os.getenv(f"{provider.upper()}_BASE_URL")
    api_key = os.getenv(f"{provider.upper()}_API_KEY")

    difficulty = config.get_difficulty()
    temperature = difficulty_to_temperature(difficulty)

    board = FENSerializer.from_fen(fen)
    validator = RuleValidator()
    legal_moves = validator.get_legal_moves(board, side)
    valid_moves = [m.to_ucci() for m in legal_moves]

    if os.getenv("CHESS_LLM_MOCK", "").lower() in {"1", "true", "yes"}:
        if valid_moves:
            mock_move = random.choice(valid_moves)
            state["llm_move"] = None
            state["last_output"] = mock_move
            state["last_error"] = None
            logger.info(f"mock LLM 走子: {mock_move}")
        else:
            state["llm_move"] = None
            state["last_output"] = None
            state["last_error"] = "没有合法走子"
        return state

    request = MoveRequest(
        fen=fen,
        side=side,
        valid_moves=valid_moves,
        history=state.get("move_history", [])[-5:],  # 最多5步历史
        prompt_version="minimal",
        thread_id=state.get("thread_id", ""),
        difficulty=difficulty.value if isinstance(difficulty, Difficulty) else str(difficulty),
    )

    try:
        client = LLMClientFactory.create(
            provider=provider,
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            timeout=config.get("model.timeout", 15),
            temperature=temperature,
        )

        response = client.invoke(request)

        if response.source == "error":
            raise Exception(response.error_message or "LLM 调用失败")

        raw_output = response.raw_output or ""
        state["llm_move"] = None  # 初始化，由 parse_node 填充
        state["last_output"] = raw_output

        logger.info(f"LLM 原始输出: {raw_output[:100]}...")

        client.close()

    except Exception as e:
        error_str = str(e)
        logger.error(f"LLM 调用异常: {e}")
        state["last_error"] = f"LLM 调用失败: {e}"
        state["llm_move"] = None
        state["last_output"] = None

        if any(code in error_str for code in ("401", "403", "Authorization")):
            state["retry_count"] = 999  # 强制超过重试上限

    return state


def parse_node(state: AgentState) -> AgentState:
    """
    解析节点 - 解析 LLM 输出为 UCCI 坐标

    输入: AgentState (包含 llm_move/raw_output, valid_moves)
    输出: 更新后的 AgentState (添加 llm_move)

    主要职责:
    - 调用 MoveOutputParser 解析原始输出
    - 提取 UCCI 坐标
    """
    raw_output = state.get("last_output", "") or ""
    fen = state["fen"]
    side = state["current_turn"]

    board = FENSerializer.from_fen(fen)
    validator = RuleValidator()
    legal_moves = validator.get_legal_moves(board, side)
    valid_moves = [m.to_ucci() for m in legal_moves]

    if raw_output:
        parsed_move = MoveOutputParser.parse(raw_output, valid_moves)
        state["llm_move"] = parsed_move
        logger.debug(f"parse: 原始输出='{raw_output}' -> 解析结果={parsed_move}")
    else:
        state["llm_move"] = None
        state["last_error"] = "LLM 未返回有效输出"
        logger.warning("parse: LLM 未返回有效输出")

    return state


def validate_node(state: AgentState) -> AgentState:
    """
    校验节点 - 校验走子合法性

    输入: AgentState (包含 fen, current_turn, llm_move)
    输出: 更新后的 AgentState (添加 validated_move)

    主要职责:
    - 调用 RuleValidator 校验走子
    - 如果非法，注入错误信息
    """
    fen = state["fen"]
    side = state["current_turn"]
    llm_move = state.get("llm_move")

    if not llm_move:
        state["validated_move"] = None
        state["last_error"] = "无法解析 LLM 输出"
        return state

    board = FENSerializer.from_fen(fen)
    validator = RuleValidator()
    legal_moves = validator.get_legal_moves(board, side)
    valid_moves = [m.to_ucci() for m in legal_moves]

    if llm_move in valid_moves:
        state["validated_move"] = llm_move
        state["last_error"] = None
        logger.info(f"validate: 走子 {llm_move} 合法")
    else:
        state["validated_move"] = None
        state["last_error"] = f"走子 {llm_move} 不在合法走子列表中"
        logger.warning(f"validate: 走子 {llm_move} 非法")

    return state


def apply_move_node(state: AgentState) -> AgentState:
    """
    应用走子节点 - 将校验通过的走子应用到棋盘

    输入: AgentState (包含 fen, current_turn, validated_move)
    输出: 更新后的 AgentState (更新 fen, move_history, fen_history)

    主要职责:
    - 应用走子生成新棋盘
    - 更新 FEN 历史
    - 切换走子方
    """
    fen = state["fen"]
    side = state["current_turn"]
    validated_move = state.get("validated_move")

    if not validated_move:
        logger.warning("apply_move: 没有有效走子，跳过")
        return state

    board = FENSerializer.from_fen(fen)
    validator = RuleValidator()
    legal_moves = validator.get_legal_moves(board, side)
    move_obj = next((m for m in legal_moves if m.to_ucci() == validated_move), None)

    if not move_obj:
        logger.error(f"apply_move: 找不到走子对象 {validated_move}")
        state["last_error"] = "走子对象不存在"
        return state

    new_board = validator.apply_move(board, move_obj)
    new_fen = FENSerializer.to_fen(new_board)

    state["fen"] = new_fen
    state["move_history"] = [*state.get("move_history", []), validated_move]
    state["fen_history"] = [*state.get("fen_history", []), new_fen]
    state["current_turn"] = opposite_side(side)

    logger.info(f"apply_move: {validated_move} -> 新 FEN: {new_fen[:50]}...")

    return state


def check_termination_node(state: AgentState) -> AgentState:
    """
    检查终局节点 - 检测游戏是否结束

    输入: AgentState (包含 fen, current_turn)
    输出: 更新后的 AgentState (添加 game_status)

    主要职责:
    - 调用 GameTerminationChecker 检测终局
    - 更新 game_status
    """
    fen = state["fen"]

    board = FENSerializer.from_fen(fen)
    checker = GameTerminationChecker()
    is_over, reason = checker.is_game_over(board)

    if is_over:
        reason_str: str = reason if reason else "draw"
        state["game_status"] = reason_str  # type: ignore[typeddict-item]
        logger.info(f"游戏结束: {reason}")
    else:
        state["game_status"] = "ongoing"

    return state


def retry_node(state: AgentState) -> AgentState:
    """
    重试节点 - 处理重试逻辑

    输入: AgentState (包含 retry_count, last_error, last_output)
    输出: 更新后的 AgentState (增加 retry_count, 更新 last_error)

    主要职责:
    - 增加重试计数
    - 更新错误信息用于 Prompt 注入
    """
    retry_count = state.get("retry_count", 0) + 1
    state["retry_count"] = retry_count

    last_output = str(state.get("last_output", "未知"))
    last_error = str(state.get("last_error", "未知错误"))
    state["last_error"] = f"上次输出: {last_output}。错误: {last_error}。请重新输出合法走子。"

    logger.warning(f"retry: 重试次数 {retry_count}, 错误: {last_error[:100]}")

    return state


def fallback_node(state: AgentState) -> AgentState:
    """
    降级节点 - 降级为随机合法走子

    输入: AgentState (包含 fen, current_turn)
    输出: 更新后的 AgentState (添加 validated_move，随机选择)

    主要职责:
    - 从合法走子列表中随机选择
    - 作为兜底策略
    """
    fen = state["fen"]
    side = state["current_turn"]

    board = FENSerializer.from_fen(fen)
    validator = RuleValidator()
    legal_moves = validator.get_legal_moves(board, side)

    if not legal_moves:
        logger.error("fallback: 没有合法走子可用")
        state["validated_move"] = None
        state["last_error"] = "没有合法走子"
        return state

    random_move = random.choice(legal_moves)
    random_ucci = random_move.to_ucci()

    state["validated_move"] = random_ucci
    state["last_error"] = None

    logger.info(f"fallback: 降级为随机走子 {random_ucci}")

    return state


def should_retry(state: AgentState) -> Literal["retry", "fallback", "apply"]:
    """
    条件分支判断 - 确定下一步流向

    返回值:
    - "retry": 重试 (走子非法但重试次数 < 3)
    - "fallback": 降级 (重试次数 >= 3 或其他不可重试错误)
    - "apply": 应用走子 (走子合法)
    """
    retry_count = state.get("retry_count", 0)
    validated_move = state.get("validated_move")
    last_error = state.get("last_error")

    if validated_move:
        return "apply"

    if last_error:
        if any(code in last_error for code in ("401", "403", "Authorization")):
            logger.warning(f"检测到认证错误，直接降级到 fallback: {last_error[:50]}...")
            return "fallback"

        if "超时" in last_error:
            return "fallback"

    # 根据难度获取最大重试次数
    config = ConfigManager()
    difficulty_str = config.get_difficulty()

    try:
        difficulty = Difficulty(difficulty_str)
    except ValueError:
        difficulty = Difficulty.MEDIUM  # 默认

    # 难度越高，重试次数越少（因为更期望精确结果）
    max_retries_map = {
        Difficulty.EASY: 5,  # 简单模式多重试，增加探索机会
        Difficulty.MEDIUM: 3,  # 中等模式标准重试
        Difficulty.HARD: 2,  # 困难模式少重试，快速失败转降级
    }
    max_retries = max_retries_map.get(difficulty, 3)

    if retry_count >= max_retries:
        return "fallback"

    return "retry"


def should_continue(state: AgentState) -> Literal["continue", "end"]:
    """
    继续判断 - 确定是否继续游戏

    返回值:
    - "continue": 继续游戏
    - "end": 游戏结束
    """
    game_status = state.get("game_status", GameStatus.ONGOING)

    if game_status == GameStatus.ONGOING:
        return "continue"

    return "end"
