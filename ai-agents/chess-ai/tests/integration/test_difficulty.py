"""
Integration tests for difficulty system end-to-end workflow.
Tests the full chain: ConfigManager -> Agent nodes -> LLM client -> prompt builder -> retry logic.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

from chess_ai.agent.nodes import call_llm_node, should_retry
from chess_ai.infra.config import ConfigManager
from chess_ai.infra.difficulty import Difficulty, difficulty_to_temperature
from chess_ai.llm import MoveRequest, PromptBuilder


class TestDifficultyIntegration:
    """End-to-end integration tests for difficulty system."""

    def setup_method(self) -> None:
        """Set up temporary config for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name) / "test_config.yaml"
        # Reset ConfigManager singleton for clean state
        ConfigManager._instance = None

    def teardown_method(self) -> None:
        """Clean up temporary config."""
        self.temp_dir.cleanup()
        ConfigManager._instance = None

    def _create_test_config(self, difficulty: str) -> Path:
        """Create a test config file with specified difficulty."""
        config_content = f"""
game:
  difficulty: "{difficulty}"
  human_side: "red"
  ai_side: "black"

model:
  name: "test-model"
  provider: "openai"
  temperature: 0.3
  max_tokens: 1000
  timeout: 10
  prompt_version: "minimal"

agent:
  max_retries: 3
  retry_delay: 0.5
"""
        self.temp_path.write_text(config_content.strip())
        return self.temp_path

    def test_easy_difficulty_end_to_end(self) -> None:
        """Test Easy difficulty flows through entire system correctly."""
        config_path = self._create_test_config("easy")

        # 1. ConfigManager reads difficulty correctly
        config = ConfigManager(config_path)
        assert config.get_difficulty() == Difficulty.EASY

        # 2. Temperature mapping is correct
        temperature = difficulty_to_temperature(config.get_difficulty())
        assert temperature == 0.8

        # 3. Prompt builder includes Easy difficulty hint
        request = MoveRequest(
            fen="rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1",
            side="red",
            valid_moves=["h2e2", "h2e3", "h2f2"],
            difficulty="easy",
        )
        prompt = PromptBuilder.build(request)
        assert "# 难度提示：你是在陪新手练习，请偶尔尝试非常规走子，体验象棋乐趣。" in prompt

        # 4. Retry logic uses Easy difficulty max_retries (5)
        with patch("chess_ai.agent.nodes.ConfigManager") as mock_config_cls:
            mock_config = mock_config_cls.return_value
            mock_config.get_difficulty.return_value = Difficulty.EASY

            state = {
                "retry_count": 4,
                "last_error": "Invalid move",
                "validated_move": None,
            }
            # With 4 retries (< 5 max for EASY), should retry
            assert should_retry(state) == "retry"

            # With 5 retries (>= 5 max for EASY), should fallback
            state["retry_count"] = 5
            assert should_retry(state) == "fallback"

        # 5. Verify ConfigManager persistence
        config.set_difficulty(Difficulty.EASY)
        config.save()

        # New instance should load the same difficulty
        new_config = ConfigManager(config_path)
        assert new_config.get_difficulty() == Difficulty.EASY

    def test_medium_difficulty_end_to_end(self) -> None:
        """Test Medium difficulty flows through entire system correctly."""
        config_path = self._create_test_config("medium")

        # 1. ConfigManager reads difficulty correctly
        config = ConfigManager(config_path)
        assert config.get_difficulty() == Difficulty.MEDIUM

        # 2. Temperature mapping is correct
        temperature = difficulty_to_temperature(config.get_difficulty())
        assert temperature == 0.3

        # 3. Prompt builder includes Medium difficulty hint
        request = MoveRequest(
            fen="rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1",
            side="red",
            valid_moves=["h2e2", "h2e3", "h2f2"],
            difficulty="medium",
        )
        prompt = PromptBuilder.build(request)
        assert "# 难度提示：保持稳定发挥，选择当前局面的合理走子。" in prompt

        # 4. Retry logic uses Medium difficulty max_retries (3)
        with patch("chess_ai.agent.nodes.ConfigManager") as mock_config_cls:
            mock_config = mock_config_cls.return_value
            mock_config.get_difficulty.return_value = Difficulty.MEDIUM

            state = {
                "retry_count": 2,
                "last_error": "Invalid move",
                "validated_move": None,
            }
            # With 2 retries (< 3 max for MEDIUM), should retry
            assert should_retry(state) == "retry"

            # With 3 retries (>= 3 max for MEDIUM), should fallback
            state["retry_count"] = 3
            assert should_retry(state) == "fallback"

    def test_hard_difficulty_end_to_end(self) -> None:
        """Test Hard difficulty flows through entire system correctly."""
        config_path = self._create_test_config("hard")

        # 1. ConfigManager reads difficulty correctly
        config = ConfigManager(config_path)
        assert config.get_difficulty() == Difficulty.HARD

        # 2. Temperature mapping is correct
        temperature = difficulty_to_temperature(config.get_difficulty())
        assert temperature == 0.1

        # 3. Prompt builder includes Hard difficulty hint
        request = MoveRequest(
            fen="rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1",
            side="red",
            valid_moves=["h2e2", "h2e3", "h2f2"],
            difficulty="hard",
        )
        prompt = PromptBuilder.build(request)
        assert "# 难度提示：这是高水平对局，请选择当前最优或次优走子。" in prompt

        # 4. Retry logic uses Hard difficulty max_retries (2)
        with patch("chess_ai.agent.nodes.ConfigManager") as mock_config_cls:
            mock_config = mock_config_cls.return_value
            mock_config.get_difficulty.return_value = Difficulty.HARD

            state = {
                "retry_count": 1,
                "last_error": "Invalid move",
                "validated_move": None,
            }
            # With 1 retry (< 2 max for HARD), should retry
            assert should_retry(state) == "retry"

            # With 2 retries (>= 2 max for HARD), should fallback
            state["retry_count"] = 2
            assert should_retry(state) == "fallback"

    def test_llm_client_receives_correct_temperature(self) -> None:
        """Test that LLMClientFactory receives correct temperature based on difficulty."""
        with (
            patch("chess_ai.agent.nodes.ConfigManager") as mock_config_cls,
            patch("chess_ai.agent.nodes.LLMClientFactory") as mock_llm_factory,
            patch("chess_ai.agent.nodes.FENSerializer") as mock_fen,
            patch("chess_ai.agent.nodes.RuleValidator") as mock_validator,
        ):
            # Setup mocks
            mock_config = mock_config_cls.return_value
            mock_config.get_difficulty.return_value = Difficulty.EASY
            mock_config.get.return_value = "deepseek-chat"  # model.name

            mock_validator_instance = mock_validator.return_value
            mock_validator_instance.get_legal_moves.return_value = []

            mock_client_instance = mock_llm_factory.create.return_value
            mock_client_instance.invoke.return_value = type(
                "obj", (object,), {"source": "success", "raw_output": "e2e4", "error_message": None}
            )()

            mock_fen.to_fen.return_value = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w -"
            mock_fen.from_fen.return_value = type("obj", (object,), {})()

            # Execute the node
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

            # Verify LLMClientFactory.create was called with correct temperature (0.8 for EASY)
            call_kwargs = mock_llm_factory.create.call_args[1]
            assert call_kwargs["temperature"] == 0.8

            # Verify difficulty was passed to MoveRequest
            # This is verified indirectly through the prompt builder test above

    def test_difficulty_persistence_via_save_load(self) -> None:
        """Test that difficulty setting persists correctly through save/load cycle."""
        # Start with medium difficulty
        config_path = self._create_test_config("medium")
        config = ConfigManager(config_path)

        # Change to hard
        config.set_difficulty(Difficulty.HARD)
        assert config.get_difficulty() == Difficulty.HARD

        # Save to file
        config.save()

        # Load fresh instance
        ConfigManager._instance = None  # Reset singleton
        new_config = ConfigManager(config_path)

        # Should preserve the hard difficulty setting
        assert new_config.get_difficulty() == Difficulty.HARD

        # Verify it's actually written to YAML
        content = config_path.read_text()
        assert "difficulty: hard" in content
