# -*- coding: utf-8 -*-
"""ch02_market_landscape/analysis.py - 第二章 市场格局分析

从品牌、国家、市场细分三个维度全面解析全球 EV 市场竞争格局，
量化各品牌的销量排名、市占率分布与产品线宽度，构建品牌定位图谱。

输出产物（共7个）：
1. brand_sales_ranking.csv — 品牌销量排名表（TOP10/TOP20）
2. brand_market_share.png — 品牌市占率饼图
3. brand_segment_crosstab.csv — 品牌×市场细分交叉表
4. country_sales_distribution.png — 国家销量分布柱状图
5. segment_distribution.png — 市场细分分布饼图
6. brand_positioning_map.png — 品牌定位散点图（价格×销量×产品线宽度）
7. ch02_report.md — 章节分析报告
"""

import sys
from pathlib import Path

# ========== 项目根目录 ==========
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

from utils.config import OUTPUT_BASE, PLT_STYLE
from utils.data_loader import load_preprocessed
from utils.output_manager import ensure_dir, save_dataframe, save_figure, save_markdown


def calc_market_share(series: pd.Series) -> pd.Series:
    """计算各分组占总量的百分比（市占率）。"""
    return (series / series.sum() * 100).round(2)


def calc_concentration_ratio(series: pd.Series, top_n: int = 3) -> float:
    """计算集中度比率 CRn（前N名占总量的百分比）。"""
    return series.head(top_n).sum() / series.sum() * 100


def setup_plt_style():
    """设置 matplotlib 全局样式。"""
    try:
        plt.style.use(PLT_STYLE["style"])
    except OSError:
        plt.style.use("seaborn-v0_8-whitegrid")
    sns.set_palette(PLT_STYLE["color_palette"])
    plt.rcParams.update({
        "font.size": PLT_STYLE["font_size"],
        "figure.dpi": PLT_STYLE["figure_dpi"],
        "savefig.dpi": PLT_STYLE["save_dpi"],
    })


def format_thousands(x: float, pos=None) -> str:
    """坐标轴千分位格式化器。"""
    return f"{int(x):,}"


def step1_brand_sales_ranking(df: pd.DataFrame, chapter_output: Path):
    """Step 1: 品牌销量排名计算"""
    print("\n" + "="*60)
    print("Step 1: 品牌销量排名计算")
    print("="*60)

    # 按品牌汇总销量
    brand_sales = (
        df.groupby("brand")["annual_sales_units"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"annual_sales_units": "total_sales"})
    )

    # 添加排名列
    brand_sales["rank"] = range(1, len(brand_sales) + 1)

    # 计算市占率
    brand_sales["market_share_pct"] = calc_market_share(brand_sales["total_sales"])

    # 计算累计市占率
    brand_sales["cumulative_share_pct"] = brand_sales["market_share_pct"].cumsum()

    # 输出 TOP10 和 TOP20
    top10 = brand_sales.head(10)
    top20 = brand_sales.head(20)

    print("\n=== 品牌销量排名 TOP10 ===")
    print(top10[["rank", "brand", "total_sales", "market_share_pct", "cumulative_share_pct"]].to_string(index=False))

    # 计算集中度指标
    cr3 = calc_concentration_ratio(brand_sales["total_sales"], top_n=3)
    cr5 = calc_concentration_ratio(brand_sales["total_sales"], top_n=5)
    cr10 = calc_concentration_ratio(brand_sales["total_sales"], top_n=10)
    print(f"\nCR3={cr3:.1f}%, CR5={cr5:.1f}%, CR10={cr10:.1f}%")

    # 保存产物
    save_dataframe(brand_sales, chapter_output / "brand_sales_ranking.csv", index=False)

    # 验证检查
    assert len(brand_sales) == 20, f"品牌数应为20，实际为{len(brand_sales)}"
    assert abs(brand_sales["market_share_pct"].sum() - 100) < 0.01, "市占率之和不等于100%"
    assert cr10 > 60, f"TOP10销量占比应>60%，实际为{cr10:.1f}%"

    print("[OK] Step 1 完成")
    return brand_sales, top10, cr3, cr5, cr10


def step2_brand_market_share_viz(brand_sales: pd.DataFrame, chapter_output: Path, cr3: float, cr5: float, cr10: float):
    """Step 2: 品牌市占率可视化"""
    print("\n" + "="*60)
    print("Step 2: 品牌市占率可视化")
    print("="*60)

    setup_plt_style()

    # 图2a: 水平柱状图（TOP20全品牌）
    fig, ax = plt.subplots(figsize=(14, 9))

    # 数据准备（倒序，使最大值在顶部）
    plot_data = brand_sales.sort_values("total_sales", ascending=True)

    # 颜色映射：TOP5用深色，其余用浅色
    colors = ["#2c3e50" if i >= 15 else "#7f8c8d" for i in range(20)]

    bars = ax.barh(
        y=plot_data["brand"],
        width=plot_data["total_sales"],
        color=colors,
        edgecolor="white",
        linewidth=0.5,
    )

    # 在柱体右侧标注数值
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + plot_data["total_sales"].max() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{width:,.0f}",
            va="center",
            fontsize=9,
        )

    ax.set_xlabel("Annual Sales Units", fontsize=12)
    ax.set_title("EV Brand Sales Ranking (TOP 20)", fontsize=16, fontweight="bold", pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_thousands))

    # 添加集中度标注
    textstr = f"CR3 = {cr3:.1f}%\nCR5 = {cr5:.1f}%\nCR10 = {cr10:.1f}%"
    props = dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8)
    ax.text(0.75, 0.25, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment="top", bbox=props)

    plt.tight_layout()
    save_figure(fig, chapter_output / "brand_market_share.png", dpi=150)
    plt.close()

    print("[OK] 品牌市占率图已保存")


def step3_brand_profile(df: pd.DataFrame):
    """Step 3: 品牌均价与产品线宽度分析"""
    print("\n" + "="*60)
    print("Step 3: 品牌均价与产品线宽度分析")
    print("="*60)

    brand_profile = (
        df.groupby("brand")
        .agg(
            avg_price=("price_usd", "mean"),
            median_price=("price_usd", "median"),
            std_price=("price_usd", "std"),
            total_sales=("annual_sales_units", "sum"),
            n_models=("model", "nunique"),
            n_variants=("variant", "nunique"),
            avg_rating=("customer_rating", "mean"),
        )
        .round(2)
        .sort_values("avg_price", ascending=False)
        .reset_index()
    )

    # 添加价格区间标签
    price_bins = [0, 30000, 50000, 80000, float("inf")]
    price_labels = ["<30K", "30K-50K", "50K-80K", ">80K"]
    brand_profile["price_tier"] = pd.cut(
        brand_profile["avg_price"], bins=price_bins, labels=price_labels
    )

    print("\n=== 品牌综合实力表 ===")
    print(brand_profile[["brand", "avg_price", "n_models", "total_sales", "avg_rating"]].to_string(index=False))

    # 验证检查
    assert len(brand_profile) == 20, f"品牌数应为20，实际为{len(brand_profile)}"
    assert brand_profile["n_models"].max() >= 3, "产品线宽度最大值应>=3"

    print("[OK] Step 3 完成")
    return brand_profile


def step4_country_distribution(df: pd.DataFrame, chapter_output: Path):
    """Step 4: 国家销量分布分析"""
    print("\n" + "="*60)
    print("Step 4: 国家销量分布分析")
    print("="*60)

    country_stats = (
        df.groupby("country_of_origin")
        .agg(
            total_sales=("annual_sales_units", "sum"),
            n_brands=("brand", "nunique"),
            avg_price=("price_usd", "mean"),
            n_models=("model", "nunique"),
        )
        .round(2)
        .sort_values("total_sales", ascending=False)
        .reset_index()
    )

    country_stats["sales_share_pct"] = (
        country_stats["total_sales"] / country_stats["total_sales"].sum() * 100
    ).round(2)

    print("\n=== 国家销量分布 ===")
    print(country_stats.to_string(index=False))

    # 可视化：国家销量分布图
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # 颜色映射
    country_color_map = {
        "US": "#e74c3c", "China": "#3498db", "Germany": "#2ecc71",
        "Japan": "#f39c12", "South Korea": "#9b59b6", "Sweden": "#1abc9c",
    }
    bar_colors = [country_color_map.get(c, "#95a5a6") for c in country_stats["country_of_origin"]]

    # 左图：销量柱状图
    ax1 = axes[0]
    bars1 = ax1.bar(
        country_stats["country_of_origin"],
        country_stats["total_sales"],
        color=bar_colors,
        edgecolor="white",
        linewidth=1,
    )
    for bar in bars1:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2, height + country_stats["total_sales"].max() * 0.01,
            f"{height:,.0f}", ha="center", va="bottom", fontsize=10, fontweight="bold"
        )
    ax1.set_title("Sales Volume by Country of Origin", fontsize=14, fontweight="bold")
    ax1.set_ylabel("Annual Sales Units")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(format_thousands))

    # 右图：品牌数量柱状图
    ax2 = axes[1]
    bars2 = ax2.bar(
        country_stats["country_of_origin"],
        country_stats["n_brands"],
        color=bar_colors,
        edgecolor="white",
        linewidth=1,
    )
    for bar in bars2:
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2, height + 0.1,
            f"{int(height)}", ha="center", va="bottom", fontsize=11, fontweight="bold"
        )
    ax2.set_title("Number of Brands by Country", fontsize=14, fontweight="bold")
    ax2.set_ylabel("Brand Count")
    ax2.set_ylim(0, country_stats["n_brands"].max() + 2)

    plt.tight_layout()
    save_figure(fig, chapter_output / "country_sales_distribution.png", dpi=150)
    plt.close()

    # 验证检查
    assert len(country_stats) >= 5, f"国家数应>=5，实际为{len(country_stats)}"
    assert abs(country_stats["sales_share_pct"].sum() - 100) < 0.01, "销量占比之和不等于100%"

    print("[OK] 国家销量分布图已保存")
    return country_stats


def step5_segment_distribution(df: pd.DataFrame, chapter_output: Path):
    """Step 5: 市场细分结构分析"""
    print("\n" + "="*60)
    print("Step 5: 市场细分结构分析")
    print("="*60)

    segment_order = ["Budget", "Mid-range", "Premium", "Luxury"]

    segment_stats = (
        df.groupby("market_segment")
        .agg(
            n_models=("model", "nunique"),
            total_records=("brand", "count"),
            total_sales=("annual_sales_units", "sum"),
            avg_price=("price_usd", "mean"),
            avg_range=("range_miles", "mean"),
            avg_battery=("battery_capacity_kwh", "mean"),
        )
        .round(2)
        .reindex(segment_order)
        .reset_index()
    )

    segment_stats["sales_share_pct"] = (
        segment_stats["total_sales"] / segment_stats["total_sales"].sum() * 100
    ).round(2)

    print("\n=== 市场细分结构 ===")
    print(segment_stats.to_string(index=False))

    # 可视化：市场细分分布图
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # 左图：销量占比饼图
    ax1 = axes[0]
    pie_colors = ["#27ae60", "#f1c40f", "#e67e22", "#c0392b"]
    wedges, texts, autotexts = ax1.pie(
        segment_stats["total_sales"],
        labels=segment_stats["market_segment"],
        autopct="%1.1f%%",
        colors=pie_colors,
        startangle=90,
        pctdistance=0.75,
        wedgeprops=dict(width=0.5, edgecolor="white", linewidth=2),
    )
    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_fontweight("bold")
    ax1.set_title("Sales Share by Market Segment", fontsize=14, fontweight="bold")

    # 右图：各细分车型数 + 均价双轴柱状图
    ax2 = axes[1]
    x = range(len(segment_order))
    width = 0.35

    bars1 = ax2.bar(
        [i - width / 2 for i in x], segment_stats["total_records"],
        width=width, label="Record Count", color="#3498db", edgecolor="white"
    )
    ax2.set_ylabel("Record Count", color="#3498db")
    ax2.tick_params(axis="y", labelcolor="#3498db")

    ax2_twin = ax2.twinx()
    bars2 = ax2_twin.bar(
        [i + width / 2 for i in x], segment_stats["avg_price"],
        width=width, label="Avg Price (USD)", color="#e74c3c", edgecolor="white"
    )
    ax2_twin.set_ylabel("Avg Price (USD)", color="#e74c3c")
    ax2_twin.tick_params(axis="y", labelcolor="#e74c3c")
    ax2_twin.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x:,.0f}"))

    ax2.set_xticks(list(x))
    ax2.set_xticklabels(segment_order)
    ax2.set_title("Records & Avg Price by Segment", fontsize=14, fontweight="bold")

    # 合并图例
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.tight_layout()
    save_figure(fig, chapter_output / "segment_distribution.png", dpi=150)
    plt.close()

    # 验证检查
    assert len(segment_stats) == 4, f"市场细分数应为4，实际为{len(segment_stats)}"
    assert abs(segment_stats["sales_share_pct"].sum() - 100) < 0.01, "销量占比之和不等于100%"

    print("[OK] 市场细分分布图已保存")
    return segment_stats


def step6_brand_segment_crosstab(df: pd.DataFrame, brand_sales: pd.DataFrame, chapter_output: Path):
    """Step 6: 品牌 x 市场细分交叉分析"""
    print("\n" + "="*60)
    print("Step 6: 品牌 x 市场细分交叉分析")
    print("="*60)

    segment_order = ["Budget", "Mid-range", "Premium", "Luxury"]

    # 交叉表：车型数量
    crosstab_count = pd.crosstab(df["brand"], df["market_segment"])
    crosstab_count = crosstab_count.reindex(columns=segment_order, fill_value=0)

    # 交叉表：销量
    crosstab_sales = pd.crosstab(
        df["brand"], df["market_segment"],
        values=df["annual_sales_units"], aggfunc="sum"
    ).fillna(0)
    crosstab_sales = crosstab_sales.reindex(columns=segment_order, fill_value=0)

    # 行归一化（各品牌在各细分的销量占比）
    crosstab_pct = crosstab_sales.div(crosstab_sales.sum(axis=1), axis=0) * 100

    # 识别各品牌主力细分
    brand_main_segment = crosstab_pct.idxmax(axis=1).reset_index()
    brand_main_segment.columns = ["brand", "main_segment"]
    brand_main_segment["main_segment_pct"] = crosstab_pct.max(axis=1).values
    brand_main_segment = brand_main_segment.sort_values("main_segment_pct", ascending=False)

    print("\n=== 各品牌主力市场细分 ===")
    print(brand_main_segment.to_string(index=False))

    # 保存交叉表
    save_dataframe(crosstab_count, chapter_output / "brand_segment_crosstab.csv")

    # 可视化：堆叠柱状图
    fig, ax = plt.subplots(figsize=(16, 9))

    crosstab_plot = crosstab_sales.loc[brand_sales["brand"]]  # 按销量排名排列品牌
    pie_colors = ["#27ae60", "#f1c40f", "#e67e22", "#c0392b"]
    crosstab_plot.plot(
        kind="barh", stacked=True, ax=ax,
        color=pie_colors, edgecolor="white", linewidth=0.5
    )

    ax.set_xlabel("Annual Sales Units")
    ax.set_title("Brand Sales by Market Segment (Stacked)", fontsize=16, fontweight="bold", pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_thousands))
    ax.legend(title="Segment", bbox_to_anchor=(1.02, 1), loc="upper left")

    plt.tight_layout()
    save_figure(fig, chapter_output / "brand_segment_stacked.png", dpi=150)
    plt.close()

    # 验证检查
    assert len(crosstab_count) == 20, f"交叉表行数应为20，实际为{len(crosstab_count)}"
    assert len(crosstab_count.columns) == 4, f"交叉表列数应为4，实际为{len(crosstab_count.columns)}"

    print("[OK] 品牌 x 细分交叉分析完成")
    return crosstab_count, crosstab_sales


def step7_brand_positioning_map(df: pd.DataFrame, brand_sales: pd.DataFrame, brand_profile: pd.DataFrame, chapter_output: Path):
    """Step 7: 品牌定位图谱绘制"""
    print("\n" + "="*60)
    print("Step 7: 品牌定位图谱绘制")
    print("="*60)

    # 合并数据
    brand_position = brand_sales.merge(
        brand_profile[["brand", "avg_price", "n_models", "avg_rating"]],
        on="brand", how="left"
    )

    # 添加国家信息
    brand_country = df.groupby("brand")["country_of_origin"].first().reset_index()
    brand_position = brand_position.merge(brand_country, on="brand", how="left")

    # 国家颜色映射
    country_colors = {
        "US": "#e74c3c", "China": "#3498db", "Germany": "#2ecc71",
        "Japan": "#f39c12", "South Korea": "#9b59b6", "Sweden": "#1abc9c",
    }
    brand_position["color"] = brand_position["country_of_origin"].map(country_colors)

    # 绘制气泡图
    fig, ax = plt.subplots(figsize=(16, 11))

    # 气泡大小缩放
    bubble_scale = brand_position["n_models"] * 80

    # 绘制气泡
    for idx, row in brand_position.iterrows():
        ax.scatter(
            row["avg_price"], row["total_sales"],
            s=bubble_scale.iloc[idx],
            c=row["color"],
            alpha=0.6,
            edgecolors="black",
            linewidth=0.8,
        )
        # 品牌名标注
        ax.annotate(
            row["brand"],
            (row["avg_price"], row["total_sales"]),
            textcoords="offset points",
            xytext=(8, 8),
            fontsize=8,
            alpha=0.85,
        )

    # 象限分割线
    median_price = brand_position["avg_price"].median()
    median_sales = brand_position["total_sales"].median()
    ax.axvline(x=median_price, color="gray", linestyle="--", linewidth=1, alpha=0.7)
    ax.axhline(y=median_sales, color="gray", linestyle="--", linewidth=1, alpha=0.7)

    # 象限标注
    ax.text(0.02, 0.98, "High Sales / Low Price\n(Mass Market Leader)",
            transform=ax.transAxes, fontsize=9, va="top", color="#27ae60", fontstyle="italic")
    ax.text(0.98, 0.98, "High Sales / High Price\n(Premium Market Leader)",
            transform=ax.transAxes, fontsize=9, va="top", ha="right", color="#e74c3c", fontstyle="italic")
    ax.text(0.02, 0.02, "Low Sales / Low Price\n(Economy Challenger)",
            transform=ax.transAxes, fontsize=9, va="bottom", color="#f39c12", fontstyle="italic")
    ax.text(0.98, 0.02, "Low Sales / High Price\n(Niche Player)",
            transform=ax.transAxes, fontsize=9, va="bottom", ha="right", color="#8e44ad", fontstyle="italic")

    # 图例（国家颜色）
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=c, label=k, edgecolor="black") for k, c in country_colors.items()]
    ax.legend(handles=legend_elements, title="Country of Origin", loc="center left",
              bbox_to_anchor=(1.02, 0.5), fontsize=10)

    ax.set_xlabel("Average Price (USD)", fontsize=13)
    ax.set_ylabel("Total Annual Sales Units", fontsize=13)
    ax.set_title("EV Brand Positioning Map\n(Bubble Size = Number of Models)", fontsize=16, fontweight="bold", pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(format_thousands))

    plt.tight_layout()
    save_figure(fig, chapter_output / "brand_positioning_map.png", dpi=150)
    plt.close()

    # 验证检查
    assert len(brand_position) == 20, f"品牌定位图谱应包含20个品牌，实际为{len(brand_position)}"

    print("[OK] 品牌定位图谱已保存")
    return brand_position


def step8_generate_report(
    chapter_output: Path,
    top10: pd.DataFrame,
    cr3: float, cr5: float, cr10: float,
    country_stats: pd.DataFrame,
    segment_stats: pd.DataFrame
):
    """Step 8: 章节报告生成"""
    print("\n" + "="*60)
    print("Step 8: 章节报告生成")
    print("="*60)

    report_content = f"""# 第二章 市场格局分析

> **章节编号**: ch02 | **分析类型**: 分析探索型（原型B） | **优先级**: P0

---

## 2.1 品牌销量排名

全球EV市场呈现明显的头部集中效应。TOP10品牌销量之和占总销量的 **{cr10:.1f}%**，CR3达到 **{cr3:.1f}%**。

### TOP10 品牌销量排名

| 排名 | 品牌 | 总销量 | 市占率(%) | 累计市占率(%) |
|------|------|--------|-----------|---------------|
"""

    # 添加TOP10数据行
    for _, row in top10.iterrows():
        report_content += f"| {int(row['rank'])} | {row['brand']} | {row['total_sales']:,.0f} | {row['market_share_pct']:.2f} | {row['cumulative_share_pct']:.2f} |\n"

    report_content += f"""
**关键发现**：
- 市场集中度：CR3={cr3:.1f}%，CR5={cr5:.1f}%，CR10={cr10:.1f}%
- 头部品牌（TOP5）占据市场主导地位，长尾品牌竞争激烈

## 2.2 品牌市占率分布

![品牌市占率图](brand_market_share.png)

## 2.3 国家销量分布

![国家销量分布图](country_sales_distribution.png)

| 国家 | 总销量 | 品牌数 | 销量占比(%) | 均价(USD) |
|------|--------|--------|-------------|-----------|
"""

    for _, row in country_stats.iterrows():
        report_content += f"| {row['country_of_origin']} | {row['total_sales']:,.0f} | {int(row['n_brands'])} | {row['sales_share_pct']:.2f} | {row['avg_price']:,.0f} |\n"

    report_content += f"""
## 2.4 市场细分结构

![市场细分分布图](segment_distribution.png)

| 细分 | 记录数 | 总销量 | 销量占比(%) | 均价(USD) | 平均续航(英里) |
|------|--------|--------|-------------|-----------|---------------|
"""

    for _, row in segment_stats.iterrows():
        report_content += f"| {row['market_segment']} | {int(row['total_records'])} | {row['total_sales']:,.0f} | {row['sales_share_pct']:.2f} | {row['avg_price']:,.0f} | {row['avg_range']:.1f} |\n"

    report_content += f"""
## 2.5 品牌 x 市场细分交叉分析

![品牌细分堆叠图](brand_segment_stacked.png)

## 2.6 品牌定位图谱

![品牌定位图谱](brand_positioning_map.png)

品牌定位图谱以均价为X轴、总销量为Y轴、产品线宽度为气泡大小，将20个品牌映射到四个象限：
- **大众市场领导者**（高销量/低价格）：销量领先且定价亲民的品牌
- **高端市场领导者**（高销量/高价格）：兼具销量和溢价能力的品牌
- **经济型挑战者**（低销量/低价格）：定价亲民但销量有待提升的品牌
- **利基市场玩家**（低销量/高价格）：专注高端细分市场的品牌

## 2.7 本章小结

本章从品牌、国家、市场细分三个维度全面解析了全球EV市场竞争格局。核心结论如下：

1. **品牌集中度高**：TOP10品牌占据超过60%的市场份额，头部效应显著
2. **国家分布不均**：中美两国品牌在销量和品牌数量上占据主导地位
3. **细分结构多元**：四个市场细分均有代表性品牌覆盖，Premium和Mid-range为竞争最激烈的区间
4. **品牌定位分化**：20个品牌在价格-销量二维空间中呈现明显的差异化定位

---

*报告生成时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
*数据来源：cleaned_data.csv（1070行 x 27列）*
"""

    save_markdown(report_content, chapter_output / "ch02_report.md")
    print("[OK] 章节报告已保存: ch02_report.md")


def main():
    """主函数：执行全部8个分析步骤"""
    print("\n" + "="*70)
    print("第二章 市场格局分析 - 开始执行")
    print("="*70)

    # 创建输出目录
    chapter_output = ensure_dir(OUTPUT_BASE / "ch02_market_landscape")
    print(f"[INFO] 输出目录: {chapter_output}")

    # 加载数据
    print("\n[INFO] 加载清洗后数据...")
    df = load_preprocessed(chapter="ch01_data_cleaning", filename="cleaned_data.csv")
    print(f"[INFO] 数据形状: {df.shape}")

    # 执行各步骤
    brand_sales, top10, cr3, cr5, cr10 = step1_brand_sales_ranking(df, chapter_output)
    step2_brand_market_share_viz(brand_sales, chapter_output, cr3, cr5, cr10)
    brand_profile = step3_brand_profile(df)
    country_stats = step4_country_distribution(df, chapter_output)
    segment_stats = step5_segment_distribution(df, chapter_output)
    step6_brand_segment_crosstab(df, brand_sales, chapter_output)
    step7_brand_positioning_map(df, brand_sales, brand_profile, chapter_output)
    step8_generate_report(chapter_output, top10, cr3, cr5, cr10, country_stats, segment_stats)

    print("\n" + "="*70)
    print("第二章 市场格局分析 - 执行完成")
    print("="*70)
    print(f"\n输出产物列表 ({chapter_output}):")
    for f in sorted(chapter_output.glob("*")):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
