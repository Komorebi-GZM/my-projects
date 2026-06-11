"""
LLM Prompt 与输出解析集成测试。
"""

from __future__ import annotations

from chess_ai.llm import MoveOutputParser, MoveRequest, PromptBuilder


def test_prompt_valid_moves_can_round_trip_through_parser() -> None:
    """Prompt 中给出的合法走子能从带噪声模型输出中解析回来。"""
    valid_moves = ["h2e2", "a3a4", "b2b5"]
    request = MoveRequest(
        fen="rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w -",
        side="red",
        valid_moves=valid_moves,
        history=["a9a8"],
        difficulty="medium",
    )

    prompt = PromptBuilder.build(request)
    parsed_move = MoveOutputParser.parse("根据局势，我选择 h2-e2。", valid_moves)

    assert "h2e2" in prompt
    assert "a3a4" in prompt
    assert parsed_move == "h2e2"
