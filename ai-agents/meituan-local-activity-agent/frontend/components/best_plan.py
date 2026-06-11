"""最优方案组件 — 最终推荐方案详细展示"""


def render_best_plan(result: dict) -> str:
    """渲染最优方案高亮卡片。返回 HTML 字符串。"""
    best_plan = result.get("best_plan", {})
    final_score = result.get("final_score", 0)
    exec_result = result.get("execution_result", {})

    if not best_plan:
        return ""

    intent = result.get("intent", {})
    weather = intent.get("weather", {})
    weather_str = ""
    if isinstance(weather, dict):
        w = weather.get("weather", "")
        t = weather.get("temperature", "")
        if w or t:
            weather_str = f"{w} {t}".strip()

    name = best_plan.get("name", "")
    desc = best_plan.get("description", "")
    budget = best_plan.get("total_budget", 0)
    duration = best_plan.get("estimated_duration_minutes", 0)
    pois = best_plan.get("pois", [])
    highlights = best_plan.get("highlights", [])

    # POI timeline
    pois_html = ""
    if pois:
        poi_items = ""
        icon_map = {
            "restaurant": "🍽", "food": "🍽", "餐饮": "🍽",
            "entertainment": "🎭", "娱乐": "🎭", "activity": "🎯",
            "scenic": "🏞", "景点": "🏞", "park": "🌳",
            "shopping": "🛍", "购物": "🛍",
        }
        for j, poi in enumerate(pois):
            poi_name = poi.get("name", f"地点 {j+1}")
            poi_type = poi.get("type", "")
            poi_price = poi.get("price", poi.get("avg_price", ""))
            poi_dur = poi.get("duration_minutes", "")

            icon = "📍"
            for k, v in icon_map.items():
                if k in str(poi_type).lower():
                    icon = v
                    break

            meta_parts = []
            if poi_type:
                meta_parts.append(poi_type)
            if poi_price:
                meta_parts.append(f"¥{poi_price}")
            if poi_dur:
                meta_parts.append(f"{poi_dur}分钟")

            poi_items += f"""
            <div class="poi-item">
                <div class="poi-dot">{icon}</div>
                <div class="poi-info">
                    <div class="poi-name">{poi_name}</div>
                    <div class="poi-meta">{" · ".join(meta_parts)}</div>
                </div>
            </div>"""

        pois_html = f'<div class="poi-timeline">{poi_items}</div>'

    # Highlights
    highlights_html = ""
    if highlights:
        tags = "".join(f'<span class="highlight-tag">{h}</span>' for h in highlights[:6])
        highlights_html = f'<div class="plan-highlights mt-md">{tags}</div>'

    # Execution results
    exec_html = ""
    exec_success = exec_result.get("success", False)
    exec_results_list = exec_result.get("results", [])
    if exec_results_list:
        success_count = sum(1 for r in exec_results_list if r.get("success"))
        total_count = len(exec_results_list)

        exec_items = ""
        for r in exec_results_list:
            poi_name = r.get("poi_name", "未知地点")
            success = r.get("success", False)
            icon_class = "exec-icon-success" if success else "exec-icon-fail"
            icon_char = "✓" if success else "✗"
            status_text = "预订成功" if success else r.get("error", "预订失败")
            exec_items += f"""
            <div class="exec-item">
                <div class="exec-icon {icon_class}">{icon_char}</div>
                <span>{poi_name}</span>
                <span class="text-muted" style="margin-left:auto; font-size:0.8rem;">{status_text}</span>
            </div>"""

        exec_status = "全部预订成功" if success_count == total_count else f"{success_count}/{total_count} 预订成功"
        exec_html = f"""
        <div class="exec-results">
            <div style="font-size:0.85rem; font-weight:600; color:var(--success); margin-bottom:0.5rem;">
                {exec_status}
            </div>
            {exec_items}
        </div>"""
    elif exec_result.get("error"):
        exec_html = f"""
        <div class="exec-results">
            <div style="font-size:0.85rem; color:var(--error);">
                执行失败：{exec_result.get("error", "")}
            </div>
        </div>"""

    # Score display
    score_color = "var(--success)" if final_score >= 7.5 else ("var(--warning)" if final_score >= 5.5 else "var(--error)")

    return f"""
    <div class="section-header animate-in">
        <div class="section-icon" style="background: linear-gradient(135deg, var(--primary-400), var(--primary-600)); color: white;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
        </div>
        <h2>推荐方案</h2>
    </div>
    <div class="best-plan-card animate-in animate-in-delay-1">
        <div class="best-plan-header">
            <div class="best-plan-icon">🏆</div>
            <div class="best-plan-title">
                <h2>{name}</h2>
                <div class="score-display">综合评分 <span style="color:{score_color}; font-weight:700;">{final_score:.2f}</span> / 10</div>
            </div>
            <div class="best-plan-score-badge">{final_score:.1f}</div>
        </div>
        {f'<div class="weather-badge">🌤 {weather_str}</div>' if weather_str else ''}
        <div class="plan-desc" style="margin-bottom:1rem;">{desc}</div>
        <div class="plan-metrics">
            <div class="plan-metric">
                <span class="plan-metric-value">¥{budget}</span>
                <span class="plan-metric-label">总预算</span>
            </div>
            <div class="plan-metric">
                <span class="plan-metric-value">{duration}</span>
                <span class="plan-metric-label">分钟</span>
            </div>
            <div class="plan-metric">
                <span class="plan-metric-value">{len(pois)}</span>
                <span class="plan-metric-label">个地点</span>
            </div>
        </div>
        {pois_html}
        {highlights_html}
        {exec_html}
    </div>""".strip()
