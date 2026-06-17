#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt-03: 标签分析
对清洗后的游戏标签数据进行频率统计、共现分析、标签关联挖掘。

覆盖步骤:
  - Step 03.1: 加载清洗后数据
  - Step 03.2: 标签频率统计与 Top N 排名
  - Step 03.3: 标签分布分析（长尾分布）
  - Step 03.4: 标签共现分析（Top 共现对）
  - Step 03.5: 标签共现矩阵热力图
  - Step 03.6: 标签分布统计（每游戏标签数分布）
  - Step 03.7: 平台标签偏好对比
  - Step 03.8: 保存结果并生成报告

产物输出到: outputs/ch03_tag_analysis/
"""

import sys
import os
import logging
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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
OUTPUT_DIR = get_chapter_dir('ch03')
OUTPUT_LOG = os.path.join(OUTPUT_DIR, 'ch03_tag_analysis.log')

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
# 数据处理函数
# ============================================================

def extract_tag_list(tags_series: pd.Series) -> list:
    """从 tags 列提取所有标签列表"""
    all_tags = []
    for t in tags_series:
        if t is None or (isinstance(t, float) and np.isnan(t)):
            continue
        t_str = str(t).strip()
        if not t_str:
            continue
        all_tags.extend([x.strip() for x in t_str.split(',') if x.strip()])
    return all_tags


def compute_cooccurrence(tags_series: pd.Series, top_n: int = 30) -> pd.DataFrame:
    """计算 Top N 标签的共现矩阵"""
    # 收集所有标签列表
    all_tag_lists = []
    global_counter = Counter()
    for t in tags_series:
        if t is None or (isinstance(t, float) and np.isnan(t)):
            continue
        t_str = str(t).strip()
        if not t_str:
            continue
        tl = [x.strip() for x in t_str.split(',') if x.strip()]
        all_tag_lists.append(tl)
        for tag in tl:
            global_counter[tag] += 1

    top_tags = [tag for tag, _ in global_counter.most_common(top_n)]
    n = len(top_tags)
    cooc = np.zeros((n, n), dtype=int)
    tag_index = {tag: i for i, tag in enumerate(top_tags)}

    for tl in all_tag_lists:
        present = [tag_index[t] for t in tl if t in tag_index]
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                cooc[present[i], present[j]] += 1
                cooc[present[j], present[i]] += 1

    cooc_df = pd.DataFrame(cooc, index=top_tags, columns=top_tags)
    return cooc_df


# ============================================================
# 可视化函数
# ============================================================

def plot_top_tags(tag_counter: Counter, output_dir: str, top_n: int = 20) -> str:
    """绘制 Top N 标签柱状图"""
    tags, counts = zip(*tag_counter.most_common(top_n))

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, top_n))
    bars = ax.barh(range(top_n), counts, color=colors, alpha=0.85)
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(tags, fontsize=10)
    ax.set_xlabel('出现次数')
    ax.set_title(f'Top {top_n} 标签频率')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)

    # 在柱状图上标注数值
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax.text(count + max(counts) * 0.01, i, str(count), va='center', fontsize=8)

    plt.tight_layout()
    return save_figure(fig, f'ch03_top{top_n}_tags.png', output_dir)


def plot_tag_long_tail(tag_counter: Counter, output_dir: str) -> str:
    """绘制标签长尾分布"""
    tags, counts = zip(*tag_counter.most_common())
    cumsum = np.cumsum(counts)
    cumsum_pct = cumsum / cumsum[-1] * 100

    fig, ax1 = plt.subplots(figsize=(12, 5))

    # 柱状图（频率）
    ax1.bar(range(len(counts)), counts, color='steelblue', alpha=0.6, width=0.8)
    ax1.set_xlabel('标签排名')
    ax1.set_ylabel('出现次数', color='steelblue')
    ax1.tick_params(axis='y', labelcolor='steelblue')

    # 累计占比曲线
    ax2 = ax1.twinx()
    ax2.plot(range(len(cumsum_pct)), cumsum_pct, color='darkorange', linewidth=2)
    ax2.set_ylabel('累计占比 (%)', color='darkorange')
    ax2.tick_params(axis='y', labelcolor='darkorange')
    ax2.axhline(y=80, color='gray', linestyle='--', alpha=0.4)

    # 找到覆盖 80% 的标签数
    pct_80_idx = np.searchsorted(cumsum_pct, 80) + 1
    ax1.axvline(x=pct_80_idx, color='red', linestyle='--', alpha=0.5)
    ax1.text(pct_80_idx + 1, max(counts) * 0.8, f'80% 阈值: {pct_80_idx} 个标签',
             fontsize=10, color='red')

    plt.title('标签长尾分布（频率 + 累计占比）')
    fig.tight_layout()
    return save_figure(fig, 'ch03_tag_long_tail.png', output_dir)


def plot_cooccurrence_heatmap(cooc_df: pd.DataFrame, output_dir: str,
                               top_n: int = 20) -> str:
    """绘制标签共现热力图"""
    cooc_top = cooc_df.iloc[:top_n, :top_n]

    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(cooc_top.values, cmap='YlOrRd', aspect='auto')

    ax.set_xticks(range(top_n))
    ax.set_yticks(range(top_n))
    ax.set_xticklabels(cooc_top.columns, fontsize=8, rotation=45, ha='right')
    ax.set_yticklabels(cooc_top.index, fontsize=8)
    ax.set_title(f'Top {top_n} 标签共现矩阵')

    plt.colorbar(im, ax=ax, label='共现次数')
    plt.tight_layout()
    return save_figure(fig, f'ch03_cooccurrence_top{top_n}.png', output_dir)


def plot_top_cooccurrence_pairs(cooc_df: pd.DataFrame, output_dir: str,
                                 top_n: int = 20) -> str:
    """绘制 Top N 标签共现对柱状图"""
    pairs = []
    tags = cooc_df.index.tolist()
    for i in range(len(tags)):
        for j in range(i + 1, len(tags)):
            val = cooc_df.iloc[i, j]
            if val > 0:
                pairs.append((f'{tags[i]} + {tags[j]}', val))
    pairs.sort(key=lambda x: x[1], reverse=True)
    pairs = pairs[:top_n]

    labels, values = zip(*pairs)

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.plasma(np.linspace(0.2, 0.8, len(labels)))
    bars = ax.barh(range(len(labels)), values, color=colors, alpha=0.85)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('共现次数')
    ax.set_title(f'Top {top_n} 标签共现对')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)

    for bar, val in zip(bars, values):
        ax.text(val + max(values) * 0.005, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', fontsize=8)

    plt.tight_layout()
    return save_figure(fig, f'ch03_top{top_n}_cooccurrence_pairs.png', output_dir)


def plot_tag_count_distribution(df: pd.DataFrame, output_dir: str) -> str:
    """绘制每游戏标签数分布"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 直方图
    axes[0].hist(df['tag_count'], bins=range(0, int(df['tag_count'].max()) + 2),
                 color='teal', alpha=0.8, edgecolor='white')
    axes[0].set_xlabel('标签数量')
    axes[0].set_ylabel('游戏数量')
    axes[0].set_title('每游戏标签数分布')
    axes[0].grid(axis='y', alpha=0.3)

    # 分平台箱线图
    box_data = [
        df[df['source'] == 'poki']['tag_count'],
        df[df['source'] == 'newgrounds']['tag_count'],
    ]
    bp = axes[1].boxplot(box_data, tick_labels=['Poki', 'Newgrounds'], patch_artist=True)
    for patch, color in zip(bp['boxes'], ['#ff9999', '#66b3ff']):
        patch.set_facecolor(color)
    axes[1].set_ylabel('标签数量')
    axes[1].set_title('每游戏标签数分布（分平台箱线图）')
    axes[1].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    return save_figure(fig, 'ch03_tag_count_distribution.png', output_dir)


def plot_platform_tag_comparison(df: pd.DataFrame, output_dir: str, top_n: int = 15) -> str:
    """绘制平台标签偏好对比"""
    platform_tags = {}
    for src in ['poki', 'newgrounds']:
        sub = df[df['source'] == src]
        platform_tags[src] = Counter(extract_tag_list(sub['tags']))

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for idx, (src, ax) in enumerate(zip(['poki', 'newgrounds'], axes)):
        tags = platform_tags[src]
        top = tags.most_common(top_n)
        t, c = zip(*top)
        colors = plt.cm.Set2(np.linspace(0, 1, top_n))
        bars = ax.barh(range(top_n), c, color=colors, alpha=0.8)
        ax.set_yticks(range(top_n))
        ax.set_yticklabels(t, fontsize=9)
        ax.set_xlabel('出现次数')
        ax.set_title(f'{src} 平台 Top {top_n} 标签')
        ax.invert_yaxis()
        ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    return save_figure(fig, 'ch03_platform_tag_comparison.png', output_dir)


# ============================================================
# 报告生成
# ============================================================

def generate_report(df: pd.DataFrame, tag_counter: Counter,
                    tag_per_game_stats: dict, top_cooc_pairs: list,
                    platform_tag_top: dict, unique_tags_before: int,
                    unique_tags_after: int) -> str:
    """生成标签分析报告"""
    top20 = tag_counter.most_common(20)
    total_tags = sum(tag_counter.values())
    unique_tags = len(tag_counter)

    report = f"""# 在线小游戏标签分析报告

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. 标签数据概况

| 指标 | 值 |
|------|------|
| 分析游戏总数 | {len(df)} |
| 有标签游戏数 | {int((df['tag_count'] > 0).sum())} |
| 无标签游戏数 | {int((df['tag_count'] == 0).sum())} |
| 标签总出现次数 | {total_tags} |
| 唯一标签数（清洗后） | {unique_tags} |
| 唯一标签数（清洗前） | {unique_tags_before} |
| 清洗减少数 | {unique_tags_before - unique_tags} |

## 2. 标签频率统计

### Top 20 标签

| 排名 | 标签 | 出现次数 | 占比 |
|------|------|---------|------|
"""
    for i, (tag, count) in enumerate(top20, 1):
        pct = count / len(df) * 100
        report += f"| {i} | {tag} | {count} | {pct:.1f}% |\n"

    report += f"""
## 3. 每游戏标签数统计

| 统计量 | 值 |
|--------|------|
| 均值 | {tag_per_game_stats.get('mean', 0):.2f} |
| 中位数 | {tag_per_game_stats.get('median', 0):.1f} |
| 标准差 | {tag_per_game_stats.get('std', 0):.2f} |
| 最小值 | {tag_per_game_stats.get('min', 0)} |
| 最大值 | {tag_per_game_stats.get('max', 0)} |
| 25% 分位 | {tag_per_game_stats.get('q25', 0):.0f} |
| 75% 分位 | {tag_per_game_stats.get('q75', 0):.0f} |

## 4. 标签共现分析（Top 10 共现对）

| 排名 | 标签对 | 共现次数 |
|------|--------|---------|
"""
    for i, (pair, cnt) in enumerate(top_cooc_pairs[:10], 1):
        report += f"| {i} | {pair} | {cnt} |\n"

    report += f"""
## 5. 平台标签偏好对比

### Poki Top 10
| 排名 | 标签 | 出现次数 |
|------|------|---------|
"""
    for i, (tag, cnt) in enumerate(platform_tag_top.get('poki', [])[:10], 1):
        report += f"| {i} | {tag} | {cnt} |\n"

    report += f"""
### Newgrounds Top 10
| 排名 | 标签 | 出现次数 |
|------|------|---------|
"""
    for i, (tag, cnt) in enumerate(platform_tag_top.get('newgrounds', [])[:10], 1):
        report += f"| {i} | {tag} | {cnt} |\n"

    report += f"""
## 6. 输出产物清单

| 文件 | 说明 |
|------|------|
| `ch03_tag_frequency.csv` | 标签频率统计表 |
| `ch03_tag_stats.csv` | 标签分布统计表 |
| `ch03_top20_tags.png` | Top 20 标签柱状图 |
| `ch03_tag_long_tail.png` | 标签长尾分布图 |
| `ch03_tag_count_distribution.png` | 标签数量分布图 |
| `ch03_cooccurrence_top20.png` | 标签共现热力图 |
| `ch03_top20_cooccurrence_pairs.png` | Top 20 共现对柱状图 |
| `ch03_platform_tag_comparison.png` | 平台标签偏好对比 |
| `ch03_tag_analysis_report.md` | 本文档 |
"""
    return report


# ============================================================
# 主函数
# ============================================================

def main():
    """Prompt-03 主函数：执行标签分析全流程"""
    logger.info("=" * 60)
    logger.info("Prompt-03: 标签分析 - 开始执行")
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # Step 03.1: 加载清洗后数据
    # ------------------------------------------------------------------
    logger.info("Step 03.1: 加载清洗后数据")
    df = load_cleaned_data()
    logger.info(f"数据加载完成: {len(df)} 行 x {len(df.columns)} 列")

    # ------------------------------------------------------------------
    # Step 03.2: 标签频率统计
    # ------------------------------------------------------------------
    logger.info("Step 03.2: 标签频率统计")
    all_tags = extract_tag_list(df['tags'])
    tag_counter = Counter(all_tags)
    logger.info(f"  标签总出现次数: {sum(tag_counter.values())}")
    logger.info(f"  唯一标签数: {len(tag_counter)}")
    logger.info(f"  Top 5 标签: {tag_counter.most_common(5)}")

    # 保存标签频率统计
    tag_freq_rows = []
    for i, (tag, cnt) in enumerate(tag_counter.most_common(), 1):
        tag_freq_rows.append({'排名': i, '标签': tag, '出现次数': cnt})
    tag_freq_df = pd.DataFrame(tag_freq_rows)
    save_dataframe(tag_freq_df, 'ch03_tag_frequency.csv', OUTPUT_DIR)

    # 清洗前标签统计（对比用）
    df_original = pd.read_csv(
        os.path.join(os.path.dirname(OUTPUT_BASE), 'data', 'online-gaming-14-04-26.csv'),
        sep='\t', keep_default_na=False
    )
    all_tags_before = []
    for t in df_original['tags'].dropna():
        all_tags_before.extend([x.strip().lower() for x in t.split(',') if x.strip()])
    unique_tags_before = len(set(all_tags_before))
    unique_tags_after = len(tag_counter)
    logger.info(f"  清洗前唯一标签数: {unique_tags_before}")
    logger.info(f"  清洗后唯一标签数: {unique_tags_after}")

    # ------------------------------------------------------------------
    # Step 03.3: 长尾分布分析
    # ------------------------------------------------------------------
    logger.info("Step 03.3: 标签长尾分布分析")
    fig_longtail = plot_tag_long_tail(tag_counter, OUTPUT_DIR)
    logger.info(f"  长尾分布图: {fig_longtail}")

    fig_top_tags = plot_top_tags(tag_counter, OUTPUT_DIR)
    logger.info(f"  Top20 标签图: {fig_top_tags}")

    # ------------------------------------------------------------------
    # Step 03.4: 标签共现分析
    # ------------------------------------------------------------------
    logger.info("Step 03.4: 标签共现分析")
    cooc_df = compute_cooccurrence(df['tags'], top_n=30)
    logger.info(f"  共现矩阵: {cooc_df.shape}")

    # 提取 Top 共现对
    pairs = []
    tags_list = cooc_df.index.tolist()[:20]
    for i in range(len(tags_list)):
        for j in range(i + 1, len(tags_list)):
            val = cooc_df.loc[tags_list[i], tags_list[j]]
            if val > 0:
                pairs.append((f'{tags_list[i]} + {tags_list[j]}', int(val)))
    pairs.sort(key=lambda x: x[1], reverse=True)
    top_cooc_pairs = pairs[:20]
    logger.info(f"  Top 5 共现对: {top_cooc_pairs[:5]}")

    # ------------------------------------------------------------------
    # Step 03.5: 共现热力图
    # ------------------------------------------------------------------
    logger.info("Step 03.5: 共现热力图")
    fig_heatmap = plot_cooccurrence_heatmap(cooc_df, OUTPUT_DIR)
    logger.info(f"  共现热力图: {fig_heatmap}")

    fig_pairs = plot_top_cooccurrence_pairs(cooc_df, OUTPUT_DIR)
    logger.info(f"  共现对柱状图: {fig_pairs}")

    # ------------------------------------------------------------------
    # Step 03.6: 每游戏标签数分布
    # ------------------------------------------------------------------
    logger.info("Step 03.6: 标签数量分布")
    tag_per_game_stats = {
        'mean': df['tag_count'].mean(),
        'median': df['tag_count'].median(),
        'std': df['tag_count'].std(),
        'min': int(df['tag_count'].min()),
        'max': int(df['tag_count'].max()),
        'q25': df['tag_count'].quantile(0.25),
        'q75': df['tag_count'].quantile(0.75),
    }
    logger.info(f"  每游戏标签数: 均值={tag_per_game_stats['mean']:.2f}, 中位数={tag_per_game_stats['median']:.1f}")

    fig_tag_cnt = plot_tag_count_distribution(df, OUTPUT_DIR)
    logger.info(f"  标签数量分布图: {fig_tag_cnt}")

    # ------------------------------------------------------------------
    # Step 03.7: 平台标签偏好对比
    # ------------------------------------------------------------------
    logger.info("Step 03.7: 平台标签偏好对比")
    platform_tag_top = {}
    for src in ['poki', 'newgrounds']:
        sub = df[df['source'] == src]
        tags = extract_tag_list(sub['tags'])
        platform_tag_top[src] = Counter(tags).most_common()
        logger.info(f"  {src}: Top 3 标签 = {platform_tag_top[src][:3]}")

    # 保存平台标签偏好
    for src in ['poki', 'newgrounds']:
        rows = []
        for i, (tag, cnt) in enumerate(platform_tag_top[src], 1):
            rows.append({'排名': i, '标签': tag, '出现次数': cnt})
        save_dataframe(pd.DataFrame(rows), f'ch03_tags_{src}.csv', OUTPUT_DIR)

    fig_platform = plot_platform_tag_comparison(df, OUTPUT_DIR)
    logger.info(f"  平台标签对比图: {fig_platform}")

    # ------------------------------------------------------------------
    # Step 03.8: 保存报告
    # ------------------------------------------------------------------
    logger.info("Step 03.8: 生成报告")
    report = generate_report(df, tag_counter, tag_per_game_stats,
                             top_cooc_pairs, platform_tag_top,
                             unique_tags_before, unique_tags_after)
    save_report(report, 'ch03_tag_analysis_report.md', OUTPUT_DIR)
    logger.info("  标签分析报告已保存")

    logger.info("=" * 60)
    logger.info("Prompt-03: 标签分析 - 执行完成")
    logger.info(f"产物目录: {OUTPUT_DIR}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
