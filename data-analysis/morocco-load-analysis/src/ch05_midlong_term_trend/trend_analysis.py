"""
Prompt-05: 月度/季度中长期用电趋势分析
基于第一章清洗后的统一数据集，从中长期视角审视4城市负荷演化规律。

覆盖步骤:
  - Step 5.1: 多粒度重采样聚合（日度/月度/季度）
  - Step 5.2: STL时序分解（含短数据降级方案）
  - Step 5.3: 趋势项提取与可视化
  - Step 5.4: 季节性强度计算
  - Step 5.5: 季度负荷箱线图
  - Step 5.6: 月度负荷热力图
  - Step 5.7: 同比/环比分析

产物输出到: outputs/ch05_midlong_term_trend/
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
from statsmodels.tsa.seasonal import STL

# 导入项目工具
from utils.config import CITIES, OUTPUT_BASE, PLT_STYLE
from utils.data_loader import load_preprocessed
from utils.output_manager import save_dataframe, save_figure, ensure_dir

# === 中文字体配置 ===
plt.rcParams.update({
    'font.sans-serif': ['DejaVu Sans', 'SimHei', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei'],
    'axes.unicode_minus': False,
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'font.size': 12,
})

# === 全局配置 ===
INPUT_FILE = os.path.join(PROJECT_ROOT, 'outputs', 'ch01_data_preprocessing', 'ch01_cleaned_data.csv')
OUTPUT_DIR = os.path.join(OUTPUT_BASE, 'ch05_midlong_term_trend')
CITY_LIST = ['Laayoune', 'Boujdour', 'Foum eloued', 'Marrakech']
STL_PERIOD = 12
STL_MIN_OBS = 2 * STL_PERIOD  # 24

# 颜色方案
COLORS = {
    'Laayoune': 'steelblue',
    'Boujdour': 'darkorange',
    'Foum eloued': 'green',
    'Marrakech': 'red'
}

# 季度映射
QUARTER_MAP = {
    12: 'Q1(Winter)', 1: 'Q1(Winter)', 2: 'Q1(Winter)',
    3: 'Q2(Spring)',  4: 'Q2(Spring)',  5: 'Q2(Spring)',
    6: 'Q3(Summer)',  7: 'Q3(Summer)',  8: 'Q3(Summer)',
    9: 'Q4(Autumn)', 10: 'Q4(Autumn)', 11: 'Q4(Autumn)'
}
QUARTER_ORDER = ['Q1(Winter)', 'Q2(Spring)', 'Q3(Summer)', 'Q4(Autumn)']


# ================================================================
# Step 5.1: 多粒度重采样聚合
# ================================================================
def step_5_1_resample(df: pd.DataFrame) -> dict:
    """将10分钟高频数据聚合为日度/月度/季度平均负荷"""
    print('\n' + '=' * 60)
    print('Step 5.1: 多粒度重采样聚合')
    print('=' * 60)

    zone_cols = [c for c in df.columns if c.startswith('zone')]
    print(f"原始数据: {df.shape[0]}行, Zone列: {zone_cols}")
    print(f"城市: {df['city'].unique()}")

    resampled_data = {}
    monthly_avg_dict = {}
    monthly_sum_dict = {}

    for city in CITY_LIST:
        city_df = df[df['city'] == city].copy()

        # 等权均值（主口径）
        city_df['total_load'] = city_df[zone_cols].mean(axis=1)
        # 总量求和（辅口径）
        city_df['total_sum'] = city_df[zone_cols].sum(axis=1)

        # 多粒度聚合
        daily = city_df['total_load'].resample('D').mean()
        monthly = city_df['total_load'].resample('ME').mean()
        quarterly = city_df['total_load'].resample('QE').mean()

        # 总量口径月度
        monthly_sum = city_df['total_sum'].resample('ME').mean()

        # NaN检查与处理
        for freq_name, freq_series in [('daily', daily), ('monthly', monthly), ('quarterly', quarterly)]:
            nan_count = freq_series.isnull().sum()
            total_count = len(freq_series)
            if nan_count > 0:
                nan_ratio = nan_count / total_count * 100 if total_count > 0 else 0
                print(f"  [警告] {city} {freq_name}: {nan_count}/{total_count} NaN ({nan_ratio:.1f}%), 使用前向填充")
                freq_series = freq_series.ffill().bfill()
                if freq_name == 'daily':
                    daily = freq_series
                elif freq_name == 'monthly':
                    monthly = freq_series
                else:
                    quarterly = freq_series
            else:
                print(f"  {city} {freq_name}: 无NaN, 数据完整")

        resampled_data[city] = {
            'daily': daily,
            'monthly': monthly,
            'quarterly': quarterly
        }
        monthly_avg_dict[city] = monthly
        monthly_sum_dict[city] = monthly_sum

        print(f"{city}: 日度{len(daily)}行 ({daily.index.min().date()}~{daily.index.max().date()}), "
              f"月度{len(monthly)}行, 季度{len(quarterly)}行")
        print(f"  日度负荷范围: {daily.min():.1f}~{daily.max():.1f} kW, 均值: {daily.mean():.1f} kW")

    # 保存月度汇总数据（双口径）
    all_monthly_avg = pd.DataFrame()
    all_monthly_sum = pd.DataFrame()
    for city in CITY_LIST:
        all_monthly_avg = pd.concat([all_monthly_avg, monthly_avg_dict[city].to_frame(f'{city}_monthly_avg_kw')], axis=1)
        all_monthly_sum = pd.concat([all_monthly_sum, monthly_sum_dict[city].to_frame(f'{city}_monthly_sum_kw')], axis=1)

    all_monthly = pd.concat([all_monthly_avg, all_monthly_sum], axis=1)
    save_dataframe(all_monthly, 'ch05_daily_monthly_quarterly.csv', OUTPUT_DIR)
    print(f"\n月度汇总数据: {all_monthly.shape}, 双口径(等权均值+总量求和)")

    return resampled_data


# ================================================================
# Step 5.2: STL时序分解（含短数据降级方案）
# ================================================================
def step_5_2_stl_decomposition(resampled_data: dict) -> dict:
    """对每个城市执行STL分解，数据不足时降级为移动平均"""
    print('\n' + '=' * 60)
    print('Step 5.2: STL时序分解')
    print('=' * 60)

    stl_results = {}

    for city in CITY_LIST:
        monthly = resampled_data[city]['monthly']
        n_obs = len(monthly.dropna())
        print(f"\n{city}: 月度数据 {n_obs} 个月")

        if n_obs >= STL_MIN_OBS:
            # 正常STL分解
            method = 'STL'
            stl = STL(monthly, period=STL_PERIOD, robust=True)
            result = stl.fit()
            trend = result.trend
            seasonal = result.seasonal
            residual = result.resid
            observed = result.observed
            print(f"  方法: STL (period={STL_PERIOD}, robust=True)")
            print(f"  趋势范围: {trend.min():.1f}~{trend.max():.1f} kW")
            print(f"  季节项振幅: {seasonal.max() - seasonal.min():.1f} kW")
            print(f"  残差标准差: {residual.std():.1f} kW")
        else:
            # 降级：移动平均分解
            method = 'Moving Average'
            print(f"  [警告] {city}: 仅{n_obs}个月度数据点(<{STL_MIN_OBS})，使用移动平均替代STL")

            observed = monthly.copy()
            # 趋势项：3个月中心移动平均
            trend = observed.rolling(window=3, center=True).mean()
            trend = trend.bfill().ffill()
            # 季节项：各月历史均值 - 总均值
            monthly_mean = observed.mean()
            seasonal_pattern = observed.groupby(observed.index.month).mean() - monthly_mean
            seasonal = pd.Series(observed.index.month.map(seasonal_pattern).values, index=observed.index)
            # 残差项
            residual = observed - trend - seasonal
            print(f"  方法: 3-month Centered Moving Average (fallback)")
            print(f"  趋势范围: {trend.min():.1f}~{trend.max():.1f} kW")

        stl_results[city] = {
            'observed': observed,
            'trend': trend,
            'seasonal': seasonal,
            'residual': residual,
            'method': method
        }

        # 绘制分解图
        fig, axes = plt.subplots(4, 1, figsize=(14, 12), dpi=150, sharex=True)

        method_label = f'STL (period={STL_PERIOD}, robust=True)' if method == 'STL' else 'Moving Average (3M center)'
        title_suffix = '' if method == 'STL' else ' [MA Fallback - Data < 24 months]'

        axes[0].plot(observed, label='Observed', color='steelblue', linewidth=1.5)
        axes[0].set_title(f'{city} - Time Series Decomposition ({method_label}){title_suffix}',
                          fontsize=14, fontweight='bold')
        axes[0].legend(loc='upper right', fontsize=10)
        axes[0].grid(True, alpha=0.3)
        axes[0].set_ylabel('Load (kW)', fontsize=11)

        axes[1].plot(trend, label='Trend', color='darkorange', linewidth=2)
        axes[1].legend(loc='upper right', fontsize=10)
        axes[1].grid(True, alpha=0.3)
        axes[1].set_ylabel('Load (kW)', fontsize=11)

        axes[2].plot(seasonal, label='Seasonal', color='green', linewidth=1.5)
        axes[2].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        axes[2].legend(loc='upper right', fontsize=10)
        axes[2].grid(True, alpha=0.3)
        axes[2].set_ylabel('Load (kW)', fontsize=11)

        axes[3].plot(residual, label='Residual', color='red', alpha=0.7, linewidth=1)
        axes[3].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        axes[3].legend(loc='upper right', fontsize=10)
        axes[3].grid(True, alpha=0.3)
        axes[3].set_xlabel('Time', fontsize=12)
        axes[3].set_ylabel('Load (kW)', fontsize=11)

        plt.tight_layout()
        city_key = city.lower().replace(' ', '_')
        save_figure(fig, f'ch05_stl_decomposition_{city_key}.png', OUTPUT_DIR)

        # 保存分解数据
        decomp_df = pd.DataFrame({
            'observed': observed,
            'trend': trend,
            'seasonal': seasonal,
            'residual': residual,
            'method': method
        })
        save_dataframe(decomp_df, f'ch05_stl_components_{city_key}.csv', OUTPUT_DIR)

    print("\nStep 5.2 完成: 所有城市时序分解已执行")
    return stl_results


# ================================================================
# Step 5.3: 趋势项提取与可视化
# ================================================================
def step_5_3_trend_visualization(stl_results: dict) -> None:
    """四城市趋势对比 + 单城市趋势拟合图"""
    print('\n' + '=' * 60)
    print('Step 5.3: 趋势项提取与可视化')
    print('=' * 60)

    # 四城市趋势对比图
    fig, ax = plt.subplots(figsize=(14, 6), dpi=150)

    for city in CITY_LIST:
        r = stl_results[city]
        trend = r['trend']
        trend_start = trend.iloc[0]
        trend_end = trend.iloc[-1]
        trend_change = trend_end - trend_start
        trend_pct = (trend_change / trend_start) * 100 if trend_start != 0 else 0
        direction = "Up" if trend_change > 0 else ("Down" if trend_change < 0 else "Flat")
        print(f"  {city}: Trend {direction} ({trend_pct:+.1f}%), {trend_start:.1f} -> {trend_end:.1f} kW [{r['method']}]")

        ax.plot(trend.index, trend, label=f'{city} ({r["method"]})',
                color=COLORS.get(city, 'gray'), linewidth=2)

    ax.set_title('4-City Load Long-term Trend Comparison (Decomposed Trend Component)',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Trend Load (kW)', fontsize=12)
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    save_figure(fig, 'ch05_trend_component.png', OUTPUT_DIR)

    # 单城市趋势拟合图
    for city in CITY_LIST:
        r = stl_results[city]
        fig, ax = plt.subplots(figsize=(14, 5), dpi=150)
        ax.plot(r['observed'].index, r['observed'], label='Monthly Avg Load',
                color='steelblue', alpha=0.5, linewidth=1)
        ax.plot(r['trend'].index, r['trend'], label=f'Trend ({r["method"]})',
                color='darkorange', linewidth=2.5)
        ax.fill_between(r['observed'].index, r['observed'], r['trend'],
                        alpha=0.15, color='gray', label='Seasonal + Residual')

        method_note = '' if r['method'] == 'STL' else ' [MA Fallback]'
        ax.set_title(f'{city} - Monthly Load vs Trend Component{method_note}',
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Load (kW)', fontsize=12)
        ax.legend(fontsize=10, loc='best')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        city_key = city.lower().replace(' ', '_')
        save_figure(fig, f'ch05_trend_fit_{city_key}.png', OUTPUT_DIR)

    print("\nStep 5.3 完成: 趋势项可视化已生成")


# ================================================================
# Step 5.4: 季节性强度计算
# ================================================================
def step_5_4_seasonal_strength(stl_results: dict) -> pd.DataFrame:
    """计算季节性强度指标 F_s"""
    print('\n' + '=' * 60)
    print('Step 5.4: 季节性强度计算')
    print('=' * 60)

    records = []

    for city in CITY_LIST:
        r = stl_results[city]
        var_s = r['seasonal'].var()
        var_r = r['residual'].var()

        f_s = max(0, 1 - var_r / (var_s + var_r)) if (var_s + var_r) > 0 else 0.0

        if f_s > 0.7:
            level = 'Strong'
        elif f_s > 0.4:
            level = 'Moderate'
        else:
            level = 'Weak'

        # 对降级城市标注
        if r['method'] != 'STL':
            level += ' (MA fallback)'

        records.append({
            'city': city,
            'var_seasonal': round(var_s, 4),
            'var_residual': round(var_r, 4),
            'seasonal_strength': round(f_s, 4),
            'strength_level': level,
            'decomposition_method': r['method']
        })
        print(f"  {city}: F_s = {f_s:.4f} ({level}), Var(S)={var_s:.2f}, Var(R)={var_r:.2f} [{r['method']}]")

    strength_df = pd.DataFrame(records)
    save_dataframe(strength_df, 'ch05_seasonal_strength.csv', OUTPUT_DIR, index=False)

    # 可视化：季节性强度对比柱状图
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    strength_sorted = strength_df.sort_values('seasonal_strength', ascending=True)
    bar_colors = ['#e74c3c' if v > 0.7 else ('#f39c12' if v > 0.4 else '#27ae60')
                  for v in strength_sorted['seasonal_strength']]

    bars = ax.barh(strength_sorted['city'], strength_sorted['seasonal_strength'],
                   color=bar_colors, edgecolor='white', height=0.6)

    for bar, val in zip(bars, strength_sorted['seasonal_strength']):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f'{val:.3f}', va='center', fontsize=11, fontweight='bold')

    ax.set_xlabel('Seasonal Strength F_s', fontsize=12)
    ax.set_title('4-City Load Seasonal Strength Comparison', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 1.1)
    ax.axvline(x=0.7, color='red', linestyle='--', alpha=0.5, label='Strong threshold (0.7)')
    ax.axvline(x=0.4, color='orange', linestyle='--', alpha=0.5, label='Moderate threshold (0.4)')
    ax.legend(fontsize=10, loc='lower right')
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    save_figure(fig, 'ch05_seasonal_strength.png', OUTPUT_DIR)

    print("\nStep 5.4 完成: 季节性强度计算完毕")
    return strength_df


# ================================================================
# Step 5.5: 季度负荷箱线图
# ================================================================
def step_5_5_quarterly_boxplot(resampled_data: dict) -> None:
    """绘制每个城市四个季度的日负荷分布箱线图"""
    print('\n' + '=' * 60)
    print('Step 5.5: 季度负荷箱线图')
    print('=' * 60)

    sahara_cities = ['Laayoune', 'Boujdour', 'Foum eloued']

    for city in CITY_LIST:
        daily = resampled_data[city]['daily'].to_frame(name='load_kw')
        daily['quarter'] = daily.index.month.map(QUARTER_MAP)

        # 统计摘要
        print(f"\n  {city} Quarterly Load Statistics:")
        for q in QUARTER_ORDER:
            q_data = daily[daily['quarter'] == q]['load_kw']
            if len(q_data) > 0:
                print(f"    {q}: n={len(q_data)}, mean={q_data.mean():.1f}, "
                      f"median={q_data.median():.1f}, std={q_data.std():.1f}, "
                      f"range=[{q_data.min():.1f}, {q_data.max():.1f}]")

        # 绘制箱线图
        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
        sns.boxplot(data=daily, x='quarter', y='load_kw', order=QUARTER_ORDER,
                    palette='Set2', ax=ax, width=0.6,
                    flierprops={'marker': 'o', 'markersize': 4, 'alpha': 0.5})
        sns.stripplot(data=daily, x='quarter', y='load_kw', order=QUARTER_ORDER,
                      color='black', alpha=0.3, size=3, ax=ax, jitter=True)

        subtitle = ''
        if city in sahara_cities:
            subtitle = '\n(Note: Sahara city - extreme heat may cause unique load patterns)'

        ax.set_title(f'{city} - Quarterly Load Distribution (Daily Data){subtitle}',
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Quarter', fontsize=12)
        ax.set_ylabel('Daily Avg Load (kW)', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        city_key = city.lower().replace(' ', '_')
        save_figure(fig, f'ch05_quarterly_boxplot_{city_key}.png', OUTPUT_DIR)

    print("\nStep 5.5 完成: 季度负荷箱线图已生成")


# ================================================================
# Step 5.6: 月度负荷热力图
# ================================================================
def step_5_6_monthly_heatmap(resampled_data: dict) -> None:
    """绘制月份x年份的月度负荷热力图"""
    print('\n' + '=' * 60)
    print('Step 5.6: 月度负荷热力图')
    print('=' * 60)

    for city in CITY_LIST:
        monthly = resampled_data[city]['monthly'].to_frame(name='load_kw')
        monthly['year'] = monthly.index.year
        monthly['month'] = monthly.index.month

        # 构建透视表
        pivot = monthly.pivot_table(values='load_kw', index='month', columns='year', aggfunc='mean')
        pivot.index = [f'{m}' for m in pivot.index]

        print(f"\n  {city}: years={pivot.columns.tolist()}, months={pivot.index.tolist()}, "
              f"missing={pivot.isnull().sum().sum()}")
        if pivot.notna().any().any():
            print(f"    min={pivot.min().min():.1f} kW, max={pivot.max().max():.1f} kW")

        # 绘制热力图
        fig, ax = plt.subplots(figsize=(10, 7), dpi=150)
        sns.heatmap(pivot, ax=ax, cmap='YlOrRd', annot=True, fmt='.1f',
                    linewidths=0.5, linecolor='white',
                    cbar_kws={'label': 'Monthly Avg Load (kW)', 'shrink': 0.8})

        ax.set_title(f'{city} - Monthly Load Heatmap (kW)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Month', fontsize=12)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

        plt.tight_layout()
        city_key = city.lower().replace(' ', '_')
        save_figure(fig, f'ch05_monthly_heatmap_{city_key}.png', OUTPUT_DIR)

    print("\nStep 5.6 完成: 月度负荷热力图已生成")


# ================================================================
# Step 5.7: 同比/环比分析
# ================================================================
def step_5_7_yoy_mom_analysis(resampled_data: dict) -> pd.DataFrame:
    """计算月度负荷的同比/环比变化率"""
    print('\n' + '=' * 60)
    print('Step 5.7: 同比/环比分析')
    print('=' * 60)

    yoy_mom_records = []

    for city in CITY_LIST:
        monthly = resampled_data[city]['monthly']

        mom = monthly.pct_change(periods=1) * 100   # 环比 (%)
        yoy = monthly.pct_change(periods=12) * 100  # 同比 (%)

        temp = pd.DataFrame({
            'monthly_avg_kw': monthly,
            'mom_change_pct': mom,
            'yoy_change_pct': yoy
        })
        temp['city'] = city
        yoy_mom_records.append(temp)

        n_months = len(monthly)
        n_yoy_valid = yoy.dropna().shape[0]
        print(f"\n  {'=' * 50}")
        print(f"  {city} - YoY / MoM Analysis")
        print(f"  {'=' * 50}")
        print(f"    Data range: {monthly.index.min().date()} ~ {monthly.index.max().date()} ({n_months} months)")
        print(f"    MoM NaN: {mom.isnull().sum()} (1st month has no MoM)")
        print(f"    YoY NaN: {yoy.isnull().sum()} (first 12 months have no YoY)")

        if n_months < 13:
            print(f"    [WARNING] {city}: Only {n_months} months of data, YoY analysis has no statistical significance")

        recent = temp[['monthly_avg_kw', 'mom_change_pct', 'yoy_change_pct']].tail(6)
        print(f"\n    Last 6 months:")
        print(recent.to_string(float_format=lambda x: f'{x:.1f}' if pd.notna(x) else 'NaN'))

        valid_mom = mom.dropna()
        if len(valid_mom) > 0:
            print(f"\n    MoM stats: mean={valid_mom.mean():.2f}%, std={valid_mom.std():.2f}%, "
                  f"range=[{valid_mom.min():.2f}%, {valid_mom.max():.2f}%]")

        valid_yoy = yoy.dropna()
        if len(valid_yoy) > 0:
            print(f"    YoY stats: mean={valid_yoy.mean():.2f}%, std={valid_yoy.std():.2f}%, "
                  f"range=[{valid_yoy.min():.2f}%, {valid_yoy.max():.2f}%]")

    # 保存汇总表
    yoy_mom_df = pd.concat(yoy_mom_records)
    save_dataframe(yoy_mom_df, 'ch05_yoy_mom_analysis.csv', OUTPUT_DIR)

    # 同比变化率图
    fig, ax = plt.subplots(figsize=(14, 6), dpi=150)
    for city in CITY_LIST:
        city_data = yoy_mom_df[yoy_mom_df['city'] == city]
        valid = city_data['yoy_change_pct'].dropna()
        if len(valid) > 0:
            ax.plot(city_data.index, city_data['yoy_change_pct'],
                    label=city, color=COLORS.get(city, 'gray'),
                    linewidth=1.5, marker='o', markersize=4)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
    ax.set_title('4-City Monthly Load YoY Change Rate (%)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('YoY Change Rate (%)', fontsize=12)
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    save_figure(fig, 'ch05_yoy_change_rate.png', OUTPUT_DIR)

    # 环比变化率图
    fig, ax = plt.subplots(figsize=(14, 6), dpi=150)
    for city in CITY_LIST:
        city_data = yoy_mom_df[yoy_mom_df['city'] == city]
        ax.plot(city_data.index, city_data['mom_change_pct'],
                label=city, color=COLORS.get(city, 'gray'),
                linewidth=1.5, marker='o', markersize=4)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
    ax.set_title('4-City Monthly Load MoM Change Rate (%)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('MoM Change Rate (%)', fontsize=12)
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    save_figure(fig, 'ch05_mom_change_rate.png', OUTPUT_DIR)

    print("\nStep 5.7 完成: 同比/环比分析完毕")
    return yoy_mom_df


# ================================================================
# Main
# ================================================================
def main():
    print('=' * 60)
    print('Prompt-05: Mid-long Term Trend Analysis')
    print('=' * 60)
    print(f'Input: {INPUT_FILE}')
    print(f'Output: {OUTPUT_DIR}')

    # 确保输出目录存在
    ensure_dir(OUTPUT_DIR)

    # 加载数据
    print('\nLoading data...')
    df = load_preprocessed(INPUT_FILE)
    print(f"Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Time range: {df.index.min()} ~ {df.index.max()}")

    # Step 5.1: 多粒度重采样
    resampled_data = step_5_1_resample(df)

    # Step 5.2: STL时序分解
    stl_results = step_5_2_stl_decomposition(resampled_data)

    # Step 5.3: 趋势项可视化
    step_5_3_trend_visualization(stl_results)

    # Step 5.4: 季节性强度
    strength_df = step_5_4_seasonal_strength(stl_results)

    # Step 5.5: 季度箱线图
    step_5_5_quarterly_boxplot(resampled_data)

    # Step 5.6: 月度热力图
    step_5_6_monthly_heatmap(resampled_data)

    # Step 5.7: 同比/环比
    yoy_mom_df = step_5_7_yoy_mom_analysis(resampled_data)

    # 总结
    print('\n' + '=' * 60)
    print('Prompt-05 COMPLETE - All artifacts generated')
    print('=' * 60)

    # 列出所有产物
    artifacts = sorted(os.listdir(OUTPUT_DIR))
    print(f'\nTotal artifacts in {OUTPUT_DIR}: {len(artifacts)}')
    for a in artifacts:
        fpath = os.path.join(OUTPUT_DIR, a)
        size_kb = os.path.getsize(fpath) / 1024
        print(f'  {a} ({size_kb:.1f} KB)')


if __name__ == '__main__':
    main()
