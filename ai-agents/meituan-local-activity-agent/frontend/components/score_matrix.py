"""评分矩阵组件 — Agent 评审结果表格"""


def render_score_matrix(result: dict) -> str:
    """渲染评审评分矩阵。返回 HTML 字符串。"""
    r1 = result.get("round1_reviews", {})
    r2 = result.get("round2_reviews", {})
    candidates = result.get("candidates", [])
    final_score = result.get("final_score", 0)

    if not candidates or (not r1 and not r2):
        return ""

    # Agent 配置
    agent_config = {
        "体验Agent": {"icon": "🌟", "weight": 0.30, "color": "#F59E0B"},
        "安全Agent": {"icon": "🛡", "weight": 0.25, "color": "#EF4444"},
        "效率Agent": {"icon": "⚡", "weight": 0.20, "color": "#3B82F6"},
        "预算Agent": {"icon": "💰", "weight": 0.25, "color": "#10B981"},
    }

    # 收集每个 agent 每个 plan 的最终评分 (R2 覆盖 R1)
    scores = {}  # {agent_name: {candidate_id: {"score": x, "veto": bool}}}
    all_agents = set()

    for round_data in [r1, r2]:
        if not round_data:
            continue
        reviews = round_data.get("reviews", {})
        if not isinstance(reviews, dict):
            continue
        for agent_name, agent_reviews in reviews.items():
            all_agents.add(agent_name)
            if not isinstance(agent_reviews, dict):
                continue
            for cid, review in agent_reviews.items():
                if cid not in scores:
                    scores[cid] = {}
                if agent_name not in scores[cid]:
                    scores[cid][agent_name] = {}
                scores[cid][agent_name] = {
                    "score": review.get("score", 5.0) if not review.get("veto") else 0,
                    "veto": review.get("veto", False),
                    "veto_reason": review.get("veto_reason", ""),
                }

    if not scores:
        return ""

    # 方案列头
    plan_headers = ""
    for i, c in enumerate(candidates):
        cid = c.get("id", f"plan_{i}")
        label = c.get("name", f"方案 {chr(65 + i)}")
        # 截短名称
        if len(label) > 10:
            label = label[:10] + "..."
        plan_headers += f'<th style="text-align:center">{label}</th>'

    # Agent 行
    agent_rows = ""
    for agent_name in sorted(all_agents, key=lambda a: agent_config.get(a, {}).get("weight", 0), reverse=True):
        config = agent_config.get(agent_name, {"icon": "📋", "weight": 0.25, "color": "#6B7280"})
        weight_pct = int(config["weight"] * 100)

        cells = ""
        for i, c in enumerate(candidates):
            cid = c.get("id", f"plan_{i}")
            agent_data = scores.get(cid, {}).get(agent_name, {})

            if agent_data.get("veto"):
                cells += f'<td class="score-cell score-veto">否决</td>'
            else:
                score = agent_data.get("score", 0)
                score_class = "score-high" if score >= 7.5 else ("score-mid" if score >= 5.5 else "score-low")
                cells += f'<td class="score-cell {score_class}">{score:.1f}</td>'

        agent_rows += f"""
        <tr>
            <td>
                <div class="agent-name">
                    {config["icon"]} {agent_name}
                    <span class="agent-weight">{weight_pct}%</span>
                </div>
            </td>
            <td></td>
            {cells}
        </tr>"""

    # 最终加权分行
    final_cells = ""
    for i, c in enumerate(candidates):
        cid = c.get("id", f"plan_{i}")
        # 计算该方案的加权分
        agent_scores_for_plan = scores.get(cid, {})
        weighted_sum = 0
        total_weight = 0
        for aname, adata in agent_scores_for_plan.items():
            if adata.get("veto"):
                continue
            w = agent_config.get(aname, {}).get("weight", 0.25)
            weighted_sum += adata.get("score", 0) * w
            total_weight += w
        plan_score = weighted_sum / total_weight if total_weight > 0 else 0
        is_best = abs(plan_score - final_score) < 0.01
        style = 'font-weight:800; color: var(--primary-700);' if is_best else ''
        final_cells += f'<td class="score-cell final-score" style="{style}">{plan_score:.2f}</td>'

    return f"""
    <div class="section-header animate-in">
        <div class="section-icon" style="background: var(--warning-bg); color: var(--warning);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 20V10"/>
                <path d="M18 20V4"/>
                <path d="M6 20v-4"/>
            </svg>
        </div>
        <h2>AI 评审矩阵</h2>
        <span class="section-sub">双轮加权评审</span>
    </div>
    <div class="score-card animate-in animate-in-delay-1">
        <table class="score-table">
            <thead>
                <tr>
                    <th>评审维度</th>
                    <th>权重</th>
                    {plan_headers}
                </tr>
            </thead>
            <tbody>
                {agent_rows}
                <tr class="final-row">
                    <td colspan="2" style="font-weight:700; color: var(--primary-700);">
                        加权总分
                    </td>
                    {final_cells}
                </tr>
            </tbody>
        </table>
    </div>""".strip()
