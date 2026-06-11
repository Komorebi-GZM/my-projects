def coordinate(jd_parsed: dict, jargon_translated: dict, gaps: dict) -> dict:
    """Merge JD parse, jargon translation, and gap analysis into final output."""
    return {
        "硬技能": jd_parsed.get("硬技能", []),
        "软技能": jd_parsed.get("软技能", []),
        "经验要求": jd_parsed.get("经验要求", ""),
        "学历要求": jd_parsed.get("学历要求", ""),
        "HR黑话翻译": jargon_translated,
        "差距分析": {
            "差距项": gaps.get("差距项", []),
            "弥补时间估计": gaps.get("弥补时间估计", "")
        }
    }