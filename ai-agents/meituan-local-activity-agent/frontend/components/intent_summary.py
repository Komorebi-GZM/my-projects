"""Intent 摘要组件 — 解析后的用户意图展示"""


_FIELD_LABELS = {
    "budget": ("预算", lambda v: f"¥{v}"),
    "max_distance_km": ("距离", lambda v: f"{v}km"),
    "group.count": ("人数", lambda v: f"{v}人"),
    "group.type": ("关系", lambda v: str(v)),
    "activity": ("活动", lambda v: str(v)),
    "food": ("饮食", lambda v: str(v)),
    "district": ("区域", lambda v: str(v)),
    "city": ("城市", lambda v: str(v)),
    "constraints.budget": ("预算", lambda v: f"¥{v}"),
    "constraints.max_distance_km": ("距离", lambda v: f"{v}km"),
    "location.city": ("城市", lambda v: str(v)),
    "location.district": ("区域", lambda v: str(v)),
    "group.count": ("人数", lambda v: f"{v}人"),
    "group.type": ("关系", lambda v: str(v)),
    "preferences.activity": ("活动", lambda v: str(v)),
    "preferences.food": ("饮食", lambda v: str(v)),
}

def _resolve_field(field: str, intent: dict):
    """将字段路径映射为 (display_label, display_value)"""
    parts = field.split(".")
    if len(parts) == 2:
        raw = intent.get(parts[0], {}).get(parts[1]) if isinstance(intent.get(parts[0]), dict) else None
    else:
        raw = intent.get("constraints", {}).get(field) or intent.get("preferences", {}).get(field) or intent.get("location", {}).get(field)
    if raw is None or raw == "" or str(raw) == "无偏好":
        return None
    label, fmt_fn = _FIELD_LABELS.get(field, (field, str))
    return label, fmt_fn(raw)


def render_intent_summary(intent: dict) -> str:
    """渲染解析后的用户意图摘要卡片。返回 HTML 字符串。"""
    if not intent:
        return ""

    # 提取可展示字段
    items = []

    # 城市
    location = intent.get("location", {})
    if isinstance(location, dict):
        city = location.get("city", "")
        if city:
            items.append(("城市", city))

    # 天气
    weather = intent.get("weather", {})
    if isinstance(weather, dict):
        w = weather.get("weather", "")
        t = weather.get("temperature", "")
        parts = []
        if w:
            parts.append(w)
        if t:
            parts.append(t)
        if parts:
            items.append(("天气", "、".join(parts)))

    # 时间
    time_data = intent.get("time", {})
    if isinstance(time_data, dict):
        time_val = time_data.get("range", "")
        flex = time_data.get("flexibility", "")
        if time_val:
            label = f"{time_val}"
            if flex:
                label += f" (弹性 {flex})"
            items.append(("时间", label))

    # 场景
    scene = intent.get("scene", "")
    if scene:
        items.append(("场景", scene))

    # 团队
    group = intent.get("group", {})
    if isinstance(group, dict):
        gtype = group.get("type", "")
        gcount = group.get("count", "")
        children = group.get("children", [])
        label = ""
        if gtype:
            label += gtype
        if gcount:
            label += f" {gcount}人"
        if children:
            label += f" (含{len(children)}儿童)"
        if label:
            items.append(("人员", label))

    # 预算
    constraints = intent.get("constraints", {})
    if isinstance(constraints, dict):
        budget = constraints.get("budget")
        if budget:
            items.append(("预算", f"¥{budget}"))
        distance = constraints.get("max_distance_km")
        if distance:
            items.append(("距离", f"{distance}km 内"))

    # 偏好
    prefs = intent.get("preferences", {})
    if isinstance(prefs, dict):
        pref_parts = []
        for key, val in prefs.items():
            if val and str(val).strip() not in ("无偏好", "无", "不限", ""):
                pref_parts.append(f"{key}: {val}")
        if pref_parts:
            items.append(("偏好", "、".join(pref_parts)))

    # 缺失字段 — 显示填充值
    missing = intent.get("missing_fields", [])
    if isinstance(missing, list) and missing:
        fill_parts = []
        for f in missing:
            resolved = _resolve_field(f, intent)
            if resolved is not None:
                fill_parts.append(f"{resolved[0]} {resolved[1]}")
        missing_text = "、".join(fill_parts)
    else:
        missing_text = ""

    # 构建 HTML
    items_html = ""
    for label, value in items:
        items_html += f"""
        <div class="intent-item">
            <span class="intent-label">{label}</span>
            <span class="intent-value">{value}</span>
        </div>"""

    missing_html = ""
    if missing_text:
        missing_html = f"""
        <div class="intent-missing">
            部分信息未指定，已智能填充：{missing_text}
        </div>"""

    return f"""
    <div class="section-header animate-in">
        <div class="section-icon" style="background: var(--info-bg); color: var(--info);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="16" x2="12" y2="12"/>
                <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
        </div>
        <h2>意图解析</h2>
    </div>
    <div class="intent-card animate-in animate-in-delay-1">
        <div class="intent-grid">
            {items_html}
        </div>
        {missing_html}
    </div>""".strip()
