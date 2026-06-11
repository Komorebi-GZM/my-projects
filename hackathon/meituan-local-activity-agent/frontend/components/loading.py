"""加载动画组件"""


def render_loading() -> str:
    """渲染简洁的加载状态。返回 HTML 字符串。"""
    return (
        '<div class="loader-container">'
        '<div class="loader-pulse"></div>'
        '<div class="loader-text">AI 正在为你规划最佳方案</div>'
        '<div class="loader-sub">预计需要 30-60 秒，请稍候...</div>'
        '</div>'
    )
