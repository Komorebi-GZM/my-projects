from agents.path_skill.coordinator import finalize_path_skill


def test_finalize_path_skill_merges_all_sections():
    """coordinator merges ability_dims, ladder, skills, resources into final output."""
    ability_dims = {
        "岗位名称": "数据分析师",
        "能力维度": ["SQL", "Python", "Tableau"]
    }
    ladder = {
        "step1_校园项目": "参加数学建模竞赛",
        "step2_实习title": "数据分析师实习",
        "step3_实习积累关键词": "SQL取数、Tableau可视化",
        "step4_秋招目标岗位": "数据分析师"
    }
    skills = [
        {"技能名": "SQL", "优先级": "高"},
        {"技能名": "Python", "优先级": "高"},
        {"技能名": "Tableau", "优先级": "中"}
    ]
    resources = [
        {"技能名": "SQL", "资源": [{"name": "B站-SQL", "url": "https://..."}]},
        {"技能名": "Python", "资源": [{"name": "B站-Python", "url": "https://..."}]},
        {"技能名": "Tableau", "资源": []}
    ]

    result = finalize_path_skill(ability_dims, ladder, skills, resources)

    assert isinstance(result, dict)
    assert "岗位名称" in result
    assert "能力维度" in result
    assert "阶梯路径" in result
    assert "推荐技能" in result
    assert "学习资源" in result
    assert result["岗位名称"] == "数据分析师"
    assert len(result["能力维度"]) == 3
    assert len(result["推荐技能"]) == 3
    assert len(result["学习资源"]) == 3