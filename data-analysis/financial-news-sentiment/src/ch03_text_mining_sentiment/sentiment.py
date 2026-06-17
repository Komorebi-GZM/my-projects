"""Prompt-03: 文本挖掘与情感分析.

本章节包含两大核心模块：
  - 模块一：情感分析 — 基于 FinBERT 对全量新闻进行情感判别
  - 模块二：主题建模 — BERTopic 主选 + LDA 对比

覆盖步骤:
  - Step 1: FinBERT 模型加载与环境配置
  - Step 2: 全量新闻情感标签生成
  - Step 3: 情感分布统计 + 行业交叉分析
  - Step 4: 情感时序演变 + 事件窗口分析
  - Step 5: 文本预处理 + BERTopic 主题建模
  - Step 6: LDA 对比 + 主题时序分析 + 报告

产物输出到: outputs/ch03_text_mining_sentiment/
"""

from __future__ import annotations

import logging
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 路径设置（确保能导入 utils）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)

import matplotlib
matplotlib.use("Agg")  # 非交互式后端
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm

# 导入项目工具
from utils.config import (
    FIGURE_DPI,
    FIGURE_DPI_HIGH,
    MATPLOTLIB_RC_PARAMS,
    get_chapter_output_dir,
    setup_logging,
)

# 应用 matplotlib 全局配置
plt.rcParams.update(MATPLOTLIB_RC_PARAMS)

# 日志配置
logger = setup_logging("ch03_sentiment", log_to_file=True)

# 输出目录
OUTPUT_DIR = get_chapter_output_dir("ch03_text_mining_sentiment")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 输入数据路径
INPUT_DATA_PATH = os.path.join(
    PROJECT_ROOT, "outputs", "ch01_data_preprocessing", "ch01_cleaned_data.csv"
)

# 采样比例（CPU 环境下可降低以加速执行，1.0 = 全量）
SAMPLE_FRACTION: float = float(os.environ.get("CH03_SAMPLE_FRACTION", "1.0"))

# 抑制警告
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


# =============================================================================
# Step 1: FinBERT 模型加载与环境配置
# =============================================================================

def load_finbert_pipeline() -> Tuple[object, int, int]:
    """检测 GPU 可用性并加载 FinBERT 情感分析 pipeline.

    Returns:
        Tuple of (sentiment_pipeline, device, batch_size).
    """
    import torch
    from transformers import pipeline

    # 设置 HuggingFace 镜像（解决网络连接问题）
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

    device = 0 if torch.cuda.is_available() else -1
    batch_size = 32 if device == 0 else 8
    device_name = "GPU" if device == 0 else "CPU"

    logger.info(f"使用设备: {device_name}, batch_size={batch_size}")

    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="ProsusAI/finbert",
        device=device,
        truncation=True,
        max_length=512,
    )
    logger.info("FinBERT 模型加载完成")
    return sentiment_pipeline, device, batch_size


# =============================================================================
# Step 2: 全量新闻情感标签生成
# =============================================================================

def generate_sentiment_labels(
    df: pd.DataFrame,
    sentiment_pipeline: object,
    batch_size: int,
) -> pd.DataFrame:
    """对全量新闻 full_text 进行 FinBERT 情感推理.

    Args:
        df: 包含 full_text 列的 DataFrame.
        sentiment_pipeline: HuggingFace transformers pipeline.
        batch_size: 批量推理大小.

    Returns:
        添加了 sentiment, confidence, sentiment_score 列的 DataFrame.
    """
    texts = df["full_text"].tolist()
    results: List[Dict] = []

    for i in tqdm(
        range(0, len(texts), batch_size),
        desc="FinBERT 推理中",
        total=len(texts) // batch_size + 1,
    ):
        batch = texts[i : i + batch_size]
        batch_results = sentiment_pipeline(batch)
        results.extend(batch_results)

    df["sentiment"] = [r["label"].lower() for r in results]
    df["confidence"] = [r["score"] for r in results]
    df["sentiment_score"] = df["sentiment"].map(
        {"positive": 1, "neutral": 0, "negative": -1}
    )

    # 保存情感标签
    df[["sentiment", "confidence", "sentiment_score"]].to_csv(
        os.path.join(OUTPUT_DIR, "ch03_sentiment_labels.csv"), index=False
    )

    coverage = df["sentiment"].notna().mean() * 100
    logger.info(f"情感标签覆盖率: {coverage:.1f}%")

    # 情感分布统计
    sent_dist = df["sentiment"].value_counts(normalize=True) * 100
    for label, ratio in sent_dist.items():
        logger.info(f"  {label}: {ratio:.1f}%")

    return df


# =============================================================================
# Step 3: 情感分布统计 + 行业交叉分析
# =============================================================================

def plot_sentiment_distribution(df: pd.DataFrame) -> None:
    """生成情感分布饼图和行业情感对比箱线图.

    Args:
        df: 包含 sentiment, sentiment_score, categories_list 列的 DataFrame.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # 情感分布饼图
    sent_counts = df["sentiment"].value_counts()
    colors = {"positive": "#2ecc71", "neutral": "#95a5a6", "negative": "#e74c3c"}
    pie_colors = [colors.get(label, "#3498db") for label in sent_counts.index]
    ax1.pie(
        sent_counts.values,
        labels=sent_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=pie_colors,
    )
    ax1.set_title("FinBERT Sentiment Distribution", fontsize=14)

    # 行业情感箱线图
    df["primary_category"] = df["categories_list"].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else "Unknown"
    )
    top10_cats = df["primary_category"].value_counts().head(10).index
    df_top10 = df[df["primary_category"].isin(top10_cats)]
    order = (
        df_top10.groupby("primary_category")["sentiment_score"]
        .mean()
        .sort_values()
        .index
    )
    sns.boxplot(
        data=df_top10,
        x="primary_category",
        y="sentiment_score",
        order=order,
        ax=ax2,
        palette="RdYlGn",
    )
    ax2.set_title("Top 10 Categories - Sentiment Score Distribution", fontsize=14)
    ax2.set_xlabel("Category")
    ax2.set_ylabel("Sentiment Score")
    ax2.tick_params(axis="x", rotation=45)
    ax2.axhline(0, color="gray", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, "ch03_sentiment_by_category.png"),
        dpi=FIGURE_DPI_HIGH,
        bbox_inches="tight",
    )
    plt.close()
    logger.info("情感分布 + 行业对比图已保存")

    # 单独保存饼图（满足产物清单要求）
    fig2, ax3 = plt.subplots(figsize=(8, 6))
    ax3.pie(
        sent_counts.values,
        labels=sent_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=pie_colors,
    )
    ax3.set_title("FinBERT Sentiment Distribution", fontsize=14)
    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, "ch03_sentiment_distribution.png"),
        dpi=FIGURE_DPI_HIGH,
        bbox_inches="tight",
    )
    plt.close()
    logger.info("情感分布饼图已保存")


# =============================================================================
# Step 4: 情感时序演变 + 事件窗口分析
# =============================================================================

def plot_sentiment_timeline(df: pd.DataFrame) -> None:
    """生成月度情感趋势图和事件窗口情感变化图.

    Args:
        df: 包含 date, sentiment_score 列的 DataFrame.
    """
    df["date"] = pd.to_datetime(df["date"])
    monthly_sentiment = (
        df.set_index("date")
        .resample("M")["sentiment_score"]
        .agg(["mean", "std", "count"])
    )

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # 月度情感趋势
    axes[0].plot(
        monthly_sentiment.index,
        monthly_sentiment["mean"],
        linewidth=1.5,
        label="Monthly Mean",
        color="#2c3e50",
    )
    axes[0].fill_between(
        monthly_sentiment.index,
        monthly_sentiment["mean"] - monthly_sentiment["std"],
        monthly_sentiment["mean"] + monthly_sentiment["std"],
        alpha=0.2,
        label="+/- 1 std",
    )
    axes[0].axhline(0, color="gray", linestyle="--", alpha=0.5)
    axes[0].set_title("Monthly Sentiment Score Trend", fontsize=14)
    axes[0].set_xlabel("Date")
    axes[0].set_ylabel("Sentiment Score")
    axes[0].legend()

    # 事件窗口分析
    events = {"COVID-19": "2020-03-01", "Russia-Ukraine War": "2022-02-01"}
    colors = ["red", "blue"]
    for (name, date_str), color in zip(events.items(), colors):
        event_date = pd.Timestamp(date_str)
        axes[1].axvline(event_date, color=color, linestyle="--", alpha=0.7, label=name)
    axes[1].plot(
        monthly_sentiment.index,
        monthly_sentiment["mean"],
        linewidth=1.5,
        color="#2c3e50",
    )
    axes[1].axhline(0, color="gray", linestyle="--", alpha=0.5)
    axes[1].set_title("Major Event Windows - Sentiment Changes", fontsize=14)
    axes[1].set_xlabel("Date")
    axes[1].set_ylabel("Sentiment Score")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, "ch03_sentiment_timeline.png"),
        dpi=FIGURE_DPI_HIGH,
        bbox_inches="tight",
    )
    plt.close()
    logger.info("情感时序趋势图已保存")

    # 单独保存事件窗口分析图
    fig2, ax = plt.subplots(figsize=(14, 6))
    for (name, date_str), color in zip(events.items(), colors):
        event_date = pd.Timestamp(date_str)
        ax.axvline(event_date, color=color, linestyle="--", alpha=0.7, label=name)
    ax.plot(
        monthly_sentiment.index,
        monthly_sentiment["mean"],
        linewidth=1.5,
        color="#2c3e50",
    )
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax.set_title("Major Event Windows - Sentiment Changes", fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Sentiment Score")
    ax.legend()
    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, "ch03_event_window_sentiment.png"),
        dpi=FIGURE_DPI_HIGH,
        bbox_inches="tight",
    )
    plt.close()
    logger.info("事件窗口情感变化图已保存")


# =============================================================================
# Step 5: 文本预处理 + BERTopic 主题建模
# =============================================================================

def preprocess_texts(texts: List[str]) -> List[str]:
    """对文本进行 spaCy 预处理（小写、去停用词、lemmatization）.

    Args:
        texts: 原始文本列表.

    Returns:
        预处理后的文本列表.
    """
    import spacy

    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

    def _clean(text: str) -> str:
        doc = nlp(str(text).lower())
        return " ".join(
            token.lemma_
            for token in doc
            if not token.is_stop and not token.is_punct and len(token) > 2
        )

    docs = [_clean(t) for t in tqdm(texts, desc="文本预处理")]
    return docs


def run_bertopic(
    docs: List[str],
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, object]:
    """运行 BERTopic 主题建模.

    Args:
        docs: 预处理后的文本列表.
        df: 原始 DataFrame（用于关联日期等信息）.

    Returns:
        Tuple of (topic_results_df, topic_model).
    """
    from bertopic import BERTopic

    logger.info("开始 BERTopic 主题建模...")
    topic_model = BERTopic(
        nr_topics="auto",
        verbose=True,
        embedding_model="all-MiniLM-L6-v2",
    )
    topics, probs = topic_model.fit_transform(docs)

    # 保存主题分类结果
    topic_df = pd.DataFrame({"topic_id": topics, "topic_prob": probs})
    topic_df.to_csv(
        os.path.join(OUTPUT_DIR, "ch03_topic_model_results.csv"), index=False
    )

    # 主题信息
    topic_info = topic_model.get_topic_info()
    n_topics = len(topic_info[topic_info["Topic"] != -1])
    logger.info(f"识别到 {n_topics} 个主题（排除 outlier）")

    # 保存 BERTopic 可视化
    try:
        fig = topic_model.visualize_topics()
        fig.write_html(
            os.path.join(OUTPUT_DIR, "ch03_topic_visualization.html")
        )
        logger.info("BERTopic 可视化已保存")
    except Exception as e:
        logger.warning(f"BERTopic 可视化生成失败: {e}")
        # 创建简单的 HTML 占位
        html_content = """<!DOCTYPE html>
<html><head><title>BERTopic Visualization</title></head>
<body><h1>BERTopic Topic Visualization</h1>
<p>Interactive visualization could not be generated. See topic_model_results.csv for details.</p></body></html>"""
        Path(os.path.join(OUTPUT_DIR, "ch03_topic_visualization.html")).write_text(
            html_content, encoding="utf-8"
        )

    return topic_df, topic_model


# =============================================================================
# Step 6: LDA 对比 + 主题时序分析 + 报告
# =============================================================================

def run_lda_comparison(
    docs: List[str],
) -> Tuple[int, float, object]:
    """运行 LDA 主题模型并与 BERTopic 对比.

    Args:
        docs: 预处理后的文本列表.

    Returns:
        Tuple of (best_n_topics, best_coherence, best_lda_model).
    """
    from gensim import corpora
    from gensim.models import CoherenceModel, LdaModel

    texts_split = [d.split() for d in docs]
    dictionary = corpora.Dictionary(texts_split)
    dictionary.filter_extremes(no_below=10, no_above=0.5)
    corpus = [dictionary.doc2bow(t) for t in texts_split]

    logger.info(f"词典大小: {len(dictionary)}, 语料库大小: {len(corpus)}")

    best_score, best_n, best_lda = 0.0, 8, None
    results = []

    for n in range(8, 16):
        lda = LdaModel(
            corpus, num_topics=n, id2word=dictionary, random_state=42, passes=5
        )
        cm = CoherenceModel(
            model=lda, texts=texts_split, dictionary=dictionary, coherence="c_v"
        )
        score = cm.get_coherence()
        results.append((n, score))
        logger.info(f"Topics={n}, Coherence={score:.4f}")
        if score > best_score:
            best_score, best_n, best_lda = score, n, lda

    logger.info(f"最优主题数: {best_n}, Coherence: {best_score:.4f}")
    return best_n, best_score, best_lda


def plot_topic_timeline_heatmap(
    df: pd.DataFrame, topics: List[int]
) -> None:
    """绘制主题热度月度时序热力图.

    Args:
        df: 包含 date 列的 DataFrame.
        topics: 每条新闻的主题 ID 列表.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["topic_id"] = topics

    # 过滤掉 outlier topic (-1)
    df_filtered = df[df["topic_id"] != -1].copy()

    topic_monthly = (
        df_filtered.groupby(
            [pd.Grouper(key="date", freq="M"), "topic_id"]
        )
        .size()
        .unstack(fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(16, 8))
    sns.heatmap(topic_monthly.T, cmap="YlOrRd", ax=ax, cbar_kws={"label": "Count"})
    ax.set_title("Topic Heatmap - Monthly Timeline", fontsize=14)
    ax.set_xlabel("Month")
    ax.set_ylabel("Topic ID")

    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, "ch03_topic_timeline_heatmap.png"),
        dpi=FIGURE_DPI_HIGH,
        bbox_inches="tight",
    )
    plt.close()
    logger.info("主题时序热力图已保存")


def generate_sentiment_report(
    df: pd.DataFrame,
    monthly_sentiment: pd.DataFrame,
) -> None:
    """生成情感分析 Markdown 报告.

    Args:
        df: 包含情感标签的 DataFrame.
        monthly_sentiment: 月度情感统计 DataFrame.
    """
    # 情感分布统计
    sent_counts = df["sentiment"].value_counts()
    sent_pct = df["sentiment"].value_counts(normalize=True) * 100

    # 行业情感统计
    df["primary_category"] = df["categories_list"].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else "Unknown"
    )
    cat_sentiment = (
        df.groupby("primary_category")["sentiment_score"]
        .agg(["mean", "std", "count"])
        .sort_values("mean", ascending=False)
        .head(15)
    )

    # 事件窗口分析
    df["date"] = pd.to_datetime(df["date"])
    events = {
        "COVID-19 (2020-03)": ("2020-02-01", "2020-04-30"),
        "Russia-Ukraine War (2022-02)": ("2022-01-01", "2022-03-31"),
    }
    event_stats = {}
    for name, (start, end) in events.items():
        mask = (df["date"] >= start) & (df["date"] <= end)
        event_df = df[mask]
        if len(event_df) > 0:
            event_stats[name] = {
                "count": len(event_df),
                "mean_sentiment": event_df["sentiment_score"].mean(),
                "positive_pct": (
                    (event_df["sentiment"] == "positive").mean() * 100
                ),
                "negative_pct": (
                    (event_df["sentiment"] == "negative").mean() * 100
                ),
            }

    # 生成报告
    report_lines = [
        "# Sentiment Analysis Report (FinBERT)\n",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        f"**Total Articles Analyzed**: {len(df):,}\n",
        f"**Model**: ProsusAI/finbert\n",
        "",
        "## 1. Overall Sentiment Distribution\n",
        "",
        "| Sentiment | Count | Percentage |",
        "|-----------|-------|------------|",
    ]
    for label in ["positive", "neutral", "negative"]:
        count = sent_counts.get(label, 0)
        pct = sent_pct.get(label, 0)
        report_lines.append(f"| {label.capitalize()} | {count:,} | {pct:.1f}% |")

    report_lines.extend([
        "",
        "## 2. Sentiment by Category (Top 15)\n",
        "",
        "| Category | Mean Score | Std | Count |",
        "|----------|-----------|-----|-------|",
    ])
    for cat, row in cat_sentiment.iterrows():
        report_lines.append(
            f"| {cat} | {row['mean']:.3f} | {row['std']:.3f} | {int(row['count']):,} |"
        )

    report_lines.extend([
        "",
        "## 3. Sentiment Timeline Analysis\n",
        "",
        "The monthly sentiment trend shows how market sentiment evolved over time. ",
        "Key observations:\n",
        "",
    ])

    # 添加月度趋势关键数据点
    if len(monthly_sentiment) > 0:
        most_positive_month = monthly_sentiment["mean"].idxmax()
        most_negative_month = monthly_sentiment["mean"].idxmin()
        report_lines.append(
            f"- **Most Positive Month**: {most_positive_month.strftime('%Y-%m')} "
            f"(score: {monthly_sentiment.loc[most_positive_month, 'mean']:.3f})\n"
        )
        report_lines.append(
            f"- **Most Negative Month**: {most_negative_month.strftime('%Y-%m')} "
            f"(score: {monthly_sentiment.loc[most_negative_month, 'mean']:.3f})\n"
        )
        overall_mean = monthly_sentiment["mean"].mean()
        report_lines.append(
            f"- **Overall Monthly Average**: {overall_mean:.3f}\n"
        )

    report_lines.extend([
        "",
        "## 4. Event Window Analysis\n",
        "",
        "| Event | Articles | Mean Score | Positive % | Negative % |",
        "|-------|----------|-----------|------------|------------|",
    ])
    for name, stats in event_stats.items():
        report_lines.append(
            f"| {name} | {stats['count']:,} | {stats['mean_sentiment']:.3f} "
            f"| {stats['positive_pct']:.1f}% | {stats['negative_pct']:.1f}% |"
        )

    report_lines.extend([
        "",
        "## 5. Confidence Score Analysis\n",
        "",
        f"- **Mean Confidence**: {df['confidence'].mean():.4f}\n",
        f"- **Median Confidence**: {df['confidence'].median():.4f}\n",
        f"- **Min Confidence**: {df['confidence'].min():.4f}\n",
        f"- **Max Confidence**: {df['confidence'].max():.4f}\n",
        "",
        "## 6. Key Findings\n",
        "",
        f"1. The dataset is predominantly **{sent_counts.index[0]}** "
        f"({sent_pct.iloc[0]:.1f}%), reflecting the general nature of financial news reporting.\n",
        f"2. The average sentiment score is **{df['sentiment_score'].mean():.3f}**, "
        f"indicating a slight {'positive' if df['sentiment_score'].mean() > 0 else 'negative' if df['sentiment_score'].mean() < 0 else 'neutral'} bias in financial news.\n",
    ])

    # 添加事件窗口发现
    for name, stats in event_stats.items():
        direction = "positive" if stats["mean_sentiment"] > 0 else "negative"
        report_lines.append(
            f"3. During {name}, sentiment was predominantly **{direction}** "
            f"(mean score: {stats['mean_sentiment']:.3f}).\n"
        )

    report_content = "\n".join(report_lines)
    report_path = os.path.join(OUTPUT_DIR, "ch03_sentiment_analysis_report.md")
    Path(report_path).write_text(report_content, encoding="utf-8")
    logger.info(f"情感分析报告已保存: {report_path}")


def generate_topic_report(
    topic_model: object,
    n_topics_bertopic: int,
    lda_n_topics: int,
    lda_coherence: float,
    df: pd.DataFrame,
    topics: List[int],
) -> None:
    """生成主题分析 Markdown 报告.

    Args:
        topic_model: BERTopic 模型.
        n_topics_bertopic: BERTopic 识别的主题数.
        lda_n_topics: LDA 最优主题数.
        lda_coherence: LDA 最优 Coherence Score.
        df: 原始 DataFrame.
        topics: 每条新闻的主题 ID 列表.
    """
    report_lines = [
        "# Topic Analysis Report (BERTopic + LDA)\n",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        f"**Total Articles Analyzed**: {len(df):,}\n",
        "",
        "## 1. BERTopic Results\n",
        "",
        f"- **Number of Topics**: {n_topics_bertopic}\n",
        f"- **Embedding Model**: all-MiniLM-L6-v2\n",
        "",
        "### Topic Details\n",
        "",
        "| Topic ID | Top Keywords | Article Count |",
        "|----------|-------------|---------------|",
    ]

    topic_info = topic_model.get_topic_info()
    for _, row in topic_info.iterrows():
        topic_id = row["Topic"]
        if topic_id == -1:
            label = "Outlier"
        else:
            try:
                top_words = topic_model.get_topic(topic_id)
                keywords = ", ".join([w for w, _ in top_words[:5]])
                label = keywords
            except Exception:
                label = "N/A"
        count = row.get("Count", 0)
        report_lines.append(f"| {topic_id} | {label} | {count:,} |")

    report_lines.extend([
        "",
        "## 2. LDA Comparison\n",
        "",
        f"- **Optimal Number of Topics**: {lda_n_topics}\n",
        f"- **Coherence Score (c_v)**: {lda_coherence:.4f}\n",
        "",
        "### Model Comparison\n",
        "",
        "| Metric | BERTopic | LDA |",
        "|--------|----------|-----|",
        f"| Number of Topics | {n_topics_bertopic} | {lda_n_topics} |",
        f"| Coherence (c_v) | N/A | {lda_coherence:.4f} |",
        f"| Interpretability | High (keyword-based) | Moderate |",
        f"| Training Speed | Moderate | Fast |",
        "",
        "## 3. Topic Distribution\n",
        "",
    ])

    # 主题分布统计
    topic_counts = pd.Series(topics).value_counts().sort_index()
    report_lines.append("| Topic ID | Article Count | Percentage |")
    report_lines.append("|----------|--------------|------------|")
    for tid, count in topic_counts.items():
        pct = count / len(topics) * 100
        report_lines.append(f"| {tid} | {count:,} | {pct:.1f}% |")

    report_lines.extend([
        "",
        "## 4. Key Findings\n",
        "",
        f"1. BERTopic identified **{n_topics_bertopic}** distinct topics from the financial news corpus.\n",
        f"2. LDA with {lda_n_topics} topics achieved a coherence score of **{lda_coherence:.4f}**"
        + (" (>= 0.4 threshold met)" if lda_coherence >= 0.4 else " (< 0.4 threshold, consider adjusting parameters)") + ".\n",
    ])

    # 最大主题
    if len(topic_counts) > 0:
        largest_topic = topic_counts.idxmax()
        largest_pct = topic_counts.max() / len(topics) * 100
        report_lines.append(
            f"3. The largest topic (ID: {largest_topic}) contains "
            f"**{largest_pct:.1f}%** of all articles.\n"
        )

    report_content = "\n".join(report_lines)
    report_path = os.path.join(OUTPUT_DIR, "ch03_topic_analysis_report.md")
    Path(report_path).write_text(report_content, encoding="utf-8")
    logger.info(f"主题分析报告已保存: {report_path}")


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    """主函数：执行 ch03 全部分析步骤."""
    logger.info("=" * 60)
    logger.info("ch03 文本挖掘与情感分析 — 开始执行")
    logger.info("=" * 60)

    # 加载数据
    logger.info(f"加载数据: {INPUT_DATA_PATH}")
    df = pd.read_csv(INPUT_DATA_PATH)
    logger.info(f"数据加载完成: {df.shape[0]:,} 行 x {df.shape[1]} 列")

    # 采样（CPU 环境下加速）
    if SAMPLE_FRACTION < 1.0:
        original_count = len(df)
        df = df.sample(frac=SAMPLE_FRACTION, random_state=42).reset_index(drop=True)
        logger.info(f"采样: {original_count:,} -> {len(df):,} ({SAMPLE_FRACTION*100:.0f}%)")

    # Step 1: FinBERT 模型加载
    logger.info("\n--- Step 1: FinBERT 模型加载 ---")
    sentiment_pipeline, device, batch_size = load_finbert_pipeline()

    # Step 2: 全量情感标签生成
    logger.info("\n--- Step 2: 情感标签生成 ---")
    df = generate_sentiment_labels(df, sentiment_pipeline, batch_size)

    # Step 3: 情感分布统计 + 行业交叉分析
    logger.info("\n--- Step 3: 情感分布统计 ---")
    plot_sentiment_distribution(df)

    # Step 4: 情感时序演变 + 事件窗口分析
    logger.info("\n--- Step 4: 情感时序分析 ---")
    plot_sentiment_timeline(df)

    # 计算月度情感统计（供报告使用）
    df["date"] = pd.to_datetime(df["date"])
    monthly_sentiment = (
        df.set_index("date")
        .resample("M")["sentiment_score"]
        .agg(["mean", "std", "count"])
    )

    # Step 5: 文本预处理 + BERTopic 主题建模
    logger.info("\n--- Step 5: BERTopic 主题建模 ---")
    docs = preprocess_texts(df["full_text"].tolist())
    topic_df, topic_model = run_bertopic(docs, df)
    topics = topic_df["topic_id"].tolist()

    # Step 6: LDA 对比 + 主题时序分析 + 报告
    logger.info("\n--- Step 6: LDA 对比 + 报告生成 ---")
    lda_n_topics, lda_coherence, lda_model = run_lda_comparison(docs)

    plot_topic_timeline_heatmap(df, topics)

    # 统计 BERTopic 主题数（排除 outlier）
    n_topics_bertopic = len(
        topic_model.get_topic_info()[topic_model.get_topic_info()["Topic"] != -1]
    )

    generate_sentiment_report(df, monthly_sentiment)
    generate_topic_report(
        topic_model, n_topics_bertopic, lda_n_topics, lda_coherence, df, topics
    )

    logger.info("\n" + "=" * 60)
    logger.info(f"ch03 完成。产物已输出到: {OUTPUT_DIR}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
