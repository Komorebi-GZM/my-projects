#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt-02: 热度分析
对清洗后的游戏数据进行热度指标分析，揭示热度分布特征与头部效应。

覆盖步骤:
  - Step 02.1: 加载清洗后数据
  - Step 02.2: 热度指标基本统计
  - Step 02.3: 热度分布分析（直方图 + 箱线图）
  - Step 02.4: 头部效应分析（Pareto 原则验证）
  - Step 02.5: Top N 游戏排名
  - Step 02.6: 热度指标相关性分析
  - Step 02.7: 热度报告生成与保存

产物输出到: outputs/ch02_popularity_analysis/
"""

import sys
import os
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime

# ---------------------------------------------------------------------------
# 路径设置
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

from utils.config import PROJECT_ROOT, OUTPUT_BASE, PLT_STYLE
from utils.data_loader import load_cleaned_data
from utils.output_manager import get_chapter_dir, save_dataframe, save_figure, save_report

# ---------------------------------------------------------------------------
# 可视化全局样式
# ---------------------------------------------------------------------------
for _k, _v in PLT_STYLE.items():
    plt.rcParams[_k] = _v

# ---------------------------------------------------------------------------
# 日志配置
# ---------------------------------------------------------------------------
OUTPUT_DIR = get_chapter_dir('ch02')
OUTPUT_LOG = os.path.join(OUTPUT_DIR, 'ch02_popularity_analysis.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(OUTPUT_LOG, mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


# ============================================================
# 核心分析函数
# ============================================================

def calc_basic_stats(df: pd.DataFrame, col: str) -> dict:
    """计算单列基本统计量"""
    vals = df[col].dropna()
    return {
        'min': vals.min(), 'max': vals.max(),
        'mean': vals.mean(), 'median': vals.median(),
        'std': vals.std(), 'q25': vals.quantile(0.25),
        'q75': vals.quantile(0.75),
    }


def plot_likes_distribution(df: pd.DataFrame, output_dir: str) -> str:
    """绘制点赞数分布图（直方图 + 箱线图）"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 直方图（对数坐标）
    likes_log = np.log1p(df['likes'].fillna(0).astype(float))
    axes[0].hist(likes_log, bins=50, color='steelblue', edgecolor='white', alpha=0.8)
    axes[0].set_xlabel('log1p(likes)')
    axes[0].set_ylabel('游戏数量')
    axes[0].set_title('点赞数分布（对数变换）')
    axes[0].grid(axis='y', alpha=0.3)

    # 箱线图（分平台）
    box_data = [
        df[df['source'] == 'poki']['likes'].fillna(0).astype(float),
        df[df['source'] == 'newgrounds']['likes'].fillna(0).astype(float),
    ]
    bp = axes[1].boxplot(box_data, tick_labels=['Poki', 'Newgrounds'], patch_artist=True)
    for patch, color in zip(bp['boxes'], ['#ff9999', '#66b3ff']):
        patch.set_facecolor(color)
    axes[1].set_ylabel('likes')
    axes[1].set_title('点赞数分布（分平台箱线图）')
    axes[1].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    return save_figure(fig, 'ch02_likes_distribution.png', output_dir)


def plot_like_ratio_distribution(df: pd.DataFrame, output_dir: str) -> str:
    """绘制点赞率分布图"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 点赞率直方图
    ratio = df['like_ratio'].dropna()
    axes[0].hist(ratio, bins=50, color='seagreen', edgecolor='white', alpha=0.8)
    axes[0].set_xlabel('like_ratio')
    axes[0].set_ylabel('游戏数量')
    axes[0].set_title('点赞率分布')
    axes[0].grid(axis='y', alpha=0.3)

    # 分平台点赞率箱线图
    box_data = [
        df[df['source'] == 'poki']['like_ratio'].dropna(),
        df[df['source'] == 'newgrounds']['like_ratio'].dropna(),
    ]
    bp = axes[1].boxplot(box_data, tick_labels=['Poki', 'Newgrounds'], patch_artist=True)
    for patch, color in zip(bp['boxes'], ['#ff9999', '#66b3ff']):
        patch.set_facecolor(color)
    axes[1].set_ylabel('like_ratio')
    axes[1].set_title('点赞率分布（分平台箱线图）')
    axes[1].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    return save_figure(fig, 'ch02_like_ratio_distribution.png', output_dir)


def plot_dislikes_vs_likes(df: pd.DataFrame, output_dir: str) -> str:
    """绘制点赞 vs 踩数散点图"""
    fig, ax = plt.subplots(figsize=(8, 6))

    colors = {'poki': '#ff6b6b', 'newgrounds': '#4ecdc4'}
    for source in ['poki', 'newgrounds']:
        subset = df[df['source'] == source]
        likes_log = np.log1p(subset['likes'].fillna(0).astype(float))
        dislikes_log = np.log1p(subset['dislikes'].fillna(0).astype(float))
        ax.scatter(likes_log, dislikes_log, c=colors[source],
                   label=source, alpha=0.4, s=10)

    ax.set_xlabel('log1p(likes)')
    ax.set_ylabel('log1p(dislikes)')
    ax.set_title('点赞数 vs 踩数散点图（分平台）')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    return save_figure(fig, 'ch02_likes_vs_dislikes.png', output_dir)


def plot_head_effect(df: pd.DataFrame, output_dir: str) -> str:
    """绘制头部效应分析图（累计占比曲线）"""
    fig, ax = plt.subplots(figsize=(10, 5))

    sorted_likes = df['likes'].fillna(0).astype(float).sort_values(ascending=False).values
    cumsum = np.cumsum(sorted_likes)
    cumsum_pct = cumsum / cumsum[-1] * 100
    x_pct = np.arange(1, len(cumsum_pct) + 1) / len(cumsum_pct) * 100

    ax.plot(x_pct, cumsum_pct, linewidth=2, color='darkorange')
    ax.axhline(y=80, color='gray', linestyle='--', alpha=0.5, label='80% 阈值')
    ax.axvline(x=20, color='gray', linestyle='--', alpha=0.5, label='20% 阈值')
    ax.set_xlabel('游戏占比 (%)')
    ax.set_ylabel('点赞累计占比 (%)')
    ax.set_title('头部效应分析 — 累计点赞占比曲线')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    return save_figure(fig, 'ch02_head_effect.png', output_dir)


def plot_top_games_bar(df: pd.DataFrame, output_dir: str, top_n: int = 20) -> str:
    """绘制 Top N 游戏点赞数柱状图"""
    top = df.nlargest(top_n, 'likes')[['name', 'likes', 'source']].copy()

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['#ff6b6b' if s == 'poki' else '#4ecdc4' for s in top['source']]
    bars = ax.barh(range(len(top)), top['likes'].values, color=colors, alpha=0.8)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top['name'].str[:25].tolist(), fontsize=9)
    ax.set_xlabel('likes')
    ax.set_title(f'Top {top_n} 游戏（按点赞数排序）')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)

    # 图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#ff6b6b', label='Poki'),
        Patch(facecolor='#4ecdc4', label='Newgrounds'),
    ]
    ax.legend(handles=legend_elements, loc='lower right')

    plt.tight_layout()
    return save_figure(fig, f'ch02_top{top_n}_games.png', output_dir)


def generate_stats_summary(df: pd.DataFrame, stats: dict) -> pd.DataFrame:
    """生成热度统计汇总表"""
    rows = []
    metrics = ['likes', 'dislikes', 'like_ratio', 'tag_count']
    for metric in metrics:
        s = stats.get(metric, {})
        rows.append({
            '指标': metric,
            '最小值': s.get('min', np.nan),
            '最大值': s.get('max', np.nan),
            '均值': round(s.get('mean', np.nan), 4),
            '中位数': round(s.get('median', np.nan), 4),
            '标准差': round(s.get('std', np.nan), 4),
            '25%分位': round(s.get('q25', np.nan), 4),
            '75%分位': round(s.get('q75', np.nan), 4),
        })
    return pd.DataFrame(rows)


def generate_report(df: pd.DataFrame, stats: dict, top_games: pd.DataFrame,
                    head_effect: dict, corr_matrix: pd.DataFrame,
                    platform_stats: dict) -> str:
    """生成热度分析 Markdown 报告"""
    report = f"""# 在线小游戏热度分析报告

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 数据源：`{stats.get('data_source', 'ch01_cleaned_online_gaming.csv')}`

## 1. 数据概况

| 指标 | 值 |
|------|------|
| 分析游戏总数 | {len(df)} |
| Poki 平台 | {int((df['source'] == 'poki').sum())} |
| Newgrounds 平台 | {int((df['source'] == 'newgrounds').sum())} |
| 点赞总数 | {int(df['likes'].sum())} |
| 踩总数 | {int(df['dislikes'].sum())} |

## 2. 热度指标基本统计

"""
    report += "| 指标 | 最小值 | 最大值 | 均值 | 中位数 | 标准差 | 25%分位 | 75%分位 |\n"
    report += "|------|--------|--------|------|--------|--------|---------|---------|\n"
    for metric in ['likes', 'dislikes', 'like_ratio', 'tag_count']:
        s = stats.get(metric, {})
        report += f"| {metric} | {s.get('min', '')} | {s.get('max', '')} | {round(s.get('mean', 0), 2)} | {round(s.get('median', 0), 2)} | {round(s.get('std', 0), 2)} | {round(s.get('q25', 0), 2)} | {round(s.get('q75', 0), 2)} |\n"

    # 分平台统计
    report += f"""
## 3. 分平台统计

| 平台 | 游戏数 | 点赞均值 | 点赞中位数 | 踩均值 | 踩中位数 | 点赞率均值 |
|------|--------|----------|------------|--------|----------|-----------|
"""
    for src in ['poki', 'newgrounds']:
        ps = platform_stats.get(src, {})
        report += f"| {src} | {ps.get('count', 0)} | {round(ps.get('likes_mean', 0), 2)} | {round(ps.get('likes_median', 0), 2)} | {round(ps.get('dislikes_mean', 0), 2)} | {round(ps.get('dislikes_median', 0), 2)} | {round(ps.get('like_ratio_mean', 0), 4)} |\n"

    # 头部效应
    report += f"""
## 4. 头部效应分析

| 指标 | 值 |
|------|------|
| Top 1% 游戏点赞占比 | {head_effect.get('top_1_pct', 0):.1f}% |
| Top 5% 游戏点赞占比 | {head_effect.get('top_5_pct', 0):.1f}% |
| Top 10% 游戏点赞占比 | {head_effect.get('top_10_pct', 0):.1f}% |
| Top 20% 游戏点赞占比 | {head_effect.get('top_20_pct', 0):.1f}% |
| 80% 点赞所需游戏占比 | {head_effect.get('pct_for_80', 0):.1f}% |
| Gini 系数（近似） | {head_effect.get('gini_approx', 0):.4f} |

## 5. Top 20 游戏排名

| 排名 | 游戏名称 | 平台 | 点赞数 | 踩数 | 点赞率 | 标签数 |
|------|----------|------|--------|------|--------|--------|
"""
    for i, (_, row) in enumerate(top_games.head(20).iterrows(), 1):
        report += f"| {i} | {row['name'][:30]} | {row['source']} | {int(row['likes'])} | {int(row['dislikes'])} | {row.get('like_ratio', 0):.4f} | {int(row.get('tag_count', 0))} |\n"

    # 相关性矩阵
    report += f"""
## 6. 指标相关性分析

| 指标 | likes | dislikes | log_likes | like_ratio | tag_count |
|------|-------|----------|-----------|------------|-----------|
"""
    for col1 in ['likes', 'dislikes', 'log_likes', 'like_ratio', 'tag_count']:
        if col1 not in corr_matrix.columns:
            continue
        vals = ' | '.join(
            f"{corr_matrix.loc[col1, col2]:.4f}" if col2 in corr_matrix.columns else '-'
            for col2 in ['likes', 'dislikes', 'log_likes', 'like_ratio', 'tag_count']
            if col2 in corr_matrix.columns
        )
        report += f"| {col1} | {vals} |\n"

    report += f"""
## 7. 输出产物清单

| 文件 | 说明 |
|------|------|
| `ch02_popularity_stats.csv` | 热度指标统计表 |
| `ch02_likes_distribution.png` | 点赞数分布图 |
| `ch02_like_ratio_distribution.png` | 点赞率分布图 |
| `ch02_likes_vs_dislikes.png` | 点赞 vs 踩散点图 |
| `ch02_head_effect.png` | 头部效应分析图 |
| `ch02_top20_games.png` | Top 20 游戏柱状图 |
| `ch02_popularity_analysis_report.md` | 本文档 |
"""
    return report


# ============================================================
# 主函数
# ============================================================

def main():
    """Prompt-02 主函数：执行热度分析全流程"""
    logger.info("=" * 60)
    logger.info("Prompt-02: 热度分析 - 开始执行")
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # Step 02.1: 加载清洗后数据
    # ------------------------------------------------------------------
    logger.info("Step 02.1: 加载清洗后数据")
    df = load_cleaned_data()
    logger.info(f"数据加载完成: {len(df)} 行 x {len(df.columns)} 列")

    # 数值列保证 float 类型
    for col in ['likes', 'dislikes']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)
    for col in ['log_likes', 'log_dislikes', 'like_ratio']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    stats = {'data_source': 'ch01_cleaned_online_gaming.csv'}

    # ------------------------------------------------------------------
    # Step 02.2: 热度指标基本统计
    # ------------------------------------------------------------------
    logger.info("Step 02.2: 热度指标基本统计")
    for metric in ['likes', 'dislikes', 'like_ratio', 'tag_count']:
        stats[metric] = calc_basic_stats(df, metric)
        logger.info(f"  {metric}: mean={stats[metric]['mean']:.2f}, median={stats[metric]['median']:.2f}")

    # 分平台统计
    platform_stats = {}
    for src in ['poki', 'newgrounds']:
        sub = df[df['source'] == src]
        platform_stats[src] = {
            'count': len(sub),
            'likes_mean': sub['likes'].mean(),
            'likes_median': sub['likes'].median(),
            'dislikes_mean': sub['dislikes'].mean(),
            'dislikes_median': sub['dislikes'].median(),
            'like_ratio_mean': sub['like_ratio'].mean(),
        }
        logger.info(f"  {src}: {len(sub)} 款游戏, 点赞均值 {platform_stats[src]['likes_mean']:.0f}")

    # ------------------------------------------------------------------
    # Step 02.3: 热度分布分析
    # ------------------------------------------------------------------
    logger.info("Step 02.3: 热度分布分析 - 生成图表")
    fig_likes = plot_likes_distribution(df, OUTPUT_DIR)
    logger.info(f"  点赞数分布图: {fig_likes}")
    fig_ratio = plot_like_ratio_distribution(df, OUTPUT_DIR)
    logger.info(f"  点赞率分布图: {fig_ratio}")

    # ------------------------------------------------------------------
    # Step 02.4: 头部效应分析
    # ------------------------------------------------------------------
    logger.info("Step 02.4: 头部效应分析")
    sorted_likes = df['likes'].fillna(0).astype(float).sort_values(ascending=False).values
    total_likes = sorted_likes.sum()
    head_effect = {}

    cumsum = np.cumsum(sorted_likes)
    n = len(sorted_likes)
    head_effect['top_1_pct'] = float(cumsum[int(n * 0.01) - 1] / total_likes * 100) if int(n * 0.01) > 0 else 0
    head_effect['top_5_pct'] = float(cumsum[int(n * 0.05) - 1] / total_likes * 100) if int(n * 0.05) > 0 else 0
    head_effect['top_10_pct'] = float(cumsum[int(n * 0.10) - 1] / total_likes * 100) if int(n * 0.10) > 0 else 0
    head_effect['top_20_pct'] = float(cumsum[int(n * 0.20) - 1] / total_likes * 100) if int(n * 0.20) > 0 else 0

    # 找到累计占比达 80% 所需的游戏占比
    pct_for_80 = np.searchsorted(cumsum, total_likes * 0.8) / n * 100
    head_effect['pct_for_80'] = float(pct_for_80)

    # 近似 Gini 系数（基于洛伦兹曲线）
    lorentz = cumsum / total_likes
    uniform = np.arange(1, n + 1) / n
    gini_approx = 1 - 2 * np.trapezoid(lorentz, uniform)
    head_effect['gini_approx'] = float(gini_approx)

    logger.info(f"  Top 1% 游戏点赞占比: {head_effect['top_1_pct']:.1f}%")
    logger.info(f"  Top 20% 游戏点赞占比: {head_effect['top_20_pct']:.1f}%")
    logger.info(f"  80% 点赞所需游戏占比: {head_effect['pct_for_80']:.1f}%")

    fig_head = plot_head_effect(df, OUTPUT_DIR)
    logger.info(f"  头部效应图: {fig_head}")

    # ------------------------------------------------------------------
    # Step 02.5: Top N 游戏排名
    # ------------------------------------------------------------------
    logger.info("Step 02.5: Top 20 游戏排名")
    top_games = df.nlargest(20, 'likes')[['name', 'source', 'likes', 'dislikes', 'like_ratio', 'tag_count']].copy()
    logger.info(f"  排名第一: {top_games.iloc[0]['name']} ({int(top_games.iloc[0]['likes'])} likes)")

    fig_top = plot_top_games_bar(df, OUTPUT_DIR)
    logger.info(f"  Top20 柱状图: {fig_top}")

    # ------------------------------------------------------------------
    # Step 02.6: 相关性分析
    # ------------------------------------------------------------------
    logger.info("Step 02.6: 指标相关性分析")
    corr_cols = ['likes', 'dislikes', 'log_likes', 'log_dislikes', 'like_ratio', 'tag_count']
    corr_matrix = df[corr_cols].corr()
    logger.info("  相关性矩阵:")
    for col in corr_cols:
        logger.info(f"    {col}: likes_corr={corr_matrix.loc[col, 'likes']:.4f}")

    # ------------------------------------------------------------------
    # Step 02.7: 保存统计表 + 生成报告
    # ------------------------------------------------------------------
    logger.info("Step 02.7: 保存产物")
    stats_df = generate_stats_summary(df, stats)
    save_dataframe(stats_df, 'ch02_popularity_stats.csv', OUTPUT_DIR)
    logger.info("  统计表已保存")

    # Top 20 排名表
    top20_save = top_games.copy()
    top20_save.insert(0, 'rank', range(1, len(top20_save) + 1))
    save_dataframe(top20_save, 'ch02_top20_games.csv', OUTPUT_DIR)

    # 分平台统计表
    platform_rows = []
    for src, ps in platform_stats.items():
        ps_row = {'platform': src}
        ps_row.update(ps)
        platform_rows.append(ps_row)
    save_dataframe(pd.DataFrame(platform_rows), 'ch02_platform_stats.csv', OUTPUT_DIR)

    # 生成 Markdown 报告
    report = generate_report(df, stats, top_games, head_effect, corr_matrix, platform_stats)
    save_report(report, 'ch02_popularity_analysis_report.md', OUTPUT_DIR)
    logger.info("  分析报告已保存")

    # 最终汇总
    logger.info("=" * 60)
    logger.info("Prompt-02: 热度分析 - 执行完成")
    logger.info(f"产物目录: {OUTPUT_DIR}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
