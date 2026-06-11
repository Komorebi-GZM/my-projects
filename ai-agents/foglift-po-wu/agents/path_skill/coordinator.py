def finalize_path_skill(ability_dims: dict, ladder: dict, skills: list, resources: list) -> dict:
    """Merge ability_dims, ladder, skills, resources into final output."""
    return {
        "岗位名称": ability_dims.get("岗位名称", ""),
        "能力维度": ability_dims.get("能力维度", []),
        "阶梯路径": ladder,
        "推荐技能": skills,
        "学习资源": resources
    }