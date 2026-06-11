"""方案卡片组件 — 候选方案展示"""


def render_plan_cards(candidates: list, best_plan_id: str = None) -> str:
    """渲染候选方案卡片网格。返回 HTML 字符串。"""
    if not candidates:
        return ""

    cards_html = ""
    for i, plan in enumerate(candidates):
        pid = plan.get("id", f"plan_{i}")
        name = plan.get("name", f"方案 {chr(65 + i)}")
        desc = plan.get("description", "")
        budget = plan.get("total_budget", 0)
        duration = plan.get("estimated_duration_minutes", 0)
        highlights = plan.get("highlights", [])
        pois = plan.get("pois", [])
        is_best = pid == best_plan_id or (i == 0 and best_plan_id is None and len(candidates) == 1)

        # Badge
        badge_class = "plan-badge plan-badge-winner" if is_best else "plan-badge plan-badge-badge"
        badge_text = "最优方案" if is_best else f"方案 {chr(65 + i)}"

        # POI timeline
        pois_html = ""
        if pois:
            poi_items = ""
            for j, poi in enumerate(pois):
                poi_name = poi.get("name", f"地点 {j+1}")
                poi_type = poi.get("type", "")
                poi_price = poi.get("price", poi.get("avg_price", ""))
                poi_dur = poi.get("duration_minutes", "")

                icon_map = {
                    "restaurant": "🍽", "food": "🍽", "餐饮": "🍽",
                    "entertainment": "🎭", "娱乐": "🎭", "activity": "🎯",
                    "scenic": "🏞", "景点": "🏞", "park": "🌳",
                    "shopping": "🛍", "购物": "🛍",
                }
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

            pois_html = f"""
            <div class="poi-timeline">
                {poi_items}
            </div>"""

        # Highlights
        highlights_html = ""
        if highlights:
            tags = "".join(f'<span class="highlight-tag">{h}</span>' for h in highlights[:4])
            highlights_html = f'<div class="plan-highlights">{tags}</div>'

        card_class = "plan-card" + (" is-best" if is_best else "")
        delay_class = f"animate-in-delay-{min(i + 1, 5)}"

        cards_html += f"""
        <div class="{card_class} animate-in {delay_class}">
            <span class="{badge_class}">{badge_text}</span>
            <div class="plan-name">{name}</div>
            <div class="plan-desc">{desc}</div>
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
        </div>"""

    return f"""
    <div class="section-header animate-in">
        <div class="section-icon" style="background: var(--primary-100); color: var(--primary-700);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="7" height="7"/>
                <rect x="14" y="3" width="7" height="7"/>
                <rect x="14" y="14" width="7" height="7"/>
                <rect x="3" y="14" width="7" height="7"/>
            </svg>
        </div>
        <h2>候选方案</h2>
        <span class="section-sub">共 {len(candidates)} 个方案</span>
    </div>
    <div class="plans-grid">
        {cards_html}
    </div>""".strip()
