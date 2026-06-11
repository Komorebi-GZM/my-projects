"""
LangGraph 状态机定义与编译
"""

from __future__ import annotations

import logging
from typing import Any, Literal

from langgraph.graph import END, StateGraph

from .nodes import (
    apply_move_node,
    call_llm_node,
    check_termination_node,
    fallback_node,
    parse_node,
    prepare_node,
    retry_node,
    should_continue,
    should_retry,
    validate_node,
)
from .state import AgentState, create_initial_state

logger = logging.getLogger(__name__)


class ChessAgentGraph:
    """
    中国象棋 AI Agent 状态机图定义

    工作流:
    prepare -> call_llm -> parse -> validate -> (条件分支)
                                                    │
                        ┌─────────────────────────┼─────────────────────────┐
                        │                         │                         │
                        ▼                         ▼                         ▼
                    apply_move              retry (<3)                fallback
                        │                         │                         │
                        ▼                         ▼                         ▼
                check_termination    call_llm (循环)           apply_move (降级)
                        │                                              │
                        ▼                                              ▼
                ┌─────────────────┐                                  END
                │  条件继续判断   │
                └────────┬────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
           continue               end
              │                     │
              ▼                     ▼
             END                  END
    """

    def __init__(self, checkpoint: bool = False):
        """
        初始化状态机

        Args:
            checkpoint: 是否启用检查点持久化
        """
        self._checkpoint = checkpoint
        self._graph: StateGraph | None = None
        self._compiled: Any = None

    def build(self) -> StateGraph:
        """
        构建状态机图

        Returns:
            编译后的 StateGraph
        """
        if self._graph is not None:
            return self._graph

        # 创建状态图
        builder = StateGraph(AgentState)

        # 添加节点
        builder.add_node("prepare", prepare_node)
        builder.add_node("call_llm", call_llm_node)
        builder.add_node("parse", parse_node)
        builder.add_node("validate", validate_node)
        builder.add_node("apply_move", apply_move_node)
        builder.add_node("check_termination", check_termination_node)
        builder.add_node("retry", retry_node)
        builder.add_node("fallback", fallback_node)

        # 添加边
        # 主流程：prepare -> call_llm -> parse -> validate
        builder.add_edge("prepare", "call_llm")
        builder.add_edge("call_llm", "parse")
        builder.add_edge("parse", "validate")

        # 条件分支：validate -> apply_move / retry / fallback
        builder.add_conditional_edges(
            "validate",
            should_retry,
            {
                "apply": "apply_move",
                "retry": "retry",
                "fallback": "fallback",
            },
        )

        # retry 循环回 call_llm
        builder.add_edge("retry", "call_llm")

        # apply_move -> check_termination
        builder.add_edge("apply_move", "check_termination")

        # fallback 降级后也要应用走子
        builder.add_edge("fallback", "apply_move")

        # check_termination -> 继续或结束
        builder.add_conditional_edges(
            "check_termination",
            should_continue,
            {
                "continue": END,
                "end": END,
            },
        )

        # 设置入口点
        builder.set_entry_point("prepare")

        self._graph = builder
        return builder

    def compile(self) -> Any:
        """
        编译状态机

        Returns:
            编译后的可执行图
        """
        if self._compiled is not None:
            return self._compiled

        builder = self.build()

        # 检查点默认关闭（桌面应用，状态由 AgentOrchestrator 管理）
        # 如需启用检查点持久化，请设置 enable_checkpoint=True
        self._compiled = builder.compile()

        return self._compiled

    def invoke(
        self,
        state: AgentState | dict,
        config: dict | None = None,
    ) -> AgentState:
        """
        执行状态机

        Args:
            state: 初始状态
            config: LangGraph 配置（包含 thread_id 等）

        Returns:
            最终状态
        """
        graph = self.compile()
        result = graph.invoke(state, config=config)
        return result  # type: ignore[no-any-return]

    def get_state(self, config: dict) -> AgentState:
        """
        获取当前状态

        Args:
            config: LangGraph 配置

        Returns:
            当前状态
        """
        graph = self.compile()
        result = graph.get_state(config)
        return result  # type: ignore[no-any-return]

    def get_history(self, config: dict) -> list[AgentState]:
        """
        获取状态历史

        Args:
            config: LangGraph 配置

        Returns:
            状态历史列表
        """
        graph = self.compile()
        return list(graph.get_state_history(config))


def create_agent(
    thread_id: str,
    fen: str,
    current_turn: str = "black",
    enable_checkpoint: bool = True,
) -> tuple[Any, AgentState]:
    """
    创建并返回 Agent 实例和初始状态

    Args:
        thread_id: 对局唯一标识
        fen: 初始 FEN 字符串
        current_turn: 当前走子方
        enable_checkpoint: 是否启用检查点

    Returns:
        (编译后的 Agent, 初始状态)
    """
    if current_turn in ("red", "black"):
        current_turn_typed: Literal["red", "black"] = current_turn  # type: ignore[assignment]
    else:
        current_turn_typed = "black"
    graph = ChessAgentGraph(checkpoint=enable_checkpoint)
    initial_state = create_initial_state(fen, current_turn_typed, thread_id)

    return graph.compile(), initial_state


def run_single_turn(
    agent: Any,
    state: AgentState,
    config: dict,
) -> AgentState:
    """
    执行单回合

    Args:
        agent: 编译后的 Agent
        state: 当前状态
        config: LangGraph 配置

    Returns:
        更新后的状态
    """
    result = agent.invoke(state, config=config)
    return result  # type: ignore[no-any-return]
