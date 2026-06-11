"""
本地生活短时活动规划 Agent — 单页流程前端
美团 Hackathon MVP

架构：后台线程调用 API + st.fragment 轮询结果，不阻塞主连接。
"""

import threading
import streamlit as st
import requests
import uuid

from config import BACKEND_URL, api_url
from styles import inject_css
from components import (
    render_intent_summary,
    render_plan_cards,
    render_score_matrix,
    render_best_plan,
    render_loading,
    render_trace_viewer,
)


def _clean_html(html: str) -> str:
    """去掉每行首的空格，防止 Streamlit Markdown 误判为代码块。

    Streamlit 的 markdown 会把行首 ≥4 空格的内容渲染成 <pre><code>。
    组件 f-string 中的 Python 缩进会泄漏到 HTML 里，导致所有 HTML
    被当作代码块展示。此 helper 把每行前面所有空格去掉。
    """
    if not html:
        return html
    return "\n".join(line.lstrip() for line in html.splitlines())

# ---- Page Config ----
st.set_page_config(
    page_title="活动规划 AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---- CSS ----
inject_css()

# ---- Session State ----
if "result" not in st.session_state:
    st.session_state.result = None
if "loading" not in st.session_state:
    st.session_state.loading = False
if "error" not in st.session_state:
    st.session_state.error = None

# ---- Thread-safe result cache (avoids Streamlit session_state sync issues) ----
_api_lock = threading.Lock()
_api_result = {"done": False, "result": None, "error": None}


def _call_api(user_input: str, city: str = "上海"):
    """后台线程：调用后端 API，结果写入全局缓存。"""
    global _api_result
    try:
        trace_id = str(uuid.uuid4())
        response = requests.post(
            api_url("/api/plan"),
            json={"user_input": user_input, "trace_id": trace_id, "city": city},
            timeout=180,
        )
        with _api_lock:
            if response.status_code == 200:
                _api_result["result"] = response.json()
                _api_result["error"] = None
            else:
                _api_result["error"] = f"后端错误 ({response.status_code}): {response.text[:200]}"
            _api_result["done"] = True
    except requests.exceptions.ConnectionError:
        with _api_lock:
            _api_result["error"] = f"无法连接后端服务，请确认后端已启动 ({BACKEND_URL})"
            _api_result["done"] = True
    except requests.exceptions.Timeout:
        with _api_lock:
            _api_result["error"] = "请求超时，请稍后重试"
            _api_result["done"] = True
    except Exception as e:
        with _api_lock:
            _api_result["error"] = f"未知错误: {e}"
            _api_result["done"] = True


# ---- Hero Section ----
st.markdown("""
<div class="hero">
    <div class="hero-badge">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
        </svg>
        美团 Hackathon · AI Agent
    </div>
    <h1>本地生活短时活动规划</h1>
    <p>描述你的想法，AI Agent 为你生成最优活动方案</p>
</div>
""", unsafe_allow_html=True)

# ---- Input Section ----
st.markdown("""
<div class="input-section">
    <label class="input-label">描述你的活动需求</label>
""", unsafe_allow_html=True)

CITIES = ["北京", "上海", "杭州", "成都", "广州", "深圳", "重庆", "南京", "武汉", "西安", "长沙", "苏州", "天津", "厦门", "青岛"]
city = st.selectbox("城市", CITIES, index=1, key="city_selector")

user_input = st.text_area(
    label="user_input",
    label_visibility="collapsed",
    placeholder="例如：周末想带父母和孩子去玩，预算 300 左右，想找个有亲子活动的地方",
    height=80,
    key="plan_input",
)

st.markdown("""
</div>
""", unsafe_allow_html=True)

# ---- Submit / Reset Buttons ----
col_a, col_b = st.columns([1, 5])
with col_a:
    submitted = st.button("✨  开始规划", use_container_width=True, type="primary",
                          disabled=st.session_state.loading)
with col_b:
    if st.session_state.result:
        if st.button("🔄  重新规划", use_container_width=False):
            st.session_state.result = None
            st.session_state.error = None
            st.rerun()

# ---- Trigger API Call (non-blocking) ----
if submitted and user_input and not st.session_state.loading:
    with _api_lock:
        _api_result.clear()
        _api_result.update({"done": False, "result": None, "error": None})
    st.session_state.loading = True
    st.session_state.error = None
    st.session_state.result = None
    city = st.session_state.get("city_selector", "上海")
    threading.Thread(target=_call_api, args=(user_input, city), daemon=True).start()


# ---- Loading Fragment (auto-refresh every 2s) ----
@st.fragment(run_every="2s")
def _loading_fragment():
    """加载状态 fragment：每 2 秒检查后台线程结果。"""
    with _api_lock:
        done = _api_result["done"]
        result = _api_result["result"]
        error = _api_result["error"]

    if st.session_state.loading and not done:
        st.markdown(_clean_html(render_loading()), unsafe_allow_html=True)
    elif done:
        # 后台线程完成，同步到 session_state 并触发全局 rerun
        st.session_state.result = result
        st.session_state.error = error
        st.session_state.loading = False
        with _api_lock:
            _api_result.clear()
            _api_result.update({"done": False, "result": None, "error": None})
        st.rerun()


_loading_fragment()

# ---- Error Display ----
if st.session_state.error:
    st.markdown(f"""
    <div class="error-card animate-in">
        <h3>规划失败</h3>
        <p>{st.session_state.error}</p>
    </div>
    """, unsafe_allow_html=True)

# ---- Results Display ----
if st.session_state.result:
    result = st.session_state.result

    # Check for error in result
    if result.get("error"):
        st.markdown(f"""
        <div class="error-card animate-in">
            <h3>规划失败</h3>
            <p>{result['error']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 1. Intent Summary
        intent_html = render_intent_summary(result.get("intent", {}))
        if intent_html:
            st.markdown(_clean_html(intent_html), unsafe_allow_html=True)

        # 2. Candidate Plans
        candidates = result.get("candidates", [])
        best_plan = result.get("best_plan", {})
        best_plan_id = best_plan.get("id") if best_plan else None
        plans_html = render_plan_cards(candidates, best_plan_id)
        if plans_html:
            st.markdown(_clean_html(plans_html), unsafe_allow_html=True)

        # 3. Score Matrix
        score_html = render_score_matrix(result)
        if score_html:
            st.markdown(_clean_html(score_html), unsafe_allow_html=True)

        # 4. Best Plan
        best_html = render_best_plan(result)
        if best_html:
            st.markdown(_clean_html(best_html), unsafe_allow_html=True)

        # 5. Trace Footer
        trace_html = render_trace_viewer(result.get("trace_id", ""))
        if trace_html:
            st.markdown(_clean_html(trace_html), unsafe_allow_html=True)
