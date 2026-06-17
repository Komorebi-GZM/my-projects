"""Prompt-05: 事件驱动策略分析.

基于 impact_tier、relevance_score、情感标签等维度，
构建新闻影响力评估体系，识别高影响力新闻事件，
分析事件发布后的舆情扩散模式，输出事件日历与影响力评分。

注意: 因数据集不含股价数据，本章聚焦舆情层面的事件影响力分析。

产物输出到: outputs/ch05_event_driven_strategy/
"""

from __future__ import annotations

import ast
import logging
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

from utils.config import (
    FIGURE_DPI_HIGH,
    MATPLOTLIB_RC_PARAMS,
    get_chapter_output_dir,
    setup_logging,
)

plt.rcParams.update(MATPLOTLIB_RC_PARAMS)

logger = setup_logging("ch05_events", log_to_file=True)
OUTPUT_DIR = get_chapter_output_dir("ch05_event_driven_strategy")
os.makedirs(OUTPUT_DIR, exist_ok=True)

warnings.filterwarnings("ignore", category=FutureWarning)


# =============================================================================
# Step 1: 数据加载与高影响力事件筛选
# =============================================================================

def load_data() -> pd.DataFrame:
    """加载 ch01 + ch03 数据并合并."""
    logger.info("Step 1: 加载数据...")
    ch01_path = os.path.join(
        PROJECT_ROOT, "outputs", "ch01_data_preprocessing", "ch01_cleaned_data.csv"
    )
    sentiment_path = os.path.join(
        PROJECT_ROOT, "outputs", "ch03_text_mining_sentiment", "ch03_sentiment_labels.csv"
    )
    df = pd.read_csv(ch01_path, parse_dates=["date"])
    sentiment = pd.read_csv(sentiment_path)
    df["sentiment_score"] = sentiment["sentiment_score"].values
    df["sentiment"] = sentiment["sentiment"].values
    logger.info(f"  数据: {len(df):,} 行")
    return df


def filter_high_impact_events(df: pd.DataFrame) -> pd.DataFrame:
    """筛选高影响力事件 (impact_tier=HIGH & relevance_score>=7)."""
    events = df[(df["impact_tier"] == "HIGH") & (df["relevance_score"] >= 7)].copy()
    logger.info(f"  高影响力事件: {len(events)} 条")
    if len(events) < 10:
        logger.warning(f"  事件不足 10 条，降低阈值至 relevance_score>=5")
        events = df[(df["impact_tier"] == "HIGH") & (df["relevance_score"] >= 5)].copy()
        logger.info(f"  降低阈值后: {len(events)} 条")
    return events


# =============================================================================
# Step 2: 事件类型分类 + 窗口分析
# =============================================================================

def parse_categories(cat_str) -> list:
    """安全解析 categories_list."""
    if isinstance(cat_str, list):
        return cat_str
    try:
        result = ast.literal_eval(cat_str)
        if isinstance(result, list):
            return result
    except Exception:
        pass
    return [str(cat_str)]


def classify_event(row) -> str:
    """基于 categories 将事件分为 5 类."""
    cats = parse_categories(row.get("categories_list", []))
    cats_str = " ".join(cats).lower()

    if any(k in cats_str for k in ["policy", "regulation", "government", "rbi", "tax", "sebi"]):
        return "Policy"
    elif any(k in cats_str for k in ["earning", "result", "revenue", "profit", "q1", "q2", "q3", "q4", "financial"]):
        return "Earnings"
    elif any(k in cats_str for k in ["war", "conflict", "geopolitical", "sanction", "oil", "terror"]):
        return "Geopolitical"
    elif any(k in cats_str for k in ["bank", "fintech", "it", "pharma", "auto", "tech", "telecom"]):
        return "Industry"
    else:
        return "Other"


def compute_window_analysis(
    events: pd.DataFrame, df: pd.DataFrame, window: int = 7
) -> pd.DataFrame:
    """计算每个事件的窗口情感变化."""
    logger.info(f"Step 2: 窗口分析 (window={window}天)...")

    events["event_type"] = events.apply(classify_event, axis=1)
    logger.info(f"  事件类型分布: {events['event_type'].value_counts().to_dict()}")

    results = []
    for _, event in events.iterrows():
        event_date = event["date"]
        if pd.isna(event_date):
            continue

        # 事件窗口
        window_df = df[
            (df["date"] >= event_date - pd.Timedelta(days=window))
            & (df["date"] <= event_date + pd.Timedelta(days=window))
        ]
        # 基线窗口
        baseline_df = df[
            (df["date"] < event_date - pd.Timedelta(days=window))
            & (df["date"] >= event_date - pd.Timedelta(days=window * 3))
        ]

        baseline_mean = baseline_df["sentiment_score"].mean() if len(baseline_df) > 0 else 0
        window_mean = window_df["sentiment_score"].mean() if len(window_df) > 0 else 0

        cats = parse_categories(event.get("categories_list", []))
        results.append({
            "date": event_date,
            "title": event.get("title", ""),
            "event_type": event["event_type"],
            "relevance_score": event["relevance_score"],
            "window_sentiment_mean": window_mean,
            "baseline_sentiment_mean": baseline_mean,
            "sentiment_change": window_mean - baseline_mean,
            "affected_categories": ", ".join(cats[:3]),
            "news_count_in_window": len(window_df),
        })

    impact_df = pd.DataFrame(results)
    if len(impact_df) > 0:
        impact_df["date"] = pd.to_datetime(impact_df["date"])
    logger.info(f"  窗口分析完成: {len(impact_df)} 个事件")
    return impact_df


# =============================================================================
# Step 3: 影响力评分 + 可视化 + 报告
# =============================================================================

def compute_influence_score(impact_df: pd.DataFrame) -> pd.DataFrame:
    """构建综合影响力评分."""
    logger.info("Step 3: 影响力评分...")

    impact_df["breadth"] = impact_df["affected_categories"].apply(lambda x: len(x.split(", ")))

    scaler = MinMaxScaler()
    for col in ["relevance_score", "sentiment_change", "breadth"]:
        vals = impact_df[[col]].values
        impact_df[f"{col}_norm"] = scaler.fit_transform(vals)

    impact_df["influence_score"] = (
        0.3 * impact_df["relevance_score_norm"]
        + 0.3 * impact_df["sentiment_change_norm"].abs()
        + 0.2 * impact_df["breadth_norm"]
        + 0.2 * impact_df["window_sentiment_mean"].abs()
    )

    logger.info(f"  评分范围: [{impact_df['influence_score'].min():.3f}, {impact_df['influence_score'].max():.3f}]")
    return impact_df


def save_results(impact_df: pd.DataFrame) -> None:
    """保存事件日历和影响力评分."""
    # 事件日历（按日期排序）
    calendar = impact_df.sort_values("date").reset_index(drop=True)
    calendar.to_csv(os.path.join(OUTPUT_DIR, "ch05_event_calendar.csv"), index=False)
    logger.info("  事件日历已保存")

    # 影响力评分（按评分降序）
    scores = impact_df.sort_values("influence_score", ascending=False).reset_index(drop=True)
    scores.to_csv(os.path.join(OUTPUT_DIR, "ch05_influence_score.csv"), index=False)
    logger.info("  影响力评分已保存")


def plot_event_analysis(impact_df: pd.DataFrame) -> None:
    """绘制事件分析 4 子图."""
    logger.info("  生成可视化...")

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 1. 事件类型分布
    type_counts = impact_df["event_type"].value_counts()
    colors = sns.color_palette("Set2", len(type_counts))
    axes[0, 0].pie(type_counts.values, labels=type_counts.index, autopct="%1.1f%%", colors=colors)
    axes[0, 0].set_title("Event Type Distribution", fontsize=13)

    # 2. Top10 行业平均影响力
    industry_impact = (
        impact_df.groupby("affected_categories")["influence_score"]
        .mean().sort_values(ascending=False).head(10)
    )
    axes[0, 1].barh(range(len(industry_impact)), industry_impact.values, color="steelblue")
    axes[0, 1].set_yticks(range(len(industry_impact)))
    axes[0, 1].set_yticklabels(industry_impact.index, fontsize=9)
    axes[0, 1].invert_yaxis()
    axes[0, 1].set_title("Top 10 Industries by Avg Influence Score", fontsize=13)

    # 3. 情感变化分布
    axes[1, 0].hist(impact_df["sentiment_change"].dropna(), bins=30, color="steelblue", edgecolor="white")
    axes[1, 0].axvline(0, color="red", linestyle="--", alpha=0.7)
    axes[1, 0].set_title("Sentiment Change Distribution (Event Window)", fontsize=13)
    axes[1, 0].set_xlabel("Sentiment Change")
    axes[1, 0].set_ylabel("Count")

    # 4. 事件类型间情感传染效应
    event_types = impact_df["event_type"].unique()
    contagion = pd.DataFrame(index=event_types, columns=event_types, dtype=float)
    for t1 in event_types:
        for t2 in event_types:
            t1_sent = impact_df[impact_df["event_type"] == t1]["sentiment_change"]
            t2_sent = impact_df[impact_df["event_type"] == t2]["sentiment_change"]
            if len(t1_sent) > 2 and len(t2_sent) > 2:
                contagion.loc[t1, t2] = t1_sent.corr(t2_sent)
            else:
                contagion.loc[t1, t2] = 0
    sns.heatmap(
        contagion.astype(float), cmap="RdBu_r", center=0,
        annot=True, fmt=".2f", ax=axes[1, 1], linewidths=0.5,
    )
    axes[1, 1].set_title("Sentiment Contagion Between Event Types", fontsize=13)

    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, "ch05_event_analysis.png"),
        dpi=FIGURE_DPI_HIGH, bbox_inches="tight",
    )
    plt.close()
    logger.info("  事件分析图已保存")


def generate_report(impact_df: pd.DataFrame) -> None:
    """生成事件分析报告."""
    logger.info("  生成报告...")

    type_counts = impact_df["event_type"].value_counts()
    top_events = impact_df.nlargest(10, "influence_score")

    lines = [
        "# Event-Driven Strategy Analysis Report\n",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        f"**Total High-Impact Events**: {len(impact_df)}\n",
        "",
        "## 1. Event Type Distribution\n",
        "",
        "| Event Type | Count | Percentage |",
        "|------------|-------|------------|",
    ]
    for etype, count in type_counts.items():
        pct = count / len(impact_df) * 100
        lines.append(f"| {etype} | {count} | {pct:.1f}% |")

    lines.extend([
        "",
        "## 2. Top 10 Most Influential Events\n",
        "",
        "| Rank | Date | Title | Type | Influence Score |",
        "|------|------|-------|------|----------------|",
    ])
    for rank, (_, row) in enumerate(top_events.iterrows(), 1):
        title = str(row["title"])[:60]
        date = row["date"].strftime("%Y-%m-%d") if hasattr(row["date"], "strftime") else str(row["date"])
        lines.append(f"| {rank} | {date} | {title} | {row['event_type']} | {row['influence_score']:.3f} |")

    lines.extend([
        "",
        "## 3. Sentiment Impact Analysis\n",
        "",
        f"- **Mean Sentiment Change**: {impact_df['sentiment_change'].mean():.4f}\n",
        f"- **Median Sentiment Change**: {impact_df['sentiment_change'].median():.4f}\n",
        f"- **Positive Impact Events**: {(impact_df['sentiment_change'] > 0).sum()} ({(impact_df['sentiment_change'] > 0).mean()*100:.1f}%)\n",
        f"- **Negative Impact Events**: {(impact_df['sentiment_change'] < 0).sum()} ({(impact_df['sentiment_change'] < 0).mean()*100:.1f}%)\n",
        "",
        "## 4. Key Findings\n",
        "",
        f"1. A total of **{len(impact_df)}** high-impact events were identified.\n",
        f"2. The most common event type is **{type_counts.index[0]}** ({type_counts.iloc[0]} events, {type_counts.iloc[0]/len(impact_df)*100:.1f}%).\n",
    ])

    # 最具影响力事件
    if len(top_events) > 0:
        top = top_events.iloc[0]
        lines.append(
            f"3. The most influential event was on {top['date'].strftime('%Y-%m-%d') if hasattr(top['date'], 'strftime') else top['date']}: "
            f'"{str(top["title"])[:80]}..." (score: {top["influence_score"]:.3f}).\n'
        )

    lines.extend([
        "",
        "## 5. Methodology\n",
        "",
        "- **Event Selection**: impact_tier=HIGH & relevance_score>=7",
        "- **Event Classification**: Rule-based (Policy / Earnings / Geopolitical / Industry / Other)",
        "- **Window Analysis**: ±7 days around event date",
        "- **Influence Score**: Weighted combination (relevance 30% + sentiment_change 30% + breadth 20% + sentiment_abs 20%)\n",
        "",
        "## 6. Output Files\n",
        "",
        "- `ch05_event_calendar.csv` - Event calendar sorted by date\n",
        "- `ch05_influence_score.csv` - Events ranked by influence score\n",
        "- `ch05_event_analysis.png` - 4-panel visualization\n",
    ])

    report_path = os.path.join(OUTPUT_DIR, "ch05_event_analysis_report.md")
    Path(report_path).write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"  报告已保存: {report_path}")


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    logger.info("=" * 60)
    logger.info("ch05 事件驱动策略分析 — 开始执行")
    logger.info("=" * 60)

    df = load_data()
    events = filter_high_impact_events(df)
    impact_df = compute_window_analysis(events, df)
    impact_df = compute_influence_score(impact_df)
    save_results(impact_df)
    plot_event_analysis(impact_df)
    generate_report(impact_df)

    logger.info("\n" + "=" * 60)
    logger.info(f"ch05 完成。产物: {OUTPUT_DIR}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
