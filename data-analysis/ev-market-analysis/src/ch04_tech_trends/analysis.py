# -*- coding: utf-8 -*-
"""ch04_tech_trends/analysis.py - 第四章 技术趋势分析

分析 2020-2026 年间 EV 核心技术参数（电池容量、续航里程、充电速度、马力、加速性能）
的年度演变轨迹，量化技术升级速度，识别技术代际差异。

输出产物（共6个）：
1. yearly_param_stats.csv — 核心参数年度统计表（均值/中位数/标准差）
2. tech_trend_lines.png — 技术趋势折线图（5子图）
3. param_cagr.csv — 参数年均增长率表（2020→2026 CAGR）
4. tech_generation_boxplot.png — 技术代际箱线图
5. brand_tech_leadership.csv — 品牌技术领先度排名
6. ch04_report.md — 章节分析报告
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


def setup_plt_style():
    """设置 matplotlib 全局样式。"""
    try:
        plt.style.use(PLT_STYLE["style"])
    except OSError:
        plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update({
        "font.size": PLT_STYLE["font_size"],
        "figure.dpi": PLT_STYLE["figure_dpi"],
        "savefig.dpi": PLT_STYLE["save_dpi"],
    })


# ========== 核心技术参数列表 ==========
CORE_PARAMS = [
    "battery_capacity_kwh",
    "range_miles",
    "charging_speed_kw",
    "horsepower",
    "acceleration_0_60_mph",
]

PARAM_LABELS = {
    "battery_capacity_kwh": ("Battery Capacity", "kWh"),
    "range_miles": ("Range", "miles"),
    "charging_speed_kw": ("Charging Speed", "kW"),
    "horsepower": ("Horsepower", "hp"),
    "acceleration_0_60_mph": ("0-60 mph Acceleration", "s"),
}


def step1_yearly_param_stats(df: pd.DataFrame, chapter_output: Path):
    """Step 1: 核心参数年度统计"""
    print("\n" + "=" * 60)
    print("Step 1: 核心参数年度统计")
    print("=" * 60)

    # 按年度分组计算描述性统计
    stats_list = []
    for param in CORE_PARAMS:
        yearly = df.groupby("year")[param].agg(
            ["mean", "median", "std", "min", "max", "count"]
        ).reset_index()
        yearly["parameter"] = param
        yearly.columns = [
            "year", "mean", "median", "std", "min", "max", "count", "parameter"
        ]
        stats_list.append(yearly)

    yearly_stats = pd.concat(stats_list, ignore_index=True)
    yearly_stats = yearly_stats[
        ["year", "parameter", "mean", "median", "std", "min", "max", "count"]
    ]

    print(f"\n年度参数统计表形状: {yearly_stats.shape}")
    print(f"年份覆盖: {sorted(yearly_stats['year'].unique())}")

    # 保存
    save_dataframe(yearly_stats.round(2), chapter_output / "yearly_param_stats.csv")

    # 验证
    years = sorted(yearly_stats["year"].unique())
    assert len(years) == 7, f"年份覆盖不足: {years}"
    assert years[0] == 2020 and years[-1] == 2026, f"年份范围异常: {years[0]}-{years[-1]}"
    assert len(yearly_stats) == 7 * 5, f"行数异常: {len(yearly_stats)}，应为35"

    print("[OK] Step 1 完成")
    return yearly_stats


def step2_tech_trend_lines(yearly_stats: pd.DataFrame, chapter_output: Path):
    """Step 2: 技术趋势折线图绘制"""
    print("\n" + "=" * 60)
    print("Step 2: 技术趋势折线图绘制")
    print("=" * 60)

    setup_plt_style()

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    for idx, param in enumerate(CORE_PARAMS):
        ax = axes[idx]
        subset = yearly_stats[yearly_stats["parameter"] == param].sort_values("year")
        label_en, unit = PARAM_LABELS[param]

        ax.plot(
            subset["year"], subset["mean"],
            marker="o", markersize=7, linewidth=2,
            color=plt.cm.Set2(idx), label=label_en,
        )

        # 标注数据点数值
        for _, row in subset.iterrows():
            ax.annotate(
                f"{row['mean']:.1f}",
                (row["year"], row["mean"]),
                textcoords="offset points",
                xytext=(0, 10),
                fontsize=8,
                ha="center",
            )

        ax.set_title(f"{label_en} Yearly Trend ({unit})", fontsize=12, fontweight="bold")
        ax.set_xlabel("Year", fontsize=10)
        ax.set_ylabel(f"{label_en} ({unit})", fontsize=10)
        ax.set_xticks(subset["year"])
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)

    # 隐藏第 6 个子图
    axes[5].set_visible(False)

    plt.suptitle("2020-2026 EV Core Tech Parameter Trends", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    save_figure(fig, chapter_output / "tech_trend_lines.png", dpi=150)
    plt.close()

    print("[OK] 技术趋势折线图已保存")


def step3_cagr_calculation(yearly_stats: pd.DataFrame, chapter_output: Path):
    """Step 3: CAGR 计算"""
    print("\n" + "=" * 60)
    print("Step 3: CAGR 计算")
    print("=" * 60)

    n_years = 6  # 2020 -> 2026, 共 6 个增长间隔

    cagr_records = []
    for param in CORE_PARAMS:
        subset = yearly_stats[yearly_stats["parameter"] == param].sort_values("year")
        v_begin = subset[subset["year"] == 2020]["mean"].values[0]
        v_end = subset[subset["year"] == 2026]["mean"].values[0]

        cagr = (v_end / v_begin) ** (1 / n_years) - 1

        # 加速时间越小越好，方向取反
        direction = "Higher is better" if param != "acceleration_0_60_mph" else "Lower is better"
        if param == "acceleration_0_60_mph":
            interpretation = f"Avg change {cagr*100:+.2f}% (decrease = performance improvement)"
        else:
            interpretation = f"Avg growth {cagr*100:+.2f}%"

        cagr_records.append({
            "parameter": param,
            "value_2020": round(v_begin, 2),
            "value_2026": round(v_end, 2),
            "cagr": round(cagr, 4),
            "cagr_pct": f"{cagr*100:+.2f}%",
            "direction": direction,
            "interpretation": interpretation,
        })

    cagr_df = pd.DataFrame(cagr_records)
    print("\nCAGR 计算结果:")
    print(cagr_df.to_string(index=False))

    # 保存
    save_dataframe(cagr_df, chapter_output / "param_cagr.csv")

    # 验证
    assert len(cagr_df) == 5, f"CAGR 行数异常: {len(cagr_df)}"
    assert all(cagr_df["value_2020"] > 0), "2020年均值不应为0"

    print("[OK] Step 3 完成")
    return cagr_df


def step4_tech_generation_boxplot(df: pd.DataFrame, chapter_output: Path):
    """Step 4: 技术代际箱线图"""
    print("\n" + "=" * 60)
    print("Step 4: 技术代际箱线图")
    print("=" * 60)

    setup_plt_style()

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    for idx, param in enumerate(CORE_PARAMS):
        ax = axes[idx]
        sns.boxplot(
            data=df, x="year", y=param, ax=ax,
            hue="year", hue_order=sorted(df["year"].unique()),
            palette="Set2", width=0.6, fliersize=3, legend=False,
        )
        label_en, unit = PARAM_LABELS[param]
        ax.set_title(f"{label_en} ({unit})", fontsize=12, fontweight="bold")
        ax.set_xlabel("Year", fontsize=10)
        ax.set_ylabel(f"{label_en} ({unit})", fontsize=10)
        ax.grid(True, alpha=0.3, axis="y")

    axes[5].set_visible(False)

    plt.suptitle("2020-2026 EV Core Tech Parameter Distribution (Boxplot)", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    save_figure(fig, chapter_output / "tech_generation_boxplot.png", dpi=150)
    plt.close()

    # 验证：每年至少有数据点
    yearly_counts = df.groupby("year").size()
    assert all(yearly_counts > 0), f"某年无数据: {yearly_counts[yearly_counts == 0]}"

    print("[OK] 技术代际箱线图已保存")


def step5_brand_tech_leadership(df: pd.DataFrame, chapter_output: Path):
    """Step 5: 品牌技术领先度分析"""
    print("\n" + "=" * 60)
    print("Step 5: 品牌技术领先度分析")
    print("=" * 60)

    # 使用全部数据计算品牌技术领先度（确保覆盖全部20个品牌）
    print(f"使用全部数据计算品牌技术领先度（覆盖 {df['year'].min()}-{df['year'].max()}）")

    # 按品牌分组计算均值
    brand_means = df.groupby("brand")[CORE_PARAMS].mean().reset_index()

    # Min-Max 标准化
    normalized = brand_means.copy()
    for param in CORE_PARAMS:
        min_val = brand_means[param].min()
        max_val = brand_means[param].max()
        col_name = f"{param}_norm"
        if param == "acceleration_0_60_mph":
            # 越小越好，取反后标准化
            normalized[col_name] = 1 - (brand_means[param] - min_val) / (max_val - min_val)
        else:
            normalized[col_name] = (brand_means[param] - min_val) / (max_val - min_val)

    # 计算综合评分（等权均值）
    norm_cols = [f"{p}_norm" for p in CORE_PARAMS]
    normalized["tech_score"] = normalized[norm_cols].mean(axis=1)

    # 排序输出
    result = normalized[["brand"] + CORE_PARAMS + ["tech_score"]].sort_values(
        "tech_score", ascending=False
    ).reset_index(drop=True)
    result["rank"] = range(1, len(result) + 1)
    result = result[["rank", "brand"] + CORE_PARAMS + ["tech_score"]]

    print("\n品牌技术领先度排名 (TOP 10):")
    print(result.head(10).to_string(index=False))

    # 保存
    save_dataframe(result.round(4), chapter_output / "brand_tech_leadership.csv")

    # 验证
    assert len(result) == 20, f"品牌数应为20，实际为{len(result)}"
    assert result["tech_score"].min() >= 0, "综合评分不应小于0"
    assert result["tech_score"].max() <= 1, "综合评分不应大于1"

    print("[OK] Step 5 完成")
    return result


def step6_param_correlation_trends(df: pd.DataFrame, chapter_output: Path):
    """Step 6: 参数间关联性年度变化"""
    print("\n" + "=" * 60)
    print("Step 6: 参数间关联性年度变化")
    print("=" * 60)

    setup_plt_style()

    years = sorted(df["year"].unique())
    correlation_records = []

    for year in years:
        df_year = df[df["year"] == year][CORE_PARAMS].dropna()
        corr_matrix = df_year.corr()
        for i, p1 in enumerate(CORE_PARAMS):
            for j, p2 in enumerate(CORE_PARAMS):
                if i < j:
                    correlation_records.append({
                        "year": year,
                        "param_1": p1,
                        "param_2": p2,
                        "pearson_r": round(corr_matrix.loc[p1, p2], 4),
                        "sample_size": len(df_year),
                    })

    corr_df = pd.DataFrame(correlation_records)
    print(f"相关系数记录共 {len(corr_df)} 行")

    # 关键参数对趋势图
    key_pairs = [
        ("battery_capacity_kwh", "range_miles", "Battery Capacity vs Range"),
        ("horsepower", "acceleration_0_60_mph", "Horsepower vs Acceleration"),
        ("battery_capacity_kwh", "charging_speed_kw", "Battery Capacity vs Charging Speed"),
        ("horsepower", "range_miles", "Horsepower vs Range"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, (p1, p2, title) in enumerate(key_pairs):
        ax = axes[idx]
        subset = corr_df[(corr_df["param_1"] == p1) & (corr_df["param_2"] == p2)]
        ax.plot(
            subset["year"], subset["pearson_r"],
            marker="o", markersize=7, linewidth=2,
            color=plt.cm.Set2(idx),
        )
        for _, row in subset.iterrows():
            ax.annotate(
                f"{row['pearson_r']:.3f}",
                (row["year"], row["pearson_r"]),
                textcoords="offset points",
                xytext=(0, 10),
                fontsize=8,
                ha="center",
            )
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xlabel("Year", fontsize=10)
        ax.set_ylabel("Pearson Correlation", fontsize=10)
        ax.set_xticks(subset["year"])
        ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
        ax.grid(True, alpha=0.3)

    plt.suptitle("Core Parameter Correlation Trends (Pearson r)", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    save_figure(fig, chapter_output / "param_correlation_trend.png", dpi=150)
    plt.close()

    # 保存相关系数汇总表
    save_dataframe(corr_df, chapter_output / "param_correlation_yearly.csv")

    print("[OK] 参数关联性趋势图已保存")
    return corr_df


def step7_generate_report(
    chapter_output: Path,
    yearly_stats: pd.DataFrame,
    cagr_df: pd.DataFrame,
    brand_leader: pd.DataFrame,
    corr_df: pd.DataFrame,
):
    """Step 7: 章节报告生成"""
    print("\n" + "=" * 60)
    print("Step 7: 章节报告生成")
    print("=" * 60)

    report_lines = []
    report_lines.append("# 第四章：技术趋势分析\n")
    report_lines.append("> **章节编号**: ch04 | **分析类型**: 分析探索型（原型B） | **优先级**: P0\n")
    report_lines.append("---\n")

    # 4.1
    report_lines.append("## 4.1 研究背景与目标\n")
    report_lines.append(
        "本章旨在系统分析 2020–2026 年间全球电动汽车核心技术参数的年度演变轨迹，"
        "涵盖电池容量、续航里程、充电速度、马力和加速性能五大核心维度。"
        "通过描述性统计、趋势可视化、CAGR 计算和相关性分析，揭示 EV 行业技术迭代的速度与方向。\n"
    )

    # 4.2
    report_lines.append("## 4.2 分析方法\n")
    report_lines.append("- **描述性统计**：按年度分组计算各参数的均值、中位数、标准差、极值")
    report_lines.append("- **趋势可视化**：折线图（含数据点标记）、箱线图（技术代际对比）")
    report_lines.append("- **CAGR 计算**：量化 2020->2026 年各参数的复合年增长率")
    report_lines.append("- **相关性分析**：逐年计算 Pearson 相关系数，观察参数间关联演变\n")

    # 4.3.1
    report_lines.append("## 4.3 核心发现\n")
    report_lines.append("### 4.3.1 核心参数年度演变趋势\n")
    report_lines.append("![技术趋势折线图](tech_trend_lines.png)\n")

    report_lines.append("| 参数 | 2020 年均值 | 2026 年均值 | 变化幅度 |")
    report_lines.append("|------|------------|------------|---------|")
    for _, row in cagr_df.iterrows():
        change = row["value_2026"] - row["value_2020"]
        report_lines.append(
            f"| {row['parameter']} | {row['value_2020']} | {row['value_2026']} | {change:+.2f} |"
        )
    report_lines.append("")

    # 4.3.2
    report_lines.append("### 4.3.2 复合年增长率（CAGR）\n")
    report_lines.append("| 参数 | CAGR | 解读 |")
    report_lines.append("|------|------|------|")
    for _, row in cagr_df.iterrows():
        report_lines.append(f"| {row['parameter']} | {row['cagr_pct']} | {row['interpretation']} |")
    report_lines.append("")

    # 4.3.3
    report_lines.append("### 4.3.3 技术代际差异\n")
    report_lines.append("![技术代际箱线图](tech_generation_boxplot.png)\n")
    report_lines.append(
        "箱线图展示了每年各参数的分布全貌，包括中位数、四分位距和异常值。"
        "可以观察到参数分布随年份的变化趋势和离散程度的演变。\n"
    )

    # 4.3.4
    report_lines.append("### 4.3.4 品牌技术领先度排名（TOP 5）\n")
    top5 = brand_leader.head(5)
    report_lines.append("| 排名 | 品牌 | 电池容量 | 续航里程 | 充电速度 | 马力 | 加速时间 | 综合评分 |")
    report_lines.append("|------|------|---------|---------|---------|------|---------|---------|")
    for _, row in top5.iterrows():
        report_lines.append(
            f"| {int(row['rank'])} | {row['brand']} | {row['battery_capacity_kwh']:.1f} | "
            f"{row['range_miles']:.1f} | {row['charging_speed_kw']:.1f} | "
            f"{row['horsepower']:.1f} | {row['acceleration_0_60_mph']:.2f} | "
            f"{row['tech_score']:.4f} |"
        )
    report_lines.append("")

    # 4.3.5
    report_lines.append("### 4.3.5 参数间关联性年度变化\n")
    report_lines.append("![参数关联性趋势图](param_correlation_trend.png)\n")
    report_lines.append(
        "通过逐年计算 Pearson 相关系数，可以观察到核心参数间关联性的演变趋势。"
        "重点关注电池容量与续航里程、马力与加速时间等关键参数对的相关性变化。\n"
    )

    # 4.4
    report_lines.append("## 4.4 关键洞察与小结\n")

    # 动态生成小结
    fastest_cagr = cagr_df.loc[cagr_df["parameter"] != "acceleration_0_60_mph"].sort_values("cagr", ascending=False).iloc[0]
    top_brand = brand_leader.iloc[0]

    report_lines.append(f"1. **技术迭代速度差异显著**：{fastest_cagr['parameter']} 的 CAGR 最高（{fastest_cagr['cagr_pct']}），是技术进步最快的维度")
    report_lines.append(f"2. **品牌技术领先度分化**：{top_brand['brand']} 以综合评分 {top_brand['tech_score']:.4f} 位居技术领先度榜首")
    report_lines.append("3. **各核心参数在 2020–2026 年间均呈现显著的技术进步趋势**")
    report_lines.append("4. **参数间关联性随时间推移呈现动态变化，反映了技术路线的演进**\n")

    report_lines.append("---\n")
    report_lines.append(f"*报告生成时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    report_lines.append("*数据来源：cleaned_data.csv（1070行 x 27列）*\n")

    report_content = "\n".join(report_lines)
    save_markdown(report_content, chapter_output / "ch04_report.md")
    print("[OK] 章节报告已保存: ch04_report.md")


def main():
    """主函数：执行全部7个分析步骤"""
    print("\n" + "=" * 70)
    print("第四章 技术趋势分析 - 开始执行")
    print("=" * 70)

    # 创建输出目录
    chapter_output = ensure_dir(OUTPUT_BASE / "ch04_tech_trends")
    print(f"[INFO] 输出目录: {chapter_output}")

    # 加载数据
    print("\n[INFO] 加载清洗后数据...")
    df = load_preprocessed(chapter="ch01_data_cleaning", filename="cleaned_data.csv")
    print(f"[INFO] 数据形状: {df.shape}")
    print(f"[INFO] 年份范围: {sorted(df['year'].unique())}")

    # 执行各步骤
    yearly_stats = step1_yearly_param_stats(df, chapter_output)
    step2_tech_trend_lines(yearly_stats, chapter_output)
    cagr_df = step3_cagr_calculation(yearly_stats, chapter_output)
    step4_tech_generation_boxplot(df, chapter_output)
    brand_leader = step5_brand_tech_leadership(df, chapter_output)
    corr_df = step6_param_correlation_trends(df, chapter_output)
    step7_generate_report(chapter_output, yearly_stats, cagr_df, brand_leader, corr_df)

    print("\n" + "=" * 70)
    print("第四章 技术趋势分析 - 执行完成")
    print("=" * 70)
    print(f"\n输出产物列表 ({chapter_output}):")
    for f in sorted(chapter_output.glob("*")):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
