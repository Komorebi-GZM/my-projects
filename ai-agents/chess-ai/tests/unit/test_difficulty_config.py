"""
难度配置单元测试
"""

import pytest

from chess_ai.infra.config import ConfigManager
from chess_ai.infra.difficulty import Difficulty


class TestDifficultyConfig:
    """测试 ConfigManager 的 difficulty 相关方法"""

    def test_get_difficulty_returns_enum(self) -> None:
        """get_difficulty() 返回 Difficulty 枚举"""
        config = ConfigManager()
        difficulty = config.get_difficulty()
        assert isinstance(difficulty, Difficulty)

    def test_get_difficulty_default_is_medium(self) -> None:
        """默认难度为 MEDIUM"""
        config = ConfigManager()
        assert config.get_difficulty() == Difficulty.MEDIUM

    def test_set_difficulty_accepts_enum(self) -> None:
        """set_difficulty() 接受 Difficulty 枚举"""
        config = ConfigManager()
        config.set_difficulty(Difficulty.HARD)
        assert config.get_difficulty() == Difficulty.HARD

    def test_set_difficulty_accepts_string(self) -> None:
        """set_difficulty() 接受小写字符串"""
        config = ConfigManager()
        config.set_difficulty("easy")
        assert config.get_difficulty() == Difficulty.EASY

    def test_set_difficulty_invalid_string_raises(self) -> None:
        """无效字符串抛出 ValueError"""
        config = ConfigManager()
        with pytest.raises(ValueError):
            config.set_difficulty("invalid")
