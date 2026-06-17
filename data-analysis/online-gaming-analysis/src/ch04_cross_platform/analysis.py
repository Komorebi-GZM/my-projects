#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt-04: 跨平台对比分析
对比 Poki 和 Newgrounds 两个平台在热度、标签、用户互动等方面的差异。

覆盖步骤:
  - Step 04.1: 加载清洗后数据
  - Step 04.2: 平台基本特征对比
  - Step 04.3: 热度指标差异分析（统计检验）
  - Step 04.4: 平台标签偏好对比
  - Step 04.5: 平台点赞率分布对比
  - Step 04.6: 平台指标相关性对比
  - Step 04.7: 关键差异总结与报告生成

产物输出到: outputs/ch04_cross_platform/
"""

import sys
import os
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats as scipy_stats
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
OUTPUT_DIR = get_chapter_dir('ch04')
OUTPUT_LOG = os.path.join(OUTPUT_DIR, 'ch04_platform_analysis.log')

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
# 统计分析函数
# ============================================================

def compute_platform_stats(df: pd.DataFrame) -> dict:
    """计算各平台的基本统计量"""
    platforms = {}
    for src in ['poki', 'newgrounds']:
        sub = df[df['source'] == src]
        likes = sub['likes'].fillna(0).astype(float)
        dislikes = sub['dislikes'].fillna(0).astype(float)
        like_ratio = sub['like_ratio'].dropna()
        tag_count = sub['tag_count']

        platforms[src] = {
            'count': len(sub),
            'likes_mean': likes.mean(),
            'likes_median': likes.median(),
            'likes_std': likes.std(),
            'dislikes_mean': dislikes.mean(),
            'dislikes_median': dislikes.median(),
            'dislikes_std': dislikes.std(),
            'like_ratio_mean': like_ratio.mean(),
            'like_ratio_median': like_ratio.median(),
            'like_ratio_std': like_ratio.std(),
            'tag_count_mean': tag_count.mean(),
            'tag_count_median': tag_count.median(),
            'tag_count_std': tag_count.std(),
            'total_likes': int(likes.sum()),
            'total_dislikes': int(dislikes.sum()),
        }
    return platforms


def run_statistical_tests(df: pd.DataFrame, metric: str) -> dict:
    """对某指标执行 Mann-Whitney U 检验（两平台差异）"""
    poki_vals = df[df['source'] == 'poki'][metric].dropna().astype(float)
    ng_vals = df[df['source'] == 'newgrounds'][metric].dropna().astype(float)

    if len(poki_vals) < 2 or len(ng_vals) < 2:
        return {'poki_n': len(poki_vals), 'ng_n': len(ng_vals),
                'poki_mean': float(poki_vals.mean()) if len(poki_vals) > 0 else float('nan'),
                'ng_mean': float(ng_vals.mean()) if len(ng_vals) > 0 else float('nan'),
                'u_stat': float('nan'), 'p_value': float('nan'),
                'significant': False, 'test': '样本量不足'}

    u_stat, p_value = scipy_stats.mannwhitneyu(poki_vals, ng_vals, alternative='two-sided')

    return {
        'poki_n': len(poki_vals),
        'ng_n': len(ng_vals),
        'poki_mean': round(float(poki_vals.mean()), 4),
        'ng_mean': round(float(ng_vals.mean()), 4),
        'u_stat': round(float(u_stat), 2),
        'p_value': float(p_value),
        'significant': p_value < 0.05,
        'test': 'Mann-Whitney U',
    }


# ============================================================
# 可视化函数
# ============================================================

def plot_metric_comparison(df: pd.DataFrame, output_dir: str) -> str:
    """绘制平台指标对比箱线图"""
    metrics = [
        ('likes', '点赞数', 'log'),
        ('dislikes', '踩数', 'log'),
        ('like_ratio', '点赞率', 'linear'),
        ('tag_count', '标签数量', 'linear'),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, (metric, label, scale) in enumerate(metrics):
        ax = axes[idx]
        box_data = [
            df[df['source'] == 'poki'][metric].dropna().astype(float),
            df[df['source'] == 'newgrounds'][metric].dropna().astype(float),
        ]
        bp = ax.boxplot(box_data, tick_labels=['Poki', 'Newgrounds'], patch_artist=True)
        for patch, color in zip(bp['boxes'], ['#ff9999', '#66b3ff']):
            patch.set_facecolor(color)
        if scale == 'log':
            ax.set_yscale('log')
        ax.set_ylabel(label)
        ax.set_title(f'{label} 对比')
        ax.grid(axis='y', alpha=0.3)

    plt.suptitle('Poki vs Newgrounds 平台指标对比', fontsize=14, y=1.02)
    plt.tight_layout()
    return save_figure(fig, 'ch04_metric_comparison.png', output_dir)


def plot_like_ratio_hist_comparison(df: pd.DataFrame, output_dir: str) -> str:
    """绘制平台点赞率直方图对比"""
    fig, ax = plt.subplots(figsize=(10, 5))

    bins = np.linspace(0, 1, 30)
    for src, color, label in [('poki', '#ff6b6b', 'Poki'), ('newgrounds', '#4ecdc4', 'Newgrounds')]:
        vals = df[df['source'] == src]['like_ratio'].dropna()
        ax.hist(vals, bins=bins, alpha=0.6, color=color, label=label, density=True)

    ax.set_xlabel('like_ratio')
    ax.set_ylabel('密度')
    ax.set_title('平台点赞率分布对比')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    return save_figure(fig, 'ch04_like_ratio_comparison.png', output_dir)


def plot_likes_log_comparison(df: pd.DataFrame, output_dir: str) -> str:
    """绘制平台 log(likes) 分布对比"""
    fig, ax = plt.subplots(figsize=(10, 5))

    bins = np.linspace(0, 18, 40)
    for src, color, label in [('poki', '#ff6b6b', 'Poki'), ('newgrounds', '#4ecdc4', 'Newgrounds')]:
        vals = np.log1p(df[df['source'] == src]['likes'].fillna(0).astype(float))
        ax.hist(vals, bins=bins, alpha=0.6, color=color, label=label, density=True)

    ax.set_xlabel('log1p(likes)')
    ax.set_ylabel('密度')
    ax.set_title('平台点赞数分布对比（对数）')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    return save_figure(fig, 'ch04_likes_dist_comparison.png', output_dir)


def plot_tag_count_comparison(df: pd.DataFrame, output_dir: str) -> str:
    """绘制平台标签数量分布对比"""
    fig, ax = plt.subplots(figsize=(10, 5))

    max_tags = int(df['tag_count'].max()) + 1
    bins = np.arange(-0.5, max_tags, 1)
    width = 0.35
    poki_vals = df[df['source'] == 'poki']['tag_count']
    ng_vals = df[df['source'] == 'newgrounds']['tag_count']

    ax.hist(poki_vals, bins=bins, alpha=0.7, color='#ff6b6b', label='Poki', density=True)
    ax.hist(ng_vals, bins=bins, alpha=0.5, color='#4ecdc4', label='Newgrounds', density=True)
    ax.set_xlabel('标签数量')
    ax.set_ylabel('密度')
    ax.set_title('平台标签数量分布对比')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    return save_figure(fig, 'ch04_tag_count_comparison.png', output_dir)


def plot_platform_correlation_scatter(df: pd.DataFrame, output_dir: str) -> str:
    """绘制平台相关性散点图对比"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for idx, (src, ax) in enumerate(zip(['poki', 'newgrounds'], axes)):
        sub = df[df['source'] == src]
        likes_log = np.log1p(sub['likes'].fillna(0).astype(float))
        dislikes_log = np.log1p(sub['dislikes'].fillna(0).astype(float))
        ax.scatter(likes_log, dislikes_log, alpha=0.3, s=5,
                   c='#ff6b6b' if src == 'poki' else '#4ecdc4')
        ax.set_xlabel('log1p(likes)')
        ax.set_ylabel('log1p(dislikes)')
        ax.set_title(f'{src} 平台 likes vs dislikes')
        ax.grid(alpha=0.3)

    plt.tight_layout()
    return save_figure(fig, 'ch04_platform_correlation.png', output_dir)


# ============================================================
# 报告生成
# ============================================================

def generate_report(df: pd.DataFrame, platform_stats: dict,
                    test_results: dict, top_tags_by_platform: dict) -> str:
    """生成跨平台对比分析报告"""
    poki = platform_stats['poki']
    ng = platform_stats['newgrounds']

    report = f"""# 在线小游戏跨平台对比分析报告

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 对比平台：Poki vs Newgrounds

## 1. 数据概况

| 指标 | Poki | Newgrounds |
|------|------|------------|
| 游戏数量 | {poki['count']} | {ng['count']} |
| 占比 | {poki['count'] / len(df) * 100:.1f}% | {ng['count'] / len(df) * 100:.1f}% |
| 点赞总数 | {poki['total_likes']:,} | {ng['total_likes']:,} |
| 踩总数 | {poki['total_dislikes']:,} | {ng['total_dislikes']:,} |

## 2. 热度指标对比

| 指标 | Poki 均值 | Newgrounds 均值 | Poki 中位数 | Newgrounds 中位数 |
|------|-----------|-----------------|-------------|-------------------|
| likes | {poki['likes_mean']:.1f} | {ng['likes_mean']:.1f} | {poki['likes_median']:.1f} | {ng['likes_median']:.1f} |
| dislikes | {poki['dislikes_mean']:.1f} | {ng['dislikes_mean']:.1f} | {poki['dislikes_median']:.1f} | {ng['dislikes_median']:.1f} |
| like_ratio | {poki['like_ratio_mean']:.4f} | {ng['like_ratio_mean']:.4f} | {poki['like_ratio_median']:.4f} | {ng['like_ratio_median']:.4f} |
| tag_count | {poki['tag_count_mean']:.2f} | {ng['tag_count_mean']:.2f} | {poki['tag_count_median']:.1f} | {ng['tag_count_median']:.1f} |

## 3. 统计检验结果（Mann-Whitney U）

| 指标 | Poki 均值 | NG 均值 | U 统计量 | p 值 | 显著差异 |
|------|----------|---------|----------|------|---------|
"""
    for metric, result in test_results.items():
        sig = '是' if result.get('significant') else '否'
        report += f"| {metric} | {result.get('poki_mean', 'N/A')} | {result.get('ng_mean', 'N/A')} | {result.get('u_stat', 'N/A')} | {result.get('p_value', 'N/A'):.6f} | {sig} |\n"

    report += f"""
## 4. 平台标签偏好对比

### Poki Top 10 标签
| 排名 | 标签 | 出现次数 |
|------|------|---------|
"""
    for i, (tag, cnt) in enumerate(top_tags_by_platform.get('poki', [])[:10], 1):
        report += f"| {i} | {tag} | {cnt} |\n"

    report += f"""
### Newgrounds Top 10 标签
| 排名 | 标签 | 出现次数 |
|------|------|---------|
"""
    for i, (tag, cnt) in enumerate(top_tags_by_platform.get('newgrounds', [])[:10], 1):
        report += f"| {i} | {tag} | {cnt} |\n"

    # 关键差异总结
    report += f"""
## 5. 关键差异总结

### 规模差异
- Poki 平台仅 **{poki['count']}** 款游戏，但其平均点赞数（**{poki['likes_mean']:.0f}**）远高于 Newgrounds（**{ng['likes_mean']:.0f}**）
- Newgrounds 平台游戏数量（**{ng['count']}**）是 Poki 的 **{ng['count'] / poki['count']:.1f} 倍**

### 热度差异
- Poki 游戏热度方差更大（标准差 {poki['likes_std']:.0f} vs {ng['likes_std']:.0f}）
"""
    if len(test_results) > 0:
        sig_metrics = [m for m, r in test_results.items() if r.get('significant')]
        if sig_metrics:
            report += f"- 在 {'、'.join(sig_metrics)} 指标上存在显著统计差异（p < 0.05）\n"

    report += f"""
### 标签差异
- Poki 平台标签更丰富：最多 **{int(df[df['source'] == 'poki']['tag_count'].max())}** 个标签/游戏
- Newgrounds 平台标签分布更集中：中位数 **{ng['tag_count_median']:.1f}** 个标签/游戏

## 6. 输出产物清单

| 文件 | 说明 |
|------|------|
| `ch04_platform_comparison.csv` | 平台对比统计表 |
| `ch04_statistical_tests.csv` | 统计检验结果表 |
| `ch04_metric_comparison.png` | 指标对比箱线图 |
| `ch04_like_ratio_comparison.png` | 点赞率分布对比 |
| `ch04_likes_dist_comparison.png` | 点赞数分布对比 |
| `ch04_tag_count_comparison.png` | 标签数量分布对比 |
| `ch04_platform_correlation.png` | 平台相关性散点图 |
| `ch04_platform_analysis_report.md` | 本文档 |
"""
    return report


# ============================================================
# 主函数
# ============================================================

def main():
    """Prompt-04 主函数：执行跨平台对比分析"""
    logger.info("=" * 60)
    logger.info("Prompt-04: 跨平台对比分析 - 开始执行")
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # Step 04.1: 加载数据
    # ------------------------------------------------------------------
    logger.info("Step 04.1: 加载清洗后数据")
    df = load_cleaned_data()
    logger.info(f"数据加载完成: {len(df)} 行 x {len(df.columns)} 列")

    # 数值列处理
    for col in ['likes', 'dislikes']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)
    for col in ['like_ratio']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # ------------------------------------------------------------------
    # Step 04.2: 平台基本特征对比
    # ------------------------------------------------------------------
    logger.info("Step 04.2: 平台基本特征对比")
    platform_stats = compute_platform_stats(df)
    for src in ['poki', 'newgrounds']:
        ps = platform_stats[src]
        logger.info(f"  {src}: {ps['count']} 款游戏, 点赞均值 {ps['likes_mean']:.0f}, "
                    f"点赞率均值 {ps['like_ratio_mean']:.4f}")

    # 保存平台对比表
    comparison_rows = []
    for src, ps in platform_stats.items():
        row = {'platform': src}
        row.update(ps)
        comparison_rows.append(row)
    save_dataframe(pd.DataFrame(comparison_rows), 'ch04_platform_comparison.csv', OUTPUT_DIR)

    # ------------------------------------------------------------------
    # Step 04.3: 统计检验
    # ------------------------------------------------------------------
    logger.info("Step 04.3: 统计检验")
    test_results = {}
    for metric in ['likes', 'dislikes', 'like_ratio', 'tag_count']:
        test_results[metric] = run_statistical_tests(df, metric)
        sig = "显著差异" if test_results[metric]['significant'] else "无显著差异"
        logger.info(f"  {metric}: p={test_results[metric]['p_value']:.6f} ({sig})")

    # 保存检验结果
    test_rows = []
    for metric, result in test_results.items():
        row = {'metric': metric}
        row.update(result)
        test_rows.append(row)
    save_dataframe(pd.DataFrame(test_rows), 'ch04_statistical_tests.csv', OUTPUT_DIR)

    # ------------------------------------------------------------------
    # Step 04.4: 平台标签偏好
    # ------------------------------------------------------------------
    logger.info("Step 04.4: 平台标签偏好对比")
    top_tags_by_platform = {}
    df['tags'] = df['tags'].fillna('')
    for src in ['poki', 'newgrounds']:
        sub = df[df['source'] == src]
        all_tags = []
        for t in sub['tags']:
            if t:
                all_tags.extend([x.strip() for x in t.split(',') if x.strip()])
        from collections import Counter
        top_tags_by_platform[src] = Counter(all_tags).most_common()
        logger.info(f"  {src} Top 3: {top_tags_by_platform[src][:3]}")

    # ------------------------------------------------------------------
    # Step 04.5-04.6: 可视化
    # ------------------------------------------------------------------
    logger.info("Step 04.5: 生成对比图表")
    fig1 = plot_metric_comparison(df, OUTPUT_DIR)
    logger.info(f"  指标对比图: {fig1}")

    fig2 = plot_like_ratio_hist_comparison(df, OUTPUT_DIR)
    logger.info(f"  点赞率对比图: {fig2}")

    fig3 = plot_likes_log_comparison(df, OUTPUT_DIR)
    logger.info(f"  点赞分布对比: {fig3}")

    fig4 = plot_tag_count_comparison(df, OUTPUT_DIR)
    logger.info(f"  标签数量对比: {fig4}")

    logger.info("Step 04.6: 平台相关性对比")
    fig5 = plot_platform_correlation_scatter(df, OUTPUT_DIR)
    logger.info(f"  相关性对比: {fig5}")

    # ------------------------------------------------------------------
    # Step 04.7: 报告生成
    # ------------------------------------------------------------------
    logger.info("Step 04.7: 生成报告")
    report = generate_report(df, platform_stats, test_results, top_tags_by_platform)
    save_report(report, 'ch04_platform_analysis_report.md', OUTPUT_DIR)
    logger.info("  跨平台对比报告已保存")

    logger.info("=" * 60)
    logger.info("Prompt-04: 跨平台对比分析 - 执行完成")
    logger.info(f"产物目录: {OUTPUT_DIR}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
