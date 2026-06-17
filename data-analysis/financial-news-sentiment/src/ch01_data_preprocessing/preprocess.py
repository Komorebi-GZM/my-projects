#!/usr/bin/env python3
"""数据预处理主脚本.

本脚本对原始金融新闻数据进行全面的清洗和预处理，包括：
1. 日期解析与验证
2. categories 字段拆分（多分类 -> 多行）
3. matched_keywords 字段拆分
4. 文本清洗（title + description 合并为 full_text，去除特殊字符）
5. 数据类型优化（category 类型、内存优化）
6. 重复检测与去重
7. 异常值检测（relevance_score, impact_tier）
8. 保存清洗后数据

Usage:
    # 运行完整预处理流程
    python -m src.ch01_data_preprocessing.preprocess

    # 从项目根目录运行
    python src/ch01_data_preprocessing/preprocess.py

Output:
    outputs/ch01_data_preprocessing/
        ch01_cleaned_data.csv          - 清洗后的数据
        ch01_data_quality_report.md    - 数据质量报告
        ch01_missing_values_summary.csv - 缺失值汇总
        ch01_duplicates.csv            - 重复记录

Author:
    financial_news_sentiment_analysis project
"""

from __future__ import annotations

import logging
import re
import warnings
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

# 将项目根目录添加到 sys.path
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.utils.config import (
    MATPLOTLIB_RC_PARAMS,
    setup_logging,
)
from src.utils.data_loader import load_raw_data
from src.utils.output_manager import OutputManager

# =============================================================================
# 初始化
# =============================================================================
# 配置 matplotlib
import matplotlib
matplotlib.rcParams.update(MATPLOTLIB_RC_PARAMS)

# 配置日志
logger = setup_logging(__name__, log_to_file=True)

# 忽略警告
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# 输出管理器
output_mgr = OutputManager("ch01_data_preprocessing")


# =============================================================================
# Step 1: 日期解析与验证
# =============================================================================
def parse_and_validate_dates(
    df: pd.DataFrame,
    date_col: str = "date",
) -> pd.DataFrame:
    """解析并验证日期列.

    将日期列转换为 datetime 类型，检查日期范围合理性，
    标记无效日期并记录日志.

    Args:
        df: 原始 DataFrame.
        date_col: 日期列名，默认为 'date'.

    Returns:
        处理后的 DataFrame（原地修改）.
    """
    logger.info("=" * 60)
    logger.info("Step 1: 日期解析与验证")
    logger.info("=" * 60)

    if date_col not in df.columns:
        logger.warning("日期列 '%s' 不存在，跳过日期解析", date_col)
        date_candidates = [c for c in df.columns if "date" in c.lower()]
        if date_candidates:
            logger.info("检测到可能的日期列: %s", date_candidates)
            date_col = date_candidates[0]
        else:
            logger.error("未找到日期列，请手动指定")
            return df

    # 解析日期
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    # 统计解析结果
    total: int = len(df)
    valid: int = int(df[date_col].notna().sum())
    invalid: int = total - valid
    logger.info("日期解析结果: 有效 %d / 总计 %d (无效: %d)",
                valid, total, invalid)

    if invalid > 0:
        logger.warning("存在 %d 条无效日期记录", invalid)
        # 删除无效日期行
        df = df.dropna(subset=[date_col]).reset_index(drop=True)
        logger.info("已删除无效日期行，剩余 %d 行", len(df))

    # 日期范围验证（数据集预期 2016-2026）
    min_date = df[date_col].min()
    max_date = df[date_col].max()
    logger.info("日期范围: %s ~ %s", min_date.date(), max_date.date())

    # 提取时间特征（便于后续分析）
    df["year"] = df[date_col].dt.year
    df["month"] = df[date_col].dt.month
    df["day"] = df[date_col].dt.day
    df["day_of_week"] = df[date_col].dt.dayofweek  # 0=Monday
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    logger.info("已提取时间特征: year, month, day, day_of_week, is_weekend")

    return df


# =============================================================================
# Step 2: categories 字段拆分
# =============================================================================
def split_categories(
    df: pd.DataFrame,
    cat_col: str = "categories",
) -> pd.DataFrame:
    """拆分 categories 字段（多分类 -> 多行）.

    将单个新闻的多个分类标签拆分为多行，便于后续分类统计.
    注意：本步骤不实际拆分行（保留原始行），而是新增 categories_list 列
    用于后续分析.

    Args:
        df: 输入 DataFrame.
        cat_col: 分类字段名，默认为 'categories'.

    Returns:
        处理后的 DataFrame.
    """
    logger.info("=" * 60)
    logger.info("Step 2: categories 字段处理")
    logger.info("=" * 60)

    if cat_col not in df.columns:
        logger.warning("分类列 '%s' 不存在，跳过", cat_col)
        return df

    original_rows: int = len(df)

    # 统计原始分类信息
    multi_cat_count: int = int(df[cat_col].str.contains("\\|", na=False).sum())
    logger.info("含多个分类的新闻数: %d / %d (%.1f%%)",
                multi_cat_count, original_rows,
                multi_cat_count / original_rows * 100)

    # 新增 categories_list 列（拆分为列表）
    # 先转为 str 避免 category 类型导致 unhashable type 错误
    df["categories_list"] = df[cat_col].astype(str).apply(
        lambda x: [c.strip() for c in x.split("|")] if x != "nan" and x else []
    )

    # 新增 category_count 列（分类数量）
    df["category_count"] = df["categories_list"].apply(len)

    logger.info("分类数量分布:")
    cat_count_dist = df["category_count"].value_counts().sort_index()
    for cnt, num in cat_count_dist.items():
        logger.info("  %d 个分类: %d 条新闻", cnt, num)

    # 统计所有唯一分类
    all_categories: List[str] = []
    for cats in df["categories_list"]:
        all_categories.extend(cats)
    unique_cats = sorted(set(all_categories))
    logger.info("唯一分类总数: %d", len(unique_cats))
    logger.info("Top 10 分类: %s", unique_cats[:10])

    return df


# =============================================================================
# Step 3: matched_keywords 字段拆分
# =============================================================================
def split_matched_keywords(
    df: pd.DataFrame,
    kw_col: str = "matched_keywords",
) -> pd.DataFrame:
    """处理 matched_keywords 字段.

    将匹配的关键词列表拆分为列表形式，便于关键词频率统计.

    Args:
        df: 输入 DataFrame.
        kw_col: 关键词字段名，默认为 'matched_keywords'.

    Returns:
        处理后的 DataFrame.
    """
    logger.info("=" * 60)
    logger.info("Step 3: matched_keywords 字段处理")
    logger.info("=" * 60)

    if kw_col not in df.columns:
        logger.warning("关键词列 '%s' 不存在，跳过", kw_col)
        return df

    # 新增 keywords_list 列
    df["keywords_list"] = df[kw_col].astype(str).apply(
        lambda x: [k.strip() for k in x.split("|")] if x != "nan" and x else []
    )

    # 新增 keyword_count 列
    df["keyword_count"] = df["keywords_list"].apply(len)

    logger.info("关键词数量分布:")
    kw_count_dist = df["keyword_count"].value_counts().sort_index()
    for cnt, num in kw_count_dist.head(10).items():
        logger.info("  %d 个关键词: %d 条新闻", cnt, num)

    # 统计所有唯一关键词
    all_keywords: List[str] = []
    for kws in df["keywords_list"]:
        all_keywords.extend(kws)
    unique_kws = sorted(set(all_keywords))
    logger.info("唯一关键词总数: %d", len(unique_kws))
    logger.info("Top 15 关键词: %s", unique_kws[:15])

    return df


# =============================================================================
# Step 4: 文本清洗
# =============================================================================
def clean_text(text: str) -> str:
    """清洗单条文本.

    去除特殊字符、多余空格、HTML标签等.

    Args:
        text: 原始文本字符串.

    Returns:
        清洗后的文本字符串.
    """
    if not isinstance(text, str) or pd.isna(text):
        return ""

    # 去除 HTML 标签
    text = re.sub(r"<[^>]+>", "", text)

    # 去除 URL
    text = re.sub(r"https?://\S+|www\.\S+", "", text)

    # 去除多余空白字符（保留基本空格）
    text = re.sub(r"[\t\r\n]+", " ", text)

    # 去除多余空格
    text = re.sub(r" +", " ", text).strip()

    return text


def merge_and_clean_text(
    df: pd.DataFrame,
    title_col: str = "title",
    desc_col: str = "description",
    output_col: str = "full_text",
) -> pd.DataFrame:
    """合并 title + description 为 full_text 并清洗.

    将新闻标题和描述合并为一个完整文本字段，并进行清洗.

    Args:
        df: 输入 DataFrame.
        title_col: 标题列名，默认为 'title'.
        desc_col: 描述列名，默认为 'description'.
        output_col: 输出列名，默认为 'full_text'.

    Returns:
        添加了 full_text 列的 DataFrame.
    """
    logger.info("=" * 60)
    logger.info("Step 4: 文本清洗（title + description -> full_text）")
    logger.info("=" * 60)

    missing_cols: List[str] = []
    if title_col not in df.columns:
        missing_cols.append(title_col)
    if desc_col not in df.columns:
        missing_cols.append(desc_col)

    if missing_cols:
        logger.warning("文本列 %s 不存在，跳过文本合并", missing_cols)
        return df

    # 合并标题和描述
    df[output_col] = (
        df[title_col].fillna("").astype(str)
        + " . "
        + df[desc_col].fillna("").astype(str)
    )

    # 清洗文本
    df[output_col] = df[output_col].apply(clean_text)

    # 新增文本长度统计列
    df["text_length"] = df[output_col].str.len()
    df["title_length"] = df[title_col].str.len()
    df["desc_length"] = df[desc_col].str.len()

    # 统计
    text_lengths = df["text_length"]
    logger.info("文本清洗完成:")
    logger.info("  平均文本长度: %.1f 字符", text_lengths.mean())
    logger.info("  中位文本长度: %.1f 字符", text_lengths.median())
    logger.info("  最短文本: %d 字符", text_lengths.min())
    logger.info("  最长文本: %d 字符", text_lengths.max())
    logger.info("  空文本数量: %d", (text_lengths == 0).sum())

    # 标记异常短文本（< 20 字符）
    short_text_mask = df["text_length"] < 20
    logger.info("  异常短文本 (<20字符): %d 条", short_text_mask.sum())

    return df


# =============================================================================
# Step 5: 数据类型优化
# =============================================================================
def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """优化数据类型以减少内存占用.

    将低基数的字符串列转为 category 类型，
    将数值列转为最小可表示类型.

    Args:
        df: 输入 DataFrame.

    Returns:
        类型优化后的 DataFrame（原地修改）.
    """
    logger.info("=" * 60)
    logger.info("Step 5: 数据类型优化")
    logger.info("=" * 60)

    original_mem: float = df.memory_usage(deep=True).sum() / 1024**2

    # impact_tier 转为有序 category
    if "impact_tier" in df.columns:
        tier_order = pd.CategoricalDtype(
            categories=["LOW", "MEDIUM", "HIGH"], ordered=True
        )
        df["impact_tier"] = df["impact_tier"].astype(tier_order)
        logger.info("  impact_tier 转为有序 category (LOW < MEDIUM < HIGH)")

    # has_negation 确认为 bool
    if "has_negation" in df.columns:
        df["has_negation"] = df["has_negation"].astype(bool)

    # relevance_score 优化
    if "relevance_score" in df.columns:
        df["relevance_score"] = pd.to_numeric(
            df["relevance_score"], downcast="integer"
        )

    # source_file 转 category
    if "source_file" in df.columns:
        df["source_file"] = df["source_file"].astype("category")
        logger.info("  source_file 转为 category")

    # categories 转 category
    if "categories" in df.columns:
        df["categories"] = df["categories"].astype("category")

    # year, month, day 转为 category（低基数）
    for col in ["year", "month", "day", "day_of_week"]:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # url 列：标记 URL_NOT_AVAILABLE
    if "url" in df.columns:
        df["url_available"] = (df["url"] != "URL_NOT_AVAILABLE").astype(int)
        df["url"] = df["url"].astype("category")
        logger.info("  新增 url_available 列（0=不可用, 1=可用）")

    optimized_mem: float = df.memory_usage(deep=True).sum() / 1024**2
    reduction: float = (
        (1 - optimized_mem / original_mem) * 100 if original_mem > 0 else 0
    )
    logger.info("内存优化: %.2f MB -> %.2f MB (节省 %.1f%%)",
                original_mem, optimized_mem, reduction)

    return df


# =============================================================================
# Step 6: 重复检测与去重
# =============================================================================
def detect_and_remove_duplicates(
    df: pd.DataFrame,
    subset: Optional[List[str]] = None,
    keep: str = "first",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """检测并去除重复记录.

    Args:
        df: 输入 DataFrame.
        subset: 用于判断重复的列名列表. None 表示使用所有列.
        keep: 保留策略，'first' / 'last' / False.

    Returns:
        元组 (去重后的 DataFrame, 重复记录 DataFrame).
    """
    logger.info("=" * 60)
    logger.info("Step 6: 重复检测与去重")
    logger.info("=" * 60)

    original_rows: int = len(df)

    # 使用 title + date + source_file 作为去重依据
    if subset is None:
        subset = ["title", "date", "source_file"]
        # 确保列存在
        subset = [c for c in subset if c in df.columns]
        logger.info("去重依据列: %s", subset)

    duplicates = df[df.duplicated(subset=subset, keep=keep)]
    df_dedup = df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)

    removed_count: int = original_rows - len(df_dedup)
    logger.info("重复检测: 原始 %d 行, 重复 %d 行, 去重后 %d 行",
                original_rows, len(duplicates), len(df_dedup))

    if removed_count > 0:
        logger.info("去重比例: %.2f%%", removed_count / original_rows * 100)

    return df_dedup, duplicates


# =============================================================================
# Step 7: 异常值检测
# =============================================================================
def detect_outliers(
    df: pd.DataFrame,
    score_col: str = "relevance_score",
    tier_col: str = "impact_tier",
) -> pd.DataFrame:
    """检测数值型字段的异常值.

    检查 relevance_score 和 impact_tier 等字段的取值范围，
    标记超出合理范围的记录.

    Args:
        df: 输入 DataFrame.
        score_col: 相关性评分列名.
        tier_col: 影响等级列名.

    Returns:
        添加了异常标记的 DataFrame.
    """
    logger.info("=" * 60)
    logger.info("Step 7: 异常值检测")
    logger.info("=" * 60)

    # 检查 relevance_score
    if score_col in df.columns:
        scores = df[score_col].astype(float)
        logger.info("字段 '%s' 统计:", score_col)
        logger.info("  均值: %.4f", scores.mean())
        logger.info("  标准差: %.4f", scores.std())
        logger.info("  最小值: %.0f", scores.min())
        logger.info("  25%%分位: %.0f", scores.quantile(0.25))
        logger.info("  中位数: %.0f", scores.median())
        logger.info("  75%%分位: %.0f", scores.quantile(0.75))
        logger.info("  最大值: %.0f", scores.max())

        # IQR 异常检测
        q1 = scores.quantile(0.25)
        q3 = scores.quantile(0.75)
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr
        outlier_count = int((scores > upper_bound).sum())
        logger.info("  IQR 上界: %.1f, 超界记录: %d 条", upper_bound, outlier_count)

        # 标记高分异常（relevance_score > 8 为罕见高分）
        high_score_mask = scores > 8
        if high_score_mask.sum() > 0:
            logger.info("  高分异常 (score>8): %d 条", high_score_mask.sum())

    # 检查 impact_tier
    if tier_col in df.columns:
        logger.info("字段 '%s' 分布:", tier_col)
        tier_counts = df[tier_col].value_counts().sort_index()
        for tier, count in tier_counts.items():
            pct = count / len(df) * 100
            logger.info("  %s: %d (%.1f%%)", tier, count, pct)

    # 检查文本长度异常
    if "text_length" in df.columns:
        text_len = df["text_length"]
        logger.info("文本长度异常:")
        logger.info("  空文本 (len=0): %d 条", (text_len == 0).sum())
        logger.info("  超长文本 (len>2000): %d 条", (text_len > 2000).sum())

    logger.info("异常值检测完成")

    return df


# =============================================================================
# Step 8: 保存清洗后数据
# =============================================================================
def save_cleaned_data(
    df: pd.DataFrame,
    duplicates: Optional[pd.DataFrame] = None,
) -> None:
    """保存清洗后的数据和数据质量报告.

    Args:
        df: 清洗后的 DataFrame.
        duplicates: 重复记录 DataFrame（可选）.
    """
    logger.info("=" * 60)
    logger.info("Step 8: 保存清洗后数据")
    logger.info("=" * 60)

    # 保存清洗后的主数据
    output_mgr.save_dataframe(df, "ch01_cleaned_data.csv")
    logger.info("清洗后数据已保存: %d 行 x %d 列",
                df.shape[0], df.shape[1])

    # 保存重复记录（如有）
    if duplicates is not None and len(duplicates) > 0:
        output_mgr.save_dataframe(duplicates, "ch01_duplicates.csv")
        logger.info("重复记录已保存: %d 条", len(duplicates))

    # 保存缺失值汇总
    missing_summary = df.isnull().sum().reset_index()
    missing_summary.columns = ["column", "missing_count"]
    missing_summary["missing_pct"] = (
        missing_summary["missing_count"] / len(df) * 100
    ).round(2)
    missing_summary = missing_summary.sort_values(
        "missing_count", ascending=False
    )
    output_mgr.save_dataframe(missing_summary, "ch01_missing_values_summary.csv")

    # 保存分类统计
    cat_stats = _generate_category_stats(df)
    output_mgr.save_dataframe(cat_stats, "ch01_category_statistics.csv")

    # 保存关键词统计
    kw_stats = _generate_keyword_stats(df)
    output_mgr.save_dataframe(kw_stats, "ch01_keyword_statistics.csv")

    # 生成数据质量报告
    report = generate_quality_report(df, duplicates)
    output_mgr.save_markdown(report, "ch01_data_quality_report.md")

    logger.info("所有产物已保存到: %s", output_mgr.output_dir)


def _generate_category_stats(df: pd.DataFrame) -> pd.DataFrame:
    """生成分类统计表.

    Args:
        df: 清洗后的 DataFrame.

    Returns:
        分类统计 DataFrame.
    """
    if "categories_list" not in df.columns:
        return pd.DataFrame()

    # 展开所有分类
    all_cats: List[str] = []
    for cats in df["categories_list"]:
        all_cats.extend(cats)

    cat_series = pd.Series(all_cats)
    cat_stats = cat_series.value_counts().reset_index()
    cat_stats.columns = ["category", "count"]
    cat_stats["percentage"] = (cat_stats["count"] / len(df) * 100).round(2)
    return cat_stats


def _generate_keyword_stats(df: pd.DataFrame) -> pd.DataFrame:
    """生成关键词统计表.

    Args:
        df: 清洗后的 DataFrame.

    Returns:
        关键词统计 DataFrame.
    """
    if "keywords_list" not in df.columns:
        return pd.DataFrame()

    # 展开所有关键词
    all_kws: List[str] = []
    for kws in df["keywords_list"]:
        all_kws.extend(kws)

    kw_series = pd.Series(all_kws)
    kw_stats = kw_series.value_counts().head(50).reset_index()
    kw_stats.columns = ["keyword", "count"]
    kw_stats["percentage"] = (kw_stats["count"] / len(df) * 100).round(2)
    return kw_stats


def generate_quality_report(
    df: pd.DataFrame,
    duplicates: Optional[pd.DataFrame] = None,
) -> str:
    """生成数据质量报告（Markdown格式）.

    Args:
        df: 清洗后的 DataFrame.
        duplicates: 重复记录 DataFrame.

    Returns:
        Markdown 格式的报告字符串.
    """
    lines: List[str] = [
        "# 数据质量报告 — ch01 数据预处理",
        "",
        "> 本报告由 `preprocess.py` 自动生成",
        "",
        "## 1. 概述",
        "",
        f"| 指标 | 值 |",
        f"|------|-----|",
        f"| **总记录数** | {len(df):,} |",
        f"| **总列数** | {len(df.columns)} |",
        f"| **内存占用** | {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB |",
        f"| **日期范围** | {df['date'].min().date()} ~ {df['date'].max().date()} |",
        f"| **唯一分类数** | {df['categories'].nunique()} |",
        f"| **唯一关键词数** | {len(set(k for ks in df['keywords_list'] for k in ks))} |",
        "",
        "## 2. 列信息",
        "",
        "| 列名 | 数据类型 | 非空数 | 缺失率 | 唯一值数 | 示例值 |",
        "|------|----------|--------|--------|----------|--------|",
    ]

    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = int(df[col].notna().sum())
        missing_rate = (1 - non_null / len(df)) * 100
        # 跳过 list 类型列的 nunique 计算
        if dtype == "object":
            first_val = df[col].dropna().iloc[0] if non_null > 0 else None
            if isinstance(first_val, list):
                nunique = len(df)
            else:
                nunique = df[col].nunique()
        else:
            nunique = df[col].nunique()
        # 获取示例值
        sample_vals = df[col].dropna().head(2).astype(str).tolist()
        sample_str = ", ".join(sample_vals[:2])
        if len(sample_str) > 40:
            sample_str = sample_str[:37] + "..."
        lines.append(
            f"| {col} | {dtype} | {non_null:,} | "
            f"{missing_rate:.1f}% | {nunique:,} | {sample_str} |"
        )

    # 数据类型分布
    lines.extend(["", "## 3. 数据类型分布", ""])
    dtype_counts = df.dtypes.apply(str).value_counts()
    for dtype, count in dtype_counts.items():
        lines.append(f"- **{dtype}**: {count} 列")

    # 影响等级分布
    if "impact_tier" in df.columns:
        lines.extend(["", "## 4. 影响等级分布", ""])
        lines.append("| 等级 | 数量 | 占比 |")
        lines.append("|------|------|------|")
        for tier in ["LOW", "MEDIUM", "HIGH"]:
            count = int((df["impact_tier"] == tier).sum())
            pct = count / len(df) * 100
            lines.append(f"| {tier} | {count:,} | {pct:.1f}% |")

    # 否定标记统计
    if "has_negation" in df.columns:
        neg_count = int(df["has_negation"].sum())
        lines.extend(["", "## 5. 否定标记统计", ""])
        lines.append(f"- 含否定表述的新闻: **{neg_count}** 条 ({neg_count/len(df)*100:.2f}%)")

    # 文本长度统计
    if "text_length" in df.columns:
        lines.extend(["", "## 6. 文本长度统计", ""])
        tl = df["text_length"]
        lines.append(f"| 指标 | 值 |")
        lines.append(f"|------|-----|")
        lines.append(f"| 平均长度 | {tl.mean():.1f} 字符 |")
        lines.append(f"| 中位长度 | {tl.median():.1f} 字符 |")
        lines.append(f"| 最短 | {tl.min()} 字符 |")
        lines.append(f"| 最长 | {tl.max()} 字符 |")
        lines.append(f"| 空文本 | {(tl == 0).sum()} 条 |")

    # 相关性评分统计
    if "relevance_score" in df.columns:
        rs = df["relevance_score"].astype(float)
        lines.extend(["", "## 7. 相关性评分统计", ""])
        lines.append(f"| 指标 | 值 |")
        lines.append(f"|------|-----|")
        lines.append(f"| 均值 | {rs.mean():.2f} |")
        lines.append(f"| 标准差 | {rs.std():.2f} |")
        lines.append(f"| 最小值 | {rs.min():.0f} |")
        lines.append(f"| 中位数 | {rs.median():.0f} |")
        lines.append(f"| 最大值 | {rs.max():.0f} |")

    # 重复记录
    if duplicates is not None and len(duplicates) > 0:
        lines.extend([
            "",
            "## 8. 重复记录",
            "",
            f"- **检测到的重复记录数**: {len(duplicates):,}",
            f"- **去重依据**: title + date + source_file",
        ])

    # 数据来源统计
    if "source_file" in df.columns:
        lines.extend(["", "## 9. 数据来源统计", ""])
        lines.append("| 来源文件 | 记录数 | 占比 |")
        lines.append("|----------|--------|------|")
        src_counts = df["source_file"].value_counts()
        for src, count in src_counts.items():
            pct = count / len(df) * 100
            lines.append(f"| {src} | {count:,} | {pct:.1f}% |")

    # 时间分布
    if "year" in df.columns:
        lines.extend(["", "## 10. 年度分布", ""])
        lines.append("| 年份 | 记录数 | 占比 |")
        lines.append("|------|--------|------|")
        year_counts = df["year"].value_counts().sort_index()
        for year, count in year_counts.items():
            pct = count / len(df) * 100
            lines.append(f"| {year} | {count:,} | {pct:.1f}% |")

    lines.extend([
        "",
        "---",
        "",
        f"*报告生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
    ])

    return "\n".join(lines)


# =============================================================================
# 主流程
# =============================================================================
def main() -> None:
    """数据预处理主流程.

    按顺序执行以下步骤:
    1. 加载原始数据
    2. 日期解析与验证
    3. categories 字段处理
    4. matched_keywords 字段处理
    5. 文本清洗
    6. 数据类型优化
    7. 重复检测与去重
    8. 异常值检测
    9. 保存清洗后数据
    """
    logger.info("=" * 60)
    logger.info("金融新闻数据预处理 - 开始")
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # 加载原始数据
    # ------------------------------------------------------------------
    logger.info("加载原始数据...")
    try:
        df = load_raw_data()
    except FileNotFoundError as e:
        logger.error("无法加载原始数据: %s", e)
        return
    except Exception as e:
        logger.error("加载数据时发生错误: %s", e)
        return

    logger.info("原始数据: %d 行 x %d 列", df.shape[0], df.shape[1])
    logger.info("列名: %s", df.columns.tolist())

    # ------------------------------------------------------------------
    # Step 1: 日期解析与验证
    # ------------------------------------------------------------------
    df = parse_and_validate_dates(df)

    # ------------------------------------------------------------------
    # Step 2: categories 字段处理
    # ------------------------------------------------------------------
    df = split_categories(df)

    # ------------------------------------------------------------------
    # Step 3: matched_keywords 字段处理
    # ------------------------------------------------------------------
    df = split_matched_keywords(df)

    # ------------------------------------------------------------------
    # Step 4: 文本清洗
    # ------------------------------------------------------------------
    df = merge_and_clean_text(df)

    # ------------------------------------------------------------------
    # Step 5: 数据类型优化
    # ------------------------------------------------------------------
    df = optimize_dtypes(df)

    # ------------------------------------------------------------------
    # Step 6: 重复检测与去重
    # ------------------------------------------------------------------
    df, duplicates = detect_and_remove_duplicates(df)

    # ------------------------------------------------------------------
    # Step 7: 异常值检测
    # ------------------------------------------------------------------
    df = detect_outliers(df)

    # ------------------------------------------------------------------
    # Step 8: 保存清洗后数据
    # ------------------------------------------------------------------
    save_cleaned_data(df, duplicates)

    logger.info("=" * 60)
    logger.info("金融新闻数据预处理 - 完成")
    logger.info("最终数据: %d 行 x %d 列", df.shape[0], df.shape[1])
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
