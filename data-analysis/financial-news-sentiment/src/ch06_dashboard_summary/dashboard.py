"""Streamlit Dashboard: Financial News Sentiment Analysis.

运行方式:
    cd financial_news_sentiment_analysis
    streamlit run src/ch06_dashboard_summary/dashboard.py
"""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# 路径设置
SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SRC_DIR.parent
sys.path.insert(0, str(SRC_DIR))

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Financial News Sentiment Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Data Loading ─────────────────────────────────────────────
@st.cache_data
def load_data():
    """Load all chapter outputs."""
    base = PROJECT_ROOT

    df = pd.read_csv(
        os.path.join(base, "outputs", "ch01_data_preprocessing", "ch01_cleaned_data.csv"),
        parse_dates=["date"],
    )

    sent_path = os.path.join(base, "outputs", "ch03_text_mining_sentiment", "ch03_sentiment_labels.csv")
    if os.path.exists(sent_path):
        sentiment = pd.read_csv(sent_path)
        df["sentiment_score"] = sentiment["sentiment_score"].values
        df["sentiment"] = sentiment["sentiment"].values

    feat_path = os.path.join(base, "outputs", "ch04_feature_engineering", "ch04_engineered_features.csv")
    features = None
    if os.path.exists(feat_path):
        features = pd.read_csv(feat_path, index_col=0, parse_dates=True)

    evt_path = os.path.join(base, "outputs", "ch05_event_driven_strategy", "ch05_event_calendar.csv")
    events = None
    if os.path.exists(evt_path):
        events = pd.read_csv(evt_path, parse_dates=["date"])

    return df, features, events


df, features, events = load_data()

# ── Sidebar ──────────────────────────────────────────────────
st.sidebar.title("Filters")
date_min = df["date"].min().to_pydatetime()
date_max = df["date"].max().to_pydatetime()
date_range = st.sidebar.date_input("Date Range", [date_min, date_max])

if len(date_range) == 2:
    mask = (df["date"] >= pd.Timestamp(date_range[0])) & (df["date"] <= pd.Timestamp(date_range[1]))
    df_filtered = df[mask].copy()
else:
    df_filtered = df.copy()

# ── KPI Cards ────────────────────────────────────────────────
st.title("Financial News Sentiment Analysis Dashboard")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Articles", f"{len(df_filtered):,}")
col2.metric("Date Span", f"{(df_filtered['date'].max() - df_filtered['date'].min()).days} days")
if "sentiment_score" in df_filtered.columns:
    col3.metric("Avg Sentiment", f"{df_filtered['sentiment_score'].mean():.3f}")
else:
    col3.metric("Avg Sentiment", "N/A")
if events is not None:
    col4.metric("High-Impact Events", f"{len(events):,}")
else:
    col4.metric("High-Impact Events", "N/A")

st.markdown("---")

# ── Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Time Trends",
    "Industry Analysis",
    "Event Analysis",
    "Keyword Cloud",
])

# Tab 1: Time Trends
with tab1:
    st.subheader("Daily Sentiment & News Volume")

    if features is not None:
        feat_filtered = features[
            (features["date"] >= pd.Timestamp(date_range[0])) &
            (features["date"] <= pd.Timestamp(date_range[1]))
        ] if len(date_range) == 2 else features

        fig1 = px.line(
            feat_filtered, x="date", y=["sentiment_mean", "news_count"] if "news_count" in feat_filtered.columns else ["sentiment_mean"],
            title="Daily Sentiment Score & News Volume",
            labels={"value": "Value", "variable": "Metric"},
        )
        st.plotly_chart(fig1, use_container_width=True)

        if "positive_ratio" in feat_filtered.columns:
            fig2 = px.area(
                feat_filtered, x="date",
                y=["positive_ratio", "negative_ratio", "neutral_ratio"] if "neutral_ratio" in feat_filtered.columns else ["positive_ratio", "negative_ratio"],
                title="Sentiment Proportion Over Time",
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Feature data not available. Run ch04 first.")

# Tab 2: Industry Analysis
with tab2:
    st.subheader("Industry Distribution")

    def get_primary_cat(x):
        if isinstance(x, str):
            try:
                lst = ast.literal_eval(x)
                return lst[0] if lst else "Unknown"
            except Exception:
                return x
        return "Unknown"

    df_filtered["primary_cat"] = df_filtered["categories_list"].apply(get_primary_cat)
    cat_counts = df_filtered["primary_cat"].value_counts().head(15)

    fig3 = px.bar(
        x=cat_counts.values, y=cat_counts.index,
        orientation="h", title="Top 15 Industries by News Volume",
        labels={"x": "Count", "y": "Industry"},
    )
    st.plotly_chart(fig3, use_container_width=True)

    if "sentiment_score" in df_filtered.columns:
        cat_sentiment = df_filtered.groupby("primary_cat")["sentiment_score"].mean().sort_values().head(15)
        fig4 = px.bar(
            x=cat_sentiment.values, y=cat_sentiment.index,
            orientation="h", title="Top 15 Industries by Avg Sentiment",
            labels={"x": "Avg Sentiment Score", "y": "Industry"},
            color=cat_sentiment.values,
            color_continuous_scale="RdYlGn",
        )
        st.plotly_chart(fig4, use_container_width=True)

# Tab 3: Event Analysis
with tab3:
    st.subheader("High-Impact Event Analysis")

    if events is not None:
        st.metric("Total Events", len(events))

        # Event type distribution
        type_counts = events["event_type"].value_counts()
        fig5 = px.pie(values=type_counts.values, names=type_counts.index, title="Event Type Distribution")
        col_left, col_right = st.columns(2)
        with col_left:
            st.plotly_chart(fig5, use_container_width=True)

        # Top events table
        with col_right:
            st.subheader("Top 20 by Influence Score")
            st.dataframe(
                events.nlargest(20, "influence_score")[
                    ["date", "title", "event_type", "influence_score", "sentiment_change"]
                ].reset_index(drop=True),
                use_container_width=True, height=500,
            )

        # Sentiment change distribution
        fig6 = px.histogram(
            events, x="sentiment_change", nbins=30,
            title="Sentiment Change Distribution (Event Window)",
            color_discrete_sequence=["steelblue"],
        )
        fig6.add_vline(x=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("Event data not available. Run ch05 first.")

# Tab 4: Keyword Cloud
with tab4:
    st.subheader("Keyword Cloud")

    try:
        from wordcloud import WordCloud

        all_keywords = []
        for x in df_filtered["keywords_list"]:
            if isinstance(x, str):
                try:
                    all_keywords.extend(ast.literal_eval(x))
                except Exception:
                    pass
            elif isinstance(x, list):
                all_keywords.extend(x)

        if all_keywords:
            from collections import Counter
            kw_counts = Counter(all_keywords)
            wc = WordCloud(width=1000, height=500, background_color="white", max_words=150)
            wc.generate_from_frequencies(kw_counts)
            st.image(wc.to_array(), use_container_width=True)
        else:
            st.info("No keywords found in the dataset.")
    except ImportError:
        st.warning("wordcloud package not installed. Run: pip install wordcloud")

# ── Footer ───────────────────────────────────────────────────
st.markdown("---")
st.caption("Financial News Sentiment Analysis Dashboard | Data: 2016-2026 Indian Financial News")
