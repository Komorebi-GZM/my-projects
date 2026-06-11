import json
from agents.jd_translator.coordinator import coordinate


def test_coordinate_merges_all_sections():
    """coordinator merges jd + jargon + gaps into final output."""
    jd_parsed = {
        "硬技能": ["SQL", "Python"],
        "软技能": ["沟通能力"],
        "经验要求": "1-3年",
        "学历要求": "本科及以上",
        "HR黑话": ["抗压能力强"]
    }
    jargon_translated = {"抗压能力强": "需要加班，处理紧急需求"}
    gaps = {
        "差距项": [
            {"技能": "SQL", "差距描述": "缺乏数据库操作经验"},
            {"技能": "数据可视化", "差距描述": "未掌握Tableau/PowerBI"}
        ],
        "弥补时间估计": "约3个月系统学习"
    }

    result = coordinate(jd_parsed, jargon_translated, gaps)

    assert isinstance(result, dict)
    assert "硬技能" in result
    assert "软技能" in result
    assert "HR黑话翻译" in result
    assert "差距分析" in result
    assert result["HR黑话翻译"]["抗压能力强"] == "需要加班，处理紧急需求"
    assert len(result["差距分析"]["差距项"]) == 2
    assert result["差距分析"]["弥补时间估计"] == "约3个月系统学习"