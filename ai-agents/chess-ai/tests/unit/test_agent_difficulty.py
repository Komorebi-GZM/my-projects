"""
Agent 节点 difficulty 集成单元测试
"""

from unittest.mock import MagicMock, patch

from chess_ai.agent.nodes import call_llm_node
from chess_ai.infra.difficulty import Difficulty


class TestCallLLMNodeDifficulty:
    """测试 call_llm_node 根据 difficulty 调整 temperature"""

    @patch("chess_ai.agent.nodes.FENSerializer")
    @patch("chess_ai.agent.nodes.RuleValidator")
    @patch("chess_ai.agent.nodes.LLMClientFactory")
    @patch("chess_ai.agent.nodes.ConfigManager")
    def test_easy_sets_high_temperature(self, mock_config_cls, mock_llm_factory, mock_validator, mock_fen):
        """Easy 难度应将 temperature 设为 0.8"""
        mock_config = MagicMock()
        mock_config.get_difficulty.return_value = Difficulty.EASY
        mock_config_cls.return_value = mock_config

        mock_validator_instance = MagicMock()
        mock_validator.return_value = mock_validator_instance
        mock_validator_instance.get_legal_moves.return_value = []

        mock_client_instance = MagicMock()
        mock_llm_factory.create.return_value = mock_client_instance
        mock_client_instance.invoke.return_value = MagicMock(source="success", raw_output="e2e4", error_message=None)

        mock_fen.to_fen.return_value = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w -"
        mock_fen.from_fen.return_value = MagicMock()

        state = {
            "fen": "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w -",
            "current_turn": "red",
            "move_history": [],
            "retry_count": 0,
            "last_error": None,
            "game_status": "ongoing",
            "thread_id": "test-thread",
        }

        call_llm_node(state)

        call_kwargs = mock_llm_factory.create.call_args[1]
        assert call_kwargs["temperature"] == 0.8

    @patch("chess_ai.agent.nodes.FENSerializer")
    @patch("chess_ai.agent.nodes.RuleValidator")
    @patch("chess_ai.agent.nodes.LLMClientFactory")
    @patch("chess_ai.agent.nodes.ConfigManager")
    def test_hard_sets_low_temperature(self, mock_config_cls, mock_llm_factory, mock_validator, mock_fen):
        """Hard 难度应将 temperature 设为 0.1"""
        mock_config = MagicMock()
        mock_config.get_difficulty.return_value = Difficulty.HARD
        mock_config_cls.return_value = mock_config

        mock_validator_instance = MagicMock()
        mock_validator.return_value = mock_validator_instance
        mock_validator_instance.get_legal_moves.return_value = []

        mock_client_instance = MagicMock()
        mock_llm_factory.create.return_value = mock_client_instance
        mock_client_instance.invoke.return_value = MagicMock(source="success", raw_output="e2e4", error_message=None)

        mock_fen.to_fen.return_value = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w -"
        mock_fen.from_fen.return_value = MagicMock()

        state = {
            "fen": "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w -",
            "current_turn": "red",
            "move_history": [],
            "retry_count": 0,
            "last_error": None,
            "game_status": "ongoing",
            "thread_id": "test-thread",
        }

        call_llm_node(state)

        call_kwargs = mock_llm_factory.create.call_args[1]
        assert call_kwargs["temperature"] == 0.1

    @patch("chess_ai.agent.nodes.FENSerializer")
    @patch("chess_ai.agent.nodes.RuleValidator")
    @patch("chess_ai.agent.nodes.LLMClientFactory")
    @patch("chess_ai.agent.nodes.ConfigManager")
    def test_medium_sets_medium_temperature(self, mock_config_cls, mock_llm_factory, mock_validator, mock_fen):
        """Medium 难度应将 temperature 设为 0.3"""
        mock_config = MagicMock()
        mock_config.get_difficulty.return_value = Difficulty.MEDIUM
        mock_config_cls.return_value = mock_config

        mock_validator_instance = MagicMock()
        mock_validator.return_value = mock_validator_instance
        mock_validator_instance.get_legal_moves.return_value = []

        mock_client_instance = MagicMock()
        mock_llm_factory.create.return_value = mock_client_instance
        mock_client_instance.invoke.return_value = MagicMock(source="success", raw_output="e2e4", error_message=None)

        mock_fen.to_fen.return_value = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w -"
        mock_fen.from_fen.return_value = MagicMock()

        state = {
            "fen": "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w -",
            "current_turn": "red",
            "move_history": [],
            "retry_count": 0,
            "last_error": None,
            "game_status": "ongoing",
            "thread_id": "test-thread",
        }

        call_llm_node(state)

        call_kwargs = mock_llm_factory.create.call_args[1]
        assert call_kwargs["temperature"] == 0.3

    @patch.dict("os.environ", {"CHESS_LLM_MOCK": "true"})
    @patch("chess_ai.agent.nodes.FENSerializer")
    @patch("chess_ai.agent.nodes.RuleValidator")
    @patch("chess_ai.agent.nodes.LLMClientFactory")
    @patch("chess_ai.agent.nodes.ConfigManager")
    def test_mock_llm_uses_random_legal_move_without_client(
        self,
        mock_config_cls,
        mock_llm_factory,
        mock_validator,
        mock_fen,
    ):
        """Mock LLM 模式不应创建真实 LLM 客户端"""
        mock_config = MagicMock()
        mock_config.get_difficulty.return_value = Difficulty.EASY
        mock_config_cls.return_value = mock_config

        legal_move = MagicMock()
        legal_move.to_ucci.return_value = "h7h5"
        mock_validator_instance = MagicMock()
        mock_validator.return_value = mock_validator_instance
        mock_validator_instance.get_legal_moves.return_value = [legal_move]
        mock_fen.from_fen.return_value = MagicMock()

        state = {
            "fen": "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w -",
            "current_turn": "black",
            "move_history": [],
            "retry_count": 0,
            "last_error": None,
            "game_status": "ongoing",
            "thread_id": "test-thread",
        }

        result = call_llm_node(state)

        assert result["last_output"] == "h7h5"
        assert result["last_error"] is None
        mock_llm_factory.create.assert_not_called()
