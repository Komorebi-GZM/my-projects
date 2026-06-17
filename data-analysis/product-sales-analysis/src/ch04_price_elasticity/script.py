"""
ch04 价格弹性分析
分析同一产品在不同价格水平下的销量变化，计算品类级价格弹性系数。
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils.config import *
from utils.data_loader import load_preprocessed
from utils.output_manager import ensure_dir, save_dataframe, save_figure, save_markdown

def main():
    output_dir = os.path.join(OUTPUT_BASE, 'ch04_price_elasticity')
    ensure_dir(output_dir)

    # 加载清洗后数据
    df = load_preprocessed('ch01')

    # Step 1: 价格-销量散点图（整体）
    fig, ax = plt.subplots(figsize=PLT_CONFIG['figsize'])
    ax.scatter(df['Price_USD'], df['Quantity_Sold'], alpha=0.5, s=30)
    ax.set_xlabel('价格 (USD)')
    ax.set_ylabel('销量')
    ax.set_title('价格-销量散点图')
    plt.tight_layout()
    save_figure(fig, 'price_quantity_scatter.png', output_dir, PLT_CONFIG['dpi'])
    plt.close()

    # Step 2: 按品类计算价格弹性
    elasticity_results = []
    for cat in CATEGORY_LIST:
        cat_df = df[df['Category'] == cat].copy()
        if len(cat_df) < 5:
            continue
        # 计算价格和销量的对数变化
        cat_df['log_price'] = np.log(cat_df['Price_USD'].replace(0, np.nan))
        cat_df['log_qty'] = np.log(cat_df['Quantity_Sold'].replace(0, np.nan))
        cat_df = cat_df.dropna(subset=['log_price', 'log_qty'])

        if len(cat_df) > 2:
            corr = cat_df['log_price'].corr(cat_df['log_qty'])
            # 简单线性回归
            from numpy.polynomial.polynomial import polyfit
            try:
                b, a = polyfit(cat_df['log_price'], cat_df['log_qty'], 1)
                elasticity_results.append({
                    'Category': cat,
                    'Elasticity': round(b, 4),
                    'Correlation': round(corr, 4),
                    'N': len(cat_df),
                    'Type': '弹性' if b < -1 else ('刚性' if b > -0.5 else '单位弹性')
                })
            except:
                elasticity_results.append({
                    'Category': cat,
                    'Elasticity': None,
                    'Correlation': round(corr, 4),
                    'N': len(cat_df),
                    'Type': '无法计算'
                })

    elasticity_df = pd.DataFrame(elasticity_results)
    save_dataframe(elasticity_df, 'price_elasticity.csv', output_dir)

    # Step 3: 品类弹性系数柱状图
    fig, ax = plt.subplots(figsize=PLT_CONFIG['figsize'])
    valid_df = elasticity_df.dropna(subset=['Elasticity'])
    colors = ['#e74c3c' if e < -1 else '#f39c12' if e < -0.5 else '#27ae60' for e in valid_df['Elasticity']]
    ax.barh(valid_df['Category'], valid_df['Elasticity'], color=colors)
    ax.set_xlabel('价格弹性系数')
    ax.set_title('各品类价格弹性系数')
    ax.axvline(x=-1, color='red', linestyle='--', alpha=0.5, label='弹性阈值(-1)')
    ax.legend()
    plt.tight_layout()
    save_figure(fig, 'category_elasticity.png', output_dir, PLT_CONFIG['dpi'])
    plt.close()

    # Step 4: 按品类的价格-销量散点图
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()
    for i, cat in enumerate(CATEGORY_LIST):
        cat_df = df[df['Category'] == cat]
        axes[i].scatter(cat_df['Price_USD'], cat_df['Quantity_Sold'], alpha=0.6, s=25)
        axes[i].set_title(cat)
        axes[i].set_xlabel('价格')
        axes[i].set_ylabel('销量')
    plt.suptitle('各品类价格-销量关系', fontsize=14)
    plt.tight_layout()
    save_figure(fig, 'category_price_quantity.png', output_dir, PLT_CONFIG['dpi'])
    plt.close()

    # Step 5: 生成 report.md
    report = f"""# ch04 价格弹性分析

## 背景
本章基于 ch01 清洗后的 {len(df)} 条销售记录，分析价格与销量之间的关系。通过计算各品类的价格弹性系数，判断消费者对不同品类产品的价格敏感程度，为定价策略提供数据支撑。

## 分析方法
- **散点分析**：绘制价格-销量散点图，观察整体关系趋势
- **对数回归**：对价格和销量取对数后进行线性回归，斜率即为价格弹性系数
- **品类分组**：按 6 个品类分别计算弹性系数，并进行分类（弹性/刚性/单位弹性）

## 分析发现
- 各品类价格弹性系数如下：
{elasticity_df.to_markdown(index=False) if hasattr(elasticity_df, 'to_markdown') else elasticity_df.to_string(index=False)}
- 弹性分类标准：弹性（系数 < -1）、刚性（系数 > -0.5）、单位弹性（-1 <= 系数 <= -0.5）

## 小结
- 产物清单：price_quantity_scatter.png, category_elasticity.png, category_price_quantity.png, price_elasticity.csv
- 对下游章节的影响：为 ch05 业务建议提供定价策略依据
"""
    save_markdown(report, 'report.md', output_dir)
    print(f"[ch04] 价格弹性分析完成，产物保存至 {output_dir}")

if __name__ == '__main__':
    main()
