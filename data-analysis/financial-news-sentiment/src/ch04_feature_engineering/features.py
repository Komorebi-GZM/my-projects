"""Prompt-04: 特征工程.

基于情感标签、主题分类、关键词统计、时间特征等维度，
构建标准化的新闻舆情特征集，输出按日期聚合的日频特征表（目标 >= 30 个特征）。

覆盖步骤:
  - Step 1: 数据合并
  - Step 2-7: 七类特征构造（情感、主题、关键词、影响等级、文本统计、时间、交叉）
  - Step 8: 共线性检测（VIF）
  - Step 9: 特征重要性分析
  - Step 10: 可视化与报告

产物输出到: outputs/ch04_feature_engineering/
"""

from __future__ import annotations

import logging
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# 路径设置
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
from scipy import stats

from utils.config import (
    FIGURE_DPI_HIGH,
    MATPLOTLIB_RC_PARAMS,
    get_chapter_output_dir,
    setup_logging,
)

plt.rcParams.update(MATPLOTLIB_RC_PARAMS)

logger = setup_logging("ch04_features", log_to_file=True)
OUTPUT_DIR = get_chapter_output_dir("ch04_feature_engineering")
os.makedirs(OUTPUT_DIR, exist_ok=True)

warnings.filterwarnings("ignore", category=FutureWarning)


# =============================================================================
# Step 1: 数据合并
# =============================================================================

def load_and_merge_data() -> pd.DataFrame:
    """加载并合并 ch01 清洗数据、ch03 情感标签、ch03 主题分类."""
    logger.info("Step 1: 加载并合并数据...")
    
    # 加载 ch01 清洗数据
    ch01_path = os.path.join(
        PROJECT_ROOT, "outputs", "ch01_data_preprocessing", "ch01_cleaned_data.csv"
    )
    df = pd.read_csv(ch01_path, parse_dates=["date"])
    logger.info(f"  ch01 数据: {len(df):,} 行")
    
    # 加载 ch03 情感标签
    sentiment_path = os.path.join(
        PROJECT_ROOT, "outputs", "ch03_text_mining_sentiment", "ch03_sentiment_labels.csv"
    )
    sentiment = pd.read_csv(sentiment_path)
    df["sentiment"] = sentiment["sentiment"].values
    df["confidence"] = sentiment["confidence"].values
    df["sentiment_score"] = sentiment["sentiment_score"].values
    logger.info(f"  情感标签已合并")
    
    # 加载 ch03 主题分类
    topic_path = os.path.join(
        PROJECT_ROOT, "outputs", "ch03_text_mining_sentiment", "ch03_topic_model_results.csv"
    )
    topics = pd.read_csv(topic_path)
    df["topic_id"] = topics["topic_id"].values
    df["topic_prob"] = topics["topic_prob"].values
    logger.info(f"  主题分类已合并")
    
    return df


# =============================================================================
# Step 2-7: 七类特征构造
# =============================================================================

def construct_sentiment_features(df: pd.DataFrame) -> pd.DataFrame:
    """构造情感特征."""
    logger.info("Step 2: 构造情感特征...")
    
    daily = df.groupby("date").agg(
        sentiment_mean=("sentiment_score", "mean"),
        sentiment_std=("sentiment_score", "std"),
        sentiment_min=("sentiment_score", "min"),
        sentiment_max=("sentiment_score", "max"),
        positive_count=("sentiment", lambda x: (x == "positive").sum()),
        negative_count=("sentiment", lambda x: (x == "negative").sum()),
        neutral_count=("sentiment", lambda x: (x == "neutral").sum()),
        total_count=("sentiment", "size"),
        high_confidence_ratio=("confidence", lambda x: (x > 0.8).mean()),
    )
    
    daily["positive_ratio"] = daily["positive_count"] / daily["total_count"]
    daily["negative_ratio"] = daily["negative_count"] / daily["total_count"]
    daily["neutral_ratio"] = daily["neutral_count"] / daily["total_count"]
    daily["polarization_idx"] = abs(daily["positive_ratio"] - daily["negative_ratio"])
    daily["sentiment_range"] = daily["sentiment_max"] - daily["sentiment_min"]
    
    # 情感动量（5日移动平均）
    daily["sentiment_ma5"] = daily["sentiment_mean"].rolling(5, min_periods=1).mean()
    daily["sentiment_ma10"] = daily["sentiment_mean"].rolling(10, min_periods=1).mean()
    
    logger.info(f"  情感特征: {len(daily.columns)} 个")
    return daily


def construct_topic_features(df: pd.DataFrame) -> pd.DataFrame:
    """构造主题特征."""
    logger.info("Step 3: 构造主题特征...")
    
    # 每日主题数量分布
    topic_counts = df.groupby(["date", "topic_id"]).size().unstack(fill_value=0)
    topic_counts.columns = [f"topic_{c}_count" for c in topic_counts.columns]
    
    # 主题多样性（Shannon 熵）- 过滤掉负值（outlier topic -1）
    def shannon_entropy(x):
        x = x[x >= 0]  # 过滤负值
        if len(x) == 0:
            return 0
        counts = np.bincount(x)
        probs = counts[counts > 0] / len(x)
        if len(probs) == 0:
            return 0
        return -np.sum(probs * np.log(probs + 1e-10))
    
    topic_entropy = df.groupby("date")["topic_id"].apply(shannon_entropy).rename("topic_shannon_entropy")
    
    # 每日唯一主题数
    unique_topics = df.groupby("date")["topic_id"].nunique().rename("unique_topic_count")
    
    # 主导主题占比（过滤 outlier -1）
    def calc_dominant_ratio(x):
        x = x[x >= 0]  # 过滤负值
        if len(x) == 0:
            return 0
        return x.value_counts().iloc[0] / len(x)
    
    dominant_topic_ratio = df.groupby("date")["topic_id"].apply(calc_dominant_ratio).rename("dominant_topic_ratio")
    
    features = pd.concat([topic_entropy, unique_topics, dominant_topic_ratio], axis=1)
    logger.info(f"  主题特征: {len(features.columns)} 个")
    return features


def construct_impact_features(df: pd.DataFrame) -> pd.DataFrame:
    """构造影响等级特征."""
    logger.info("Step 4: 构造影响等级特征...")
    
    tier_counts = df.groupby(["date", "impact_tier"]).size().unstack(fill_value=0)
    tier_total = df.groupby("date").size()
    
    # 各等级占比
    for tier in ["HIGH", "MEDIUM", "LOW"]:
        if tier in tier_counts.columns:
            tier_counts[f"{tier.lower()}_ratio"] = tier_counts[tier] / tier_total
    
    # 加权影响分
    tier_counts["impact_weighted"] = df.groupby("date").apply(
        lambda x: (x["impact_tier"].map({"HIGH": 3, "MEDIUM": 2, "LOW": 1}) * x["relevance_score"]).mean()
    )
    
    # 高影响新闻占比
    tier_counts["high_impact_ratio"] = tier_counts.get("HIGH", 0) / tier_total
    
    logger.info(f"  影响等级特征: {len(tier_counts.columns)} 个")
    return tier_counts


def construct_text_features(df: pd.DataFrame) -> pd.DataFrame:
    """构造文本统计特征."""
    logger.info("Step 5: 构造文本统计特征...")
    
    text_stats = df.groupby("date").agg(
        avg_text_length=("text_length", "mean"),
        std_text_length=("text_length", "std"),
        avg_title_length=("title_length", "mean"),
        avg_desc_length=("desc_length", "mean"),
        news_count=("title", "size"),
        negation_ratio=("has_negation", "mean"),
        avg_category_count=("category_count", "mean"),
        avg_keyword_count=("keyword_count", "mean"),
        avg_relevance_score=("relevance_score", "mean"),
    )
    
    # 文本长度变异系数
    text_stats["text_length_cv"] = text_stats["std_text_length"] / text_stats["avg_text_length"]
    
    # 新闻数量变化率
    text_stats["news_count_change"] = text_stats["news_count"].pct_change().fillna(0)
    
    logger.info(f"  文本统计特征: {len(text_stats.columns)} 个")
    return text_stats


def construct_time_features(date_index: pd.DatetimeIndex) -> pd.DataFrame:
    """构造时间特征."""
    logger.info("Step 6: 构造时间特征...")
    
    features = pd.DataFrame(index=date_index)
    features["day_of_week"] = features.index.dayofweek
    features["month"] = features.index.month
    features["quarter"] = features.index.quarter
    features["year"] = features.index.year
    features["is_weekend"] = features["day_of_week"].isin([5, 6]).astype(int)
    features["is_month_start"] = features.index.is_month_start.astype(int)
    features["is_month_end"] = features.index.is_month_end.astype(int)
    features["is_quarter_start"] = features.index.is_quarter_start.astype(int)
    features["is_quarter_end"] = features.index.is_quarter_end.astype(int)
    features["day_of_year"] = features.index.dayofyear
    
    logger.info(f"  时间特征: {len(features.columns)} 个")
    return features


def construct_cross_features(df: pd.DataFrame) -> pd.DataFrame:
    """构造交叉特征."""
    logger.info("Step 7: 构造交叉特征...")
    
    # 情感 × 影响等级交叉
    cross = df.groupby("date").apply(
        lambda x: pd.Series({
            "high_impact_positive_ratio": ((x["impact_tier"] == "HIGH") & (x["sentiment"] == "positive")).sum() / len(x),
            "high_impact_negative_ratio": ((x["impact_tier"] == "HIGH") & (x["sentiment"] == "negative")).sum() / len(x),
            "long_text_negative_ratio": ((x["text_length"] > x["text_length"].median()) & (x["sentiment"] == "negative")).sum() / len(x),
        })
    )
    
    logger.info(f"  交叉特征: {len(cross.columns)} 个")
    return cross


# =============================================================================
# Step 8: 共线性检测（VIF）
# =============================================================================

def calculate_vif(features: pd.DataFrame) -> pd.DataFrame:
    """计算方差膨胀因子（VIF）."""
    logger.info("Step 8: 共线性检测（VIF）...")
    
    try:
        from statsmodels.stats.outliers_influence import variance_inflation_factor
        
        # 选择数值型特征
        numeric_features = features.select_dtypes(include=[np.number])
        
        # 移除常数列和高度相关列
        numeric_features = numeric_features.loc[:, numeric_features.std() > 0]
        
        # 处理无穷值和缺失值
        numeric_features = numeric_features.replace([np.inf, -np.inf], np.nan)
        numeric_features = numeric_features.fillna(numeric_features.median())
        
        vif_data = pd.DataFrame()
        vif_data["feature"] = numeric_features.columns
        vif_data["VIF"] = [variance_inflation_factor(numeric_features.values, i) 
                          for i in range(numeric_features.shape[1])]
        
        logger.info(f"  VIF 计算完成: {len(vif_data)} 个特征")
        logger.info(f"  高 VIF 特征 (>10): {(vif_data['VIF'] > 10).sum()} 个")
        
        return vif_data
    except Exception as e:
        logger.warning(f"  VIF 计算失败: {e}")
        return pd.DataFrame(columns=["feature", "VIF"])


# =============================================================================
# Step 9: 特征重要性分析
# =============================================================================

def calculate_feature_importance(features: pd.DataFrame) -> pd.DataFrame:
    """使用随机森林计算特征重要性."""
    logger.info("Step 9: 特征重要性分析...")
    
    try:
        from sklearn.ensemble import RandomForestRegressor
        
        # 使用 sentiment_mean 作为目标变量（示例）
        if "sentiment_mean" in features.columns:
            X = features.drop(columns=["sentiment_mean"], errors="ignore")
            y = features["sentiment_mean"]
            
            # 只使用数值特征
            X = X.select_dtypes(include=[np.number])
            X = X.fillna(X.median())
            
            model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            model.fit(X, y)
            
            importance = pd.DataFrame({
                "feature": X.columns,
                "importance": model.feature_importances_,
            }).sort_values("importance", ascending=False)
            
            logger.info(f"  特征重要性计算完成: Top 3 - {', '.join(importance['feature'].head(3))}")
            return importance
    except Exception as e:
        logger.warning(f"  特征重要性计算失败: {e}")
    
    return pd.DataFrame(columns=["feature", "importance"])


# =============================================================================
# Step 10: 可视化与报告
# =============================================================================

def plot_correlation_heatmap(features: pd.DataFrame) -> None:
    """绘制特征相关性热力图."""
    logger.info("Step 10: 生成可视化...")
    
    # 选择前 20 个特征绘制热力图
    numeric_features = features.select_dtypes(include=[np.number])
    if len(numeric_features.columns) > 20:
        # 选择方差最大的 20 个特征
        top_features = numeric_features.std().nlargest(20).index
        plot_features = numeric_features[top_features]
    else:
        plot_features = numeric_features
    
    corr = plot_features.corr()
    
    fig, ax = plt.subplots(figsize=(14, 12))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=False, cmap="RdBu_r", center=0,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title("Feature Correlation Heatmap (Top 20)", fontsize=14)
    
    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, "ch04_correlation_heatmap.png"),
        dpi=FIGURE_DPI_HIGH,
        bbox_inches="tight",
    )
    plt.close()
    logger.info("  相关性热力图已保存")


def plot_feature_distribution(features: pd.DataFrame) -> None:
    """绘制特征分布图."""
    # 选择 6 个关键特征绘制分布
    key_features = ["sentiment_mean", "positive_ratio", "news_count", 
                    "topic_shannon_entropy", "high_impact_ratio", "avg_text_length"]
    available_features = [f for f in key_features if f in features.columns][:6]
    
    if len(available_features) < 4:
        logger.warning("  可用特征不足，跳过分布图")
        return
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, feature in enumerate(available_features):
        axes[i].hist(features[feature].dropna(), bins=30, edgecolor="black", alpha=0.7)
        axes[i].set_title(f"{feature}", fontsize=12)
        axes[i].set_xlabel("Value")
        axes[i].set_ylabel("Frequency")
    
    plt.suptitle("Feature Distributions", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, "ch04_feature_distribution.png"),
        dpi=FIGURE_DPI_HIGH,
        bbox_inches="tight",
    )
    plt.close()
    logger.info("  特征分布图已保存")


def generate_report(features: pd.DataFrame, vif_data: pd.DataFrame, 
                    importance: pd.DataFrame, total_features: int) -> None:
    """生成特征工程报告."""
    logger.info("  生成报告...")
    
    report_lines = [
        "# Feature Engineering Report\n",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        f"**Total Features**: {total_features}\n",
        f"**Date Range**: {features.index.min().strftime('%Y-%m-%d')} to {features.index.max().strftime('%Y-%m-%d')}\n",
        f"**Total Days**: {len(features)}\n",
        "",
        "## 1. Feature Categories\n",
        "",
        "| Category | Features |",
        "|----------|----------|",
    ]
    
    # 分类统计
    sentiment_cols = [c for c in features.columns if "sentiment" in c or "positive" in c or "negative" in c]
    topic_cols = [c for c in features.columns if "topic" in c]
    impact_cols = [c for c in features.columns if "impact" in c or "ratio" in c]
    text_cols = [c for c in features.columns if "text" in c or "length" in c or "count" in c]
    time_cols = [c for c in features.columns if c in ["day_of_week", "month", "quarter", "year", "is_weekend"]]
    
    report_lines.extend([
        f"| Sentiment | {len(sentiment_cols)} |",
        f"| Topic | {len(topic_cols)} |",
        f"| Impact | {len(impact_cols)} |",
        f"| Text Stats | {len(text_cols)} |",
        f"| Time | {len(time_cols)} |",
        "",
        "## 2. Feature Statistics\n",
        "",
        "| Feature | Mean | Std | Min | Max |",
        "|---------|------|-----|-----|-----|",
    ])
    
    # 关键特征统计
    for col in ["sentiment_mean", "positive_ratio", "news_count", "topic_shannon_entropy"][:4]:
        if col in features.columns:
            stats = features[col].describe()
            report_lines.append(f"| {col} | {stats['mean']:.3f} | {stats['std']:.3f} | {stats['min']:.3f} | {stats['max']:.3f} |")
    
    # VIF 信息
    if not vif_data.empty:
        report_lines.extend([
            "",
            "## 3. Multicollinearity (VIF)\n",
            "",
            f"- **Mean VIF**: {vif_data['VIF'].mean():.2f}\n",
            f"- **Max VIF**: {vif_data['VIF'].max():.2f}\n",
            f"- **Features with VIF > 10**: {(vif_data['VIF'] > 10).sum()}\n",
            "",
            "| Top 10 High VIF Features | VIF |",
            "|--------------------------|-----|",
        ])
        for _, row in vif_data.nlargest(10, "VIF").iterrows():
            report_lines.append(f"| {row['feature']} | {row['VIF']:.2f} |")
    
    # 特征重要性
    if not importance.empty:
        report_lines.extend([
            "",
            "## 4. Feature Importance (Random Forest)\n",
            "",
            "| Feature | Importance |",
            "|---------|------------|",
        ])
        for _, row in importance.head(10).iterrows():
            report_lines.append(f"| {row['feature']} | {row['importance']:.4f} |")
    
    report_lines.extend([
        "",
        "## 5. Output Files\n",
        "",
        "- `ch04_engineered_features.csv` - 日频特征表\n",
        "- `ch04_feature_importance.csv` - 特征重要性排序\n",
        "- `ch04_correlation_heatmap.png` - 特征相关性热力图\n",
        "- `ch04_feature_distribution.png` - 特征分布图\n",
    ])
    
    report_content = "\n".join(report_lines)
    report_path = os.path.join(OUTPUT_DIR, "ch04_feature_engineering_report.md")
    Path(report_path).write_text(report_content, encoding="utf-8")
    logger.info(f"  报告已保存: {report_path}")


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    """主函数：执行 ch04 全部分析步骤."""
    logger.info("=" * 60)
    logger.info("ch04 特征工程 — 开始执行")
    logger.info("=" * 60)
    
    # Step 1: 数据合并
    df = load_and_merge_data()
    
    # Step 2-7: 构造七类特征
    sentiment_features = construct_sentiment_features(df)
    topic_features = construct_topic_features(df)
    impact_features = construct_impact_features(df)
    text_features = construct_text_features(df)
    
    # 创建完整的日期索引
    date_range = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    time_features = construct_time_features(date_range)
    cross_features = construct_cross_features(df)
    
    # 合并所有特征
    logger.info("合并所有特征...")
    features = time_features.copy()
    features = features.join(sentiment_features, how="left")
    features = features.join(topic_features, how="left")
    features = features.join(impact_features, how="left")
    features = features.join(text_features, how="left")
    features = features.join(cross_features, how="left")
    
    # 前向填充缺失值
    features = features.ffill().bfill().fillna(0)
    
    total_features = len([c for c in features.columns if c != "date"])
    logger.info(f"特征合并完成: {len(features)} 行 x {total_features} 列")
    
    # 保存特征数据
    features.to_csv(os.path.join(OUTPUT_DIR, "ch04_engineered_features.csv"))
    logger.info(f"特征数据已保存: {OUTPUT_DIR}/ch04_engineered_features.csv")
    
    # Step 8: VIF 分析
    vif_data = calculate_vif(features)
    
    # Step 9: 特征重要性
    importance = calculate_feature_importance(features)
    if not importance.empty:
        importance.to_csv(os.path.join(OUTPUT_DIR, "ch04_feature_importance.csv"), index=False)
    
    # Step 10: 可视化与报告
    plot_correlation_heatmap(features)
    plot_feature_distribution(features)
    generate_report(features, vif_data, importance, total_features)
    
    logger.info("\n" + "=" * 60)
    logger.info(f"ch04 完成。产物已输出到: {OUTPUT_DIR}")
    logger.info(f"总特征数: {total_features}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
