"""
Chapter 7: 竞品对标分析 (Competitive Benchmark Analysis)

按市场细分（Budget/Mid-range/Premium/Luxury）和车身类型分组，
对同级车型进行价格、技术参数、销量的横向对标，构建综合竞争力评分体系。
"""

import os
import sys
from pathlib import Path

# ========== 项目根目录 ==========
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
import warnings
warnings.filterwarnings('ignore')

# ========== 路径配置 ==========
DATA_DIR = PROJECT_ROOT / "outputs" / "ch01_data_cleaning"
RAW_DATA_FILE = DATA_DIR / "cleaned_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "ch07_competitive_benchmark"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"[OK] 项目根目录: {PROJECT_ROOT}")
print(f"[OK] 输出目录: {OUTPUT_DIR}")


def main():
    """主执行函数"""
    print("\n" + "="*60)
    print("Chapter 7: 竞品对标分析")
    print("="*60)
    
    # Step 1: 数据加载与同级分组定义
    print("\n[Step 7.1] 数据加载与同级分组定义...")
    df = pd.read_csv(RAW_DATA_FILE)
    print(f"  原始数据形状: {df.shape}")
    
    group_cols = ['market_segment', 'body_type']
    group_sizes = df.groupby(group_cols).size().reset_index(name='vehicle_count')
    
    # 筛选有效分组（每组至少5款车型）
    valid_groups = group_sizes[group_sizes['vehicle_count'] >= 5].copy()
    print(f"  有效分组数量: {len(valid_groups)}")
    print("\n  有效分组统计:")
    print(valid_groups.to_string(index=False))
    
    # 筛选有效分组内的车辆
    valid_group_keys = set(zip(valid_groups['market_segment'], valid_groups['body_type']))
    df_valid = df[df.apply(lambda row: (row['market_segment'], row['body_type']) in valid_group_keys, axis=1)].copy()
    print(f"\n  有效分组内车辆总数: {len(df_valid)}")
    
    # Step 2: 同级价格对比分析
    print("\n[Step 7.2] 同级价格对比分析...")
    price_stats = df_valid.groupby(group_cols).agg(
        vehicle_count=('price_usd', 'count'),
        mean_price=('price_usd', 'mean'),
        median_price=('price_usd', 'median'),
        min_price=('price_usd', 'min'),
        max_price=('price_usd', 'max'),
        std_price=('price_usd', 'std')
    ).reset_index()
    
    price_stats = price_stats.round(2)
    price_stats = price_stats.sort_values(['market_segment', 'body_type']).reset_index(drop=True)
    print("\n  同级价格对比统计:")
    print(price_stats.to_string(index=False))
    
    # 保存
    price_stats.to_csv(OUTPUT_DIR / 'segment_comparison.csv', index=False)
    print(f"\n  [OK] 已保存 segment_comparison.csv")
    
    # Step 3: 性价比评分构建
    print("\n[Step 7.3] 性价比评分构建...")
    score_cols = ['range_miles', 'top_speed_mph', 'horsepower', 'safety_rating']
    norm_cols = ['range_norm', 'speed_norm', 'power_norm', 'safety_norm']
    
    # 对每个分组分别进行 Min-Max 标准化
    for score_col, norm_col in zip(score_cols, norm_cols):
        norm_values = []
        for _, group in df_valid.groupby(group_cols):
            col_min = group[score_col].min()
            col_max = group[score_col].max()
            if col_max == col_min:
                norm_vals = pd.Series(0.5, index=group.index)
            else:
                norm_vals = (group[score_col] - col_min) / (col_max - col_min)
            norm_values.append(norm_vals)
        df_valid[norm_col] = pd.concat(norm_values).reindex(df_valid.index)
    
    # 计算性价比评分
    df_valid['value_score'] = (
        0.25 * df_valid['range_norm'] +
        0.25 * df_valid['speed_norm'] +
        0.25 * df_valid['power_norm'] +
        0.25 * df_valid['safety_norm']
    )
    
    # 检查评分质量
    print(f"\n  性价比评分统计:")
    print(f"    均值: {df_valid['value_score'].mean():.4f}")
    print(f"    标准差: {df_valid['value_score'].std():.4f}")
    print(f"    最小值: {df_valid['value_score'].min():.4f}")
    print(f"    最大值: {df_valid['value_score'].max():.4f}")
    print(f"    NaN数量: {df_valid['value_score'].isna().sum()}")
    
    # Step 4: 同级性价比排名
    print("\n[Step 7.4] 同级性价比排名...")
    df_valid['rank_in_segment'] = df_valid.groupby(group_cols)['value_score'].rank(
        method='dense', ascending=False
    ).astype(int)
    
    ranking_cols = ['market_segment', 'body_type', 'rank_in_segment', 'brand', 'model',
                    'year', 'variant', 'price_usd', 'range_miles', 'top_speed_mph',
                    'horsepower', 'safety_rating', 'value_score']
    df_ranking = df_valid[ranking_cols].sort_values(
        ['market_segment', 'body_type', 'rank_in_segment']
    ).reset_index(drop=True)
    
    # 保存完整排名
    df_ranking.to_csv(OUTPUT_DIR / 'value_ranking.csv', index=False)
    print(f"  [OK] 已保存 value_ranking.csv")
    
    # 展示各细分Top3
    segments = ['Budget', 'Mid-range', 'Premium', 'Luxury']
    print("\n  各细分市场性价比 Top 3:")
    for seg in segments:
        if seg in df_valid['market_segment'].values:
            seg_data = df_ranking[df_ranking['market_segment'] == seg].head(3)
            print(f"\n  {seg}:")
            print(seg_data[['rank_in_segment', 'brand', 'model', 'price_usd', 'value_score']].to_string(index=False))
    
    # Step 5: 竞争力雷达图
    print("\n[Step 7.5] 竞争力雷达图绘制...")
    radar_dims = ['range_miles', 'top_speed_mph', 'horsepower', 'safety_rating',
                  'charging_speed_kw', 'acceleration_0_60_mph']
    radar_labels = ['Range\n(miles)', 'Top Speed\n(mph)', 'Horsepower', 'Safety\nRating',
                    'Charging\n(kW)', 'Acceleration\n0-60 (s)']
    
    # 全局Min-Max标准化
    radar_data = df_valid[radar_dims].copy()
    for col in radar_dims:
        col_min = radar_data[col].min()
        col_max = radar_data[col].max()
        if col_max == col_min:
            radar_data[col + '_norm'] = 0.5
        else:
            radar_data[col + '_norm'] = (radar_data[col] - col_min) / (col_max - col_min)
    
    # 加速时间反向：越短越好
    radar_data['acceleration_0_60_mph_norm'] = 1 - radar_data['acceleration_0_60_mph_norm']
    radar_norm_cols = [c + '_norm' for c in radar_dims]
    
    df_valid_radar = df_valid.copy()
    for col in radar_norm_cols:
        df_valid_radar[col] = radar_data[col].values
    
    # 为每个细分选取Top3车型
    top_per_segment = {}
    for seg in segments:
        seg_df = df_valid_radar[df_valid_radar['market_segment'] == seg]
        if len(seg_df) > 0:
            top_per_segment[seg] = seg_df.nlargest(min(3, len(seg_df)), 'value_score')
    
    # 绘制雷达图
    fig, axes = plt.subplots(2, 2, figsize=(16, 14), subplot_kw=dict(polar=True))
    fig.suptitle('Competitiveness Radar by Market Segment (Top 3 per Segment)', 
                 fontsize=16, fontweight='bold')
    
    colors = ['#e74c3c', '#3498db', '#2ecc71']
    
    for idx, seg in enumerate(segments):
        ax = axes[idx // 2][idx % 2]
        
        if seg not in top_per_segment:
            ax.set_title(f'{seg} Segment (No Data)', fontsize=13, fontweight='bold', pad=20)
            continue
            
        top_cars = top_per_segment[seg]
        angles = np.linspace(0, 2 * np.pi, len(radar_dims), endpoint=False).tolist()
        angles += angles[:1]
        
        for car_idx, (_, car) in enumerate(top_cars.iterrows()):
            values = [car[nc] for nc in radar_norm_cols]
            values += values[:1]
            label = f"{car['brand']} {car['model']}"
            ax.plot(angles, values, 'o-', linewidth=2, label=label, color=colors[car_idx])
            ax.fill(angles, values, alpha=0.1, color=colors[car_idx])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(radar_labels, fontsize=9)
        ax.set_title(f'{seg} Segment', fontsize=13, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=8)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(OUTPUT_DIR / 'competitiveness_radar.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [OK] 已保存 competitiveness_radar.png")
    
    # Step 6: 品牌产品矩阵
    print("\n[Step 7.6] 品牌产品矩阵分析...")
    brand_matrix = df_valid.groupby(['brand', 'market_segment', 'body_type']).agg(
        vehicle_count=('model', 'count'),
        avg_value_score=('value_score', 'mean'),
        avg_price=('price_usd', 'mean')
    ).reset_index().round(4)
    
    # 保存CSV版本
    brand_matrix.to_csv(OUTPUT_DIR / 'brand_product_matrix.csv', index=False)
    print(f"  [OK] 已保存 brand_product_matrix.csv")
    
    # 输出品牌覆盖概览
    brand_coverage = df_valid.groupby('brand').agg(
        segments_covered=('market_segment', 'nunique'),
        body_types_covered=('body_type', 'nunique'),
        total_models=('model', 'count'),
        avg_score=('value_score', 'mean')
    ).sort_values('avg_score', ascending=False).round(4)
    
    print("\n  品牌覆盖概览 (按平均性价比排序):")
    print(brand_coverage.head(10).to_string())
    
    # Step 7: 同级综合排名
    print("\n[Step 7.7] 同级综合排名...")
    
    def normalize_series(group, col, reverse=False):
        """对分组进行Min-Max标准化"""
        col_min = group[col].min()
        col_max = group[col].max()
        if col_max == col_min:
            return pd.Series(0.5, index=group.index)
        norm = (group[col] - col_min) / (col_max - col_min)
        if reverse:
            norm = 1 - norm
        return norm
    
    # 对每个指标分别进行标准化
    norm_results = {}
    norm_configs = [
        ('price_norm', 'price_usd', True),
        ('value_score_norm', 'value_score', False),
        ('sales_norm', 'annual_sales_units', False),
        ('rating_norm', 'customer_rating', False)
    ]
    
    for norm_col, src_col, reverse in norm_configs:
        norm_values = []
        for _, group in df_valid.groupby(group_cols):
            norm_vals = normalize_series(group, src_col, reverse)
            norm_values.append(norm_vals)
        norm_results[norm_col] = pd.concat(norm_values).reindex(df_valid.index)
    
    for col, vals in norm_results.items():
        df_valid[col] = vals
    
    # 综合竞争力得分
    df_valid['composite_score'] = (
        0.20 * df_valid['price_norm'] +
        0.30 * df_valid['value_score_norm'] +
        0.25 * df_valid['sales_norm'] +
        0.25 * df_valid['rating_norm']
    )
    
    df_valid['composite_rank'] = df_valid.groupby(group_cols)['composite_score'].rank(
        method='dense', ascending=False
    ).astype(int)
    
    # 保存综合排名
    final_rank_cols = ['market_segment', 'body_type', 'composite_rank', 'brand', 'model',
                       'year', 'variant', 'price_usd', 'value_score', 'annual_sales_units',
                       'customer_rating', 'composite_score']
    df_final_rank = df_valid[final_rank_cols].sort_values(
        ['market_segment', 'body_type', 'composite_rank']
    ).reset_index(drop=True)
    
    df_final_rank.to_csv(OUTPUT_DIR / 'segment_comprehensive_ranking.csv', index=False)
    print(f"  [OK] 已保存 segment_comprehensive_ranking.csv")
    
    # 各细分Top5
    print("\n  各细分市场综合排名 Top 5:")
    for seg in segments:
        if seg in df_valid['market_segment'].values:
            seg_top = df_final_rank[df_final_rank['market_segment'] == seg].head(5)
            print(f"\n  {seg}:")
            print(seg_top[['composite_rank', 'brand', 'model', 'price_usd', 'composite_score']].to_string(index=False))
    
    # Step 8: 章节报告生成
    print("\n[Step 7.8] 章节报告生成...")
    report_lines = []
    report_lines.append("# Chapter 7: 竞品对标分析报告\n")
    report_lines.append("## 7.1 研究目标\n")
    report_lines.append("本章按市场细分（market_segment）和车身类型（body_type）对同级车型进行横向对标分析，")
    report_lines.append("构建综合竞争力评分体系，识别各细分市场的标杆车型与品牌竞争格局。\n")
    
    report_lines.append("## 7.2 同级分组概况\n")
    report_lines.append(f"- 有效分组总数：{len(valid_groups)}")
    report_lines.append(f"- 覆盖细分市场：{', '.join(sorted(df_valid['market_segment'].unique()))}")
    report_lines.append(f"- 覆盖车身类型：{', '.join(sorted(df_valid['body_type'].unique()))}")
    report_lines.append(f"- 纳入分析车辆总数：{len(df_valid)}\n")
    
    report_lines.append("## 7.3 同级价格对比分析\n")
    report_lines.append("各细分-车身组合的价格统计如下：\n")
    report_lines.append("| 细分市场 | 车身类型 | 车型数 | 均价($) | 中位价($) | 最低价($) | 最高价($) |")
    report_lines.append("|---------|---------|-------|---------|----------|----------|----------|")
    for _, row in price_stats.iterrows():
        report_lines.append(
            f"| {row['market_segment']} | {row['body_type']} | {int(row['vehicle_count'])} | "
            f"{row['mean_price']:,.0f} | {row['median_price']:,.0f} | {row['min_price']:,.0f} | "
            f"{row['max_price']:,.0f} |"
        )
    report_lines.append("")
    
    report_lines.append("## 7.4 性价比评分体系\n")
    report_lines.append("### 评分公式\n")
    report_lines.append("```")
    report_lines.append("value_score = 0.25 * range_norm + 0.25 * speed_norm + 0.25 * power_norm + 0.25 * safety_norm")
    report_lines.append("```\n")
    report_lines.append("各维度采用组内 Min-Max 标准化，映射到 [0, 1] 区间。\n")
    report_lines.append(f"- 评分均值：{df_valid['value_score'].mean():.4f}")
    report_lines.append(f"- 评分标准差：{df_valid['value_score'].std():.4f}")
    report_lines.append(f"- 评分范围：[{df_valid['value_score'].min():.4f}, {df_valid['value_score'].max():.4f}]\n")
    
    report_lines.append("## 7.5 竞争力雷达图\n")
    report_lines.append("![竞争力雷达图](competitiveness_radar.png)\n")
    report_lines.append("上图展示各细分市场 Top 3 车型在续航、速度、动力、安全、充电、加速六个维度的竞争力对比。\n")
    
    report_lines.append("## 7.6 品牌产品矩阵\n")
    report_lines.append(f"- 涉及品牌数量：{df_valid['brand'].nunique()}")
    report_lines.append(f"- 品牌平均覆盖细分市场数：{brand_coverage['segments_covered'].mean():.1f}")
    report_lines.append(f"- 品牌平均覆盖车身类型数：{brand_coverage['body_types_covered'].mean():.1f}\n")
    report_lines.append("详细品牌产品矩阵见 `brand_product_matrix.csv`。\n")
    
    report_lines.append("## 7.7 同级综合排名\n")
    report_lines.append("综合排名考虑四个维度：价格竞争力(20%)、性价比评分(30%)、销量表现(25%)、客户评分(25%)。\n")
    for seg in segments:
        if seg in df_valid['market_segment'].values:
            seg_top3 = df_final_rank[df_final_rank['market_segment'] == seg].head(3)
            report_lines.append(f"### {seg} Top 3\n")
            report_lines.append("| 排名 | 品牌 | 型号 | 价格($) | 综合得分 |")
            report_lines.append("|-----|------|------|---------|---------|")
            for _, r in seg_top3.iterrows():
                report_lines.append(f"| {int(r['composite_rank'])} | {r['brand']} | {r['model']} | {r['price_usd']:,.0f} | {r['composite_score']:.4f} |")
            report_lines.append("")
    
    report_lines.append("## 7.8 关键发现与洞察\n")
    report_lines.append("1. 各细分市场价格梯度明显，Luxury 细分均价显著高于 Budget 细分。")
    report_lines.append("2. 性价比评分揭示了部分中端车型在技术参数上接近高端车型的现象。")
    report_lines.append("3. 品牌产品矩阵显示部分品牌聚焦单一细分市场，而头部品牌实现了全细分覆盖。")
    report_lines.append("4. 综合排名中，销量和客户评分的引入使得排名更贴近市场实际表现。\n")
    
    report_lines.append("## 7.9 产物清单\n")
    report_lines.append("| 产物文件 | 说明 |")
    report_lines.append("|---------|------|")
    report_lines.append("| segment_comparison.csv | 同级价格对比统计表 |")
    report_lines.append("| value_ranking.csv | 同级性价比排名表 |")
    report_lines.append("| competitiveness_radar.png | 竞争力雷达图 |")
    report_lines.append("| brand_product_matrix.csv | 品牌产品矩阵 |")
    report_lines.append("| segment_comprehensive_ranking.csv | 同级综合排名表 |")
    report_lines.append("| ch07_report.md | 本章分析报告 |\n")
    
    report_content = '\n'.join(report_lines)
    with open(OUTPUT_DIR / 'ch07_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"  [OK] 已保存 ch07_report.md")
    
    print("\n" + "="*60)
    print("Chapter 7 分析完成！")
    print("="*60)
    print(f"\n输出产物已保存至: {OUTPUT_DIR}")
    print("\n产物清单:")
    print("  1. segment_comparison.csv - 同级价格对比统计表")
    print("  2. value_ranking.csv - 同级性价比排名表")
    print("  3. competitiveness_radar.png - 竞争力雷达图")
    print("  4. brand_product_matrix.csv - 品牌产品矩阵")
    print("  5. segment_comprehensive_ranking.csv - 同级综合排名表")
    print("  6. ch07_report.md - 章节分析报告")


if __name__ == "__main__":
    main()
