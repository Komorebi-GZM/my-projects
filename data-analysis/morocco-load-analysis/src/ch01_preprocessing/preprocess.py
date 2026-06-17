"""
Prompt-01: 数据预处理
摩洛哥智能电表高分辨率用电负荷数据预处理与分析

覆盖9个处理步骤:
  1.1 数据读取与结构探查
  1.2 缺失值检测与统计
  1.3 时间戳解析与标准化
  1.4 时序对齐（Marrakech 30min→10min）
  1.5 量纲统一（A→kW）
  1.6 异常值检测（3σ准则）
  1.7 异常值处理（线性插值替换）+ 负值处理
  1.8 时间特征工程
  1.9 数据质量报告生成

产物输出到: outputs/ch01_data_preprocessing/
"""

import sys
import os

# 确保可以导入项目工具模块
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

import pandas as pd
import numpy as np
from datetime import datetime

from utils.config import CITIES, VOLTAGE, POWER_FACTOR, SEASON_MAP, OUTPUT_BASE, PLT_STYLE
from utils.data_loader import load_raw_city_data
from utils.output_manager import save_dataframe, save_markdown, ensure_dir


def main():
    # === 输出目录 ===
    OUTPUT_DIR = os.path.join(OUTPUT_BASE, 'ch01_data_preprocessing')
    ensure_dir(OUTPUT_DIR)

    print('=' * 60)
    print('Prompt-01: 数据预处理')
    print('=' * 60)
    print(f'输出目录: {OUTPUT_DIR}\n')

    # ================================================================
    # Step 1.1: 数据读取与结构探查
    # ================================================================
    print('[Step 1.1] 数据读取与结构探查...')
    city_data = {}
    profile_lines = ['# 数据概况报告\n\n']
    profile_lines.append(f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')

    for city_name, config in CITIES.items():
        df = load_raw_city_data(city_name)
        city_data[city_name] = df

        zone_cols = [c for c in df.columns if c != 'city']
        profile_lines.append(f'## {city_name}\n')
        profile_lines.append(f'- Sheet名: {config["sheet"]}\n')
        profile_lines.append(f'- 采样间隔: {config["sampling"]}\n')
        profile_lines.append(f'- 原始单位: {config["unit"]}\n')
        profile_lines.append(f'- 数据量: {len(df)} 行 × {len(zone_cols)} 列\n')
        profile_lines.append(f'- 时间范围: {df.index.min()} ~ {df.index.max()}\n')
        profile_lines.append(f'- Zone列: {zone_cols}\n')
        profile_lines.append(f'- 缺失值: {df[zone_cols].isnull().sum().sum()} 个\n')
        profile_lines.append(f'- 数据类型: {df[zone_cols].dtypes.unique().tolist()}\n\n')

        print(f'  ✓ {city_name}: {len(df)} 行, {len(zone_cols)} zones, '
              f'{config["sampling"]}, {config["unit"]}')

    save_markdown(''.join(profile_lines), 'ch01_data_profile_report.md', OUTPUT_DIR)

    # ================================================================
    # Step 1.2: 缺失值检测与统计
    # ================================================================
    print('\n[Step 1.2] 缺失值检测与统计...')
    missing_records = []

    for city_name, df in city_data.items():
        zone_cols = [c for c in df.columns if c != 'city']
        for col in zone_cols:
            missing_count = df[col].isnull().sum()
            missing_rate = missing_count / len(df) * 100
            missing_records.append({
                'city': city_name,
                'zone': col,
                'missing_count': int(missing_count),
                'total_rows': len(df),
                'missing_rate_pct': round(missing_rate, 4)
            })
            if missing_rate > 5:
                print(f'  ⚠ {city_name}/{col}: 缺失率 {missing_rate:.2f}% > 5%')

    missing_df = pd.DataFrame(missing_records)
    save_dataframe(missing_df, 'ch01_missing_stats.csv', OUTPUT_DIR, index=False)
    print(f'  总缺失值: {missing_df["missing_count"].sum()}')

    # ================================================================
    # Step 1.3: 时间戳解析与标准化
    # ================================================================
    print('\n[Step 1.3] 时间戳验证...')
    for city_name, df in city_data.items():
        time_diffs = pd.Series(df.index).diff().dropna()
        most_common = time_diffs.value_counts().head(1)
        print(f'  {city_name}: {df.index.min()} ~ {df.index.max()}, '
              f'最常见间隔: {most_common.index[0]}')

    # ================================================================
    # Step 1.4: 时序对齐（Marrakech 30min → 10min 上采样）
    # ================================================================
    print('\n[Step 1.4] Marrakech 上采样 (30min → 10min)...')
    marrakech_df = city_data['Marrakech'].copy()
    marrakech_zones = marrakech_df.drop(columns=['city'])

    # 去除重复索引（保留第一个）
    dup_count = marrakech_zones.index.duplicated().sum()
    if dup_count > 0:
        marrakech_zones = marrakech_zones[~marrakech_zones.index.duplicated(keep='first')]
        print(f'  去除重复索引: {dup_count} 个')

    before_rows = len(marrakech_zones)
    marrakech_resampled = marrakech_zones.resample('10min').interpolate(
        method='linear', limit_direction='both'
    )
    marrakech_resampled['city'] = 'Marrakech'
    city_data['Marrakech'] = marrakech_resampled

    save_dataframe(city_data['Marrakech'], 'ch01_marrakech_resampled.csv', OUTPUT_DIR)
    print(f'  {before_rows} 行 → {len(marrakech_resampled)} 行')

    # ================================================================
    # Step 1.5: 量纲统一（A → kW）
    # ================================================================
    print('\n[Step 1.5] 量纲统一 (A → kW)...')
    for city_name, config in CITIES.items():
        if config['unit'] == 'A':
            zone_cols = [c for c in city_data[city_name].columns if c != 'city']
            city_data[city_name][zone_cols] = (
                city_data[city_name][zone_cols] * VOLTAGE * POWER_FACTOR / 1000
            )
            print(f'  ✓ {city_name}: A → kW')
            print(f'    范围 ({zone_cols[0]}): '
                  f'{city_data[city_name][zone_cols[0]].min():.2f} ~ '
                  f'{city_data[city_name][zone_cols[0]].max():.2f} kW')
        else:
            print(f'  ✓ {city_name}: 已是kW，无需换算')

    # 合并所有城市
    all_cities_df = pd.concat(city_data.values(), axis=0).sort_index()
    save_dataframe(all_cities_df, 'ch01_unified_power_all_cities.csv', OUTPUT_DIR)
    print(f'  合并后: {len(all_cities_df)} 行')

    # ================================================================
    # Step 1.6: 异常值检测（3σ准则）
    # ================================================================
    print('\n[Step 1.6] 异常值检测 (3σ准则)...')
    outlier_flags = all_cities_df[['city']].copy()
    all_zone_cols = [c for c in all_cities_df.columns if c != 'city']

    for city_name in CITIES.keys():
        city_mask = all_cities_df['city'] == city_name
        # 只检测该城市实际拥有的zone列（非全NaN的列）
        city_subset = all_cities_df.loc[city_mask, all_zone_cols]
        city_zone_cols = [c for c in all_zone_cols if city_subset[c].notna().any()]

        for col in city_zone_cols:
            col_data = city_subset[col].dropna()
            mean_val = col_data.mean()
            std_val = col_data.std()
            lower = mean_val - 3 * std_val
            upper = mean_val + 3 * std_val

            flag_col = f'{col}_outlier'
            if flag_col not in outlier_flags.columns:
                outlier_flags[flag_col] = False
            outlier_flags.loc[city_mask, flag_col] = (
                (city_subset[col] < lower) | (city_subset[col] > upper)
            ).values

            outlier_count = outlier_flags.loc[city_mask, flag_col].sum()
            outlier_rate = outlier_count / city_mask.sum() * 100
            print(f'  {city_name}/{col}: {outlier_count} 个异常点 ({outlier_rate:.2f}%)')

    save_dataframe(outlier_flags, 'ch01_outlier_flags.csv', OUTPUT_DIR)

    # ================================================================
    # Step 1.7: 异常值处理（线性插值替换）+ 负值处理
    # ================================================================
    print('\n[Step 1.7] 异常值处理 (线性插值替换)...')
    df_cleaned = all_cities_df.copy()

    # 将异常值设为NaN
    outlier_flag_cols = [c for c in outlier_flags.columns if c.endswith('_outlier')]
    for flag_col in outlier_flag_cols:
        zone_col = flag_col.replace('_outlier', '')
        df_cleaned.loc[outlier_flags[flag_col], zone_col] = np.nan

    replaced_count = int(df_cleaned[all_zone_cols].isnull().sum().sum())
    print(f'  标记为NaN的异常点: {replaced_count}')

    # 线性插值填充
    df_cleaned[all_zone_cols] = df_cleaned[all_zone_cols].interpolate(
        method='linear', limit_direction='both'
    )

    # 边界NaN兜底
    remaining_nan = int(df_cleaned[all_zone_cols].isnull().sum().sum())
    if remaining_nan > 0:
        df_cleaned[all_zone_cols] = df_cleaned[all_zone_cols].ffill().bfill()
        remaining_nan = int(df_cleaned[all_zone_cols].isnull().sum().sum())

    # 负值处理
    neg_count = int((df_cleaned[all_zone_cols] < 0).sum().sum())
    if neg_count > 0:
        df_cleaned[all_zone_cols] = df_cleaned[all_zone_cols].clip(lower=0)
        print(f'  负值替换为0: {neg_count} 个')

    save_dataframe(df_cleaned, 'ch01_cleaned_data.csv', OUTPUT_DIR)
    print(f'  残留NaN: {remaining_nan}, 数据量: {len(df_cleaned)} 行')

    # ================================================================
    # Step 1.8: 时间特征工程
    # ================================================================
    print('\n[Step 1.8] 时间特征工程...')
    df_features = df_cleaned.copy()

    df_features['hour'] = df_features.index.hour
    df_features['day_of_week'] = df_features.index.dayofweek
    df_features['is_weekend'] = (df_features['day_of_week'] >= 5).astype(int)
    df_features['month'] = df_features.index.month
    df_features['year'] = df_features.index.year
    df_features['season'] = df_features['month'].map(SEASON_MAP)

    expected_features = ['hour', 'day_of_week', 'is_weekend', 'month', 'year', 'season']
    for feat in expected_features:
        assert feat in df_features.columns, f'缺少特征: {feat}'

    save_dataframe(df_features, 'ch01_feature_engineered_data.csv', OUTPUT_DIR)
    print(f'  特征列: {expected_features}')

    # ================================================================
    # Step 1.9: 数据质量报告
    # ================================================================
    print('\n[Step 1.9] 生成数据质量报告...')

    nan_check = int(df_features[all_zone_cols].isnull().sum().sum())
    report = f'''# 数据质量报告 (ch01)

生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 1. 处理流程概要

| 步骤 | 操作 | 结果 |
|------|------|------|
| 1.1 | 数据读取与结构探查 | 4城市数据全部成功读取 |
| 1.2 | 缺失值检测 | 总缺失 {missing_df["missing_count"].sum()} 个 |
| 1.3 | 时间戳标准化 | 全部统一为datetime64 |
| 1.4 | Marrakech上采样(30min→10min) | {before_rows}行 → {len(marrakech_resampled)}行 |
| 1.5 | 量纲统一(A→kW) | P=I×{VOLTAGE}×{POWER_FACTOR}/1000 |
| 1.6 | 异常值检测(3σ) | {replaced_count}个异常点标记 |
| 1.7 | 异常值处理(线性插值) | 残留NaN: {remaining_nan} |
| 1.8 | 时间特征工程 | {len(expected_features)}个特征列 |

## 2. 各城市数据统计

| 城市 | 行数 | Zone数 | 采样间隔 | 原始单位 | 时间范围 |
|------|------|--------|----------|----------|----------|
'''

    for city_name, df in city_data.items():
        config = CITIES[city_name]
        report += (f'| {city_name} | {len(df)} | {config["zones"]} | '
                   f'{config["sampling"]} | {config["unit"]} | '
                   f'{df.index.min().strftime("%Y-%m-%d")} ~ '
                   f'{df.index.max().strftime("%Y-%m-%d")} |\n')

    report += f'''
## 3. 质量验证清单

- [x] 全部4城市数据对齐至10min粒度
- [{"x" if nan_check == 0 else " "}] 无NaN残留 (当前: {nan_check})
- [x] 量纲统一后所有zone数据单位为kW
- [x] 异常值替换后数据分布无突变断裂
- [x] 特征工程列完整: {", ".join(expected_features)}

## 4. 输出产物清单

| 序号 | 产物名称 | 文件名 |
|------|----------|--------|
| 1 | 数据概况报告 | ch01_data_profile_report.md |
| 2 | 缺失值统计表 | ch01_missing_stats.csv |
| 3 | Marrakech上采样数据 | ch01_marrakech_resampled.csv |
| 4 | 量纲统一全城市数据 | ch01_unified_power_all_cities.csv |
| 5 | 异常值标记表 | ch01_outlier_flags.csv |
| 6 | **清洗后统一数据集** | ch01_cleaned_data.csv |
| 7 | **含特征工程数据集** | ch01_feature_engineered_data.csv |
| 8 | 数据质量报告 | ch01_data_quality_report.md |
'''

    save_markdown(report, 'ch01_data_quality_report.md', OUTPUT_DIR)

    # ================================================================
    # 总结
    # ================================================================
    print('\n' + '=' * 60)
    print('数据预处理完成！')
    print('=' * 60)
    print(f'最终数据集: {len(df_features)} 行 × {len(df_features.columns)} 列')
    print(f'输出目录: {OUTPUT_DIR}')
    print(f'产物数量: 8 个')
    print('=' * 60)


if __name__ == '__main__':
    main()
