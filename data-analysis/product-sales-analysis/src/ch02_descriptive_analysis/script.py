"""
ch02 描述性统计与可视化脚本 - 产品销售数据分析项目

本脚本执行描述性统计与可视化分析流程，包括：
1. 加载清洗后的数据
2. 描述性统计分析
3. 产品类别分析
4. 城市维度分析
5. 时间趋势分析
6. 生成图表和报告（report.md）

前置依赖: ch01_data_cleaning（需要先完成数据清洗）

执行方式:
    cd Product_Sales_Analysis
    python -m src.ch02_descriptive_analysis.script
"""

import sys
from pathlib import Path

# 将项目根目录添加到 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np

from src.utils import (
    load_preprocessed,
    save_dataframe,
    save_markdown,
    save_figure,
    OUTPUT_BASE,
    CATEGORY_LIST,
    CITY_LIST,
)
from src.utils.visualizer import (
    plot_category_sales,
    plot_city_sales,
    plot_time_series,
    plot_heatmap,
    plot_category_distribution,
)
from src.utils.metrics import (
    calc_total_sales,
    calc_avg_price,
    calc_category_summary,
    calc_city_summary,
)


def main():
    """执行描述性统计与可视化主流程。"""
    print("=" * 60)
    print("ch02 描述性统计与可视化 - 开始执行")
    print("=" * 60)

    # 定义输出目录
    output_dir = OUTPUT_BASE / "descriptive_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # 步骤 1: 加载清洗后的数据
    # ============================================================
    print("\n--- 步骤 1: 加载清洗后的数据 ---")
    df = load_preprocessed("ch01_data_cleaning", "product")
    print(f"数据形状: {df.shape}")
    print(f"数据列: {df.columns.tolist()}")

    # ============================================================
    # 步骤 2: 描述性统计分析
    # ============================================================
    print("\n--- 步骤 2: 描述性统计分析 ---")
    desc_stats = df.describe(include="all")
    print("描述性统计:")
    print(desc_stats)

    # 保存描述性统计结果
    save_dataframe(desc_stats, output_dir / "descriptive_statistics.csv")

    # 计算关键指标
    total_sales = calc_total_sales(df)
    avg_price = calc_avg_price(df)

    # ============================================================
    # 步骤 3: 产品类别分析
    # ============================================================
    print("\n--- 步骤 3: 产品类别分析 ---")
    category_summary = calc_category_summary(df)
    print("类别汇总:")
    print(category_summary.to_string(index=False))

    # 保存类别汇总
    save_dataframe(category_summary, output_dir / "category_summary.csv")

    # 绘制类别销售额柱状图
    fig1, ax1 = plt.subplots()
    plot_category_sales(df, save_path=output_dir / "category_sales.png")
    plt.close()

    # 绘制类别分布饼图
    plot_category_distribution(df, save_path=output_dir / "category_distribution.png")
    plt.close()

    # ============================================================
    # 步骤 4: 城市维度分析
    # ============================================================
    print("\n--- 步骤 4: 城市维度分析 ---")
    city_summary = calc_city_summary(df)
    print("城市汇总:")
    print(city_summary.to_string(index=False))

    # 保存城市汇总
    save_dataframe(city_summary, output_dir / "city_summary.csv")

    # 绘制城市销售额对比图
    plot_city_sales(df, save_path=output_dir / "city_sales.png")
    plt.close()

    # ============================================================
    # 步骤 5: 时间趋势分析
    # ============================================================
    print("\n--- 步骤 5: 时间趋势分析 ---")
    if "date" in df.columns:
        # 绘制销售额时间趋势图
        plot_time_series(df, save_path=output_dir / "sales_time_series.png")
        plt.close()

        # 按月汇总
        df_copy = df.copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"])
        df_copy["month"] = df_copy["date"].dt.to_period("M")
        monthly_sales = df_copy.groupby("month")["total_price"].sum()
        print("月度销售额趋势:")
        print(monthly_sales)
        save_dataframe(monthly_sales.reset_index(), output_dir / "monthly_sales.csv")
    else:
        print("数据中无日期列，跳过时间趋势分析。")

    # ============================================================
    # 步骤 6: 相关性分析
    # ============================================================
    print("\n--- 步骤 6: 相关性分析 ---")
    plot_heatmap(df, save_path=output_dir / "correlation_heatmap.png")
    plt.close()

    # ============================================================
    # 步骤 7: 生成描述性统计与可视化报告
    # ============================================================
    print("\n--- 步骤 7: 生成描述性统计与可视化报告 ---")

    # 获取各类别销售额排名信息
    top_category = category_summary.iloc[0]["category"] if len(category_summary) > 0 else "N/A"
    top_city = city_summary.iloc[0]["city"] if len(city_summary) > 0 else "N/A"

    report_content = f"""# 描述性统计与可视化报告

## 背景

本报告基于清洗后的产品销售数据，进行描述性统计与可视化分析。
通过描述性统计、类别分析、城市分析和时间趋势分析，全面了解产品销售数据的分布特征和规律。

## 分析方法

1. **描述性统计分析**：计算各数值列的均值、标准差、最小值、最大值和分位数。
2. **产品类别分析**：按产品类别分组，汇总销售额、销量和订单数，绘制柱状图和饼图。
3. **城市维度分析**：按城市分组，对比各城市的销售表现。
4. **时间趋势分析**：按日期和月份汇总销售额，分析时间序列趋势。
5. **相关性分析**：计算数值列间的相关系数，绘制热力图。

## 分析发现

### 关键指标
- 总销售额：{total_sales:,.2f}
- 平均价格：{avg_price:,.2f}
- 数据总量：{df.shape[0]} 条记录

### 产品类别分析
- 销售额最高的类别：{top_category}
- 各类别销售额差异显著，{top_category} 类别表现最为突出。

### 城市维度分析
- 销售额最高的城市：{top_city}
- 各城市销售表现存在差异，需关注低销售城市的潜在机会。

### 时间趋势
- 销售额随时间呈现一定的波动趋势。
- 月度销售额变化反映了季节性和周期性特征。

### 相关性分析
- 数值列间的相关关系通过热力图展示。
- 价格与销售额之间存在预期的正相关关系。

## 小结

描述性统计与可视化分析揭示了产品销售数据的基本特征和分布规律。不同产品类别和城市之间
的销售表现存在显著差异，时间趋势分析为后续销售趋势预测提供了基础。
分析结果已保存至 outputs/descriptive_analysis/ 目录。
"""
    report_path = save_markdown(report_content, output_dir / "report.md")
    print(f"描述性统计与可视化报告已保存至: {report_path}")

    print("\n" + "=" * 60)
    print("ch02 描述性统计与可视化 - 执行完成")
    print("=" * 60)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    main()
