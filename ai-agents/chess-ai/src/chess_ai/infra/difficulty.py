"""
AI 难度系统 - 难度枚举与温度映射
"""

from __future__ import annotations

from enum import StrEnum


class Difficulty(StrEnum):
    """
    AI 难度级别

    难度影响 LLM temperature，从而控制 AI 决策的随机性：
    - EASY: 更随机，适合新手
    - MEDIUM: 平衡，常规对弈
    - HARD: 精确，高水平对弈
    """

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


def difficulty_to_temperature(difficulty: Difficulty) -> float:
    """
    将难度映射为 LLM temperature

    Args:
        difficulty: 难度级别

    Returns:
        temperature 值 (0.0-1.0)

    映射规则:
        EASY   → 0.8 (高随机性，探索性走子)
        MEDIUM → 0.3 (平衡，稳定走子)
        HARD   → 0.1 (低随机性，精确走子)
    """
    mapping: dict[Difficulty, float] = {
        Difficulty.EASY: 0.8,
        Difficulty.MEDIUM: 0.3,
        Difficulty.HARD: 0.1,
    }
    return mapping[difficulty]
