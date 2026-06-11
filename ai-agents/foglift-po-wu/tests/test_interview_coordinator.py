from agents.interview.coordinator import finalize_interview


def test_finalize_interview_merges_analysis_and_encouragement():
    """coordinator merges analysis and encouragement into final output."""
    analysis = {
        "内容分": 85,
        "逻辑分": 70,
        "匹配分": 80,
        "总分": 79
    }
    encouragement = {
        "敢投指数": 79,
        "鼓励语": "你回答得很棒！",
        "亮点": ["逻辑清晰"],
        "建议": "可以再丰富一下项目经历"
    }

    result = finalize_interview(analysis, encouragement)

    assert isinstance(result, dict)
    assert "评分" in result
    assert "敢投指数" in result
    assert "鼓励语" in result
    assert result["敢投指数"] == 79
    assert result["评分"]["总分"] == 79