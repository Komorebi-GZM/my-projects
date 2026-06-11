def finalize_interview(analysis: dict, encouragement: dict) -> dict:
    """Merge analysis and encouragement into final output."""
    return {
        "评分": {
            "内容分": analysis.get("内容分", 0),
            "逻辑分": analysis.get("逻辑分", 0),
            "匹配分": analysis.get("匹配分", 0),
            "总分": analysis.get("总分", 0)
        },
        "敢投指数": encouragement.get("敢投指数", 0),
        "鼓励语": encouragement.get("鼓励语", ""),
        "亮点": encouragement.get("亮点", []),
        "建议": encouragement.get("建议", "")
    }