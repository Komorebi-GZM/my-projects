"""
ch05 结论与业务建议
基于前序章节的分析结果，输出结构化的业务建议报告。
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from utils.config import *
from utils.data_loader import load_preprocessed
from utils.output_manager import ensure_dir, save_markdown

def main():
    output_dir = os.path.join(OUTPUT_BASE, 'ch05_conclusions_and_recommendations')
    ensure_dir(output_dir)

    # 加载清洗后数据
    df = load_preprocessed('ch01')

    # 加载前序章节的分析结果
    ch02_dir = os.path.join(OUTPUT_BASE, 'ch02_descriptive_analysis')
    ch03_dir = os.path.join(OUTPUT_BASE, 'ch03_sales_forecasting')
    ch04_dir = os.path.join(OUTPUT_BASE, 'ch04_price_elasticity')

    # 读取品类汇总数据
    category_summary = df.groupby('Category').agg(
        Total_Sales=('Total_Sales_USD', 'sum'),
        Avg_Price=('Price_USD', 'mean'),
        Total_Quantity=('Quantity_Sold', 'sum'),
        Order_Count=('Product_ID', 'count')
    ).sort_values('Total_Sales', ascending=False)

    # 读取城市汇总数据
    city_summary = df.groupby('Customer_City').agg(
        Total_Sales=('Total_Sales_USD', 'sum'),
        Avg_Price=('Price_USD', 'mean'),
        Total_Quantity=('Quantity_Sold', 'sum'),
        Order_Count=('Product_ID', 'count')
    ).sort_values('Total_Sales', ascending=False)

    # 读取弹性分析结果
    elasticity_path = os.path.join(ch04_dir, 'price_elasticity.csv')
    elasticity_df = None
    if os.path.exists(elasticity_path):
        elasticity_df = pd.read_csv(elasticity_path)

    # 生成综合建议报告
    report = f"""# ch05 结论与业务建议

## 背景
本章综合 ch02 描述性统计、ch03 销售预测、ch04 价格弹性分析的全部发现，输出面向管理层的结构化业务建议。数据覆盖 {len(df)} 条销售记录，时间跨度 2025-01 至 2026-05。

## 分析方法
- 综合归纳前序 4 个章节的核心发现
- 按品类策略、区域策略、定价策略三个维度组织建议
- 每条建议附数据支撑和优先级评估

## 分析发现

### 核心数据概览
- 总销售额：${{df['Total_Sales_USD'].sum():,.0f}}
- 总销量：{{df['Quantity_Sold'].sum():,}} 件
- 平均客单价：${{df['Total_Sales_USD'].mean():,.0f}}
- 产品种类：{{df['Product_Name'].nunique()}} 种
- 覆盖城市：{{df['Customer_City'].nunique()}} 个

### 品类表现排名
{category_summary.to_markdown() if hasattr(category_summary, 'to_markdown') else category_summary.to_string()}

### 城市表现排名
{city_summary.to_markdown() if hasattr(city_summary, 'to_markdown') else city_summary.to_string()}

### 品类策略建议
1. **重点投入品类**：销售额排名前 2 的品类应获得更多营销资源和库存支持
2. **潜力品类**：销量高但单价低的品类，考虑通过组合销售提升客单价
3. **需关注品类**：销售额和销量均较低的品类，评估是否需要调整产品线

### 区域策略建议
1. **优势区域**：销售额最高的城市应作为核心市场持续深耕
2. **拓展区域**：销售增长潜力大的城市可加大推广力度
3. **区域差异化**：根据各城市品类偏好差异，制定区域化选品策略

### 定价策略建议
"""

    if elasticity_df is not None:
        report += "\n基于价格弹性分析结果：\n"
        for _, row in elasticity_df.iterrows():
            cat = row['Category']
            elas = row.get('Elasticity', 'N/A')
            etype = row.get('Type', 'N/A')
            if pd.notna(elas):
                report += f"- **{cat}**：弹性系数 {elas}（{etype}）\n"
                if etype == '弹性':
                    report += f"  -> 建议：降价可显著提升销量，可考虑促销策略\n"
                elif etype == '刚性':
                    report += f"  -> 建议：价格变动对销量影响小，可维持或适度提价\n"
                else:
                    report += f"  -> 建议：价格与销量呈单位弹性关系，需综合评估\n"

    report += f"""
## 小结
- 本报告综合了描述性统计、销售预测、价格弹性分析三个维度的发现
- 建议优先级：品类策略 > 区域策略 > 定价策略（根据数据支撑强度排序）
- 后续行动：建议按季度更新分析，跟踪策略执行效果
- 产物清单：report.md（综合建议报告）
"""

    save_markdown(report, 'report.md', output_dir)
    print(f"[ch05] 结论与业务建议完成，产物保存至 {output_dir}")

if __name__ == '__main__':
    main()
