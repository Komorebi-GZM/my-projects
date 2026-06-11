import streamlit as st
import requests
import json
from html import escape


# 先启动后端     uvicorn main:app --reload --port 8000
# 再启动前端     streamlit run app_streamlit.py

API_URL = "http://localhost:8000/agent_invoke"

# ========================================
# 页面配置
# ========================================
st.set_page_config(
    page_title="FogLift·破雾 - 职业发展助手",
    layout="wide",
    page_icon="assets/foglift-logo.svg"
)

# ========================================
# 自定义CSS注入
# ========================================
st.markdown("""
<style>
/* =============================
    FogLift 破雾晨光变量
    深夜底色 + 青蓝/薄荷/暖金三功能强调色
=============================*/
:root {
  --reflect-bg: #030014;
  --reflect-bg-deep: #02010B;
  --reflect-bg-warm: #080512;
  --reflect-text: #FFFFFF;
  --reflect-text-secondary: #F4F0FF;
  --reflect-text-muted: rgba(239,237,253,0.7);
  --reflect-text-subtle: rgba(239,237,253,0.6);
  --reflect-card-bg: rgba(255,255,255,0.026);
  --reflect-card-hover: rgba(255,255,255,0.058);
  --reflect-border: rgba(255,255,255,0.095);
  --reflect-border-strong: rgba(255,255,255,0.18);
  --reflect-input-bg: #0B0718;
  --reflect-input-focus: #120D22;
  --reflect-cyan: #8EEBFF;
  --reflect-mint: #A9F5C8;
  --reflect-amber: #FFE3A3;
  --reflect-lilac: #D9CCFF;
  --reflect-coral: #FFB7A1;
  --page-accent: var(--reflect-cyan);
  --page-accent-soft: rgba(142,235,255,0.16);
  --page-accent-faint: rgba(142,235,255,0.07);
  --reflect-muted: var(--reflect-text-muted);
  --reflect-accent: var(--page-accent);
  --reflect-text-soft: var(--reflect-text-secondary);
  --reflect-bg-card: var(--reflect-card-bg);
  --reflect-fade-card: rgba(255,255,255,0.03);
  --reflect-radius-sm: 8px;
  --reflect-radius-md: 12px;
  --reflect-radius-lg: 16px;
  --reflect-ease: cubic-bezier(0.22, 1, 0.36, 1);
}

/* ========================================
    全局样式
======================================== */
html, body, .stApp,
[data-testid="stAppViewContainer"],
.main,
.block-container {
  background:
    radial-gradient(circle at 50% -18%, rgba(255,227,163,0.13) 0, rgba(255,227,163,0.045) 24%, transparent 48%),
    radial-gradient(circle at 18% 8%, rgba(142,235,255,0.13) 0, transparent 28%),
    radial-gradient(circle at 84% 6%, rgba(169,245,200,0.11) 0, transparent 30%),
    linear-gradient(180deg, rgba(12,18,34,0.72) 0%, rgba(3,0,20,0) 360px),
    var(--reflect-bg) !important;
  color: var(--reflect-text) !important;
  min-height: 100vh;
  font-family: system-ui, -apple-system, sans-serif;
}

[data-testid="stHeader"],
[data-testid="stToolbar"] {
  background: transparent !important;
  color: var(--reflect-text) !important;
}

.block-container {
  padding-top: 0 !important;
  max-width: 100% !important;
  position: relative;
  z-index: 1;
}

[data-testid="stAppViewContainer"] > .main {
  position: relative;
  z-index: 1;
}

/* Streamlit text reset: scoped only to text containers, never all div/span nodes. */
[data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"],
[data-testid="stCaptionContainer"],
.stAlert,
.stExpander {
  color: var(--reflect-text) !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stCaptionContainer"] p {
  color: var(--reflect-text-muted) !important;
}

[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
  color: var(--reflect-text-secondary) !important;
  font-weight: 500 !important;
}

[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] b,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] h5,
[data-testid="stMarkdownContainer"] h6 {
  color: var(--reflect-text) !important;
  font-weight: 500 !important;
}

button:focus-visible,
input:focus-visible,
textarea:focus-visible,
[role="radio"]:focus-visible {
  outline: 2px solid var(--page-accent) !important;
  outline-offset: 3px !important;
}

/* 顶部Header模拟 - 符合Reflect全宽布局 */
.main-header {
  background: none !important;
  padding: 173px 0 48px 0 !important;
  margin-bottom: 0;
  text-align: center;
  border-radius: 0;
  box-shadow: none !important;
  position: relative;
  overflow: hidden;
  min-height: 380px;
}
.main-header::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 64px;
  width: 320px;
  height: 320px;
  transform: translateX(-50%);
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.06);
  box-shadow:
    0 0 0 72px rgba(255,255,255,0.018),
    0 0 0 144px rgba(255,255,255,0.012),
    inset 0 0 48px rgba(244,240,255,0.05);
  opacity: 0.85;
  animation: orbitRotate 28s linear infinite;
  z-index: 0;
}
.main-header::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 214px;
  width: 8px;
  height: 8px;
  margin-left: 158px;
  border-radius: 50%;
  background: var(--reflect-text-secondary);
  box-shadow:
    -235px -94px 0 -2px rgba(244,240,255,0.8),
    -70px 102px 0 -3px rgba(244,240,255,0.7),
    120px -118px 0 -3px rgba(244,240,255,0.65),
    210px 82px 0 -3px rgba(244,240,255,0.55);
  animation: orbitDot 18s linear infinite;
  z-index: 0;
}
.main-header > * {
  position: relative;
  z-index: 1;
}
@keyframes orbitRotate {
  from { transform: translateX(-50%) rotate(0deg); }
  to { transform: translateX(-50%) rotate(360deg); }
}
@keyframes orbitDot {
  from { transform: rotate(0deg) translateX(24px) rotate(0deg); }
  to { transform: rotate(360deg) translateX(24px) rotate(-360deg); }
}
.main-header h1 {
  color: var(--reflect-text) !important;
  font-size: 72px !important;
  font-weight: 500 !important;
  margin: 0 0 12px 0;
  letter-spacing: -1.5px;
  line-height: 80px !important;
}
.main-header p {
  color: var(--reflect-text-muted) !important;
  font-size: 16px;
  font-weight: 400;
  max-width: 600px;
  margin: 0 auto;
}

/* 主卡片(Reflect风格: rgba(255,255,255,0.01) 几乎不可见) */
.home-shell {
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto 72px;
}
.home-hero {
  position: relative;
  overflow: hidden;
  min-height: 430px;
  padding: 92px 16px 56px;
  text-align: center;
}
.home-hero h1 {
  color: var(--reflect-text) !important;
  font-size: 72px !important;
  line-height: 80px !important;
  font-weight: 500 !important;
  margin: 12px auto;
  max-width: 880px;
}
.home-hero p {
  color: var(--reflect-text-muted) !important;
  font-size: 16px;
  line-height: 1.7;
  margin: 0 auto;
  max-width: 640px;
}
.reflect-badge {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border: 1px solid color-mix(in srgb, var(--page-accent) 36%, transparent);
  border-radius: 999px;
  color: var(--reflect-text-secondary);
  background:
    linear-gradient(90deg, var(--page-accent-faint), rgba(255,255,255,0.018));
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 0 26px var(--page-accent-faint);
}
.hero-orbit {
  position: absolute;
  left: 50%;
  top: 24px;
  width: 380px;
  height: 380px;
  margin-left: -190px;
  border-radius: 50%;
  pointer-events: none;
  opacity: 0.95;
  z-index: 0;
}
.hero-orbit::before {
  content: '';
  position: absolute;
  inset: 132px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 35% 28%, rgba(255,227,163,0.16), transparent 34%),
    rgba(3,0,20,0.86);
  box-shadow:
    0 0 80px rgba(244,240,255,0.09),
    0 0 120px rgba(142,235,255,0.06),
    0 0 160px rgba(169,245,200,0.04);
}
.hero-orbit-ring {
  position: absolute;
  inset: var(--orbit-inset);
  border: 1px solid color-mix(in srgb, var(--orbit-color) 22%, rgba(255,255,255,0.07));
  border-radius: 50%;
  animation: orbitRotate var(--orbit-duration) linear infinite;
}
.hero-orbit-ring span {
  position: absolute;
  top: -3px;
  left: 50%;
  width: 6px;
  height: 6px;
  margin-left: -3px;
  border-radius: 50%;
  background: var(--orbit-color);
  box-shadow: 0 0 22px color-mix(in srgb, var(--orbit-color) 70%, transparent);
}
.ring-one { --orbit-inset: 22px; --orbit-duration: 26s; --orbit-color: var(--reflect-cyan); }
.ring-two { --orbit-inset: 74px; --orbit-duration: 20s; --orbit-color: var(--reflect-mint); animation-direction: reverse; }
.ring-three { --orbit-inset: 126px; --orbit-duration: 14s; --orbit-color: var(--reflect-amber); }
.home-hero > *:not(.hero-orbit) {
  position: relative;
  z-index: 1;
}
.capability-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin: 16px 0 28px;
}
.capability-card {
  min-height: 178px;
  padding: 24px;
  border: 1px solid var(--reflect-border);
  border-radius: var(--reflect-radius-lg);
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--card-accent) 8%, transparent), transparent 48%),
    var(--reflect-card-bg);
  position: relative;
  overflow: hidden;
  transition: transform 0.28s var(--reflect-ease), border-color 0.28s var(--reflect-ease), background 0.28s var(--reflect-ease);
}
.capability-card::before {
  content: '';
  position: absolute;
  left: 18px;
  right: 18px;
  top: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--card-accent), transparent);
  opacity: 0.8;
}
.capability-card:hover {
  transform: translateY(-4px);
  border-color: color-mix(in srgb, var(--card-accent) 34%, transparent);
  background: var(--reflect-card-hover);
}
.capability-card:nth-child(1) { --card-accent: var(--reflect-cyan); }
.capability-card:nth-child(2) { --card-accent: var(--reflect-mint); }
.capability-card:nth-child(3) { --card-accent: var(--reflect-amber); }
.capability-card-label {
  color: var(--reflect-text-subtle);
  font-size: 13px;
  margin-bottom: 14px;
}
.capability-card h3 {
  color: var(--reflect-text);
  font-size: 24px;
  line-height: 32px;
  font-weight: 500;
  margin: 0 0 10px;
}
.capability-card p {
  color: var(--reflect-text-muted);
  font-size: 15px;
  line-height: 1.7;
  margin: 0;
}
.agent-flow-preview {
  margin-top: 20px;
  padding: 24px;
  border: 1px solid var(--reflect-border);
  border-radius: var(--reflect-radius-lg);
  background: rgba(255,255,255,0.01);
}
.agent-flow-preview h3 {
  color: var(--reflect-text);
  font-size: 32px;
  line-height: 40px;
  font-weight: 500;
  margin: 0 0 16px;
}
.agent-flow-steps {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}
.agent-flow-step {
  border-left: 1px solid var(--reflect-border-strong);
  padding: 4px 0 4px 14px;
}
.agent-flow-step strong {
  display: block;
  color: var(--reflect-text-secondary);
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 6px;
}
.agent-flow-step span {
  color: var(--reflect-text-muted);
  font-size: 13px;
  line-height: 1.6;
}
.section-header {
  text-align: center;
  padding: 72px 16px 40px;
}
.section-header h2 {
  color: var(--reflect-text);
  font-size: 56px;
  line-height: 64px;
  font-weight: 500;
  margin: 12px auto;
  max-width: 820px;
}
.section-header p {
  color: var(--reflect-text-muted);
  font-size: 16px;
  line-height: 1.7;
  max-width: 640px;
  margin: 0 auto;
}
.workspace-card {
  width: min(1040px, calc(100% - 32px));
  margin: 0 auto 24px;
  padding: 24px;
  background:
    linear-gradient(135deg, var(--page-accent-faint), transparent 42%),
    var(--reflect-card-bg);
  border: 1px solid var(--reflect-border);
  border-radius: var(--reflect-radius-lg);
  position: relative;
  overflow: hidden;
  transition: border-color 0.28s var(--reflect-ease), background 0.28s var(--reflect-ease);
}
.workspace-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, var(--page-accent), var(--reflect-lilac));
  opacity: 0.8;
}
.workspace-card::after {
  content: '';
  position: absolute;
  right: -120px;
  top: -120px;
  width: 280px;
  height: 280px;
  border-radius: 50%;
  background: radial-gradient(circle, var(--page-accent-soft), transparent 66%);
  opacity: 0.55;
  pointer-events: none;
}
.workspace-card h3 {
  color: var(--reflect-text);
  font-size: 32px;
  line-height: 40px;
  font-weight: 500;
  margin: 0 0 8px;
}
.workspace-card p {
  color: var(--reflect-text-muted);
  font-size: 16px;
  line-height: 1.7;
  margin: 0;
}
.agent-pipeline {
  width: min(1040px, calc(100% - 32px));
  margin: 16px auto;
  padding: 18px 20px;
  border: 1px solid color-mix(in srgb, var(--page-accent) 26%, var(--reflect-border));
  border-radius: var(--reflect-radius-md);
  background:
    linear-gradient(90deg, var(--page-accent-faint), transparent),
    var(--reflect-card-bg);
}
.agent-pipeline-label {
  color: var(--reflect-text-subtle);
  font-size: 13px;
  margin-bottom: 10px;
}
.agent-pipeline ol {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 0;
  margin: 0;
  list-style: none;
}
.agent-pipeline li {
  color: var(--reflect-text-secondary);
  border: 1px solid color-mix(in srgb, var(--page-accent) 24%, var(--reflect-border));
  border-radius: 999px;
  padding: 8px 12px;
  font-size: 14px;
  animation: pipelinePulse 1.8s ease-in-out infinite;
  animation-delay: calc(var(--step-index, 0) * 0.12s);
}
@keyframes pipelinePulse {
  0%, 100% { background: rgba(255,255,255,0.018); }
  50% { background: var(--page-accent-faint); }
}
.result-note {
  color: var(--reflect-text-muted);
  background: var(--reflect-card-bg);
  border: 1px solid var(--reflect-border);
  border-radius: var(--reflect-radius-sm);
  padding: 14px 16px;
  line-height: 1.6;
}
.result-section-kicker {
  color: var(--reflect-text-subtle);
  font-size: 13px;
  margin-bottom: 8px;
}
.feature-card {
  background:
    linear-gradient(180deg, var(--page-accent-faint), transparent 36%),
    var(--reflect-card-bg) !important;
  border-radius: var(--reflect-radius-lg);
  border: 1px solid var(--reflect-border) !important;
  box-shadow: none !important;
  padding: 32px;
  position: relative;
  overflow: hidden;
  transition: transform 0.28s var(--reflect-ease), border-color 0.28s var(--reflect-ease), background 0.28s var(--reflect-ease);
  color: var(--reflect-text-secondary);
}
.feature-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--page-accent), transparent);
  opacity: 0.38;
}
.feature-card:hover {
  transform: translateY(-2px);
  border-color: color-mix(in srgb, var(--page-accent) 28%, transparent) !important;
  background: var(--reflect-card-hover) !important;
}

/* 标题 */
.card-header {
  border: none;
  padding-bottom: 8px;
  margin-bottom: 18px;
}
.card-header h3 {
  font-size: 32px;
  font-weight: 500;
  color: var(--reflect-text);
  margin: 0;
  line-height: 40px;
}

/* 技能标签 - 极简 */
.skill-tag {
  background: rgba(255,255,255,0.018);
  border: 1px solid color-mix(in srgb, var(--page-accent) 20%, var(--reflect-border));
  color: var(--reflect-text-secondary);
  font-size: 14px;
  border-radius: 999px;
  margin: 4px 6px 4px 0;
  padding: 6px 18px;
  display: inline-flex;
  align-items: center;
  font-weight: 500;
  transition: border-color 0.22s var(--reflect-ease), background 0.22s var(--reflect-ease), transform 0.22s var(--reflect-ease);
}
.skill-tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 8px 0 16px;
}
.skill-tag-list .skill-tag {
  margin: 0;
}
.skill-tag:hover {
  border-color: color-mix(in srgb, var(--page-accent) 38%, transparent);
  background: var(--page-accent-faint);
  transform: translateY(-1px);
}
.skill-tag-hard {
  border-color: color-mix(in srgb, var(--reflect-cyan) 34%, var(--reflect-border));
}
.skill-tag-soft {
  border-color: color-mix(in srgb, var(--reflect-mint) 24%, var(--reflect-border));
}

/* ========================================
    Reflect组件深色极简风格
    Rule: 无阴影、无渐变、仅白色透明度层级
======================================== */

/* 黑话卡片 - 透明+左边框 */
.jargon-card {
  background: linear-gradient(90deg, var(--page-accent-faint), transparent);
  border-left: 2px solid var(--page-accent);
  padding: 16px;
  margin: 12px 0;
  border-radius: 0 var(--reflect-radius-sm) var(--reflect-radius-sm) 0;
}
.jargon-card .jargon-term {
  font-weight: 500;
  color: var(--reflect-text);
  font-size: 16px;
  margin-bottom: 4px;
}
.jargon-card .jargon-translation {
  color: var(--reflect-text-muted);
  font-size: 14px;
  line-height: 1.6;
}

/* 差距分析 */
.gap-item {
  background: linear-gradient(90deg, var(--page-accent-faint), transparent);
  border-left: 2px solid var(--page-accent);
  padding: 16px;
  margin: 12px 0;
  border-radius: 0 var(--reflect-radius-sm) var(--reflect-radius-sm) 0;
}
.gap-item .gap-skill {
  font-weight: 500;
  color: var(--reflect-text);
  font-size: 16px;
}
.gap-item .gap-desc {
  color: var(--reflect-text-muted);
  font-size: 14px;
  margin-top: 6px;
  line-height: 1.6;
}
.gap-time-card {
  background:
    linear-gradient(135deg, var(--page-accent-faint), transparent 52%),
    var(--reflect-card-bg);
  border: 1px solid color-mix(in srgb, var(--page-accent) 22%, var(--reflect-border));
  border-radius: var(--reflect-radius-md);
  padding: 16px;
  margin-top: 16px;
  text-align: center;
}
.gap-time-card .time-label {
  font-size: 14px;
  color: var(--reflect-text-muted);
}
.gap-time-card .time-value {
  font-size: 20px;
  font-weight: 500;
  color: var(--reflect-text-secondary);
  margin-top: 4px;
}

/* 时间轴 - 极简 */
.timeline {
  position: relative;
  padding-left: 24px;
}
.timeline::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 0;
  bottom: 0;
  width: 1.5px;
  background: linear-gradient(180deg, var(--page-accent), var(--reflect-border));
}
.timeline-item {
  position: relative;
  margin-bottom: 24px;
  padding: 16px;
  background:
    linear-gradient(135deg, var(--page-accent-faint), transparent 52%),
    var(--reflect-card-bg);
  border: 1px solid color-mix(in srgb, var(--page-accent) 18%, var(--reflect-border));
  border-radius: var(--reflect-radius-sm);
  transition: transform 0.24s var(--reflect-ease), border-color 0.24s var(--reflect-ease);
}
.timeline-item:hover {
  transform: translateX(2px);
  border-color: color-mix(in srgb, var(--page-accent) 34%, transparent);
}
.timeline-item::before {
  content: '';
  position: absolute;
  left: -18px;
  top: 20px;
  width: 8px;
  height: 8px;
  background: var(--page-accent);
  border-radius: 50%;
  box-shadow: 0 0 16px var(--page-accent-soft);
}
.timeline-item .step-title {
  font-weight: 500;
  color: var(--reflect-text-secondary);
  font-size: 14px;
  margin-bottom: 4px;
}
.timeline-item .step-content {
  color: var(--reflect-text);
  font-size: 15px;
  line-height: 1.6;
}

/* 优先级标签 */
.priority-high, .priority-medium, .priority-low {
  display: inline-block;
  padding: 2px 10px;
  border: 1px solid color-mix(in srgb, var(--page-accent) 22%, var(--reflect-border));
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  color: var(--reflect-text-muted);
  background: var(--reflect-card-bg);
}
.priority-high {
  color: var(--reflect-amber);
  border-color: rgba(255,227,163,0.34);
}
.priority-medium {
  color: var(--reflect-cyan);
  border-color: rgba(142,235,255,0.3);
}
.priority-low {
  color: var(--reflect-mint);
  border-color: rgba(169,245,200,0.28);
}

/* 资源卡片 */
.resource-card {
  background:
    linear-gradient(135deg, var(--page-accent-faint), transparent 54%),
    var(--reflect-card-bg);
  border: 1px solid color-mix(in srgb, var(--page-accent) 18%, var(--reflect-border));
  border-radius: var(--reflect-radius-sm);
  padding: 16px;
  margin: 8px 0;
  transition: border-color 0.22s var(--reflect-ease), transform 0.22s var(--reflect-ease), background 0.22s var(--reflect-ease);
}
.resource-card:hover {
  border-color: color-mix(in srgb, var(--page-accent) 34%, transparent);
  transform: translateY(-1px);
}
.resource-card .resource-title {
  font-weight: 500;
  color: var(--reflect-text);
  font-size: 15px;
  margin-bottom: 8px;
}
.resource-card .resource-link {
  color: var(--reflect-text-muted);
  font-size: 13px;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 4px;
}
.resource-card .resource-link:hover {
  color: var(--reflect-text-secondary);
}

/* 评分 -> 圆形进度环 */
.score-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
  margin: 20px 0;
}
.score-ring {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.score-ring-svg {
  width: 80px;
  height: 80px;
  transform: rotate(-90deg);
}
.score-ring-bg {
  fill: none;
  stroke: var(--reflect-border);
  stroke-width: 4;
}
.score-ring-fg {
  fill: none;
  stroke: var(--page-accent);
  stroke-width: 4;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.6s var(--reflect-ease);
}
.score-ring-value {
  position: absolute;
  font-size: 22px;
  font-weight: 500;
  color: var(--reflect-text);
  margin-top: 20px;
}
.score-ring-label {
  font-size: 13px;
  color: var(--reflect-text-muted);
  text-align: center;
}
.score-ring-wrap {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 敢投指数 */
.confidence-meter {
  background:
    radial-gradient(circle at 50% 0%, var(--page-accent-soft), transparent 46%),
    var(--reflect-card-bg);
  border: 1px solid color-mix(in srgb, var(--page-accent) 24%, var(--reflect-border));
  border-radius: var(--reflect-radius-lg);
  padding: 40px 30px;
  text-align: center;
  margin: 20px 0;
}
.confidence-meter .meter-value {
  font-size: 72px;
  font-weight: 500;
  color: var(--reflect-text);
  letter-spacing: -3px;
  line-height: 80px;
}
.confidence-meter .meter-label {
  font-size: 16px;
  color: var(--reflect-text-muted);
  margin-top: 8px;
}

/* 鼓励语气泡 */
.cheer-bubble {
  background:
    linear-gradient(135deg, var(--page-accent-faint), transparent 52%),
    var(--reflect-card-bg);
  border: 1px solid color-mix(in srgb, var(--page-accent) 20%, var(--reflect-border));
  border-radius: var(--reflect-radius-md);
  padding: 24px;
  margin: 20px 0;
  position: relative;
}
.cheer-bubble::before {
  content: '"';
  position: absolute;
  top: 4px;
  left: 16px;
  font-size: 48px;
  color: var(--page-accent);
  opacity: 0.25;
  font-family: serif;
  line-height: 1;
}
.cheer-bubble .cheer-text {
  font-size: 17px;
  color: var(--reflect-text);
  line-height: 1.6;
  font-style: italic;
  padding-left: 20px;
}

/* 亮点和建议 */
.highlight-section, .advice-section {
  background:
    linear-gradient(135deg, var(--page-accent-faint), transparent 52%),
    var(--reflect-card-bg);
  border: 1px solid color-mix(in srgb, var(--page-accent) 20%, var(--reflect-border));
  border-radius: var(--reflect-radius-sm);
  padding: 16px;
  margin: 12px 0;
}
.highlight-section h4, .advice-section h4 {
  color: var(--reflect-text-secondary);
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 500;
}
.highlight-section li, .advice-section p {
  color: var(--reflect-text-muted);
  margin: 6px 0;
  line-height: 1.6;
}
.highlight-section ul {
  margin: 0;
  padding-left: 20px;
}

/* 输入框 - scoped to Streamlit/BaseWeb inputs for readable dark UI. */
div[data-testid="stTextInput"] div[data-baseweb="input"],
div[data-testid="stTextArea"] div[data-baseweb="textarea"] {
  background: var(--reflect-input-bg) !important;
  border: 1px solid color-mix(in srgb, var(--page-accent) 18%, rgba(255,255,255,0.14)) !important;
  border-radius: var(--reflect-radius-sm) !important;
  box-shadow: none !important;
}
div[data-testid="stTextInput"] div[data-baseweb="input"] *,
div[data-testid="stTextArea"] div[data-baseweb="textarea"] * {
  background: var(--reflect-input-bg) !important;
}
div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
div[data-testid="stTextArea"] div[data-baseweb="textarea"]:focus-within {
  background: var(--reflect-input-focus) !important;
  border-color: color-mix(in srgb, var(--page-accent) 52%, rgba(244,240,255,0.42)) !important;
  box-shadow: 0 0 0 3px var(--page-accent-faint) !important;
}
div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within *,
div[data-testid="stTextArea"] div[data-baseweb="textarea"]:focus-within * {
  background: var(--reflect-input-focus) !important;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
.stTextArea textarea,
.stTextInput input {
  background-color: var(--reflect-input-bg) !important;
  color: var(--reflect-text) !important;
  caret-color: var(--reflect-text-secondary) !important;
  -webkit-text-fill-color: var(--reflect-text) !important;
  font-family: system-ui, -apple-system, sans-serif !important;
  font-size: 15px !important;
  line-height: 1.6 !important;
  box-shadow: none !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus,
.stTextArea textarea:focus,
.stTextInput input:focus {
  background-color: var(--reflect-input-focus) !important;
  color: var(--reflect-text) !important;
  -webkit-text-fill-color: var(--reflect-text) !important;
  outline: none !important;
}
div[data-testid="stTextInput"] input:-webkit-autofill,
div[data-testid="stTextArea"] textarea:-webkit-autofill,
.stTextInput input:-webkit-autofill,
.stTextArea textarea:-webkit-autofill {
  box-shadow: 0 0 0 1000px var(--reflect-input-bg) inset !important;
  -webkit-box-shadow: 0 0 0 1000px var(--reflect-input-bg) inset !important;
  -webkit-text-fill-color: var(--reflect-text) !important;
  caret-color: var(--reflect-text-secondary) !important;
}
div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder,
.stTextArea textarea::placeholder,
.stTextInput input::placeholder {
  color: rgba(244,240,255,0.52) !important;
  -webkit-text-fill-color: rgba(244,240,255,0.52) !important;
  opacity: 1 !important;
}
div[data-testid="stTextInput"] input:disabled,
div[data-testid="stTextArea"] textarea:disabled {
  color: rgba(244,240,255,0.48) !important;
  -webkit-text-fill-color: rgba(244,240,255,0.48) !important;
}

/* 按钮 */
.stButton button {
  background:
    linear-gradient(135deg, var(--page-accent-faint), rgba(255,255,255,0.014)) !important;
  border: 1px solid color-mix(in srgb, var(--page-accent) 24%, var(--reflect-border)) !important;
  border-radius: var(--reflect-radius-sm) !important;
  color: var(--reflect-text) !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  padding: 10px 20px !important;
  transition: transform 0.22s var(--reflect-ease), background 0.22s var(--reflect-ease), border-color 0.22s var(--reflect-ease), color 0.22s var(--reflect-ease);
  width: auto !important;
  box-shadow: none !important;
}
.stButton button:hover {
  background: var(--page-accent) !important;
  border-color: var(--page-accent) !important;
  color: #030014 !important;
  transform: translateY(-1px);
}
.stButton button:active {
  transform: scale(0.98);
}

/* 消息框 */
.stAlert {
  background:
    linear-gradient(135deg, var(--page-accent-faint), transparent 52%),
    var(--reflect-card-bg) !important;
  border: 1px solid color-mix(in srgb, var(--page-accent) 20%, var(--reflect-border)) !important;
  border-radius: var(--reflect-radius-sm) !important;
  color: var(--reflect-text) !important;
  box-shadow: none !important;
}
.stAlert > div { color: var(--reflect-text) !important; }

/* 分割线 */
hr {
  border: none !important;
  height: 1px !important;
  background: var(--reflect-border) !important;
  margin: 24px 0 !important;
}

/* expander */
.streamlit-expanderHeader {
  color: var(--reflect-text) !important;
  font-size: 14px !important;
  background: var(--reflect-card-bg) !important;
  border: 1px solid color-mix(in srgb, var(--page-accent) 18%, var(--reflect-border)) !important;
  border-radius: var(--reflect-radius-sm) !important;
  padding: 10px 14px !important;
  transition: border-color 0.3s var(--reflect-ease);
  box-shadow: none !important;
}
.streamlit-expanderHeader:hover {
  border-color: color-mix(in srgb, var(--page-accent) 32%, transparent);
}

/* spinner */
.stSpinner > div > div {
  border-color: var(--page-accent) transparent transparent transparent !important;
}

/* 滚动揭幕 */
.fade-in {
  opacity: 0;
  transform: translateY(20px);
  animation: reflectReveal 0.6s var(--reflect-ease) forwards;
}
@keyframes reflectReveal {
  to { opacity: 1; transform: translateY(0); }
}

/* 破雾晨光粒子背景: 远星点 + 漂浮粒子 + 顶部雾光 */
.stApp::before {
  content: '';
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  pointer-events: none;
  z-index: 0;
  background-image:
    radial-gradient(1px 1px at 10% 20%, rgba(244,240,255,0.22) 50%, transparent 100%),
    radial-gradient(1px 1px at 30% 60%, rgba(142,235,255,0.22) 50%, transparent 100%),
    radial-gradient(1px 1px at 50% 10%, rgba(255,227,163,0.22) 50%, transparent 100%),
    radial-gradient(1px 1px at 70% 40%, rgba(169,245,200,0.18) 50%, transparent 100%),
    radial-gradient(1px 1px at 90% 80%, rgba(244,240,255,0.22) 50%, transparent 100%),
    radial-gradient(2px 2px at 15% 75%, rgba(142,235,255,0.32) 50%, transparent 100%),
    radial-gradient(2px 2px at 45% 90%, rgba(169,245,200,0.30) 50%, transparent 100%),
    radial-gradient(2px 2px at 80% 15%, rgba(255,227,163,0.30) 50%, transparent 100%);
  background-repeat: no-repeat;
  animation: starDrift 14s ease-in-out infinite;
}
.stApp::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  opacity: 0.34;
  background-image:
    radial-gradient(3px 3px at 12% 32%, rgba(142,235,255,0.15) 0, transparent 72%),
    radial-gradient(4px 4px at 76% 28%, rgba(255,227,163,0.12) 0, transparent 72%),
    radial-gradient(3px 3px at 64% 74%, rgba(169,245,200,0.13) 0, transparent 72%),
    linear-gradient(rgba(255,255,255,0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px);
  background-size: 100% 100%, 100% 100%, 100% 100%, 72px 72px, 72px 72px;
  mask-image: linear-gradient(to bottom, rgba(0,0,0,0.85), transparent 62%);
  animation: fogGrid 18s ease-in-out infinite;
}
@keyframes starDrift {
  0%, 100% { opacity: 0.9; transform: translate3d(0, 0, 0) scale(1); }
  50% { opacity: 0.45; transform: translate3d(10px, -14px, 0) scale(1.02); }
}
@keyframes fogGrid {
  0%, 100% { transform: translate3d(0, 0, 0); opacity: 0.34; }
  50% { transform: translate3d(-8px, 10px, 0); opacity: 0.24; }
}

/* prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
  .fade-in { opacity: 1; transform: none; animation: none; }
  .stApp::before { animation: none; opacity: 0.2; }
  .stApp::after { animation: none; }
  .page-transition,
  .page-transition::before,
  .page-transition .section-header,
  .page-transition .home-hero,
  .page-transition .workspace-card,
  .page-transition .feature-card,
  .page-transition .capability-card,
  .page-transition .agent-flow-preview {
    animation: none !important;
    opacity: 1 !important;
    transform: none !important;
    filter: none !important;
  }
}

/* 隐藏sidebar */
section[data-testid="stSidebar"] { display: none !important; }

/* Native Streamlit navigation. Keep page switching on first-party widgets. */
.native-brand {
  margin: 18px auto 8px auto;
  width: min(1120px, calc(100% - 32px));
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--reflect-text-secondary);
}
.foglift-logo-mark {
  width: 42px;
  height: 42px;
  flex: 0 0 42px;
  border-radius: 14px;
  overflow: visible;
  filter: drop-shadow(0 0 18px var(--page-accent-faint));
}
.foglift-logo-mark .logo-shell {
  fill: rgba(255,255,255,0.035);
  stroke: color-mix(in srgb, var(--page-accent) 34%, rgba(255,255,255,0.14));
  stroke-width: 1.15;
}
.foglift-logo-mark .logo-mist {
  fill: none;
  stroke: rgba(244,240,255,0.72);
  stroke-width: 2.2;
  stroke-linecap: round;
}
.foglift-logo-mark .logo-path {
  fill: none;
  stroke: var(--reflect-mint);
  stroke-width: 2.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.foglift-logo-mark .logo-dawn {
  fill: var(--reflect-amber);
  filter: drop-shadow(0 0 8px rgba(255,227,163,0.42));
}
.foglift-logo-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.foglift-logo-name {
  color: var(--reflect-text);
  font-size: 18px;
  line-height: 22px;
  font-weight: 600;
  letter-spacing: 0;
}
.foglift-logo-subtitle {
  color: var(--reflect-text-subtle);
  font-size: 12px;
  line-height: 16px;
  letter-spacing: 0;
}
div[data-testid="stRadio"] {
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto !important;
  padding: 10px 0 18px 0;
}
div[data-testid="stRadio"] > label {
  color: var(--reflect-text-muted) !important;
  font-size: 13px !important;
  margin-bottom: 8px !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding: 6px;
  border: 1px solid var(--reflect-border);
  border-radius: 18px;
  background:
    linear-gradient(90deg, rgba(142,235,255,0.045), rgba(169,245,200,0.026), rgba(255,227,163,0.035)),
    rgba(255,255,255,0.025);
  position: relative;
  overflow: hidden;
}
div[data-testid="stRadio"] label[data-baseweb="radio"] {
  position: relative;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  min-height: 40px;
  min-width: 104px;
  padding: 0 18px !important;
  border: 1px solid transparent;
  border-radius: 14px;
  color: var(--reflect-text-muted) !important;
  transition: background 0.24s var(--reflect-ease), color 0.24s var(--reflect-ease), border-color 0.24s var(--reflect-ease), transform 0.24s var(--reflect-ease);
}
div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child,
div[data-testid="stRadio"] label[data-baseweb="radio"] input[type="radio"] {
  position: absolute !important;
  opacity: 0 !important;
  width: 1px !important;
  height: 1px !important;
  pointer-events: none !important;
}
div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
  color: var(--reflect-text) !important;
  background: var(--page-accent-faint);
  transform: translateY(-1px);
}
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
  background:
    linear-gradient(135deg, var(--page-accent-soft), rgba(255,255,255,0.06));
  border-color: color-mix(in srgb, var(--page-accent) 42%, transparent);
  color: var(--reflect-text) !important;
  transform: translateY(-1px);
  box-shadow: inset 0 0 20px var(--page-accent-faint);
}
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked)::before {
  content: '';
  width: 6px;
  height: 6px;
  margin-right: 8px;
  border-radius: 50%;
  background: var(--page-accent);
  box-shadow: 0 0 14px var(--page-accent);
  animation: navDotBreath 1.8s ease-in-out infinite;
}
div[data-testid="stRadio"] label[data-baseweb="radio"] p {
  color: inherit !important;
  font-weight: 500 !important;
  white-space: nowrap;
}

/* 主内容区偏移header */
.main-content-offset { padding-top: 64px; }

/* 页面切换过渡 - 优化 */
.page-transition {
  --page-accent: var(--reflect-cyan);
  --page-accent-soft: rgba(142,235,255,0.16);
  --page-accent-faint: rgba(142,235,255,0.07);
  position: relative;
  isolation: isolate;
  animation: pageMistIn 0.86s var(--reflect-ease) forwards;
  transition: opacity 0.18s ease, transform 0.18s ease, filter 0.18s ease;
  will-change: opacity, transform, filter;
}
.stApp.nav-leaving .page-transition {
  opacity: 0.58;
  transform: translateY(-4px) scale(0.996);
  filter: blur(2px);
}
.page-transition::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 22px;
  width: min(860px, 92vw);
  height: 260px;
  transform: translateX(-50%) translateY(-24px) scaleX(0.86);
  pointer-events: none;
  z-index: -1;
  opacity: 0;
  background:
    radial-gradient(ellipse at 50% 20%, var(--page-accent-soft), transparent 58%),
    linear-gradient(90deg, transparent, var(--page-accent-faint), transparent);
  filter: blur(22px);
  animation: mistSweep 0.96s var(--reflect-ease) forwards;
}
.page-transition .section-header,
.page-transition .home-hero,
.page-transition .workspace-card,
.page-transition .feature-card,
.page-transition .capability-card,
.page-transition .agent-flow-preview {
  animation: contentFloatIn 0.72s var(--reflect-ease) both;
}
.page-transition .workspace-card,
.page-transition .capability-card:nth-child(1) {
  animation-delay: 0.06s;
}
.page-transition .feature-card,
.page-transition .capability-card:nth-child(2) {
  animation-delay: 0.12s;
}
.page-transition .agent-flow-preview,
.page-transition .capability-card:nth-child(3) {
  animation-delay: 0.18s;
}
.page-home {
  --page-accent: var(--reflect-cyan);
  --page-accent-soft: rgba(142,235,255,0.16);
  --page-accent-faint: rgba(142,235,255,0.07);
}
.page-jd {
  --page-accent: var(--reflect-cyan);
  --page-accent-soft: rgba(142,235,255,0.16);
  --page-accent-faint: rgba(142,235,255,0.07);
}
.page-path {
  --page-accent: var(--reflect-mint);
  --page-accent-soft: rgba(169,245,200,0.16);
  --page-accent-faint: rgba(169,245,200,0.07);
}
.page-interview {
  --page-accent: var(--reflect-amber);
  --page-accent-soft: rgba(255,227,163,0.17);
  --page-accent-faint: rgba(255,227,163,0.075);
}
@keyframes pageMistIn {
  0% { opacity: 0; transform: translateY(10px) scale(0.996); filter: blur(3px); }
  46% { opacity: 1; filter: blur(0.8px); }
  100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
}
@keyframes mistSweep {
  0% { opacity: 0; transform: translateX(-50%) translateY(-28px) scaleX(0.72); }
  38% { opacity: 0.9; }
  100% { opacity: 0; transform: translateX(-50%) translateY(18px) scaleX(1.12); }
}
@keyframes contentFloatIn {
  0% { opacity: 0; transform: translateY(14px); filter: blur(3px); }
  58% { opacity: 1; filter: blur(0.5px); }
  100% { opacity: 1; transform: translateY(0); filter: blur(0); }
}
@keyframes navDotBreath {
  0%, 100% { opacity: 0.74; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.2); }
}

/* 响应式 - Reflect断点 */
@media (max-width: 1248px) {
  .home-hero h1 { font-size: 56px !important; line-height: 64px !important; }
  .section-header h2 { font-size: 40px !important; line-height: 48px !important; }
  .main-header h1 { font-size: 56px !important; line-height: 64px !important; }
  .main-header { padding-top: 120px !important; }
  .capability-grid { grid-template-columns: 1fr; }
  .agent-flow-steps { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .home-shell { width: calc(100% - 24px); }
  .home-hero { min-height: 380px; padding: 72px 12px 48px; }
  .home-hero h1 { font-size: 38px !important; line-height: 46px !important; }
  .hero-orbit { width: 280px; height: 280px; margin-left: -140px; top: 30px; }
  .hero-orbit::before { inset: 96px; }
  .capability-card { padding: 18px; min-height: auto; }
  .agent-flow-steps { grid-template-columns: 1fr; }
  .section-header { padding: 42px 16px 28px; }
  .section-header h2 { font-size: 30px !important; line-height: 38px !important; }
  .workspace-card { width: calc(100% - 24px); padding: 18px; }
  div[data-testid="stRadio"] div[role="radiogroup"] { border-radius: 18px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
  div[data-testid="stRadio"] label[data-baseweb="radio"] { min-height: 44px; min-width: 0; padding: 0 12px !important; }
  .main-header h1 { font-size: 36px !important; line-height: 44px !important; }
  .main-header { padding-top: 80px !important; }
  .score-ring-svg { width: 60px; height: 60px; }
  .score-ring-value { font-size: 18px; margin-top: 14px; }
  .confidence-meter .meter-value { font-size: 48px; }
  .feature-card { padding: 20px; }
  .agent-pipeline ol { display: grid; grid-template-columns: 1fr; }
  .native-brand { align-items: flex-start; gap: 10px; }
  .foglift-logo-mark { width: 38px; height: 38px; flex-basis: 38px; }
  .foglift-logo-name { font-size: 17px; line-height: 21px; }
  .foglift-logo-subtitle { display: none; }
  .card-header h3,
  .workspace-card h3 { font-size: 26px; line-height: 34px; }
  .stButton button { width: 100% !important; }
}
</style>
""", unsafe_allow_html=True)


# ========================================
# 页面结构 - 顶部导航Header
# ========================================
def render_header():
    """渲染顶部导航栏"""
    nav_items = [
        ("首页", "home"),
        ("JD 翻译", "jd_translate"),
        ("路径规划", "path_skill"),
        ("面试模拟", "interview"),
    ]
    page_options = {label: page_key for label, page_key in nav_items}
    page_labels = list(page_options.keys())
    current_page = st.session_state.get("current_page", "home")
    current_label = next(
        (label for label, page_key in page_options.items() if page_key == current_page),
        page_labels[0],
    )
    nav_accent = {
        "home": ("#8EEBFF", "rgba(142,235,255,0.16)", "rgba(142,235,255,0.07)"),
        "jd_translate": ("#8EEBFF", "rgba(142,235,255,0.16)", "rgba(142,235,255,0.07)"),
        "path_skill": ("#A9F5C8", "rgba(169,245,200,0.16)", "rgba(169,245,200,0.07)"),
        "interview": ("#FFE3A3", "rgba(255,227,163,0.17)", "rgba(255,227,163,0.075)"),
    }.get(current_page, ("#8EEBFF", "rgba(142,235,255,0.16)", "rgba(142,235,255,0.07)"))

    st.markdown(f"""
    <style>
    :root {{
      --page-accent: {nav_accent[0]};
      --page-accent-soft: {nav_accent[1]};
      --page-accent-faint: {nav_accent[2]};
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="native-brand" aria-label="FogLift 破雾">
        <svg class="foglift-logo-mark" viewBox="0 0 48 48" role="img" aria-labelledby="foglift-logo-title">
            <title id="foglift-logo-title">FogLift 破雾 Logo</title>
            <defs>
                <linearGradient id="fogliftLogoShell" x1="6" y1="6" x2="42" y2="42" gradientUnits="userSpaceOnUse">
                    <stop offset="0%" stop-color="rgba(142,235,255,0.22)" />
                    <stop offset="54%" stop-color="rgba(169,245,200,0.10)" />
                    <stop offset="100%" stop-color="rgba(255,227,163,0.18)" />
                </linearGradient>
            </defs>
            <rect class="logo-shell" x="5.5" y="5.5" width="37" height="37" rx="13" fill="url(#fogliftLogoShell)" />
            <circle class="logo-dawn" cx="31.5" cy="16.5" r="3.6" />
            <path class="logo-mist" d="M13 20.5h12.2c3.1 0 5.4-1.1 7-3.2" />
            <path class="logo-mist" d="M11.5 27h17.7c3.8 0 6.3-1.3 7.8-3.8" opacity="0.72" />
            <path class="logo-mist" d="M14.5 33h13.7" opacity="0.46" />
            <path class="logo-path" d="M17 34c4.8-6.9 10.2-11.5 16.5-13.8" />
        </svg>
        <div class="foglift-logo-copy">
            <div class="foglift-logo-name">FogLift·破雾</div>
            <div class="foglift-logo-subtitle">Multi-Agent Career Copilot</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    selected_label = st.radio(
        "选择功能窗口",
        page_labels,
        index=page_labels.index(current_label),
        horizontal=True,
        key="page_selector",
    )
    selected_page = page_options[selected_label]
    if selected_page != current_page:
        st.session_state.current_page = selected_page
        st.session_state.page_transition = True
        st.rerun()


# ========================================
# 页面渲染函数
# ========================================

def render_home():
    """渲染首页总控台。"""
    st.markdown("""
    <section class="home-hero">
        <div class="hero-orbit" aria-hidden="true">
            <div class="hero-orbit-ring ring-one"><span></span></div>
            <div class="hero-orbit-ring ring-two"><span></span></div>
            <div class="hero-orbit-ring ring-three"><span></span></div>
        </div>
        <div class="reflect-badge">Multi-Agent Career Copilot</div>
        <h1>看懂 JD，走出求职迷雾</h1>
        <p>JD 翻译、技能路径、面试模拟，一次串起你的求职准备。让多 Agent 帮你拆开招聘黑话、规划成长阶梯，并模拟真实面试反馈。</p>
    </section>
    """, unsafe_allow_html=True)

    spacer_left, col1, col2, spacer_right = st.columns([3, 1.2, 1.2, 3])
    with col1:
        if st.button("开始分析 JD", key="home_primary_jd"):
            st.session_state.current_page = "jd_translate"
            st.rerun()
    with col2:
        if st.button("练习面试回答", key="home_secondary_interview"):
            st.session_state.current_page = "interview"
            st.rerun()

    st.markdown("""
    <div class="home-shell">
        <div class="capability-grid">
            <article class="capability-card">
                <div class="capability-card-label">01 / JD Translator</div>
                <h3>JD 翻译器</h3>
                <p>把招聘黑话翻译成真实工作要求，识别硬技能、软技能和个人差距。</p>
            </article>
            <article class="capability-card">
                <div class="capability-card-label">02 / Career Ladder</div>
                <h3>阶梯路径</h3>
                <p>从目标岗位反推成长路线，输出阶段任务、技能优先级和免费学习资源。</p>
            </article>
            <article class="capability-card">
                <div class="capability-card-label">03 / Interview Simulator</div>
                <h3>面试模拟</h3>
                <p>生成岗位面试题，分析回答质量，给出评分、亮点和改进建议。</p>
            </article>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav1, nav2, nav3 = st.columns(3)
    for column, page_key, button_label in [
        (nav1, "jd_translate", "翻译 JD"),
        (nav2, "path_skill", "规划路径"),
        (nav3, "interview", "开始模拟"),
    ]:
        with column:
            if st.button(button_label, key=f"home_go_{page_key}"):
                st.session_state.current_page = page_key
                st.rerun()

    st.markdown("""
    <div class="home-shell">
        <section class="agent-flow-preview">
            <h3>Agent 协作流</h3>
            <div class="agent-flow-steps">
                <div class="agent-flow-step"><strong>Supervisor</strong><span>识别意图并路由到对应子图。</span></div>
                <div class="agent-flow-step"><strong>Subgraph Agents</strong><span>按任务顺序解析、翻译、规划或评分。</span></div>
                <div class="agent-flow-step"><strong>Knowledge Base</strong><span>每个 Agent 使用知识库作为输出依据。</span></div>
                <div class="agent-flow-step"><strong>Structured Result</strong><span>返回可阅读、可执行的求职建议。</span></div>
            </div>
        </section>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(badge: str, title: str, description: str):
    """渲染任务页统一标题区。"""
    st.markdown(f"""
    <section class="section-header">
        <div class="reflect-badge">{badge}</div>
        <h2>{title}</h2>
        <p>{description}</p>
    </section>
    """, unsafe_allow_html=True)


def render_workspace_intro(title: str, description: str):
    """渲染任务输入区说明，不包裹 Streamlit 原生控件。"""
    st.markdown(f"""
    <section class="workspace-card">
        <h3>{title}</h3>
        <p>{description}</p>
    </section>
    """, unsafe_allow_html=True)


def render_agent_pipeline(steps: list[str]):
    """渲染多 Agent 执行状态。"""
    items = "".join(
        f'<li style="--step-index:{index}">{escape(step)}</li>'
        for index, step in enumerate(steps)
    )
    st.markdown(f"""
    <div class="agent-pipeline" role="status" aria-live="polite">
        <div class="agent-pipeline-label">Agent pipeline running</div>
        <ol>{items}</ol>
    </div>
    """, unsafe_allow_html=True)

def render_tag_list(items: list[str], class_name: str = "skill-tag"):
    """Inline chip list for short result labels."""
    tags = "".join(f'<span class="{class_name}">{escape(str(item))}</span>' for item in items)
    st.markdown(f'<div class="skill-tag-list">{tags}</div>', unsafe_allow_html=True)


def render_empty_result(message: str):
    st.markdown(
        f'<span style="color:var(--reflect-muted)">{escape(message)}</span>',
        unsafe_allow_html=True,
    )


def render_jd_translator():
    """渲染JD翻译器页面"""
    render_section_header(
        "JD Translator",
        "把招聘黑话翻译成真实工作要求",
        "粘贴岗位 JD 和你的背景信息，让 Agent 提取技能要求、翻译黑话并生成差距分析。",
    )
    render_workspace_intro(
        "输入 JD 与个人背景",
        "JD 越完整，技能识别和黑话翻译越准确；背景信息用于差距分析。",
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><h3>JD 文本分析</h3></div>', unsafe_allow_html=True)
        
        jd_text = st.text_area(
            "粘贴JD文本:",
            height=200,
            placeholder="例如：\n岗位职责：\n1. 负责AI产品的需求分析和产品规划\n2. 协调研发团队推动产品迭代\n\n任职要求：\n1. 本科及以上学历，3年以上产品经验\n2. 熟悉AI/ML相关技术...",
            key="jd_text_input_value",
            value=st.session_state.jd_text_input_value,
        )
        
        with st.expander("👤 用户画像（可选）", expanded=False):
            st.caption("简单描述你的背景，帮助系统更精准分析差距")
            user_profile_input = st.text_area(
                "你的背景描述:",
                placeholder="例如：山东大学大二在读，自动化专业，学过Python基础",
                height=80,
                key="user_profile_input_value",
                value=st.session_state.user_profile_input_value,
                label_visibility="collapsed"
            )
        
        if st.button("开始分析", use_container_width=True):
            if jd_text:
                try:
                    render_agent_pipeline(["JD解析师提取要求", "黑话翻译官还原真实含义", "差距分析师生成建议"])
                    with st.spinner("分析中，请稍候..."):
                        profile = None
                        if user_profile_input and user_profile_input.strip():
                            try:
                                profile = json.loads(user_profile_input)
                            except json.JSONDecodeError:
                                profile = {"背景描述": user_profile_input.strip()}
                        
                        payload = {"jd_text": jd_text}
                        if profile:
                            payload["user_profile"] = profile
                        
                        response = requests.post(
                            API_URL,
                            json={"intent": "jd_translate", "payload": payload},
                            timeout=30
                        )
                        result = response.json()
                        
                        if result.get("success"):
                            st.session_state.jd_result = result.get("result") or {}
                            st.success("✅ 分析完成!")
                            st.rerun()
                        else:
                            st.error(f"❌ 错误: {result.get('error', '未知错误')}")
                except Exception as e:
                    st.error(f"❌ 请求失败: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><h3>分析概览</h3></div>', unsafe_allow_html=True)
        render_tag_list([
            "硬技能: 技术能力、工具使用",
            "软技能: 沟通、协作、领导力",
            "经验要求: 工作年限",
            "学历要求: 学历学位",
            "HR黑话: 原文→真实含义",
            "差距分析: 背景与JD差距",
        ])
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 显示分析结果
    if "jd_result" in st.session_state and st.session_state.jd_result:
        result = st.session_state.jd_result
        
        st.markdown('<div class="feature-card fade-in">', unsafe_allow_html=True)
        st.markdown('<div class="result-section-kicker">Result Summary</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><h3>结果摘要</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h4>硬技能</h4>", unsafe_allow_html=True)
            skills = result.get("硬技能", [])
            if skills:
                render_tag_list(skills, "skill-tag skill-tag-hard")
            else:
                render_empty_result("未识别到硬技能")
            
            st.markdown("<br><h4>软技能</h4>", unsafe_allow_html=True)
            soft_skills = result.get("软技能", [])
            if soft_skills:
                render_tag_list(soft_skills, "skill-tag skill-tag-soft")
            else:
                render_empty_result("未识别到软技能")
        
        with col2:
            st.markdown("<h4>经验要求</h4>", unsafe_allow_html=True)
            st.markdown(f'<div class="gap-time-card" style="text-align:left;margin-top:0;">'
                       f'<div style="font-size:16px;color:var(--reflect-text);">{result.get("经验要求", "未提及")}</div></div>',
                       unsafe_allow_html=True)
            
            st.markdown("<h4>学历要求</h4>", unsafe_allow_html=True)
            st.markdown(f'<div class="gap-time-card" style="text-align:left;margin-top:0;">'
                       f'<div style="font-size:16px;color:var(--reflect-text);">{result.get("学历要求", "未提及")}</div></div>',
                       unsafe_allow_html=True)
        
        st.markdown('<br><h4>HR 黑话翻译</h4>', unsafe_allow_html=True)
        jargon = result.get("HR黑话翻译", {})
        if jargon:
            for term, meaning in jargon.items():
                st.markdown(f"""
                <div class="jargon-card">
                    <div class="jargon-term">{term}</div>
                    <div class="jargon-translation">{meaning}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:var(--reflect-muted)'>未识别到HR黑话</span>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 差距分析
        gaps = result.get("差距分析", {})
        if gaps.get("差距项"):
            st.markdown('<div class="feature-card fade-in">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><h3>差距分析</h3></div>', unsafe_allow_html=True)
            
            for gap in gaps.get("差距项", []):
                st.markdown(f"""
                <div class="gap-item">
                    <div class="gap-skill">• {gap.get('技能', '')}</div>
                    <div class="gap-desc">{gap.get('差距描述', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            if gaps.get("弥补时间估计"):
                st.markdown(f"""
                <div class="gap-time-card fade-in">
                    <div class="time-label">预计弥补时间</div>
                    <div class="time-value">{gaps.get('弥补时间估计')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)


def render_path_skill():
    """渲染阶梯路径页面"""
    render_section_header(
        "Career Ladder",
        "从目标岗位反推成长路径",
        "输入目标岗位，生成阶段计划、技能优先级和可执行的学习资源。",
    )
    render_workspace_intro(
        "输入你的目标岗位",
        "系统会拆解岗位能力维度，并生成四阶段路径、技能优先级和免费学习资源。",
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><h3>岗位规划</h3></div>', unsafe_allow_html=True)
        
        target_position = st.text_input(
            "目标岗位:",
            placeholder="例如：产品经理、数据分析师、AI算法工程师...",
            key="target_position_path_value",
            value=st.session_state.target_position_path_value,
        )
        
        if st.button("开始规划", use_container_width=True):
            if target_position:
                try:
                    render_agent_pipeline(["岗位拆解师提取能力维度", "阶梯规划师生成路径", "技能推荐官排序优先级", "资源检索员匹配学习资源"])
                    with st.spinner("规划中，请稍候..."):
                        response = requests.post(
                            API_URL,
                            json={"intent": "path_skill", "payload": {"target_position": target_position}},
                            timeout=30
                        )
                        result = response.json()
                        
                        if result.get("success"):
                            st.session_state.path_result = result.get("result") or {}
                            st.success("✅ 规划完成!")
                            st.rerun()
                        else:
                            st.error(f"❌ 错误: {result.get('error', '未知错误')}")
                except Exception as e:
                    st.error(f"❌ 请求失败: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
            else:
                st.warning("请输入目标岗位")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><h3>规划内容</h3></div>', unsafe_allow_html=True)
        render_tag_list([
            "能力维度: 岗位核心技能拆解",
            "阶梯路径: 4步成长路线",
            "校园项目",
            "实习title",
            "实习关键词",
            "秋招目标",
            "推荐技能: 优先级排序",
            "学习资源: 免费资源链接",
        ])
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 显示规划结果
    if "path_result" in st.session_state and st.session_state.path_result:
        result = st.session_state.path_result
        
        # 岗位名称
        st.markdown('<div class="feature-card fade-in">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><h3>岗位信息</h3></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="gap-time-card" style="text-align:left;">
            <div style="font-size:14px;color:var(--reflect-muted);margin-bottom:4px;">目标岗位</div>
            <div style="font-size:24px;font-weight:500;color:var(--reflect-accent);">{result.get('岗位名称', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 能力维度
        st.markdown('<br><h4>能力维度</h4>', unsafe_allow_html=True)
        ability_dims = result.get("能力维度", [])
        if ability_dims:
            render_tag_list(ability_dims)
        else:
            render_empty_result("暂无能力维度信息")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 阶梯路径 - 时间轴样式
        ladder = result.get("阶梯路径", {})
        if ladder:
            st.markdown('<div class="feature-card fade-in">', unsafe_allow_html=True)
            st.markdown('<div class="result-section-kicker">Career Ladder</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><h3>阶梯路径</h3></div>', unsafe_allow_html=True)
            
            st.markdown('<div class="timeline">', unsafe_allow_html=True)
            steps = [
                (ladder.get("step1_校园项目", ""), "校园项目"),
                (ladder.get("step2_实习title", ""), "实习 title"),
                (ladder.get("step3_实习积累关键词", ""), "实习积累关键词"),
                (ladder.get("step4_秋招目标岗位", ""), "秋招目标岗位"),
            ]
            for content, title in steps:
                st.markdown(f"""
                <div class="timeline-item">
                    <div class="step-title">{title}</div>
                    <div class="step-content">{content}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 推荐技能
        skills = result.get("推荐技能", [])
        if skills:
            st.markdown('<div class="feature-card fade-in">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><h3>推荐技能</h3></div>', unsafe_allow_html=True)
            
            for skill in skills:
                priority = skill.get("优先级", "中")
                priority_class = f"priority-{priority.lower()}"
                st.markdown(f"""
                <div class="resource-card fade-in">
                    <div class="resource-title">{skill.get("技能名", "")}</div>
                    <span class="{priority_class}">{priority}优先</span>
                    <div style="margin-top:8px;color:var(--reflect-muted);">{skill.get("说明", "")}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 学习资源
        resources = result.get("学习资源", [])
        if resources:
            st.markdown('<div class="feature-card fade-in">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><h3>学习资源</h3></div>', unsafe_allow_html=True)
            
            for res in resources:
                skill_name = res.get("技能名", "")
                st.markdown(f'<h4 style="color:var(--reflect-accent);font-weight:500;margin-bottom:12px;">{skill_name}</h4>', unsafe_allow_html=True)
                for r in res.get("资源", []):
                    st.markdown(f"""
                    <div class="resource-card fade-in">
                        <div class="resource-title">{r.get("name", "")}</div>
                        <a href="{r.get('url', '#')}" target="_blank" class="resource-link">
                            {r.get('url', '')}
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)


def render_interview():
    """渲染面试模拟页面"""
    render_section_header(
        "Interview Simulator",
        "用岗位面试题练出更清晰的回答",
        "生成面试题、提交回答，并获得结构化评分、亮点和改进建议。",
    )
    render_workspace_intro(
        "选择岗位并开始模拟",
        "先生成一道岗位面试题，再提交你的回答，系统会按内容、逻辑和匹配度评分。",
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><h3>面试流程</h3></div>', unsafe_allow_html=True)
        
        # 获取面试题
        if not st.session_state.question:
            target_pos = st.text_input(
                "目标岗位:",
                placeholder="例如：产品经理、数据分析师...",
                key="target_position_interview_value",
                value=st.session_state.target_position_interview_value,
            )
            
            if st.button("获取面试题", use_container_width=True):
                if target_pos:
                    try:
                        render_agent_pipeline(["面试官生成问题", "知识库匹配岗位题型", "会话状态写入"])
                        with st.spinner("生成面试题..."):
                            response = requests.post(
                                API_URL,
                                json={"intent": "interview_question", "payload": {"target_position": target_pos}},
                                timeout=30
                            )
                            result = response.json()
                            
                            if result.get("success"):
                                inner = result.get("result") or {}
                                st.session_state.interview_session = inner.get("session_id")
                                st.session_state.question = inner.get("question")
                                st.success("✅ 面试题生成成功!")
                                st.rerun()
                            else:
                                st.error(f"❌ 错误: {result.get('error', '未知错误')}")
                    except Exception as e:
                        st.error(f"❌ 请求失败: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                else:
                    st.warning("请输入目标岗位")
        
        # 显示当前面试题
        if st.session_state.question:
            st.markdown('<div style="background:var(--reflect-fade-card);padding:20px;border-radius:var(--reflect-radius-sm);margin-bottom:20px;border-left:2px solid var(--reflect-accent);">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:13px;color:var(--reflect-muted);margin-bottom:8px;">当前面试题</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:18px;font-weight:500;color:var(--reflect-text);">{st.session_state.question}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 提交回答
            st.markdown('<h4>提交你的回答</h4>', unsafe_allow_html=True)
            answer = st.text_area(
                "你的回答:",
                height=150,
                placeholder="输入你的面试回答...",
                key="answer_input_value",
                value=st.session_state.answer_input_value,
            )
            
            if st.button("评估回答", use_container_width=True):
                if answer:
                    try:
                        render_agent_pipeline(["答案分析师评分反馈", "鼓励师生成改进建议", "结构化评估结果"])
                        with st.spinner("评估中，请稍候..."):
                            response = requests.post(
                                API_URL,
                                json={
                                    "intent": "interview_answer",
                                    "payload": {
                                        "session_id": st.session_state.interview_session,
                                        "answer": answer
                                    }
                                },
                                timeout=30
                            )
                            result = response.json()
                            
                            if result.get("success"):
                                st.session_state.interview_evaluation = result.get("result") or {}
                                st.success("✅ 评估完成!")
                                st.rerun()
                            else:
                                st.error(f"❌ 错误: {result.get('error', '未知错误')}")
                    except Exception as e:
                        st.error(f"❌ 请求失败: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                else:
                    st.warning("请输入回答")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><h3>评分维度</h3></div>', unsafe_allow_html=True)
        render_tag_list([
            "内容分 (40%): 答案相关性",
            "逻辑分 (30%): 回答逻辑性",
            "匹配分 (30%): 岗位匹配度",
            "总分: 综合得分",
            "敢投指数 = 总分",
        ])
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 显示评估结果
    if "interview_evaluation" in st.session_state and st.session_state.interview_evaluation:
        result = st.session_state.interview_evaluation
        scores = result.get("评分", {})
        
        st.markdown('<div class="feature-card fade-in">', unsafe_allow_html=True)
        st.markdown('<div class="result-section-kicker">Evaluation</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><h3>评估结果</h3></div>', unsafe_allow_html=True)
        
        # 评分卡片 (SVG环形进度)
        def score_ring(value, label, r=34, stroke=4):
            c = 2 * 3.14159 * r
            offset = c - (min(value, 100) / 100) * c
            return f'''
            <div class="score-ring">
                <div class="score-ring-wrap">
                    <svg class="score-ring-svg" viewBox="0 0 80 80">
                        <circle class="score-ring-bg" cx="40" cy="40" r="{r}"/>
                        <circle class="score-ring-fg" cx="40" cy="40" r="{r}"
                            stroke-dasharray="{c}" stroke-dashoffset="{offset}"/>
                    </svg>
                    <div class="score-ring-value">{value}</div>
                </div>
                <div class="score-ring-label">{label}</div>
            </div>'''
        
        st.markdown(f'<div class="score-container">'
            + score_ring(scores.get('内容分', 0), '内容分 (40%)')
            + score_ring(scores.get('逻辑分', 0), '逻辑分 (30%)')
            + score_ring(scores.get('匹配分', 0), '匹配分 (30%)')
            + score_ring(scores.get('总分', 0), '总分')
            + '</div>', unsafe_allow_html=True)
        
        # 敢投指数
        confidence = result.get("敢投指数", 0)
        st.markdown(f"""
        <div class="confidence-meter fade-in">
            <div class="meter-value">{confidence}</div>
            <div class="meter-label">敢投指数</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 鼓励语
        if result.get("鼓励语"):
            st.markdown(f"""
            <div class="cheer-bubble fade-in">
                <div class="cheer-text">{result.get('鼓励语', '')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 亮点
        highlights = result.get("亮点", [])
        if highlights:
            st.markdown('<div class="highlight-section fade-in">', unsafe_allow_html=True)
            st.markdown('<h4>你的亮点</h4>', unsafe_allow_html=True)
            st.markdown('<ul>', unsafe_allow_html=True)
            for h in highlights:
                st.markdown(f'<li>{h}</li>', unsafe_allow_html=True)
            st.markdown('</ul>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 建议
        if result.get("建议"):
            st.markdown('<div class="advice-section fade-in">', unsafe_allow_html=True)
            st.markdown('<h4>改进建议</h4>', unsafe_allow_html=True)
            st.markdown(f'<p>{result.get("建议", "")}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)


# ========================================
# Session State 初始化
# ========================================
def init_session_state():
    """初始化所有页面的输入状态"""
    default_states = {
        "current_page": "home",
        "jd_text_input_value": "",
        "user_profile_input_value": "",
        "target_position_path_value": "",
        "target_position_interview_value": "",
        "answer_input_value": "",
        "jd_result": None,
        "path_result": None,
        "interview_session": None,
        "question": None,
        "interview_evaluation": None,
    }
    
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ========================================
# 主应用逻辑
# ========================================
def main():
    init_session_state()
    render_header()
    page = st.session_state.get("current_page", "home")
    page_classes = {
        "home": "page-home",
        "jd_translate": "page-jd",
        "path_skill": "page-path",
        "interview": "page-interview",
    }
    page_class = page_classes.get(page, "page-home")
    
    if page == "home":
        st.markdown(f'<div class="page-transition {page_class}" id="pt-{page}">', unsafe_allow_html=True)
        render_home()
        st.markdown('</div>', unsafe_allow_html=True)
    elif page == "jd_translate":
        st.markdown(f'<div class="page-transition {page_class}" id="pt-{page}">', unsafe_allow_html=True)
        render_jd_translator()
        st.markdown('</div>', unsafe_allow_html=True)
    elif page == "path_skill":
        st.markdown(f'<div class="page-transition {page_class}" id="pt-{page}">', unsafe_allow_html=True)
        render_path_skill()
        st.markdown('</div>', unsafe_allow_html=True)
    elif page == "interview":
        st.markdown(f'<div class="page-transition {page_class}" id="pt-{page}">', unsafe_allow_html=True)
        render_interview()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <script>
    (function() {{
        var app = document.querySelector('.stApp');
        var markLeaving = function() {{
            if (!app) return;
            app.classList.add('nav-leaving');
            window.setTimeout(function() {{
                app.classList.remove('nav-leaving');
            }}, 900);
        }};
        var pageButtons = new Set(['开始分析 JD', '练习面试回答', '翻译 JD', '规划路径', '开始模拟']);
        document.querySelectorAll('div[data-testid="stRadio"] label[data-baseweb="radio"], .stButton button').forEach(function(control) {{
            if (control.dataset.fogliftBound === '1') return;
            control.dataset.fogliftBound = '1';
            control.addEventListener('pointerdown', function() {{
                var isNavRadio = !!control.closest('div[data-testid="stRadio"]');
                var isPageButton = pageButtons.has((control.innerText || '').trim());
                if (isNavRadio || isPageButton) markLeaving();
            }}, {{ passive: true }});
        }});
        var el = document.querySelector('.page-transition');
        if (el) {{
            el.style.animation = 'none';
            el.offsetHeight;
            el.style.animation = 'pageMistIn 0.86s cubic-bezier(0.22, 1, 0.36, 1) forwards';
        }}
    }})();
    </script>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
