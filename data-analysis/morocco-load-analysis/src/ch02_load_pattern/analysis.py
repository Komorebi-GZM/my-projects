"""
Prompt-02: 用电负荷特征挖掘与用电规律分析
基于第一章预处理后的标准化数据，从多维度挖掘摩洛哥四城市用电行为规律。

覆盖步骤:
  - Step 2.1: 描述性统计总表
  - Step 2.2: 负荷率与变异系数计算
  - Step 2.3: 日内24h负荷曲线
  - Step 2.4: 工作日vs周末对比
  - Step 2.5: 周内负荷热力图
  - Step 2.6: 跨城市横向对比
  - Step 2.7: 居民/工业负荷分层 (KMeans)
  - Step 2.8: 居民vs工业对比分析

产物输出到: outputs/ch02_load_pattern_analysis/
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
import matplotlib.font_manager as fm
import seaborn as sns
from sklearn.cluster import KMeans

# 导入项目工具
from utils.config import CITIES, OUTPUT_BASE, PLT_STYLE
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
OUTPUT_DIR = os.path.join(OUTPUT_BASE, 'ch02_load_pattern_analysis')

DAY_NAMES_CN = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
CITY_LIST = ['Laayoune', 'Boujdour', 'Foum eloued', 'Marrakech']


def load_data():
    """加载预处理后的特征工程数据"""
    print("=" * 60)
    print("Prompt-02: 用电负荷特征挖掘与用电规律分析")
    print("=" * 60)
    print(f"\n[数据加载] {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE, parse_dates=['DateTime'])
    df = df.set_index('DateTime').sort_index()
    print(f"  数据维度: {df.shape}")
    print(f"  城市: {df['city'].unique().tolist()}")
    zone_cols = [c for c in df.columns if c.startswith('zone')]
    print(f"  Zone列: {zone_cols}")
    print(f"  时间范围: {df.index.min()} ~ {df.index.max()}")
    return df, zone_cols


# ============================================================
# Step 2.1: 描述性统计总表
# ============================================================
def step_2_1_descriptive_stats(df, zone_cols):
    """按城市+zone计算描述性统计指标"""
    print("\n" + "-" * 50)
    print("Step 2.1: 描述性统计总表")
    print("-" * 50)

    stats_records = []
    for city in CITY_LIST:
        city_df = df[df['city'] == city]
        for col in zone_cols:
            if col in city_df.columns and city_df[col].notna().sum() > 0:
                series = city_df[col].dropna()
                stats_records.append({
                    'city': city,
                    'zone': col,
                    'count': len(series),
                    'mean': round(series.mean(), 4),
                    'median': round(series.median(), 4),
                    'std': round(series.std(), 4),
                    'min': round(series.min(), 4),
                    'max': round(series.max(), 4),
                    'skew': round(series.skew(), 4),
                    'kurtosis': round(series.kurtosis(), 4),
                })

    stats_df = pd.DataFrame(stats_records)
    save_dataframe(stats_df, 'ch02_descriptive_stats.csv', OUTPUT_DIR, index=False)
    print(f"  覆盖 {stats_df['city'].nunique()} 城市, {len(stats_df)} 个zone")
    print(f"  所有均值>0: {(stats_df['mean'] > 0).all()}")
    print(f"  无NaN: {stats_df.isnull().sum().sum() == 0}")
    return stats_df


# ============================================================
# Step 2.2: 负荷率与变异系数
# ============================================================
def step_2_2_load_rate_cv(df, zone_cols):
    """计算负荷率和变异系数"""
    print("\n" + "-" * 50)
    print("Step 2.2: 负荷率与变异系数")
    print("-" * 50)

    metrics = []
    for city in CITY_LIST:
        city_df = df[df['city'] == city]
        for col in zone_cols:
            if col in city_df.columns and city_df[col].notna().sum() > 0:
                mean_val = city_df[col].mean()
                max_val = city_df[col].max()
                std_val = city_df[col].std()
                metrics.append({
                    'city': city,
                    'zone': col,
                    'mean_kW': round(mean_val, 2),
                    'max_kW': round(max_val, 2),
                    'std_kW': round(std_val, 2),
                    'load_rate': round(mean_val / max_val, 4) if max_val > 0 else 0,
                    'cv': round(std_val / mean_val, 4) if mean_val > 0 else 0,
                })

    metrics_df = pd.DataFrame(metrics)
    save_dataframe(metrics_df, 'ch02_load_rate_cv.csv', OUTPUT_DIR, index=False)
    print(f"  平均负荷率: {metrics_df['load_rate'].mean():.4f}")
    print(f"  平均CV: {metrics_df['cv'].mean():.4f}")
    return metrics_df


# ============================================================
# Step 2.3: 日内24h负荷曲线
# ============================================================
def step_2_3_daily_load_curve(df, zone_cols):
    """绘制每个城市每个zone的24小时平均负荷曲线"""
    print("\n" + "-" * 50)
    print("Step 2.3: 日内24h负荷曲线")
    print("-" * 50)

    for city in CITY_LIST:
        city_df = df[df['city'] == city]
        city_zone_cols = [c for c in zone_cols if c in city_df.columns and city_df[c].notna().sum() > 0]

        hourly = city_df.groupby('hour')[city_zone_cols].mean()

        fig, ax = plt.subplots(figsize=(14, 5))
        for col in city_zone_cols:
            ax.plot(hourly.index, hourly[col], label=col, linewidth=1.5, marker='o', markersize=3)

        ax.set_title(f'{city} - 24h Average Load Curve', fontsize=14, fontweight='bold')
        ax.set_xlabel('Hour', fontsize=12)
        ax.set_ylabel('Load (kW)', fontsize=12)
        ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xticks(range(0, 24))
        ax.set_xlim(0, 23)
        plt.tight_layout()

        fname = f'ch02_daily_load_curve_{city.lower()}.png'
        save_figure(fig, fname, OUTPUT_DIR)
        print(f"  {city}: {len(city_zone_cols)} zones")


# ============================================================
# Step 2.4: 工作日vs周末对比
# ============================================================
def step_2_4_weekday_vs_weekend(df, zone_cols):
    """工作日与周末平均负荷曲线对比"""
    print("\n" + "-" * 50)
    print("Step 2.4: 工作日vs周末对比")
    print("-" * 50)

    for city in CITY_LIST:
        city_df = df[df['city'] == city]
        city_zone_cols = [c for c in zone_cols if c in city_df.columns and city_df[c].notna().sum() > 0]

        # 计算所有zone的平均值作为综合负荷
        city_df = city_df.copy()
        city_df['avg_load'] = city_df[city_zone_cols].mean(axis=1)

        weekday_hourly = city_df[city_df['is_weekend'] == 0].groupby('hour')['avg_load'].mean()
        weekend_hourly = city_df[city_df['is_weekend'] == 1].groupby('hour')['avg_load'].mean()

        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(weekday_hourly.index, weekday_hourly.values, label='Weekday', linewidth=2, color='#2196F3', marker='o', markersize=4)
        ax.plot(weekend_hourly.index, weekend_hourly.values, label='Weekend', linewidth=2, color='#FF5722', marker='s', markersize=4)

        # 填充差异区域
        ax.fill_between(weekday_hourly.index, weekday_hourly.values, weekend_hourly.values,
                        alpha=0.15, color='gray')

        ax.set_title(f'{city} - Weekday vs Weekend Load Comparison', fontsize=14, fontweight='bold')
        ax.set_xlabel('Hour', fontsize=12)
        ax.set_ylabel('Average Load (kW)', fontsize=12)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_xticks(range(0, 24))
        ax.set_xlim(0, 23)
        plt.tight_layout()

        fname = f'ch02_weekday_vs_weekend_{city.lower()}.png'
        save_figure(fig, fname, OUTPUT_DIR)
        print(f"  {city}: weekday_mean={weekday_hourly.mean():.2f}, weekend_mean={weekend_hourly.mean():.2f}")


# ============================================================
# Step 2.5: 周内负荷热力图
# ============================================================
def step_2_5_weekly_heatmap(df, zone_cols):
    """绘制小时×星期几的热力图"""
    print("\n" + "-" * 50)
    print("Step 2.5: 周内负荷热力图")
    print("-" * 50)

    for city in CITY_LIST:
        city_df = df[df['city'] == city].copy()
        city_zone_cols = [c for c in zone_cols if c in city_df.columns and city_df[c].notna().sum() > 0]
        city_df['avg_load'] = city_df[city_zone_cols].mean(axis=1)

        pivot = city_df.pivot_table(values='avg_load', index='hour', columns='day_of_week', aggfunc='mean')
        pivot.columns = DAY_NAMES_CN

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(pivot, ax=ax, cmap='YlOrRd', annot=True, fmt='.1f', linewidths=0.5,
                    cbar_kws={'label': 'Load (kW)'})
        ax.set_title(f'{city} - Weekly Load Heatmap (kW)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Day of Week', fontsize=12)
        ax.set_ylabel('Hour', fontsize=12)
        plt.tight_layout()

        fname = f'ch02_weekly_heatmap_{city.lower()}.png'
        save_figure(fig, fname, OUTPUT_DIR)
        print(f"  {city}: load range [{pivot.min().min():.1f}, {pivot.max().max():.1f}] kW")


# ============================================================
# Step 2.6: 跨城市横向对比
# ============================================================
def step_2_6_cross_city_comparison(df, zone_cols):
    """四城市同坐标系负荷曲线对比"""
    print("\n" + "-" * 50)
    print("Step 2.6: 跨城市横向对比")
    print("-" * 50)

    city_colors = {
        'Laayoune': '#2196F3',
        'Boujdour': '#4CAF50',
        'Foum eloued': '#FF9800',
        'Marrakech': '#E91E63',
    }

    # 计算每个城市的综合平均负荷（所有zone均值）
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()

    for i, city in enumerate(CITY_LIST):
        city_df = df[df['city'] == city].copy()
        city_zone_cols = [c for c in zone_cols if c in city_df.columns and city_df[c].notna().sum() > 0]
        city_df['avg_load'] = city_df[city_zone_cols].mean(axis=1)
        hourly = city_df.groupby('hour')['avg_load'].mean()

        ax = axes[i]
        ax.plot(hourly.index, hourly.values, linewidth=2, color=city_colors[city], marker='o', markersize=3)
        ax.fill_between(hourly.index, hourly.values, alpha=0.15, color=city_colors[city])
        ax.set_title(f'{city}', fontsize=13, fontweight='bold')
        ax.set_xlabel('Hour', fontsize=10)
        ax.set_ylabel('Load (kW)', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xticks(range(0, 24, 2))
        ax.set_xlim(0, 23)

    plt.suptitle('Cross-City 24h Load Curve Comparison', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()

    save_figure(fig, 'ch02_cross_city_comparison.png', OUTPUT_DIR)

    # 额外：4城市叠加在同一图
    fig2, ax2 = plt.subplots(figsize=(14, 6))
    for city in CITY_LIST:
        city_df = df[df['city'] == city].copy()
        city_zone_cols = [c for c in zone_cols if c in city_df.columns and city_df[c].notna().sum() > 0]
        city_df['avg_load'] = city_df[city_zone_cols].mean(axis=1)
        hourly = city_df.groupby('hour')['avg_load'].mean()
        ax2.plot(hourly.index, hourly.values, linewidth=2, color=city_colors[city],
                 label=city, marker='o', markersize=3)

    ax2.set_title('Cross-City 24h Load Curve - Overlay', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Hour', fontsize=12)
    ax2.set_ylabel('Average Load (kW)', fontsize=12)
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(range(0, 24))
    ax2.set_xlim(0, 23)
    plt.tight_layout()

    save_figure(fig2, 'ch02_cross_city_comparison_overlay.png', OUTPUT_DIR)
    print("  生成2张跨城市对比图（子图+叠加）")


# ============================================================
# Step 2.7: 居民/工业负荷分层 (KMeans)
# ============================================================
def step_2_7_residential_industrial_clustering(df, zone_cols):
    """基于CV和峰谷比进行KMeans二分类"""
    print("\n" + "-" * 50)
    print("Step 2.7: 居民/工业负荷分层 (KMeans)")
    print("-" * 50)

    cluster_features = []
    for city in CITY_LIST:
        city_df = df[df['city'] == city]
        for col in zone_cols:
            if col in city_df.columns and city_df[col].notna().sum() > 0:
                series = city_df[col].dropna()
                hourly = city_df.groupby('hour')[col].mean()
                cv = series.std() / series.mean() if series.mean() > 0 else 0
                peak_valley_ratio = hourly.max() / hourly.min() if hourly.min() > 0 else 0
                cluster_features.append({
                    'city': city,
                    'zone': col,
                    'cv': round(cv, 4),
                    'peak_valley_ratio': round(peak_valley_ratio, 4),
                    'mean_kW': round(series.mean(), 2),
                    'max_kW': round(series.max(), 2),
                })

    cluster_df = pd.DataFrame(cluster_features)
    features = cluster_df[['cv', 'peak_valley_ratio']].values

    # KMeans聚类
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    cluster_df['cluster'] = kmeans.fit_predict(features)

    # 分析簇特征，判断哪个是工业/居民
    for c in [0, 1]:
        subset = cluster_df[cluster_df['cluster'] == c]
        print(f"  Cluster {c}: avg_CV={subset['cv'].mean():.4f}, "
              f"avg_peak_valley_ratio={subset['peak_valley_ratio'].mean():.2f}, "
              f"n_zones={len(subset)}")

    # 判断规则: 工业负荷特征为低CV、高峰谷比(基荷高); 居民为高CV、高峰谷比(峰谷差大)
    # 更准确: 工业低CV(平稳), 居民高CV(波动大)
    cluster_means = cluster_df.groupby('cluster')['cv'].mean()
    industrial_cluster = cluster_means.idxmin()  # 低CV = 工业
    residential_cluster = cluster_means.idxmax()  # 高CV = 居民

    cluster_df['load_type'] = cluster_df['cluster'].map({
        industrial_cluster: 'Industrial',
        residential_cluster: 'Residential',
    })

    print(f"\n  分类结果: Industrial=Cluster {industrial_cluster}, Residential=Cluster {residential_cluster}")
    print(cluster_df[['city', 'zone', 'cv', 'peak_valley_ratio', 'load_type']].to_string(index=False))

    # 保存分类结果
    save_dataframe(cluster_df, 'ch02_residential_industrial_class.csv', OUTPUT_DIR, index=False)

    # 保存聚类中心
    centers_df = pd.DataFrame(kmeans.cluster_centers_, columns=['cv', 'peak_valley_ratio'])
    centers_df['cluster'] = [0, 1]
    centers_df['load_type'] = centers_df['cluster'].map({
        industrial_cluster: 'Industrial',
        residential_cluster: 'Residential',
    })
    print(f"\n  聚类中心:\n{centers_df.to_string(index=False)}")

    return cluster_df, industrial_cluster, residential_cluster


# ============================================================
# Step 2.8: 居民vs工业对比分析
# ============================================================
def step_2_8_res_vs_ind_comparison(df, zone_cols, cluster_df):
    """基于分类结果绘制居民vs工业对比图"""
    print("\n" + "-" * 50)
    print("Step 2.8: 居民vs工业对比分析")
    print("-" * 50)

    type_colors = {'Residential': '#E91E63', 'Industrial': '#2196F3'}

    # 收集各类型zone的日内曲线
    type_hourly = {}
    for load_type in ['Residential', 'Industrial']:
        zones = cluster_df[cluster_df['load_type'] == load_type]
        all_hourly = []
        for _, row in zones.iterrows():
            city = row['city']
            zone = row['zone']
            city_df = df[(df['city'] == city)]
            if zone in city_df.columns:
                hourly = city_df.groupby('hour')[zone].mean()
                all_hourly.append(hourly)
        if all_hourly:
            combined = pd.concat(all_hourly, axis=1).mean(axis=1)
            type_hourly[load_type] = combined

    # 图1: 日内曲线对比
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    ax = axes[0]
    for load_type, hourly in type_hourly.items():
        ax.plot(hourly.index, hourly.values, linewidth=2.5,
                color=type_colors[load_type], label=load_type, marker='o', markersize=4)
    ax.set_title('Residential vs Industrial - 24h Load Curve', fontsize=13, fontweight='bold')
    ax.set_xlabel('Hour', fontsize=11)
    ax.set_ylabel('Average Load (kW)', fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(0, 24))
    ax.set_xlim(0, 23)

    # 图2: 特征对比柱状图
    ax2 = axes[1]
    type_stats = cluster_df.groupby('load_type').agg({
        'cv': 'mean',
        'peak_valley_ratio': 'mean',
        'mean_kW': 'mean',
    }).round(4)

    x = np.arange(len(type_stats.index))
    width = 0.25
    bars1 = ax2.bar(x - width, type_stats['cv'], width, label='CV', color='#FF9800')
    bars2 = ax2.bar(x, type_stats['peak_valley_ratio'], width, label='Peak/Valley Ratio', color='#4CAF50')
    bars3 = ax2.bar(x + width, type_stats['mean_kW'] / type_stats['mean_kW'].max(), width,
                     label='Mean Load (normalized)', color='#9C27B0')

    ax2.set_title('Residential vs Industrial - Feature Comparison', fontsize=13, fontweight='bold')
    ax2.set_xlabel('Load Type', fontsize=11)
    ax2.set_ylabel('Value', fontsize=11)
    ax2.set_xticks(x)
    ax2.set_xticklabels(type_stats.index, fontsize=11)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')

    # 在柱状图上标注数值
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax2.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    save_figure(fig, 'ch02_res_vs_ind_comparison.png', OUTPUT_DIR)

    # 打印统计摘要
    print("\n  类型统计摘要:")
    summary = cluster_df.groupby('load_type').agg({
        'cv': ['mean', 'std'],
        'peak_valley_ratio': ['mean', 'std'],
        'mean_kW': ['mean', 'std'],
    }).round(4)
    print(summary.to_string())


# ============================================================
# 主函数
# ============================================================
def main():
    # 加载数据
    df, zone_cols = load_data()

    # Step 2.1: 描述性统计总表
    stats_df = step_2_1_descriptive_stats(df, zone_cols)

    # Step 2.2: 负荷率与变异系数
    metrics_df = step_2_2_load_rate_cv(df, zone_cols)

    # Step 2.3: 日内24h负荷曲线
    step_2_3_daily_load_curve(df, zone_cols)

    # Step 2.4: 工作日vs周末对比
    step_2_4_weekday_vs_weekend(df, zone_cols)

    # Step 2.5: 周内负荷热力图
    step_2_5_weekly_heatmap(df, zone_cols)

    # Step 2.6: 跨城市横向对比
    step_2_6_cross_city_comparison(df, zone_cols)

    # Step 2.7: 居民/工业负荷分层
    cluster_df, ind_cluster, res_cluster = step_2_7_residential_industrial_clustering(df, zone_cols)

    # Step 2.8: 居民vs工业对比分析
    step_2_8_res_vs_ind_comparison(df, zone_cols, cluster_df)

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
    print("Prompt-02 执行完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
