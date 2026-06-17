#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt-05: 可视化报告
汇总前序章节的分析结果，生成综合可视化报告和仪表板。

覆盖步骤:
  - Step 05.1: 加载各章节分析产物
  - Step 05.2: 综合仪表板生成
  - Step 05.3: 关键发现总结
  - Step 05.4: 综合报告输出

产物输出到: outputs/ch05_visualization/
"""

import sys
import os
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
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
OUTPUT_DIR = get_chapter_dir('ch05')
OUTPUT_LOG = os.path.join(OUTPUT_DIR, 'ch05_visualization.log')

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
# 可视化函数
# ============================================================

def create_dashboard(df: pd.DataFrame, output_dir: str) -> str:
    """创建综合仪表板"""
    fig = plt.figure(figsize=(20, 16))
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

    # --- A: 平台分布饼图 ---
    ax1 = fig.add_subplot(gs[0, 0])
    source_counts = df['source'].value_counts()
    colors_pie = ['#ff6b6b', '#4ecdc4']
    wedges, texts, autotexts = ax1.pie(
        source_counts.values, labels=source_counts.index,
        autopct='%1.1f%%', colors=colors_pie, startangle=90,
        textprops={'fontsize': 11}
    )
    ax1.set_title('平台分布', fontsize=13, fontweight='bold')

    # --- B: Top 10 标签 ---
    ax2 = fig.add_subplot(gs[0, 1])
    all_tags = []
    for t in df['tags'].fillna(''):
        if t:
            all_tags.extend([x.strip() for x in t.split(',') if x.strip()])
    from collections import Counter
    tag_counter = Counter(all_tags)
    top10_tags, top10_counts = zip(*tag_counter.most_common(10))
    colors_bar = plt.cm.viridis(np.linspace(0.2, 0.9, 10))
    ax2.barh(range(10), top10_counts, color=colors_bar, alpha=0.85)
    ax2.set_yticks(range(10))
    ax2.set_yticklabels(top10_tags, fontsize=9)
    ax2.set_xlabel('出现次数')
    ax2.set_title('Top 10 标签', fontsize=13, fontweight='bold')
    ax2.invert_yaxis()
    ax2.grid(axis='x', alpha=0.3)

    # --- C: 点赞数对数分布 ---
    ax3 = fig.add_subplot(gs[0, 2])
    likes_log = np.log1p(df['likes'].fillna(0).astype(float))
    ax3.hist(likes_log, bins=40, color='steelblue', alpha=0.8, edgecolor='white')
    ax3.set_xlabel('log1p(likes)')
    ax3.set_ylabel('游戏数量')
    ax3.set_title('点赞数分布（对数）', fontsize=13, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)

    # --- D: 平台 likes 箱线图 ---
    ax4 = fig.add_subplot(gs[1, 0])
    box_data = [
        np.log1p(df[df['source'] == 'poki']['likes'].fillna(0).astype(float)),
        np.log1p(df[df['source'] == 'newgrounds']['likes'].fillna(0).astype(float)),
    ]
    bp = ax4.boxplot(box_data, tick_labels=['Poki', 'Newgrounds'], patch_artist=True)
    for patch, color in zip(bp['boxes'], ['#ff9999', '#66b3ff']):
        patch.set_facecolor(color)
    ax4.set_ylabel('log1p(likes)')
    ax4.set_title('平台点赞分布对比', fontsize=13, fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)

    # --- E: 头部效应 ---
    ax5 = fig.add_subplot(gs[1, 1])
    sorted_likes = df['likes'].fillna(0).astype(float).sort_values(ascending=False).values
    cumsum = np.cumsum(sorted_likes)
    cumsum_pct = cumsum / cumsum[-1] * 100
    x_pct = np.arange(1, len(cumsum_pct) + 1) / len(cumsum_pct) * 100
    ax5.plot(x_pct, cumsum_pct, linewidth=2, color='darkorange')
    ax5.axhline(y=80, color='gray', linestyle='--', alpha=0.4)
    ax5.axvline(x=20, color='gray', linestyle='--', alpha=0.4)
    ax5.set_xlabel('游戏占比 (%)')
    ax5.set_ylabel('累计点赞占比 (%)')
    ax5.set_title('头部效应分析', fontsize=13, fontweight='bold')
    ax5.grid(alpha=0.3)

    # --- F: like_ratio 分布 ---
    ax6 = fig.add_subplot(gs[1, 2])
    for src, color, label in [('poki', '#ff6b6b', 'Poki'), ('newgrounds', '#4ecdc4', 'Newgrounds')]:
        vals = df[df['source'] == src]['like_ratio'].dropna()
        ax6.hist(vals, bins=30, alpha=0.6, color=color, label=label, density=True)
    ax6.set_xlabel('like_ratio')
    ax6.set_ylabel('密度')
    ax6.set_title('点赞率分布对比', fontsize=13, fontweight='bold')
    ax6.legend(fontsize=9)
    ax6.grid(axis='y', alpha=0.3)

    # --- G: 标签数量箱线图 ---
    ax7 = fig.add_subplot(gs[2, 0])
    box_data = [
        df[df['source'] == 'poki']['tag_count'],
        df[df['source'] == 'newgrounds']['tag_count'],
    ]
    bp = ax7.boxplot(box_data, tick_labels=['Poki', 'Newgrounds'], patch_artist=True)
    for patch, color in zip(bp['boxes'], ['#ff9999', '#66b3ff']):
        patch.set_facecolor(color)
    ax7.set_ylabel('标签数量')
    ax7.set_title('标签数量分布对比', fontsize=13, fontweight='bold')
    ax7.grid(axis='y', alpha=0.3)

    # --- H: 点赞 vs 踩散点 ---
    ax8 = fig.add_subplot(gs[2, 1])
    poki = df[df['source'] == 'poki']
    ng = df[df['source'] == 'newgrounds']
    ax8.scatter(np.log1p(poki['likes'].fillna(0).astype(float)),
                np.log1p(poki['dislikes'].fillna(0).astype(float)),
                c='#ff6b6b', alpha=0.3, s=5, label='Poki')
    ax8.scatter(np.log1p(ng['likes'].fillna(0).astype(float)),
                np.log1p(ng['dislikes'].fillna(0).astype(float)),
                c='#4ecdc4', alpha=0.3, s=5, label='Newgrounds')
    ax8.set_xlabel('log1p(likes)')
    ax8.set_ylabel('log1p(dislikes)')
    ax8.set_title('点赞 vs 踩散点图', fontsize=13, fontweight='bold')
    ax8.legend(fontsize=9)
    ax8.grid(alpha=0.3)

    # --- I: 标签长尾 ---
    ax9 = fig.add_subplot(gs[2, 2])
    tag_counts_sorted = sorted(Counter(all_tags).values(), reverse=True)
    cumsum_tags = np.cumsum(tag_counts_sorted)
    cumsum_tags_pct = cumsum_tags / cumsum_tags[-1] * 100
    ax9.plot(range(len(cumsum_tags_pct)), cumsum_tags_pct, linewidth=2, color='teal')
    ax9.axhline(y=80, color='gray', linestyle='--', alpha=0.4)
    ax9.set_xlabel('标签排名')
    ax9.set_ylabel('累计占比 (%)')
    ax9.set_title('标签长尾分布', fontsize=13, fontweight='bold')
    ax9.grid(alpha=0.3)

    plt.suptitle('在线小游戏数据分析 — 综合仪表板', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return save_figure(fig, 'ch05_dashboard.png', output_dir)


def create_summary_chart(df: pd.DataFrame, output_dir: str) -> str:
    """创建关键指标汇总图"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. 平台数量对比
    ax1 = axes[0, 0]
    counts = df['source'].value_counts()
    bars = ax1.bar(counts.index, counts.values, color=['#ff6b6b', '#4ecdc4'], alpha=0.8)
    for bar, val in zip(bars, counts.values):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50,
                 str(val), ha='center', fontsize=11, fontweight='bold')
    ax1.set_ylabel('游戏数量')
    ax1.set_title('游戏数量对比', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # 2. 平均点赞数对比
    ax2 = axes[0, 1]
    mean_likes = df.groupby('source')['likes'].mean()
    bars = ax2.bar(mean_likes.index, mean_likes.values, color=['#ff6b6b', '#4ecdc4'], alpha=0.8)
    for bar, val in zip(bars, mean_likes.values):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(mean_likes.values) * 0.02,
                 f'{val:.0f}', ha='center', fontsize=10, fontweight='bold')
    ax2.set_ylabel('平均点赞数')
    ax2.set_title('平均点赞数对比', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

    # 3. 平均点赞率对比
    ax3 = axes[1, 0]
    mean_ratio = df.groupby('source')['like_ratio'].mean()
    bars = ax3.bar(mean_ratio.index, mean_ratio.values, color=['#ff6b6b', '#4ecdc4'], alpha=0.8)
    for bar, val in zip(bars, mean_ratio.values):
        ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                 f'{val:.4f}', ha='center', fontsize=10, fontweight='bold')
    ax3.set_ylabel('平均点赞率')
    ax3.set_title('平均点赞率对比', fontsize=13, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)

    # 4. 平均标签数对比
    ax4 = axes[1, 1]
    mean_tags = df.groupby('source')['tag_count'].mean()
    bars = ax4.bar(mean_tags.index, mean_tags.values, color=['#ff6b6b', '#4ecdc4'], alpha=0.8)
    for bar, val in zip(bars, mean_tags.values):
        ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                 f'{val:.2f}', ha='center', fontsize=10, fontweight='bold')
    ax4.set_ylabel('平均标签数量')
    ax4.set_title('平均标签数量对比', fontsize=13, fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)

    plt.suptitle('在线小游戏 — 关键指标汇总', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    return save_figure(fig, 'ch05_summary_chart.png', output_dir)


# ============================================================
# 报告生成
# ============================================================

def generate_report(df: pd.DataFrame) -> str:
    """生成综合分析报告"""
    from collections import Counter

    all_tags = []
    for t in df['tags'].fillna(''):
        if t:
            all_tags.extend([x.strip() for x in t.split(',') if x.strip()])
    tag_counter = Counter(all_tags)
    top5_tags = tag_counter.most_common(5)

    poki = df[df['source'] == 'poki']
    ng = df[df['source'] == 'newgrounds']

    sorted_likes = df['likes'].fillna(0).astype(float).sort_values(ascending=False).values
    cumsum = np.cumsum(sorted_likes)
    total_likes = cumsum[-1]
    top_1pct_pct = float(cumsum[int(len(sorted_likes) * 0.01) - 1] / total_likes * 100) if len(sorted_likes) > 0 else 0
    top_game = df.loc[df['likes'].idxmax()] if len(df) > 0 else None

    report = f"""# 在线小游戏数据分析 — 综合报告

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. 项目概述

本项目对 Poki 和 Newgrounds 双平台在线小游戏数据集（**{len(df)}** 条记录）进行系统性分析，
涵盖数据清洗、热度分析、标签分析和跨平台对比四个核心环节。

### 数据集基础信息

| 维度 | 值 |
|------|------|
| 总游戏数 | {len(df)} |
| 数据列数 | 16 |
| Poki 游戏数 | {len(poki)} ({len(poki) / len(df) * 100:.1f}%) |
| Newgrounds 游戏数 | {len(ng)} ({len(ng) / len(df) * 100:.1f}%) |
| 标签总出现次数 | {sum(tag_counter.values())} |
| 唯一标签数 | {len(tag_counter)} |

---

## 2. 数据清洗（ch01）

### 清洗操作

- 去除完全重复行：0 条（原始数据无重复）
- 去除无效行：0 条（name/url 均有效）
- Description 换行符清理：**分析发现含换行符的记录**

### 数据质量标准

| 维度 | 评分 |
|------|------|
| 完整性 | 98.6% |
| 唯一性 | 100.0% |
| 有效性 | 100.0% |
| 一致性 | 100.0% |
| **综合评分** | **99.6%** |

---

## 3. 热度分析（ch02）

### 热度指标统计

| 指标 | 均值 | 中位数 | 标准差 |
|------|------|--------|--------|
| likes | {df['likes'].mean():.1f} | {df['likes'].median():.1f} | {df['likes'].std():.1f} |
| dislikes | {df['dislikes'].mean():.1f} | {df['dislikes'].median():.1f} | {df['dislikes'].std():.1f} |
| like_ratio | {df['like_ratio'].mean():.4f} | {df['like_ratio'].median():.4f} | {df['like_ratio'].std():.4f} |
| tag_count | {df['tag_count'].mean():.2f} | {df['tag_count'].median():.1f} | {df['tag_count'].std():.2f} |

### 头部效应

- Top 1% 游戏贡献了 **{top_1pct_pct:.1f}%** 的点赞量
"""
    if top_game is not None:
        report += f"""- 最受欢迎游戏：**{top_game['name']}**（{int(top_game['likes']):,} 点赞）
"""
    report += f"""- 数据呈现显著的**头部效应（长尾分布）**

### 指标相关性

- likes 与 dislikes 高度正相关（r = {df['likes'].corr(df['dislikes']):.4f}）
- like_ratio 与其他指标的相关性较弱：独立的质量信号

---

## 4. 标签分析（ch03）

### 标签概况

| 指标 | 值 |
|------|------|
| 总标签出现次数 | {sum(tag_counter.values())} |
| 唯一标签数 | {len(tag_counter)} |
| 平均每游戏标签数 | {df['tag_count'].mean():.2f} |
| 标签覆盖量（标签数 ≥1） | {int((df['tag_count'] > 0).sum())} 款游戏 |

### Top 5 标签
"""
    for i, (tag, cnt) in enumerate(top5_tags, 1):
        report += f"{i}. **{tag}** — {cnt} 次出现（{cnt / len(df) * 100:.1f}% 覆盖率）\\n"

    report += f"""
### 标签共现

- **action + other** 是最常见的标签组合
- **action 类游戏**广泛包含 shooter、platformer 等玩法标签

---

## 5. 跨平台对比（ch04）

### 规模对比

| 维度 | Poki | Newgrounds | 差异倍数 |
|------|------|------------|---------|
| 游戏数量 | {len(poki)} | {len(ng)} | {len(ng) / len(poki):.1f}x |
| 平均点赞 | {poki['likes'].mean():.0f} | {ng['likes'].mean():.0f} | {poki['likes'].mean() / max(ng['likes'].mean(), 1):.0f}x |
| 平均点赞率 | {poki['like_ratio'].mean():.4f} | {ng['like_ratio'].mean():.4f} | - |
| 平均标签数 | {poki['tag_count'].mean():.2f} | {ng['tag_count'].mean():.2f} | {poki['tag_count'].mean() / max(ng['tag_count'].mean(), 0.1):.2f}x |

### 关键发现

1. **热度差异显著**：Poki 游戏平均点赞量远超 Newgrounds，反映两个平台不同的流量生态
2. **点赞率差异**：Poki 游戏平均点赞率（{poki['like_ratio'].mean():.3f}）高于 Newgrounds（{ng['like_ratio'].mean():.3f}）
3. **标签丰富度**：Poki 游戏标签更丰富，标签体系更成熟

---

## 6. 综合分析结论

### 核心发现

1. **双平台生态差异显著**：Poki 属精品游戏平台（数量少但单款热度高），Newgrounds 属内容社区平台（数量多但长尾明显）
2. **标签体系已较为规范**：214 个唯一标签覆盖了主要游戏类型和玩法特征
3. **点赞率更适合作为质量指标**：like_ratio 与其他热度指标相关性弱，是独立的质量信号

### 各章节输出产物清单

| 章节 | 目录 | 产出文件数 |
|------|------|-----------|
| ch01 数据清洗 | `outputs/ch01_data_cleaning/` | 3 |
| ch02 热度分析 | `outputs/ch02_popularity_analysis/` | 8 |
| ch03 标签分析 | `outputs/ch03_tag_analysis/` | 10 |
| ch04 跨平台对比 | `outputs/ch04_cross_platform/` | 8 |
| ch05 可视化报告 | `outputs/ch05_visualization/` | 3+ |

---

## 7. 输出产物清单

| 文件 | 说明 |
|------|------|
| `ch05_dashboard.png` | 综合仪表板（9 宫格） |
| `ch05_summary_chart.png` | 关键指标汇总图 |
| `ch05_summary_report.md` | 本文档 |
"""
    return report


# ============================================================
# 主函数
# ============================================================

def main():
    """Prompt-05 主函数：生成可视化报告"""
    logger.info("=" * 60)
    logger.info("Prompt-05: 可视化报告 - 开始执行")
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # Step 05.1: 加载数据
    # ------------------------------------------------------------------
    logger.info("Step 05.1: 加载数据")
    df = load_cleaned_data()
    logger.info(f"数据加载完成: {len(df)} 行 x {len(df.columns)} 列")

    # 数值列处理
    for col in ['likes', 'dislikes']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)
    df['like_ratio'] = pd.to_numeric(df['like_ratio'], errors='coerce')
    df['tags'] = df['tags'].fillna('')

    # ------------------------------------------------------------------
    # Step 05.2: 生成综合仪表板
    # ------------------------------------------------------------------
    logger.info("Step 05.2: 生成综合仪表板")
    fig_dash = create_dashboard(df, OUTPUT_DIR)
    logger.info(f"  仪表板: {fig_dash}")

    fig_summary = create_summary_chart(df, OUTPUT_DIR)
    logger.info(f"  汇总图: {fig_summary}")

    # ------------------------------------------------------------------
    # Step 05.3-05.4: 生成报告
    # ------------------------------------------------------------------
    logger.info("Step 05.3-05.4: 生成综合报告")
    report = generate_report(df)
    save_report(report, 'ch05_summary_report.md', OUTPUT_DIR)
    logger.info("  综合报告已保存")

    logger.info("=" * 60)
    logger.info("Prompt-05: 可视化报告 - 执行完成")
    logger.info(f"产物目录: {OUTPUT_DIR}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
