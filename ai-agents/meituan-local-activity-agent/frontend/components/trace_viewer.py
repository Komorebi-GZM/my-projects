"""Trace 展示组件"""


def render_trace_viewer(trace_id: str) -> str:
    """渲染 trace ID 展示。返回 HTML 字符串。"""
    if not trace_id:
        return ""
    short_id = trace_id[:8] if len(trace_id) > 8 else trace_id
    return f"""
    <div class="trace-footer">
        Trace ID: <code>{short_id}</code>
    </div>""".strip()
