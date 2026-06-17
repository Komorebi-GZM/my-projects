# -*- coding: utf-8 -*-
"""analysis.py - 时序趋势分析脚本

分析电动汽车市场的年度时序变化趋势，包括：
- Step 6.1: 数据加载
- Step 6.2: 年度总销量趋势
- Step 6.3: 年度均价趋势
- Step 6.4: 年度核心参数趋势
- Step 6.5: 三线合一图
- Step 6.6: CAGR 计算
- Step 6.7: 年度环比增长率
- Step 6.8: 品牌年度销量变化
- Step 6.9: 章节报告生成

Usage:
    python -m src.ch06_temporal_trends.analysis
"""

import sys
from pathlib import Path

# 将项目根目录加入 sys.path，确保可以导入 src.utils
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from src.utils.config import (
    OUTPUT_BASE, DOMAIN_PARAMS, ENTITY_CONFIG, PLT_STYLE,
    COLUMN_CONFIG, CHAPTER_CONFIG,
)
from src.utils.data_loader import load_preprocessed
from src.utils.output_manager import save_dataframe, save_figure, save_markdown, ensure_dir
from src.utils.visualizer import plot_time_series, plot_heatmap, plot_multi_comparison


# ============================================================================
# Step 6.1: 数据加载
# ============================================================================

def step_6_1_load_data() -> pd.DataFrame:
    """Step 6.1: 加载清洗后的数据。

    Returns
    -------
    pd.DataFrame
        清洗后的数据。
    """
    print("\n" + "=" * 60)
    print("  Step 6.1: 数据加载")
    print("=" * 60)

    df = load_preprocessed(chapter="ch01_data_cleaning", filename="cleaned_data.csv")
    print(f"\n数据形状: {df.shape[0]} 行 x {df.shape[1]} 列")
    print(f"年份范围: {df['year'].min()} - {df['year'].max()}")
    print(f"年度分布:")
    print(df["year"].value_counts().sort_index().to_string())

    return df


# ============================================================================
# Step 6.2: 年度总销量趋势
# ============================================================================

def step_6_2_yearly_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Step 6.2: 计算年度总销量趋势。

    Parameters
    ----------
    df : pd.DataFrame
        输入数据。

    Returns
    -------
    pd.DataFrame
        年度销量趋势表。
    """
    print("\n" + "=" * 60)
    print("  Step 6.2: 年度总销量趋势")
    print("=" * 60)

    yearly_sales = df.groupby("year").agg({
        "annual_sales_units": ["sum", "mean", "count"],
    }).reset_index()
    yearly_sales.columns = ["year", "total_sales", "avg_sales", "model_count"]

    print(f"\n年度销量趋势:")
    print(yearly_sales.to_string(index=False))

    return yearly_sales


# ============================================================================
# Step 6.3: 年度均价趋势
# ============================================================================

def step_6_3_yearly_price_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Step 6.3: 计算年度均价趋势。

    Parameters
    ----------
    df : pd.DataFrame
        输入数据。

    Returns
    -------
    pd.DataFrame
        年度均价趋势表。
    """
    print("\n" + "=" * 60)
    print("  Step 6.3: 年度均价趋势")
    print("=" * 60)

    yearly_price = df.groupby("year").agg({
        "price_usd": ["mean", "median", "min", "max", "std"],
    }).reset_index()
    yearly_price.columns = ["year", "mean_price", "median_price", "min_price", "max_price", "std_price"]

    print(f"\n年度均价趋势:")
    print(yearly_price.to_string(index=False))

    return yearly_price


# ============================================================================
# Step 6.4: 年度核心参数趋势
# ============================================================================

def step_6_4_yearly_param_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Step 6.4: 计算年度核心参数趋势。

    Parameters
    ----------
    df : pd.DataFrame
        输入数据。

    Returns
    -------
    pd.DataFrame
        年度核心参数趋势表。
    """
    print("\n" + "=" * 60)
    print("  Step 6.4: 年度核心参数趋势")
    print("=" * 60)

    core_params = [
        "battery_capacity_kwh",
        "range_miles",
        "charging_speed_kw",
        "horsepower",
    ]

    yearly_params = df.groupby("year")[core_params].mean().reset_index()

    print(f"\n年度核心参数趋势:")
    print(yearly_params.to_string(index=False))

    return yearly_params


# ============================================================================
# Step 6.5: 三线合一图
# ============================================================================

def step_6_5_combined_trend_chart(
    df: pd.DataFrame,
    yearly_sales: pd.DataFrame,
    yearly_price: pd.DataFrame,
    yearly_params: pd.DataFrame,
    output_dir: Path,
):
    """Step 6.5: 绘制销量、价格、核心参数三线合一图。

    Parameters
    ----------
    df : pd.DataFrame
        输入数据。
    yearly_sales : pd.DataFrame
        年度销量趋势表。
    yearly_price : pd.DataFrame
        年度均价趋势表。
    yearly_params : pd.DataFrame
        年度核心参数趋势表。
    output_dir : Path
        输出目录。
    """
    print("\n" + "=" * 60)
    print("  Step 6.5: 三线合一图")
    print("=" * 60)

    # 设置样式
    try:
        plt.style.use(PLT_STYLE["style"])
    except OSError:
        plt.style.use("seaborn-v0_8-whitegrid")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 子图 1: 年度总销量
    ax1 = axes[0, 0]
    ax1.bar(yearly_sales["year"], yearly_sales["total_sales"] / 1e6, color="steelblue", alpha=0.7)
    ax1.set_title("年度总销量趋势", fontsize=12, fontweight="bold")
    ax1.set_xlabel("年份")
    ax1.set_ylabel("总销量 (百万辆)")
    ax1.grid(True, alpha=0.3)

    # 子图 2: 年度均价
    ax2 = axes[0, 1]
    ax2.plot(yearly_price["year"], yearly_price["mean_price"] / 1000, marker="o", linewidth=2, color="darkorange")
    ax2.fill_between(
        yearly_price["year"],
        yearly_price["min_price"] / 1000,
        yearly_price["max_price"] / 1000,
        alpha=0.2,
        color="darkorange",
    )
    ax2.set_title("年度均价趋势", fontsize=12, fontweight="bold")
    ax2.set_xlabel("年份")
    ax2.set_ylabel("均价 (千 USD)")
    ax2.grid(True, alpha=0.3)

    # 子图 3: 年度续航里程
    ax3 = axes[1, 0]
    ax3.plot(yearly_params["year"], yearly_params["range_miles"], marker="s", linewidth=2, color="green")
    ax3.set_title("年度平均续航里程", fontsize=12, fontweight="bold")
    ax3.set_xlabel("年份")
    ax3.set_ylabel("续航里程 (miles)")
    ax3.grid(True, alpha=0.3)

    # 子图 4: 年度电池容量
    ax4 = axes[1, 1]
    ax4.plot(yearly_params["year"], yearly_params["battery_capacity_kwh"], marker="^", linewidth=2, color="purple")
    ax4.set_title("年度平均电池容量", fontsize=12, fontweight="bold")
    ax4.set_xlabel("年份")
    ax4.set_ylabel("电池容量 (kWh)")
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    save_figure(fig, output_dir / "yearly_trend_chart.png")
    plt.close()

    print(f"\n三线合一图已保存")


# ============================================================================
# Step 6.6: CAGR 计算
# ============================================================================

def step_6_6_cagr_calculation(
    yearly_sales: pd.DataFrame,
    yearly_price: pd.DataFrame,
    yearly_params: pd.DataFrame,
    output_dir: Path,
) -> pd.DataFrame:
    """Step 6.6: 计算关键指标的复合年增长率 (CAGR)。

    Parameters
    ----------
    yearly_sales : pd.DataFrame
        年度销量趋势表。
    yearly_price : pd.DataFrame
        年度均价趋势表。
    yearly_params : pd.DataFrame
        年度核心参数趋势表。
    output_dir : Path
        输出目录。

    Returns
    -------
    pd.DataFrame
        CAGR 计算结果表。
    """
    print("\n" + "=" * 60)
    print("  Step 6.6: CAGR 计算")
    print("=" * 60)

    years = yearly_sales["year"].values
    n_years = len(years) - 1

    cagr_results = []

    # 销量 CAGR
    start_sales = yearly_sales["total_sales"].iloc[0]
    end_sales = yearly_sales["total_sales"].iloc[-1]
    cagr_sales = (end_sales / start_sales) ** (1 / n_years) - 1
    cagr_results.append({
        "指标": "总销量",
        "起始值": f"{start_sales:,.0f}",
        "终止值": f"{end_sales:,.0f}",
        "年数": n_years,
        "CAGR (%)": round(cagr_sales * 100, 2),
    })

    # 均价 CAGR
    start_price = yearly_price["mean_price"].iloc[0]
    end_price = yearly_price["mean_price"].iloc[-1]
    cagr_price = (end_price / start_price) ** (1 / n_years) - 1
    cagr_results.append({
        "指标": "均价",
        "起始值": f"${start_price:,.0f}",
        "终止值": f"${end_price:,.0f}",
        "年数": n_years,
        "CAGR (%)": round(cagr_price * 100, 2),
    })

    # 续航 CAGR
    start_range = yearly_params["range_miles"].iloc[0]
    end_range = yearly_params["range_miles"].iloc[-1]
    cagr_range = (end_range / start_range) ** (1 / n_years) - 1
    cagr_results.append({
        "指标": "续航里程",
        "起始值": f"{start_range:.0f} miles",
        "终止值": f"{end_range:.0f} miles",
        "年数": n_years,
        "CAGR (%)": round(cagr_range * 100, 2),
    })

    # 电池容量 CAGR
    start_battery = yearly_params["battery_capacity_kwh"].iloc[0]
    end_battery = yearly_params["battery_capacity_kwh"].iloc[-1]
    cagr_battery = (end_battery / start_battery) ** (1 / n_years) - 1
    cagr_results.append({
        "指标": "电池容量",
        "起始值": f"{start_battery:.1f} kWh",
        "终止值": f"{end_battery:.1f} kWh",
        "年数": n_years,
        "CAGR (%)": round(cagr_battery * 100, 2),
    })

    cagr_df = pd.DataFrame(cagr_results)
    print(f"\nCAGR 计算结果:")
    print(cagr_df.to_string(index=False))

    # 保存结果
    save_dataframe(cagr_df, output_dir / "cagr_table.csv")

    return cagr_df


# ============================================================================
# Step 6.7: 年度环比增长率
# ============================================================================

def step_6_7_yoy_growth_rates(
    yearly_sales: pd.DataFrame,
    yearly_price: pd.DataFrame,
    output_dir: Path,
) -> pd.DataFrame:
    """Step 6.7: 计算年度环比增长率。

    Parameters
    ----------
    yearly_sales : pd.DataFrame
        年度销量趋势表。
    yearly_price : pd.DataFrame
        年度均价趋势表。
    output_dir : Path
        输出目录。

    Returns
    -------
    pd.DataFrame
        年度环比增长率表。
    """
    print("\n" + "=" * 60)
    print("  Step 6.7: 年度环比增长率")
    print("=" * 60)

    yoy_data = []
    for i in range(1, len(yearly_sales)):
        year = yearly_sales["year"].iloc[i]
        prev_year = yearly_sales["year"].iloc[i - 1]

        # 销量环比
        sales_growth = (yearly_sales["total_sales"].iloc[i] / yearly_sales["total_sales"].iloc[i - 1] - 1) * 100

        # 均价环比
        price_growth = (yearly_price["mean_price"].iloc[i] / yearly_price["mean_price"].iloc[i - 1] - 1) * 100

        yoy_data.append({
            "年份": year,
            "销量环比 (%)": round(sales_growth, 2),
            "均价环比 (%)": round(price_growth, 2),
        })

    yoy_df = pd.DataFrame(yoy_data)
    print(f"\n年度环比增长率:")
    print(yoy_df.to_string(index=False))

    # 保存结果
    save_dataframe(yoy_df, output_dir / "yoy_growth_rates.csv")

    return yoy_df


# ============================================================================
# Step 6.8: 品牌年度销量变化
# ============================================================================

def step_6_8_brand_yearly_sales(df: pd.DataFrame, output_dir: Path):
    """Step 6.8: 分析各品牌年度销量变化。

    Parameters
    ----------
    df : pd.DataFrame
        输入数据。
    output_dir : Path
        输出目录。
    """
    print("\n" + "=" * 60)
    print("  Step 6.8: 品牌年度销量变化")
    print("=" * 60)

    # 计算各品牌年度销量
    brand_yearly = df.groupby(["brand", "year"])["annual_sales_units"].sum().reset_index()

    # 获取 TOP5 品牌
    top_brands = df.groupby("brand")["annual_sales_units"].sum().nlargest(5).index.tolist()
    brand_yearly_top = brand_yearly[brand_yearly["brand"].isin(top_brands)]

    print(f"\nTOP5 品牌年度销量:")
    print(brand_yearly_top.pivot(index="brand", columns="year", values="annual_sales_units").to_string())

    # 绘制品牌年度销量变化图
    try:
        plt.style.use(PLT_STYLE["style"])
    except OSError:
        plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(12, 6))

    for brand in top_brands:
        brand_data = brand_yearly_top[brand_yearly_top["brand"] == brand]
        ax.plot(brand_data["year"], brand_data["annual_sales_units"] / 1000, marker="o", linewidth=2, label=brand)

    ax.set_title("TOP5 品牌年度销量变化", fontsize=14, fontweight="bold")
    ax.set_xlabel("年份")
    ax.set_ylabel("销量 (千辆)")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    save_figure(fig, output_dir / "brand_yearly_sales.png")
    plt.close()

    print(f"\n品牌年度销量变化图已保存")


# ============================================================================
# Step 6.9: 章节报告生成
# ============================================================================

def step_6_9_generate_report(
    yearly_sales: pd.DataFrame,
    yearly_price: pd.DataFrame,
    yearly_params: pd.DataFrame,
    cagr_df: pd.DataFrame,
    yoy_df: pd.DataFrame,
    output_dir: Path,
):
    """Step 6.9: 生成时序趋势分析章节报告。

    Parameters
    ----------
    yearly_sales : pd.DataFrame
        年度销量趋势表。
    yearly_price : pd.DataFrame
        年度均价趋势表。
    yearly_params : pd.DataFrame
        年度核心参数趋势表。
    cagr_df : pd.DataFrame
        CAGR 计算结果表。
    yoy_df : pd.DataFrame
        年度环比增长率表。
    output_dir : Path
        输出目录。
    """
    print("\n" + "=" * 60)
    print("  Step 6.9: 章节报告生成")
    print("=" * 60)

    # 合并年度趋势数据
    yearly_trends = yearly_sales.merge(yearly_price, on="year").merge(yearly_params, on="year")
    save_dataframe(yearly_trends, output_dir / "yearly_trends.csv")

    report = f"""# 时序趋势分析报告 (Chapter 06)

## 1. 分析概述

本章分析电动汽车市场的年度时序变化趋势，包括：
- 年度总销量趋势
- 年度均价趋势
- 年度核心参数趋势
- 三线合一图
- CAGR 计算
- 年度环比增长率
- 品牌年度销量变化

## 2. 年度趋势汇总

{yearly_trends.to_markdown(index=False)}

## 3. CAGR 分析

{cagr_df.to_markdown(index=False)}

## 4. 年度环比增长率

{yoy_df.to_markdown(index=False)}

## 5. 产出文件清单

| 文件名 | 说明 |
|--------|------|
| yearly_trends.csv | 年度趋势汇总表 |
| yearly_trend_chart.png | 三线合一趋势图 |
| cagr_table.csv | CAGR 计算结果 |
| yoy_growth_rates.csv | 年度环比增长率 |
| brand_yearly_sales.png | 品牌年度销量变化图 |
| ch06_report.md | 章节报告 |

## 6. 质量验证检查清单

- [ ] 数据加载成功，形状符合预期
- [ ] 年度销量趋势计算正确
- [ ] 年度均价趋势计算正确
- [ ] 年度核心参数趋势计算正确
- [ ] 三线合一图清晰可读
- [ ] CAGR 计算结果合理
- [ ] 环比增长率计算正确
- [ ] 品牌年度销量变化图展示趋势
- [ ] 所有产物文件已保存
"""

    save_markdown(report, output_dir / "ch06_report.md")
    print(f"\n章节报告已保存")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """时序趋势分析主流程。

    按顺序执行 Step 6.1 ~ Step 6.9，完成时序趋势分析并保存结果。
    """
    print("=" * 60)
    print("  电动汽车市场数据分析 - 时序趋势分析 (Chapter 06)")
    print("=" * 60)

    # 输出目录
    output_dir = OUTPUT_BASE / "ch06_temporal_trends"
    ensure_dir(output_dir)

    # Step 6.1: 数据加载
    print("\n[Step 6.1] 数据加载...")
    df = step_6_1_load_data()

    # Step 6.2: 年度总销量趋势
    print("\n[Step 6.2] 年度总销量趋势...")
    yearly_sales = step_6_2_yearly_sales_trend(df)

    # Step 6.3: 年度均价趋势
    print("\n[Step 6.3] 年度均价趋势...")
    yearly_price = step_6_3_yearly_price_trend(df)

    # Step 6.4: 年度核心参数趋势
    print("\n[Step 6.4] 年度核心参数趋势...")
    yearly_params = step_6_4_yearly_param_trends(df)

    # Step 6.5: 三线合一图
    print("\n[Step 6.5] 三线合一图...")
    step_6_5_combined_trend_chart(df, yearly_sales, yearly_price, yearly_params, output_dir)

    # Step 6.6: CAGR 计算
    print("\n[Step 6.6] CAGR 计算...")
    cagr_df = step_6_6_cagr_calculation(yearly_sales, yearly_price, yearly_params, output_dir)

    # Step 6.7: 年度环比增长率
    print("\n[Step 6.7] 年度环比增长率...")
    yoy_df = step_6_7_yoy_growth_rates(yearly_sales, yearly_price, output_dir)

    # Step 6.8: 品牌年度销量变化
    print("\n[Step 6.8] 品牌年度销量变化...")
    step_6_8_brand_yearly_sales(df, output_dir)

    # Step 6.9: 章节报告生成
    print("\n[Step 6.9] 章节报告生成...")
    step_6_9_generate_report(yearly_sales, yearly_price, yearly_params, cagr_df, yoy_df, output_dir)

    # 最终摘要
    print("\n" + "=" * 60)
    print("  时序趋势分析完成!")
    print("=" * 60)
    print(f"\n输出目录: {output_dir}")
    print(f"\n输出产物列表:")
    for f in sorted(output_dir.glob("*")):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
