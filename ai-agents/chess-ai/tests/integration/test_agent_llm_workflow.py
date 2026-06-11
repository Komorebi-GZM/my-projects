"""
Agent/LLM 工作流集成测试。
"""

from __future__ import annotations

from unittest.mock import patch

from chess_ai.agent.graph import ChessAgentGraph
from chess_ai.agent.state import create_initial_state
from chess_ai.board import Board
from chess_ai.infra.difficulty import Difficulty
from chess_ai.llm import MoveRequest, MoveResponse
from chess_ai.rules import FENSerializer


class FakeLLMClient:
    """测试用 LLM 客户端。"""

    def __init__(self, raw_output: str) -> None:
        """初始化客户端。"""
        self.raw_output = raw_output
        self.requests: list[MoveRequest] = []
        self.closed = False

    def invoke(self, request: MoveRequest) -> MoveResponse:
        """返回预设走子，并记录请求。"""
        self.requests.append(request)
        return MoveResponse(move=None, source="llm", raw_output=self.raw_output, provider="fake")

    def close(self) -> None:
        """标记客户端已关闭。"""
        self.closed = True


def test_agent_graph_applies_llm_move_without_real_api() -> None:
    """Agent 图能使用 LLM 输出的合法走子完成一次状态推进。"""
    board = Board.create_initial()
    fen = FENSerializer.to_fen(board)
    state = create_initial_state(fen=fen, current_turn="red", thread_id="integration-agent-llm")
    fake_client = FakeLLMClient("我选择 h2e2。")

    with (
        patch("chess_ai.agent.nodes.ConfigManager") as config_cls,
        patch("chess_ai.agent.nodes.LLMClientFactory") as factory,
    ):
        config = config_cls.return_value
        config.get.side_effect = lambda key, default=None: {
            "model.name": "fake-model",
            "model.provider": "openai",
            "model.timeout": 15,
        }.get(key, default)
        config.get_difficulty.return_value = Difficulty.MEDIUM
        factory.create.return_value = fake_client

        result = ChessAgentGraph().invoke(state)

    assert result["validated_move"] == "h2e2"
    assert result["move_history"] == ["h2e2"]
    assert result["current_turn"] == "black"
    assert result["game_status"] == "ongoing"
    assert fake_client.closed is True
    assert fake_client.requests[0].valid_moves
    assert "h2e2" in fake_client.requests[0].valid_moves
    assert fake_client.requests[0].difficulty == "medium"
