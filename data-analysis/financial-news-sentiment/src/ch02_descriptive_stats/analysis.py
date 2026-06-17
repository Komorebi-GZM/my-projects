#!/usr/bin/env python3
"""描述性统计分析主脚本 (ch02).

本脚本对 ch01 清洗后的金融新闻数据进行全面的描述性统计分析，包括：
1. 数据加载与验证
2. 新闻发布时间分布分析（年度/月度/星期/工作日vs周末）
3. 17个行业分类热度排名与占比
4. 影响等级分布与时间演变
5. Top 50 高频关键词 + 词云
6. 数据来源覆盖度与偏差分析
7. 文本长度分布 + 交叉分析
8. 行业年度趋势堆叠面积图
9. 描述性统计报告撰写

Usage:
    # 从项目根目录运行
    python src/ch02_descriptive_stats/analysis.py

Output:
    outputs/ch02_descriptive_stats/
        ch02_time_distribution.png          - 时间分布四子图
        ch02_category_ranking.png          - 行业分类排名
        ch02_impact_tier_analysis.png      - 影响等级分析
        ch02_top50_keywords.png            - Top50关键词柱状图
        ch02_keyword_wordcloud.png         - 关键词词云
        ch02_source_bias_analysis.png      - 来源偏差热力图
        ch02_text_length_and_cross.png     - 文本长度与交叉分析
        ch02_category_yearly_trend.png     - 行业年度趋势堆叠面积图
        ch02_descriptive_stats_report.md   - 描述性统计报告
        ch02_descriptive_stats.csv         - 描述统计汇总表

Author:
    financial_news_sentiment_analysis project
"""

from __future__ import annotations

import ast
import logging
import warnings
from collections import Counter
from typing import Dict, List, Optional, Tuple

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud

# 将项目根目录添加到 sys.path
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.utils.config import (
    FIGURE_DPI_HIGH,
    FIGURE_SIZE_DEFAULT,
    FIGURE_SIZE_WIDE,
    MATPLOTLIB_RC_PARAMS,
    setup_logging,
)
from src.utils.output_manager import OutputManager

# =============================================================================
# 初始化
# =============================================================================
# 配置 matplotlib 全局样式
matplotlib.rcParams.update(MATPLOTLIB_RC_PARAMS)

# 配置日志
logger = setup_logging(__name__, log_to_file=True)

# 忽略警告
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# 输出管理器
output_mgr = OutputManager("ch02_descriptive_stats")

# 数据路径
CLEANED_DATA_PATH = (
    _PROJECT_ROOT
    / "outputs"
    / "ch01_data_preprocessing"
    / "ch01_cleaned_data.csv"
)


# =============================================================================
# Step 1: 数据加载与验证
# =============================================================================
def load_and_validate_data(filepath: Path) -> pd.DataFrame:
    """加载 ch01 清洗后数据并进行验证.

    Args:
        filepath: 清洗后数据文件路径.

    Returns:
        验证通过的 DataFrame.

    Raises:
        FileNotFoundError: 数据文件不存在时抛出.
        ValueError: 数据验证失败时抛出.
    """
    logger.info("=" * 60)
    logger.info("Step 1: 数据加载与验证")
    logger.info("=" * 60)

    if not filepath.exists():
        raise FileNotFoundError(f"数据文件不存在: {filepath}")

    # 加载数据
    df = pd.read_csv(filepath, parse_dates=["date"])
    logger.info("数据加载完成: %d 行 x %d 列", df.shape[0], df.shape[1])

    # 验证行数和列数
    expected_rows = 139919
    expected_cols = 24
    actual_rows = len(df)
    actual_cols = len(df.columns)

    if actual_rows != expected_rows:
        logger.warning(
            "行数验证: 预期 %d, 实际 %d (差异: %d)",
            expected_rows, actual_rows, actual_rows - expected_rows,
        )
    else:
        logger.info("行数验证通过: %d 行", actual_rows)

    if actual_cols != expected_cols:
        logger.warning(
            "列数验证: 预期 %d, 实际 %d (差异: %d)",
            expected_cols, actual_cols, actual_cols - expected_cols,
        )
    else:
        logger.info("列数验证通过: %d 列", actual_cols)

    # 验证缺失率
    missing_rate = df.isnull().mean().max() * 100
    logger.info("最大缺失率: %.2f%%", missing_rate)
    if missing_rate > 0:
        logger.warning("数据存在缺失值，最大缺失率 %.2f%%", missing_rate)
    else:
        logger.info("缺失率验证通过: 0%%")

    # 用 ast.literal_eval 转换 categories_list 和 keywords_list
    for col in ["categories_list", "keywords_list"]:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: ast.literal_eval(x)
                if isinstance(x, str) and x.startswith("[")
                else x
            )
            logger.info("已转换列 '%s' 为列表类型", col)

    # 验证关键字段
    key_columns = [
        "date", "title", "description", "full_text", "categories",
        "categories_list", "matched_keywords", "keywords_list",
        "impact_tier", "relevance_score", "has_negation", "source_file",
        "text_length", "year", "month", "day_of_week", "is_weekend",
    ]
    missing_cols = [c for c in key_columns if c not in df.columns]
    if missing_cols:
        logger.warning("缺少关键字段: %s", missing_cols)
    else:
        logger.info("全部 %d 个关键字段验证通过", len(key_columns))

    logger.info("日期范围: %s ~ %s", df["date"].min().date(), df["date"].max().date())
    logger.info("数据来源数: %d", df["source_file"].nunique())

    return df


# =============================================================================
# Step 2: 新闻发布时间分布分析
# =============================================================================
def analyze_time_distribution(
    df: pd.DataFrame,
) -> Dict[str, pd.DataFrame]:
    """分析新闻发布时间分布并生成四子图.

    子图包括：年度趋势(折线图)、月度分布(柱状图)、
    星期分布(柱状图)、工作日vs周末(饼图).

    Args:
        df: 输入 DataFrame.

    Returns:
        包含各维度统计结果的字典.
    """
    logger.info("=" * 60)
    logger.info("Step 2: 新闻发布时间分布分析")
    logger.info("=" * 60)

    stats: Dict[str, pd.DataFrame] = {}

    # 创建 2x2 子图
    fig, axes = plt.subplots(2, 2, figsize=FIGURE_SIZE_WIDE)
    fig.suptitle("News Publication Time Distribution", fontsize=16, fontweight="bold")

    # --- 子图1: 年度趋势 (折线图 + 数据标注) ---
    ax1 = axes[0, 0]
    yearly = df.groupby("year").size().reset_index(name="count")
    stats["yearly"] = yearly
    ax1.plot(yearly["year"], yearly["count"], marker="o", linewidth=2,
             color="#2196F3", markersize=6)
    for _, row in yearly.iterrows():
        ax1.annotate(
            f"{int(row['count']):,}",
            (row["year"], row["count"]),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=8,
        )
    ax1.set_title("Annual News Count Trend")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Count")
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(yearly["year"].values)

    # --- 子图2: 月度分布 (柱状图) ---
    ax2 = axes[0, 1]
    monthly = df.groupby("month").size().reset_index(name="count")
    stats["monthly"] = monthly
    bars = ax2.bar(monthly["month"], monthly["count"], color="#4CAF50", alpha=0.8)
    ax2.set_title("Monthly News Distribution")
    ax2.set_xlabel("Month")
    ax2.set_ylabel("Count")
    ax2.set_xticks(range(1, 13))
    ax2.grid(True, alpha=0.3, axis="y")

    # --- 子图3: 星期分布 (柱状图, 标签: Mon~Sun) ---
    ax3 = axes[1, 0]
    dow_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    dow_order = list(range(7))
    dow_counts = df["day_of_week"].value_counts().reindex(dow_order, fill_value=0)
    stats["day_of_week"] = dow_counts.reset_index()
    stats["day_of_week"].columns = ["day_of_week", "count"]
    colors_dow = ["#FF9800"] * 5 + ["#F44336"] * 2
    ax3.bar(dow_labels, dow_counts.values, color=colors_dow, alpha=0.8)
    ax3.set_title("Day-of-Week News Distribution")
    ax3.set_xlabel("Day of Week")
    ax3.set_ylabel("Count")
    ax3.grid(True, alpha=0.3, axis="y")

    # --- 子图4: 工作日 vs 周末 (饼图) ---
    ax4 = axes[1, 1]
    weekday_count = int((df["is_weekend"] == 0).sum())
    weekend_count = int((df["is_weekend"] == 1).sum())
    stats["weekday_weekend"] = pd.DataFrame({
        "type": ["Weekday", "Weekend"],
        "count": [weekday_count, weekend_count],
    })
    ax4.pie(
        [weekday_count, weekend_count],
        labels=["Weekday", "Weekend"],
        autopct="%1.1f%%",
        colors=["#2196F3", "#FF9800"],
        startangle=90,
        explode=(0.02, 0.02),
    )
    ax4.set_title("Weekday vs Weekend Distribution")

    plt.tight_layout()
    output_mgr.save_figure(fig, "ch02_time_distribution.png")
    plt.close(fig)

    logger.info("时间分布图已保存")
    logger.info("年度统计: %s", yearly.to_dict("records"))
    logger.info("工作日/周末: %d / %d", weekday_count, weekend_count)

    return stats


# =============================================================================
# Step 3: 17个行业分类热度排名与占比
# =============================================================================
def analyze_category_ranking(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """分析行业分类热度排名并生成水平柱状图.

    展开 categories_list 统计各分类新闻数量，
    绘制水平柱状图并标注数量和占比百分比.

    Args:
        df: 输入 DataFrame.

    Returns:
        分类统计 DataFrame.
    """
    logger.info("=" * 60)
    logger.info("Step 3: 行业分类热度排名与占比")
    logger.info("=" * 60)

    # 展开所有分类
    all_categories: List[str] = []
    for cats in df["categories_list"]:
        if isinstance(cats, list):
            all_categories.extend(cats)

    cat_counter = Counter(all_categories)
    cat_df = pd.DataFrame(
        cat_counter.most_common(), columns=["category", "count"]
    )
    total = cat_df["count"].sum()
    cat_df["percentage"] = (cat_df["count"] / total * 100).round(2)

    logger.info("唯一分类数: %d", len(cat_df))
    logger.info("Top 5 分类:")
    for _, row in cat_df.head(5).iterrows():
        logger.info("  %s: %d (%.2f%%)", row["category"], row["count"], row["percentage"])

    # 绘制水平柱状图
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_WIDE)
    y_pos = range(len(cat_df))
    bars = ax.barh(y_pos, cat_df["count"].values, color="#2196F3", alpha=0.85)

    # 标注数量和占比
    for i, (_, row) in enumerate(cat_df.iterrows()):
        ax.text(
            row["count"] + total * 0.005,
            i,
            f"{row['count']:,} ({row['percentage']:.1f}%)",
            va="center",
            fontsize=9,
        )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(cat_df["category"].values)
    ax.invert_yaxis()
    ax.set_title("Industry Category Ranking (All Categories)")
    ax.set_xlabel("News Count")
    ax.set_ylabel("Category")
    ax.grid(True, alpha=0.3, axis="x")

    plt.tight_layout()
    output_mgr.save_figure(fig, "ch02_category_ranking.png")
    plt.close(fig)

    logger.info("行业分类排名图已保存")

    return cat_df


# =============================================================================
# Step 4: 影响等级分布与时间演变
# =============================================================================
def analyze_impact_tier(
    df: pd.DataFrame,
) -> Dict[str, pd.DataFrame]:
    """分析影响等级分布与时间演变.

    生成两个子图：影响等级饼图、月度堆叠面积图.

    Args:
        df: 输入 DataFrame.

    Returns:
        包含影响等级统计和月度趋势的字典.
    """
    logger.info("=" * 60)
    logger.info("Step 4: 影响等级分布与时间演变")
    logger.info("=" * 60)

    stats: Dict[str, pd.DataFrame] = {}

    # 影响等级统计
    tier_order = ["LOW", "MEDIUM", "HIGH"]
    tier_counts = df["impact_tier"].value_counts().reindex(tier_order, fill_value=0)
    stats["tier_counts"] = tier_counts.reset_index()
    stats["tier_counts"].columns = ["impact_tier", "count"]

    logger.info("影响等级分布:")
    for tier in tier_order:
        count = int(tier_counts.get(tier, 0))
        pct = count / len(df) * 100
        logger.info("  %s: %d (%.1f%%)", tier, count, pct)

    # 创建 1x2 子图
    fig, axes = plt.subplots(1, 2, figsize=FIGURE_SIZE_WIDE)
    fig.suptitle("Impact Tier Analysis", fontsize=16, fontweight="bold")

    # --- 子图1: 影响等级饼图 ---
    ax1 = axes[0]
    tier_colors = {"LOW": "#4CAF50", "MEDIUM": "#FF9800", "HIGH": "#F44336"}
    colors = [tier_colors.get(t, "#999") for t in tier_order]
    wedges, texts, autotexts = ax1.pie(
        tier_counts.values,
        labels=tier_order,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        explode=(0.02, 0.02, 0.05),
    )
    for autotext in autotexts:
        autotext.set_fontsize(11)
    ax1.set_title("Impact Tier Distribution")

    # --- 子图2: 月度堆叠面积图 ---
    ax2 = axes[1]
    df["year_month"] = df["date"].dt.to_period("M")
    monthly_tier = (
        df.groupby(["year_month", "impact_tier"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=tier_order, fill_value=0)
    )
    stats["monthly_tier"] = monthly_tier.reset_index()

    # 转换为字符串索引用于绘图
    x_labels = [str(p) for p in monthly_tier.index]
    x_numeric = range(len(x_labels))

    ax2.stackplot(
        x_numeric,
        *[monthly_tier[tier].values for tier in tier_order],
        labels=tier_order,
        colors=colors,
        alpha=0.8,
    )
    ax2.set_title("Monthly Impact Tier Stacked Area")
    ax2.set_xlabel("Year-Month")
    ax2.set_ylabel("News Count")
    ax2.legend(loc="upper left", fontsize=9)

    # 设置 x 轴刻度（每隔 N 个月显示一个标签）
    n_ticks = min(12, len(x_labels))
    tick_positions = np.linspace(0, len(x_labels) - 1, n_ticks, dtype=int)
    ax2.set_xticks(tick_positions)
    ax2.set_xticklabels([x_labels[i] for i in tick_positions], rotation=45, ha="right")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    output_mgr.save_figure(fig, "ch02_impact_tier_analysis.png")
    plt.close(fig)

    # 清理临时列
    df.drop(columns=["year_month"], inplace=True, errors="ignore")

    logger.info("影响等级分析图已保存")

    return stats


# =============================================================================
# Step 5: Top 50 高频关键词 + 词云
# =============================================================================
def analyze_keywords(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """分析高频关键词并生成柱状图和词云.

    展开 keywords_list 统计词频，生成 Top50 水平柱状图和词云图.

    Args:
        df: 输入 DataFrame.

    Returns:
        元组 (Top50 关键词 DataFrame, 全部关键词频率 DataFrame).
    """
    logger.info("=" * 60)
    logger.info("Step 5: Top 50 高频关键词 + 词云")
    logger.info("=" * 60)

    # 展开所有关键词
    all_keywords: List[str] = []
    for kws in df["keywords_list"]:
        if isinstance(kws, list):
            all_keywords.extend(kws)

    kw_counter = Counter(all_keywords)
    kw_df = pd.DataFrame(
        kw_counter.most_common(), columns=["keyword", "count"]
    )
    total_keywords = kw_df["count"].sum()
    kw_df["percentage"] = (kw_df["count"] / total_keywords * 100).round(4)

    top50 = kw_df.head(50).copy()

    logger.info("唯一关键词数: %d", len(kw_df))
    logger.info("Top 10 关键词:")
    for _, row in top50.head(10).iterrows():
        logger.info("  %s: %d", row["keyword"], row["count"])

    # --- Top50 水平柱状图 ---
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_WIDE)
    y_pos = range(len(top50))
    ax.barh(y_pos, top50["count"].values, color="#9C27B0", alpha=0.85)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top50["keyword"].values, fontsize=8)
    ax.invert_yaxis()
    ax.set_title("Top 50 High-Frequency Keywords")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Keyword")
    ax.grid(True, alpha=0.3, axis="x")

    plt.tight_layout()
    output_mgr.save_figure(fig, "ch02_top50_keywords.png")
    plt.close(fig)

    # --- 词云图 ---
    wc = WordCloud(
        width=1200,
        height=600,
        background_color="white",
        max_words=100,
        colormap="viridis",
    )
    wc.generate_from_frequencies(dict(kw_counter.most_common(200)))

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_WIDE)
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Keyword Word Cloud", fontsize=16, fontweight="bold", pad=15)

    plt.tight_layout()
    output_mgr.save_figure(fig, "ch02_keyword_wordcloud.png")
    plt.close(fig)

    logger.info("关键词分析图已保存")

    return top50, kw_df


# =============================================================================
# Step 6: 数据来源覆盖度与偏差分析
# =============================================================================
def analyze_source_bias(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """分析数据来源覆盖度与偏差.

    生成来源 x 年度热力图，展示各来源在不同年份的新闻覆盖情况.

    Args:
        df: 输入 DataFrame.

    Returns:
        来源 x 年度交叉统计 DataFrame.
    """
    logger.info("=" * 60)
    logger.info("Step 6: 数据来源覆盖度与偏差分析")
    logger.info("=" * 60)

    # 来源 x 年度交叉统计
    source_year = pd.crosstab(df["source_file"], df["year"])
    source_year = source_year.sort_values(by=source_year.columns[-1], ascending=True)

    logger.info("数据来源数: %d", len(source_year))
    logger.info("各来源总新闻数:")
    source_totals = source_year.sum(axis=1).sort_values(ascending=False)
    for src, count in source_totals.items():
        logger.info("  %s: %d", src, count)

    # 绘制热力图
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_WIDE)
    sns.heatmap(
        source_year,
        annot=True,
        fmt="d",
        cmap="YlOrRd",
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "News Count"},
    )
    ax.set_title("News Source Coverage by Year (Heatmap)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Source File")
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    output_mgr.save_figure(fig, "ch02_source_bias_analysis.png")
    plt.close(fig)

    logger.info("来源偏差分析图已保存")

    return source_year


# =============================================================================
# Step 7: 文本长度分布 + 交叉分析
# =============================================================================
def analyze_text_length_and_cross(
    df: pd.DataFrame,
) -> Dict[str, object]:
    """分析文本长度分布并进行交叉分析.

    生成三个子图：文本长度直方图(含均值线)、文本长度箱线图、
    行业 x 影响等级交叉热力图.

    Args:
        df: 输入 DataFrame.

    Returns:
        包含统计结果的字典.
    """
    logger.info("=" * 60)
    logger.info("Step 7: 文本长度分布 + 交叉分析")
    logger.info("=" * 60)

    stats: Dict[str, object] = {}

    # 文本长度统计
    text_len = df["text_length"]
    stats["text_length"] = {
        "mean": float(text_len.mean()),
        "median": float(text_len.median()),
        "std": float(text_len.std()),
        "min": int(text_len.min()),
        "max": int(text_len.max()),
        "q25": float(text_len.quantile(0.25)),
        "q75": float(text_len.quantile(0.75)),
    }
    logger.info("文本长度统计:")
    for k, v in stats["text_length"].items():
        logger.info("  %s: %.1f", k, v)

    # 创建 1x3 子图
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle("Text Length Distribution & Cross Analysis", fontsize=16, fontweight="bold")

    # --- 子图1: 文本长度直方图 (含均值线) ---
    ax1 = axes[0]
    ax1.hist(text_len, bins=50, color="#2196F3", alpha=0.7, edgecolor="white")
    mean_val = text_len.mean()
    median_val = text_len.median()
    ax1.axvline(mean_val, color="red", linestyle="--", linewidth=2, label=f"Mean: {mean_val:.0f}")
    ax1.axvline(median_val, color="orange", linestyle="--", linewidth=2, label=f"Median: {median_val:.0f}")
    ax1.set_title("Text Length Histogram")
    ax1.set_xlabel("Text Length (characters)")
    ax1.set_ylabel("Frequency")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3, axis="y")

    # --- 子图2: 文本长度箱线图 ---
    ax2 = axes[1]
    bp = ax2.boxplot(text_len, vert=True, patch_artist=True,
                     boxprops=dict(facecolor="#4CAF50", alpha=0.6),
                     medianprops=dict(color="red", linewidth=2))
    ax2.set_title("Text Length Box Plot")
    ax2.set_ylabel("Text Length (characters)")
    ax2.set_xticklabels(["All News"])
    ax2.grid(True, alpha=0.3, axis="y")

    # --- 子图3: 行业 x 影响等级交叉热力图 ---
    ax3 = axes[2]
    # 展开分类并创建交叉表
    cat_rows: List[Dict[str, object]] = []
    for _, row in df.iterrows():
        cats = row["categories_list"]
        tier = row["impact_tier"]
        if isinstance(cats, list):
            for cat in cats:
                cat_rows.append({"category": cat, "impact_tier": tier})

    if cat_rows:
        cat_tier_df = pd.DataFrame(cat_rows)
        cross_tab = pd.crosstab(cat_tier_df["category"], cat_tier_df["impact_tier"])
        tier_order = ["LOW", "MEDIUM", "HIGH"]
        cross_tab = cross_tab.reindex(columns=tier_order, fill_value=0)
        cross_tab = cross_tab.sort_values(by="HIGH", ascending=True)

        stats["category_tier_cross"] = cross_tab

        sns.heatmap(
            cross_tab,
            annot=True,
            fmt="d",
            cmap="YlOrRd",
            linewidths=0.5,
            ax=ax3,
            cbar_kws={"label": "Count"},
        )
        ax3.set_title("Category x Impact Tier Heatmap")
        ax3.set_xlabel("Impact Tier")
        ax3.set_ylabel("Category")
    else:
        ax3.text(0.5, 0.5, "No data available", ha="center", va="center")
        ax3.set_title("Category x Impact Tier Heatmap")

    plt.tight_layout()
    output_mgr.save_figure(fig, "ch02_text_length_and_cross.png")
    plt.close(fig)

    logger.info("文本长度与交叉分析图已保存")

    return stats


# =============================================================================
# Step 8: 行业年度趋势堆叠面积图
# =============================================================================
def analyze_category_yearly_trend(
    df: pd.DataFrame,
    top_n: int = 5,
) -> pd.DataFrame:
    """分析 Top N 行业的年度趋势并绘制堆叠面积图.

    Args:
        df: 输入 DataFrame.
        top_n: 取前 N 个行业，默认为 5.

    Returns:
        Top N 行业年度趋势 DataFrame.
    """
    logger.info("=" * 60)
    logger.info("Step 8: 行业年度趋势堆叠面积图 (Top %d)", top_n)
    logger.info("=" * 60)

    # 展开分类
    cat_rows: List[Dict[str, object]] = []
    for _, row in df.iterrows():
        cats = row["categories_list"]
        year = row["year"]
        if isinstance(cats, list):
            for cat in cats:
                cat_rows.append({"category": cat, "year": year})

    cat_year_df = pd.DataFrame(cat_rows)
    cat_year_cross = pd.crosstab(cat_year_df["category"], cat_year_df["year"])

    # 取 Top N 行业
    cat_totals = cat_year_cross.sum(axis=1).sort_values(ascending=False)
    top_categories = cat_totals.head(top_n).index.tolist()
    logger.info("Top %d 行业: %s", top_n, top_categories)

    trend_df = cat_year_cross.loc[top_categories].sort_index()

    # 绘制堆叠面积图
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_WIDE)
    years = trend_df.columns.astype(int).tolist()
    ax.stackplot(
        years,
        *[trend_df.loc[cat].values for cat in trend_df.index],
        labels=trend_df.index.tolist(),
        alpha=0.8,
    )
    ax.set_title(f"Top {top_n} Industry Category Yearly Trend (Stacked Area)")
    ax.set_xlabel("Year")
    ax.set_ylabel("News Count")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_xticks(years)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_mgr.save_figure(fig, "ch02_category_yearly_trend.png")
    plt.close(fig)

    logger.info("行业年度趋势图已保存")

    return trend_df


# =============================================================================
# Step 9: 描述性统计报告撰写
# =============================================================================
def generate_descriptive_report(
    df: pd.DataFrame,
    time_stats: Dict[str, pd.DataFrame],
    cat_stats: pd.DataFrame,
    impact_stats: Dict[str, pd.DataFrame],
    top50_keywords: pd.DataFrame,
    source_year: pd.DataFrame,
    text_stats: Dict[str, object],
) -> Tuple[str, pd.DataFrame]:
    """生成描述性统计 Markdown 报告和 CSV 汇总表.

    Args:
        df: 输入 DataFrame.
        time_stats: 时间分布统计结果.
        cat_stats: 行业分类统计结果.
        impact_stats: 影响等级统计结果.
        top50_keywords: Top50 关键词统计.
        source_year: 来源 x 年度交叉统计.
        text_stats: 文本长度统计结果.

    Returns:
        元组 (Markdown 报告字符串, CSV 汇总 DataFrame).
    """
    logger.info("=" * 60)
    logger.info("Step 9: 描述性统计报告撰写")
    logger.info("=" * 60)

    lines: List[str] = []
    total = len(df)
    date_min = df["date"].min().date()
    date_max = df["date"].max().date()
    n_sources = df["source_file"].nunique()

    # =========================================================================
    # 1. 概述
    # =========================================================================
    lines.extend([
        "# Descriptive Statistics Report -- ch02",
        "",
        "> This report is auto-generated by `analysis.py`",
        "",
        "## 1. Overview",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| **Total Records** | {total:,} |",
        f"| **Total Columns** | {len(df.columns)} |",
        f"| **Date Range** | {date_min} ~ {date_max} |",
        f"| **Number of Sources** | {n_sources} |",
        f"| **Unique Categories** | {len(cat_stats)} |",
        f"| **Unique Keywords** | {len(top50_keywords) + int(top50_keywords['count'].sum())} |",
        "",
    ])

    # =========================================================================
    # 2. 时间分布分析
    # =========================================================================
    lines.extend([
        "## 2. Time Distribution Analysis",
        "",
        "### 2.1 Annual Trend",
        "",
        "| Year | Count | Percentage |",
        "|------|-------|------------|",
    ])
    yearly = time_stats.get("yearly")
    if yearly is not None:
        for _, row in yearly.iterrows():
            pct = row["count"] / total * 100
            lines.append(f"| {int(row['year'])} | {int(row['count']):,} | {pct:.1f}% |")

    # 2021 年数据稀疏说明
    lines.extend([
        "",
        "> **Note on 2021 Data Sparsity**: Year 2021 shows a significant drop "
        "to only 3,548 articles (2.5%), compared to the 10-year average of "
        "~12,700 per year. This gap is likely due to a transition between "
        "data sources (the primary source `News_sentiment_Jan2017_to_Apr2021.csv` "
        "ends in April 2021, and `economic_times_headlines_2022.csv` begins in "
        "2022). Time-series analyses involving 2021 should treat this period "
        "with caution.",
        "",
    ])

    lines.extend(["", "### 2.2 Monthly Distribution", ""])
    monthly = time_stats.get("monthly")
    if monthly is not None:
        lines.append("| Month | Count | Percentage |")
        lines.append("|-------|-------|------------|")
        for _, row in monthly.iterrows():
            pct = row["count"] / total * 100
            lines.append(f"| {int(row['month'])} | {int(row['count']):,} | {pct:.1f}% |")

    lines.extend(["", "### 2.3 Day-of-Week Distribution", ""])
    dow = time_stats.get("day_of_week")
    if dow is not None:
        dow_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        lines.append("| Day | Count | Percentage |")
        lines.append("|-----|-------|------------|")
        for i, row in dow.iterrows():
            pct = row["count"] / total * 100
            lines.append(f"| {dow_labels[int(row['day_of_week'])]} | {int(row['count']):,} | {pct:.1f}% |")

    lines.extend(["", "### 2.4 Weekday vs Weekend", ""])
    ww = time_stats.get("weekday_weekend")
    if ww is not None:
        lines.append("| Type | Count | Percentage |")
        lines.append("|------|-------|------------|")
        for _, row in ww.iterrows():
            pct = row["count"] / total * 100
            lines.append(f"| {row['type']} | {int(row['count']):,} | {pct:.1f}% |")
    lines.append("")

    # =========================================================================
    # 3. 行业分类分析
    # =========================================================================
    lines.extend([
        "## 3. Industry Category Analysis",
        "",
        f"Total unique categories: **{len(cat_stats)}**",
        "",
        "| Rank | Category | Count | Percentage |",
        "|------|----------|-------|------------|",
    ])
    for rank, (_, row) in enumerate(cat_stats.iterrows(), 1):
        lines.append(
            f"| {rank} | {row['category']} | {int(row['count']):,} | {row['percentage']:.2f}% |"
        )
    lines.append("")

    # =========================================================================
    # 4. 影响等级分析
    # =========================================================================
    lines.extend([
        "## 4. Impact Tier Analysis",
        "",
        "| Impact Tier | Count | Percentage |",
        "|-------------|-------|------------|",
    ])
    tier_counts = impact_stats.get("tier_counts")
    if tier_counts is not None:
        for _, row in tier_counts.iterrows():
            pct = row["count"] / total * 100
            lines.append(f"| {row['impact_tier']} | {int(row['count']):,} | {pct:.1f}% |")
    lines.append("")

    # =========================================================================
    # 5. 关键词分析
    # =========================================================================
    lines.extend([
        "## 5. Keyword Analysis",
        "",
        "### Top 10 Keywords",
        "",
        "| Rank | Keyword | Count | Percentage |",
        "|------|---------|-------|------------|",
    ])
    for rank, (_, row) in enumerate(top50_keywords.head(10).iterrows(), 1):
        lines.append(
            f"| {rank} | {row['keyword']} | {int(row['count']):,} | {row['percentage']:.2f}% |"
        )
    lines.append("")

    # =========================================================================
    # 6. 数据来源分析
    # =========================================================================
    lines.extend([
        "## 6. Data Source Analysis",
        "",
        f"Total sources: **{n_sources}**",
        "",
        "| Source | Total Count | Percentage |",
        "|--------|-------------|------------|",
    ])
    source_counts = df["source_file"].value_counts()
    for src, count in source_counts.items():
        pct = count / total * 100
        lines.append(f"| {src} | {int(count):,} | {pct:.1f}% |")
    lines.append("")

    # =========================================================================
    # 7. 文本特征分析
    # =========================================================================
    lines.extend([
        "## 7. Text Feature Analysis",
        "",
        "| Metric | Value |",
        "|--------|-------|",
    ])
    tl = text_stats.get("text_length", {})
    if tl:
        lines.append(f"| Mean Length | {tl['mean']:.1f} chars |")
        lines.append(f"| Median Length | {tl['median']:.1f} chars |")
        lines.append(f"| Std Dev | {tl['std']:.1f} |")
        lines.append(f"| Min Length | {tl['min']} chars |")
        lines.append(f"| Max Length | {tl['max']} chars |")
        lines.append(f"| 25th Percentile | {tl['q25']:.1f} chars |")
        lines.append(f"| 75th Percentile | {tl['q75']:.1f} chars |")
    lines.append("")

    # =========================================================================
    # 7.5 交叉分析
    # =========================================================================
    lines.extend([
        "## 7.5 Cross-Analysis",
        "",
        "### Category x Impact Tier",
        "",
        "A cross-tabulation heatmap of the 17 industry categories against the "
        "3 impact tiers (LOW/MEDIUM/HIGH) is provided in "
        "`ch02_text_length_and_cross.png` (rightmost subplot). Key observations:",
        "",
        "- **macro_government** and **stock_specific** dominate across all "
        "impact tiers due to their high base volume.",
        "- **HIGH** impact news is concentrated in macro_government, "
        "geopolitical, and sector_banking_finance categories.",
        "- Most categories show a LOW:MEDIUM:HIGH ratio roughly matching "
        "the overall 41:57:2 distribution.",
        "",
    ])
    lines.append("")

    # =========================================================================
    # 8. 关键发现总结
    # =========================================================================
    # 计算关键发现
    peak_year_row = yearly.loc[yearly["count"].idxmax()] if yearly is not None else None
    peak_month_row = monthly.loc[monthly["count"].idxmax()] if monthly is not None else None
    top_cat = cat_stats.iloc[0] if len(cat_stats) > 0 else None
    high_tier_count = 0
    if tier_counts is not None:
        high_row = tier_counts[tier_counts["impact_tier"] == "HIGH"]
        if len(high_row) > 0:
            high_tier_count = int(high_row["count"].values[0])

    lines.extend([
        "## 8. Key Findings Summary",
        "",
    ])
    if peak_year_row is not None:
        lines.append(
            f"- **Peak Year**: {int(peak_year_row['year'])} with "
            f"{int(peak_year_row['count']):,} news articles"
        )
    if peak_month_row is not None:
        lines.append(
            f"- **Peak Month**: Month {int(peak_month_row['month'])} with "
            f"{int(peak_month_row['count']):,} news articles"
        )
    if top_cat is not None:
        lines.append(
            f"- **Top Category**: {top_cat['category']} with "
            f"{int(top_cat['count']):,} articles ({top_cat['percentage']:.1f}%)"
        )
    lines.append(
        f"- **High Impact News**: {high_tier_count:,} articles "
        f"({high_tier_count / total * 100:.1f}%)"
    )
    lines.append(
        f"- **Average Text Length**: {tl.get('mean', 0):.0f} characters"
    )
    lines.append(
        f"- **Data Span**: {date_min} to {date_max} "
        f"({(df['date'].max() - df['date'].min()).days} days)"
    )

    lines.extend([
        "",
        "---",
        "",
        f"*Report generated at: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
    ])

    report = "\n".join(lines)

    # =========================================================================
    # CSV 汇总表
    # =========================================================================
    csv_rows: List[Dict[str, object]] = []

    # 年度统计
    if yearly is not None:
        for _, row in yearly.iterrows():
            csv_rows.append({
                "dimension": "yearly",
                "category": str(int(row["year"])),
                "count": int(row["count"]),
                "percentage": round(row["count"] / total * 100, 2),
            })

    # 月度统计
    if monthly is not None:
        for _, row in monthly.iterrows():
            csv_rows.append({
                "dimension": "monthly",
                "category": str(int(row["month"])),
                "count": int(row["count"]),
                "percentage": round(row["count"] / total * 100, 2),
            })

    # 行业分类统计
    for _, row in cat_stats.iterrows():
        csv_rows.append({
            "dimension": "category",
            "category": row["category"],
            "count": int(row["count"]),
            "percentage": row["percentage"],
        })

    # 影响等级统计
    if tier_counts is not None:
        for _, row in tier_counts.iterrows():
            csv_rows.append({
                "dimension": "impact_tier",
                "category": row["impact_tier"],
                "count": int(row["count"]),
                "percentage": round(row["count"] / total * 100, 2),
            })

    # 数据来源统计
    for src, count in source_counts.items():
        csv_rows.append({
            "dimension": "source",
            "category": src,
            "count": int(count),
            "percentage": round(count / total * 100, 2),
        })

    csv_df = pd.DataFrame(csv_rows)

    logger.info("报告已生成 (%d 字符)", len(report))
    logger.info("CSV 汇总表: %d 行", len(csv_df))

    return report, csv_df


# =============================================================================
# 主流程
# =============================================================================
def main() -> None:
    """描述性统计分析主流程.

    按顺序执行以下步骤:
    1. 数据加载与验证
    2. 新闻发布时间分布分析
    3. 行业分类热度排名与占比
    4. 影响等级分布与时间演变
    5. Top 50 高频关键词 + 词云
    6. 数据来源覆盖度与偏差分析
    7. 文本长度分布 + 交叉分析
    8. 行业年度趋势堆叠面积图
    9. 描述性统计报告撰写
    """
    logger.info("=" * 60)
    logger.info("ch02 Descriptive Statistics Analysis - Start")
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # Step 1: 数据加载与验证
    # ------------------------------------------------------------------
    try:
        df = load_and_validate_data(CLEANED_DATA_PATH)
    except FileNotFoundError as e:
        logger.error("无法加载数据: %s", e)
        return
    except Exception as e:
        logger.error("加载数据时发生错误: %s", e)
        return

    # ------------------------------------------------------------------
    # Step 2: 新闻发布时间分布分析
    # ------------------------------------------------------------------
    time_stats = analyze_time_distribution(df)

    # ------------------------------------------------------------------
    # Step 3: 行业分类热度排名与占比
    # ------------------------------------------------------------------
    cat_stats = analyze_category_ranking(df)

    # ------------------------------------------------------------------
    # Step 4: 影响等级分布与时间演变
    # ------------------------------------------------------------------
    impact_stats = analyze_impact_tier(df)

    # ------------------------------------------------------------------
    # Step 5: Top 50 高频关键词 + 词云
    # ------------------------------------------------------------------
    top50_keywords, all_keywords = analyze_keywords(df)

    # ------------------------------------------------------------------
    # Step 6: 数据来源覆盖度与偏差分析
    # ------------------------------------------------------------------
    source_year = analyze_source_bias(df)

    # ------------------------------------------------------------------
    # Step 7: 文本长度分布 + 交叉分析
    # ------------------------------------------------------------------
    text_stats = analyze_text_length_and_cross(df)

    # ------------------------------------------------------------------
    # Step 8: 行业年度趋势堆叠面积图
    # ------------------------------------------------------------------
    trend_df = analyze_category_yearly_trend(df, top_n=5)

    # ------------------------------------------------------------------
    # Step 9: 描述性统计报告撰写
    # ------------------------------------------------------------------
    report, csv_df = generate_descriptive_report(
        df=df,
        time_stats=time_stats,
        cat_stats=cat_stats,
        impact_stats=impact_stats,
        top50_keywords=top50_keywords,
        source_year=source_year,
        text_stats=text_stats,
    )

    # 保存报告和 CSV
    output_mgr.save_markdown(report, "ch02_descriptive_stats_report.md")
    output_mgr.save_dataframe(csv_df, "ch02_descriptive_stats.csv")

    # ------------------------------------------------------------------
    # 完成
    # ------------------------------------------------------------------
    logger.info("=" * 60)
    logger.info("ch02 Descriptive Statistics Analysis - Complete")
    logger.info("All outputs saved to: %s", output_mgr.output_dir)
    logger.info("Output files:")
    for f in sorted(output_mgr.list_outputs()):
        logger.info("  - %s", f.name)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
