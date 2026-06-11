"""
AI 难度系统单元测试
"""

from chess_ai.infra.difficulty import Difficulty, difficulty_to_temperature


class TestDifficulty:
    """测试 Difficulty 枚举"""

    def test_easy_value(self) -> None:
        """Easy 枚举值为 'easy'"""
        assert Difficulty.EASY.value == "easy"

    def test_medium_value(self) -> None:
        """Medium 枚举值为 'medium'"""
        assert Difficulty.MEDIUM.value == "medium"

    def test_hard_value(self) -> None:
        """Hard 枚举值为 'hard'"""
        assert Difficulty.HARD.value == "hard"

    def test_all_values(self) -> None:
        """枚举包含全部三个级别"""
        values = {d.value for d in Difficulty}
        assert values == {"easy", "medium", "hard"}


class TestDifficultyToTemperature:
    """测试难度到温度的映射"""

    def test_easy_maps_to_0_8(self) -> None:
        """Easy 难度映射到 0.8 温度"""
        assert difficulty_to_temperature(Difficulty.EASY) == 0.8

    def test_medium_maps_to_0_3(self) -> None:
        """Medium 难度映射到 0.3 温度"""
        assert difficulty_to_temperature(Difficulty.MEDIUM) == 0.3

    def test_hard_maps_to_0_1(self) -> None:
        """Hard 难度映射到 0.1 温度"""
        assert difficulty_to_temperature(Difficulty.HARD) == 0.1

    def test_returns_float(self) -> None:
        """返回值始终为 float"""
        for difficulty in Difficulty:
            temp = difficulty_to_temperature(difficulty)
            assert isinstance(temp, float)


class TestDifficultyIntegration:
    """集成测试：难度枚举与温度映射端到端"""

    def test_sorted_by_temperature(self) -> None:
        """温度随难度递增：Easy > Medium > Hard"""
        temps = {d: difficulty_to_temperature(d) for d in Difficulty}
        assert temps[Difficulty.EASY] > temps[Difficulty.MEDIUM] > temps[Difficulty.HARD]
