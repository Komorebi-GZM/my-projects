"""
Prompt-03: 负荷峰值识别与峰值特征研究
基于预处理后的标准化数据，建立95%分位数阈值体系，识别并分析负荷峰值事件。

覆盖步骤:
  - Step 3.1: 95%分位数阈值计算 (含90%/98%参考)
  - Step 3.2: 峰值事件提取与标记 (双产物: 明细+聚合摘要)
  - Step 3.3: 峰值持续时长统计 (双口径: 城市聚合+单Zone精确)
  - Step 3.4: 峰值小时分布分析
  - Step 3.5: 峰值季节+年度分布分析
  - Step 3.6: 峰值时空热力图 (hour x month)
  - Step 3.7: 峰值成因归因 (city x year x season x hour x is_weekend)
  - Step 3.8: 异常峰值研判 (30min平滑 + 1h差分 + 3sigma)

产物输出到: outputs/ch03_peak_analysis/
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# 路径设置（确保能导入 utils）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# 导入项目工具
from utils.config import CITIES, OUTPUT_BASE, SEASON_MAP, PLT_STYLE
from utils.data_loader import load_preprocessed
from utils.output_manager import save_dataframe, save_figure

# === 中文字体配置 ===
plt.rcParams.update({
    'font.sans-serif': ['DejaVu Sans', 'SimHei', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei'],
    'axes.unicode_minus': False,
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'font.size': 12,
})

# === 全局配置 ===
INPUT_FILE = os.path.join(PROJECT_ROOT, 'outputs', 'ch01_data_preprocessing', 'ch01_feature_engineered_data.csv')
STATS_FILE = os.path.join(PROJECT_ROOT, 'outputs', 'ch02_load_pattern_analysis', 'ch02_descriptive_stats.csv')
OUTPUT_DIR = os.path.join(OUTPUT_BASE, 'ch03_peak_analysis')

CITY_LIST = ['Laayoune', 'Boujdour', 'Foum eloued', 'Marrakech']
SEASON_ORDER = ['Winter', 'Spring', 'Summer', 'Autumn']

# 城市配色
CITY_COLORS = {
    'Laayoune': '#2196F3',
    'Boujdour': '#4CAF50',
    'Foum eloued': '#FF9800',
    'Marrakech': '#E91E63',
}

# 季节配色
SEASON_COLORS = ['#4FC3F7', '#81C784', '#FFB74D', '#E57373']

# 城市名 -> 文件名slug映射（下划线替代空格）
CITY_SLUG_MAP = {
    'Laayoune': 'laayoune',
    'Boujdour': 'boujdour',
    'Foum eloued': 'foum_eloued',
    'Marrakech': 'marrakech',
}

# 每个城市的有效zone列（基于CITIES配置中的zones数量）
CITY_ZONE_MAP = {
    city: [f'zone{i}' for i in range(1, info['zones'] + 1)]
    for city, info in CITIES.items()
}


def get_valid_zones(city):
    """获取指定城市的有效zone列列表"""
    return CITY_ZONE_MAP.get(city, [])


def load_data():
    """加载特征工程数据和描述性统计"""
    print("=" * 60)
    print("Prompt-03: 负荷峰值识别与峰值特征研究")
    print("=" * 60)
    print(f"\n[数据加载] {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE, parse_dates=['DateTime'])
    df = df.set_index('DateTime').sort_index()
    print(f"  数据维度: {df.shape}")
    print(f"  城市: {df['city'].unique().tolist()}")
    zone_cols = [c for c in df.columns if c.startswith('zone')]
    print(f"  Zone列: {zone_cols}")
    print(f"  时间范围: {df.index.min()} ~ {df.index.max()}")
    time_features = [c for c in df.columns if c in ['hour', 'day_of_week', 'is_weekend', 'month', 'season', 'year']]
    print(f"  时间特征列: {time_features}")
    print(f"  有效Zone映射: { {k: len(v) for k, v in CITY_ZONE_MAP.items()} }")

    print(f"\n[参考数据] {STATS_FILE}")
    stats_df = pd.read_csv(STATS_FILE)
    print(f"  描述性统计: {stats_df.shape}")

    return df, zone_cols, stats_df


# ============================================================
# Step 3.1: 95%分位数阈值计算
# ============================================================
def step_3_1_peak_thresholds(df, zone_cols):
    """按城市+zone计算95%分位数阈值（含90%/98%参考）"""
    print("\n" + "-" * 50)
    print("Step 3.1: 95%分位数阈值计算")
    print("-" * 50)

    threshold_records = []
    for city in CITY_LIST:
        city_df = df[df['city'] == city]
        valid_zones = get_valid_zones(city)
        for col in valid_zones:
            if col in city_df.columns and city_df[col].notna().sum() > 0:
                series = city_df[col].dropna()
                q90 = series.quantile(0.90)
                q95 = series.quantile(0.95)
                q98 = series.quantile(0.98)
                max_val = series.max()
                ratio = round(q95 / max_val, 4) if max_val > 0 else 0
                threshold_records.append({
                    'city': city,
                    'zone': col,
                    'q90_threshold': round(q90, 4),
                    'q95_threshold': round(q95, 4),
                    'q98_threshold': round(q98, 4),
                    'max_value': round(max_val, 4),
                    'q95_to_max_ratio': ratio,
                })
                print(f"  {city}/{col}: q95={q95:.2f}, max={max_val:.2f}, ratio={ratio:.4f}"
                      f"{' ⚠️ ratio<0.70' if ratio < 0.70 else ''}"
                      f"{' ⚠️ ratio>0.95' if ratio > 0.95 else ''}")

    threshold_df = pd.DataFrame(threshold_records)
    save_dataframe(threshold_df, 'ch03_peak_thresholds.csv', OUTPUT_DIR, index=False)
    print(f"  覆盖 {threshold_df['city'].nunique()} 城市, {len(threshold_df)} 个zone")
    print(f"  ratio范围: [{threshold_df['q95_to_max_ratio'].min():.4f}, {threshold_df['q95_to_max_ratio'].max():.4f}]")
    print(f"  所有阈值>0: {(threshold_df['q95_threshold'] > 0).all()}")
    return threshold_df


# ============================================================
# Step 3.2: 峰值事件提取（双产物：明细+聚合摘要）
# ============================================================
def step_3_2_peak_event_extraction(df, zone_cols, threshold_df):
    """标记超出阈值的峰值点，输出完整明细和聚合摘要"""
    print("\n" + "-" * 50)
    print("Step 3.2: 峰值事件提取")
    print("-" * 50)

    peak_events = []
    summary_records = []

    for city in CITY_LIST:
        city_df = df[df['city'] == city]
        total_points = len(city_df)
        valid_zones = get_valid_zones(city)
        for col in valid_zones:
            if col in city_df.columns and city_df[col].notna().sum() > 0:
                threshold = threshold_df[
                    (threshold_df['city'] == city) & (threshold_df['zone'] == col)
                ]['q95_threshold'].values[0]
                mask = city_df[col] > threshold
                peak_count = mask.sum()

                if peak_count > 0:
                    peak_df = city_df[mask][[col]].copy()
                    peak_df = peak_df.rename(columns={col: 'peak_load_kw'})
                    peak_df['city'] = city
                    peak_df['zone'] = col
                    peak_df['threshold_kw'] = threshold
                    peak_df['excess_ratio_pct'] = ((peak_df['peak_load_kw'] - threshold) / threshold * 100).round(2)
                    peak_events.append(peak_df)

                # 聚合摘要
                summary_records.append({
                    'city': city,
                    'zone': col,
                    'total_data_points': total_points,
                    'total_peak_count': int(peak_count),
                    'peak_ratio_pct': round(peak_count / total_points * 100, 2) if total_points > 0 else 0,
                    'avg_excess_ratio_pct': round(((city_df.loc[mask, col] - threshold) / threshold * 100).mean(), 2) if peak_count > 0 else 0,
                    'max_excess_ratio_pct': round(((city_df.loc[mask, col] - threshold) / threshold * 100).max(), 2) if peak_count > 0 else 0,
                    'avg_peak_load_kw': round(city_df.loc[mask, col].mean(), 4) if peak_count > 0 else 0,
                    'max_peak_load_kw': round(city_df.loc[mask, col].max(), 4) if peak_count > 0 else 0,
                })

    # 产物A: 完整明细
    if peak_events:
        all_peaks = pd.concat(peak_events)
        all_peaks = all_peaks.sort_index()
    else:
        all_peaks = pd.DataFrame()
        print("  ⚠️ 未检测到峰值事件，请检查阈值设置")

    save_dataframe(all_peaks, 'ch03_peak_events.csv', OUTPUT_DIR, index=True)
    print(f"  峰值事件明细: {len(all_peaks)} 行")

    # 产物B: 聚合摘要
    summary_df = pd.DataFrame(summary_records)
    save_dataframe(summary_df, 'ch03_peak_events_summary.csv', OUTPUT_DIR, index=False)
    print(f"  聚合摘要: {len(summary_df)} 个zone")

    # 质量检查
    total_data = len(df)
    peak_ratio = len(all_peaks) / total_data * 100 if total_data > 0 else 0
    print(f"  峰值占比: {peak_ratio:.2f}% (理论~5%)")
    if peak_ratio < 1:
        print("  ⚠️ 峰值占比<1%，阈值可能过高")
    elif peak_ratio > 10:
        print("  ⚠️ 峰值占比>10%，阈值可能过低")

    return all_peaks, summary_df


# ============================================================
# Step 3.3: 峰值持续时长统计（双口径：城市聚合+单Zone精确）
# ============================================================
def step_3_3_peak_duration_stats(df, zone_cols, threshold_df):
    """归并连续峰值片段，分别按城市聚合和单Zone计算持续时长"""
    print("\n" + "-" * 50)
    print("Step 3.3: 峰值持续时长统计")
    print("-" * 50)

    all_duration_records = []

    # --- 口径A: 城市聚合（任一zone超阈即算峰值时段） ---
    print("  [口径A] 城市聚合...")
    for city in CITY_LIST:
        city_df = df[df['city'] == city]
        is_any_peak = pd.Series(0, index=city_df.index, dtype=int)
        valid_zones = get_valid_zones(city)
        for col in valid_zones:
            if col in city_df.columns and city_df[col].notna().sum() > 0:
                threshold = threshold_df[
                    (threshold_df['city'] == city) & (threshold_df['zone'] == col)
                ]['q95_threshold'].values[0]
                is_any_peak = is_any_peak | (city_df[col] > threshold).astype(int)

        # shift()+cumsum() 归并连续片段
        group_id = (is_any_peak != is_any_peak.shift()).cumsum()
        # 仅保留峰值片段的group_id
        peak_mask = is_any_peak == 1
        peak_group_ids = group_id[peak_mask].unique()

        for gid in peak_group_ids:
            group = city_df[peak_mask & (group_id == gid)]
            duration_minutes = len(group) * 10
            all_duration_records.append({
                'scope': 'city_aggregated',
                'city': city,
                'zone': 'all_zones',
                'group_id': gid,
                'start_time': group.index.min(),
                'end_time': group.index.max(),
                'duration_minutes': duration_minutes,
                'duration_hours': round(duration_minutes / 60, 2),
            })

    # --- 口径B: 单Zone精确 ---
    print("  [口径B] 单Zone精确...")
    for city in CITY_LIST:
        city_df = df[df['city'] == city]
        valid_zones = get_valid_zones(city)
        for col in valid_zones:
            if col in city_df.columns and city_df[col].notna().sum() > 0:
                threshold = threshold_df[
                    (threshold_df['city'] == city) & (threshold_df['zone'] == col)
                ]['q95_threshold'].values[0]
                is_peak = (city_df[col] > threshold).astype(int)
                group_id = (is_peak != is_peak.shift()).cumsum()
                peak_mask = is_peak == 1
                peak_group_ids = group_id[peak_mask].unique()

                for gid in peak_group_ids:
                    group = city_df[peak_mask & (group_id == gid)]
                    duration_minutes = len(group) * 10
                    all_duration_records.append({
                        'scope': 'zone_specific',
                        'city': city,
                        'zone': col,
                        'group_id': gid,
                        'start_time': group.index.min(),
                        'end_time': group.index.max(),
                        'duration_minutes': duration_minutes,
                        'duration_hours': round(duration_minutes / 60, 2),
                    })

    duration_df = pd.DataFrame(all_duration_records)
    save_dataframe(duration_df, 'ch03_peak_duration_stats.csv', OUTPUT_DIR, index=False)

    # 质量检查
    city_agg = duration_df[duration_df['scope'] == 'city_aggregated']
    zone_spec = duration_df[duration_df['scope'] == 'zone_specific']
    print(f"  城市聚合片段: {len(city_agg)} 个")
    print(f"  单Zone片段: {len(zone_spec)} 个")

    if len(duration_df) > 0:
        print(f"  持续时长统计(全部):")
        print(f"    min={duration_df['duration_minutes'].min()}min, "
              f"mean={duration_df['duration_minutes'].mean():.1f}min, "
              f"max={duration_df['duration_minutes'].max()}min")

        long_events = duration_df[duration_df['duration_minutes'] > 1440]  # >24h
        if len(long_events) > 0:
            print(f"  ⚠️ 存在 {len(long_events)} 个持续>24h的片段，可能存在数据质量问题")

    return duration_df


# ============================================================
# Step 3.4: 峰值小时分布
# ============================================================
def step_3_4_peak_hourly_distribution(all_peaks):
    """绘制4城市峰值事件的小时分布柱状图"""
    print("\n" + "-" * 50)
    print("Step 3.4: 峰值小时分布")
    print("-" * 50)

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()

    for i, city in enumerate(CITY_LIST):
        city_peaks = all_peaks[all_peaks['city'] == city]
        hourly_counts = city_peaks.groupby(city_peaks.index.hour).size().reindex(range(24), fill_value=0)

        ax = axes[i]
        bars = ax.bar(hourly_counts.index, hourly_counts.values,
                      color=CITY_COLORS[city], alpha=0.85, edgecolor='white', linewidth=0.5)
        ax.set_title(f'{city} - Peak Hourly Distribution', fontsize=13, fontweight='bold')
        ax.set_xlabel('Hour', fontsize=11)
        ax.set_ylabel('Peak Event Count', fontsize=11)
        ax.set_xticks(range(0, 24, 2))
        ax.set_xlim(-0.5, 23.5)
        ax.grid(True, alpha=0.3, axis='y')

        # 标注峰值最高的3个小时
        top3 = hourly_counts.nlargest(3)
        for h, cnt in top3.items():
            ax.annotate(f'{cnt}', xy=(h, cnt), xytext=(0, 4),
                        textcoords='offset points', ha='center', fontsize=9, fontweight='bold')

        print(f"  {city}: top3时段 = {top3.index.tolist()}, 总峰值 = {hourly_counts.sum()}")

    plt.suptitle('Peak Event Hourly Distribution by City', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    save_figure(fig, 'ch03_peak_hourly_distribution.png', OUTPUT_DIR)


# ============================================================
# Step 3.5: 峰值季节+年度分布
# ============================================================
def step_3_5_peak_seasonal_distribution(all_peaks):
    """绘制4城市峰值事件的季节分布柱状图（含年度维度）"""
    print("\n" + "-" * 50)
    print("Step 3.5: 峰值季节+年度分布")
    print("-" * 50)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for i, city in enumerate(CITY_LIST):
        city_peaks = all_peaks[all_peaks['city'] == city].copy()
        city_peaks['season'] = city_peaks.index.month.map(SEASON_MAP)
        city_peaks['year'] = city_peaks.index.year

        # 按季节+年度交叉统计
        season_year = city_peaks.groupby(['year', 'season']).size().unstack(fill_value=0)
        season_year = season_year.reindex(columns=SEASON_ORDER, fill_value=0)

        ax = axes[i]
        x = np.arange(len(SEASON_ORDER))
        width = 0.8 / max(len(season_year), 1)
        years = season_year.index.tolist()

        for j, year in enumerate(years):
            offset = (j - len(years) / 2 + 0.5) * width
            vals = season_year.loc[year].values
            bars = ax.bar(x + offset, vals, width * 0.9,
                          label=str(year), alpha=0.85, edgecolor='white', linewidth=0.5)
            # 标注数值
            for k, v in enumerate(vals):
                if v > 0:
                    ax.text(x[k] + offset, v + 5, str(int(v)),
                            ha='center', va='bottom', fontsize=8)

        ax.set_title(f'{city} - Peak Seasonal Distribution', fontsize=13, fontweight='bold')
        ax.set_xlabel('Season', fontsize=11)
        ax.set_ylabel('Peak Event Count', fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(SEASON_ORDER, fontsize=10)
        ax.legend(title='Year', fontsize=9, title_fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')

        # 打印年度趋势
        yearly_totals = city_peaks.groupby('year').size()
        print(f"  {city}: 年度峰值数 = {yearly_totals.to_dict()}")

    plt.suptitle('Peak Event Seasonal Distribution by City (with Year Breakdown)',
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    save_figure(fig, 'ch03_peak_seasonal_distribution.png', OUTPUT_DIR)


# ============================================================
# Step 3.6: 峰值时空热力图
# ============================================================
def step_3_6_peak_spacetime_heatmap(all_peaks):
    """绘制每城市 hour×month 峰值事件频次热力图"""
    print("\n" + "-" * 50)
    print("Step 3.6: 峰值时空热力图")
    print("-" * 50)

    for city in CITY_LIST:
        city_peaks = all_peaks[all_peaks['city'] == city].copy()
        city_peaks['hour'] = city_peaks.index.hour
        city_peaks['month'] = city_peaks.index.month

        pivot = city_peaks.pivot_table(
            index='hour', columns='month', values='peak_load_kw',
            aggfunc='count', fill_value=0
        )
        # 确保所有小时0-23和月份1-12都存在
        pivot = pivot.reindex(index=range(24), columns=range(1, 13), fill_value=0)
        pivot.columns = [f'{m}' for m in pivot.columns]

        fig, ax = plt.subplots(figsize=(14, 8))
        sns.heatmap(pivot, ax=ax, cmap='YlOrRd', annot=True, fmt='d',
                    linewidths=0.5, linecolor='white',
                    cbar_kws={'label': 'Peak Event Count'})
        ax.set_title(f'{city} - Peak Spacetime Heatmap (Hour x Month)',
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Hour', fontsize=12)
        plt.tight_layout()

        slug = CITY_SLUG_MAP[city]
        save_figure(fig, f'ch03_peak_spacetime_heatmap_{slug}.png', OUTPUT_DIR)
        print(f"  {city}: 峰值聚集区域 = 月份{pivot.sum(axis=0).nlargest(3).index.tolist()}, "
              f"时段{pivot.sum(axis=1).nlargest(3).index.tolist()}")


# ============================================================
# Step 3.7: 峰值成因归因（含年度维度）
# ============================================================
def step_3_7_peak_attribution(all_peaks):
    """五维交叉分析: city x year x season x hour x is_weekend"""
    print("\n" + "-" * 50)
    print("Step 3.7: 峰值成因归因")
    print("-" * 50)

    attribution = all_peaks.copy()
    attribution['hour'] = attribution.index.hour
    attribution['month'] = attribution.index.month
    attribution['year'] = attribution.index.year
    attribution['season'] = attribution['month'].map(SEASON_MAP)
    attribution['is_weekend'] = attribution.index.dayofweek.isin([5, 6]).astype(int)

    # 五维交叉统计
    cross_tab = attribution.groupby(['city', 'year', 'season', 'hour', 'is_weekend']).agg(
        peak_count=('peak_load_kw', 'count'),
        avg_peak_load=('peak_load_kw', 'mean'),
        max_peak_load=('peak_load_kw', 'max'),
    ).reset_index()
    cross_tab = cross_tab.sort_values('peak_count', ascending=False)
    cross_tab['avg_peak_load'] = cross_tab['avg_peak_load'].round(4)
    cross_tab['max_peak_load'] = cross_tab['max_peak_load'].round(4)

    save_dataframe(cross_tab, 'ch03_peak_attribution.csv', OUTPUT_DIR, index=False)
    print(f"  交叉表维度: {cross_tab.shape}")
    print(f"  Top5 峰值组合:")
    print(cross_tab.head(5).to_string(index=False))

    # 年度趋势汇总
    yearly = attribution.groupby(['city', 'year']).agg(
        total_peaks=('peak_load_kw', 'count'),
        avg_excess_ratio=('excess_ratio_pct', 'mean'),
        max_peak_load=('peak_load_kw', 'max'),
    ).reset_index()
    print(f"\n  年度趋势:")
    print(yearly.to_string(index=False))

    return cross_tab


# ============================================================
# Step 3.8: 异常峰值研判（30min平滑 + 1h差分 + 3σ）
# ============================================================
def step_3_8_anomaly_peak_detection(df, zone_cols, threshold_df):
    """区分规律性正常高峰与突发型异常峰值"""
    print("\n" + "-" * 50)
    print("Step 3.8: 异常峰值研判")
    print("-" * 50)

    anomaly_records = []

    for city in CITY_LIST:
        city_df = df[df['city'] == city]
        valid_zones = get_valid_zones(city)
        for col in valid_zones:
            if col in city_df.columns and city_df[col].notna().sum() > 0:
                series = city_df[col]

                # Step 1: 30min滚动平滑（窗口=3，对应30min@10min粒度）
                smoothed = series.rolling(window=3, center=True, min_periods=1).mean()

                # Step 2: 1小时差分（periods=6，对应60min@10min粒度）
                diff = smoothed.diff(periods=6).abs()

                # Step 3: 3σ阈值
                diff_mean = diff.mean()
                diff_std = diff.std()
                anomaly_threshold = diff_mean + 3 * diff_std
                anomaly_mask = diff > anomaly_threshold

                # Step 4: 峰值标记
                peak_threshold = threshold_df[
                    (threshold_df['city'] == city) & (threshold_df['zone'] == col)
                ]['q95_threshold'].values[0]
                peak_mask = series > peak_threshold

                # 异常峰值 = 既是峰值又是突变
                anomaly_peak_mask = anomaly_mask & peak_mask
                regular_peak_mask = peak_mask & ~anomaly_mask

                total = int(peak_mask.sum())
                anomaly = int(anomaly_peak_mask.sum())
                regular = int(regular_peak_mask.sum())
                ratio = round(anomaly / total * 100, 2) if total > 0 else 0

                anomaly_records.append({
                    'city': city,
                    'zone': col,
                    'total_peaks': total,
                    'anomaly_peaks': anomaly,
                    'regular_peaks': regular,
                    'anomaly_ratio': ratio,
                })

                print(f"  {city}/{col}: total={total}, anomaly={anomaly}, regular={regular}, ratio={ratio}%"
                      f"{' ⚠️ ratio>50%' if ratio > 50 else ''}")

    anomaly_df = pd.DataFrame(anomaly_records)
    save_dataframe(anomaly_df, 'ch03_anomaly_peak_flags.csv', OUTPUT_DIR, index=False)

    # 质量检查
    print(f"\n  总体异常比例: {anomaly_df['anomaly_ratio'].mean():.2f}%")
    if (anomaly_df['anomaly_peaks'] + anomaly_df['regular_peaks'] == anomaly_df['total_peaks']).all():
        print("  ✅ anomaly + regular == total (逐行验证通过)")
    else:
        print("  ⚠️ anomaly + regular != total，数据不一致")

    return anomaly_df


# ============================================================
# 主函数
# ============================================================
def main():
    # 加载数据
    df, zone_cols, stats_df = load_data()

    # Step 3.1: 阈值计算
    threshold_df = step_3_1_peak_thresholds(df, zone_cols)

    # Step 3.2: 峰值事件提取
    all_peaks, peak_summary = step_3_2_peak_event_extraction(df, zone_cols, threshold_df)

    # Step 3.3: 持续时长统计
    duration_df = step_3_3_peak_duration_stats(df, zone_cols, threshold_df)

    # Step 3.4: 小时分布
    step_3_4_peak_hourly_distribution(all_peaks)

    # Step 3.5: 季节+年度分布
    step_3_5_peak_seasonal_distribution(all_peaks)

    # Step 3.6: 时空热力图
    step_3_6_peak_spacetime_heatmap(all_peaks)

    # Step 3.7: 成因归因
    step_3_7_peak_attribution(all_peaks)

    # Step 3.8: 异常峰值
    step_3_8_anomaly_peak_detection(df, zone_cols, threshold_df)

    # === 产物汇总 ===
    print("\n" + "=" * 60)
    print("产物汇总")
    print("=" * 60)
    artifacts = sorted(os.listdir(OUTPUT_DIR))
    for a in artifacts:
        fpath = os.path.join(OUTPUT_DIR, a)
        size_kb = os.path.getsize(fpath) / 1024
        print(f"  {a} ({size_kb:.1f} KB)")
    print(f"\n共 {len(artifacts)} 个产物")
    print("=" * 60)
    print("Prompt-03 执行完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
