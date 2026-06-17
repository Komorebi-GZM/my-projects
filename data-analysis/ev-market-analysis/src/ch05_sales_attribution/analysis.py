# -*- coding: utf-8 -*-
"""ch05_sales_attribution/analysis.py - 第五章 销量归因分析

对比高销量车型与低销量车型在价格、技术参数、品牌、市场定位上的差异特征，
识别爆款车型的核心成功因素和滞销车型的关键问题。

输出产物（共7个）：
1. top10_models.csv — 销量 TOP10 车型表
2. best_seller_profile.csv — 爆款车型特征画像
3. sales_group_comparison.png — 销量分组对比图
4. price_sales_scatter.png — 价格-销量散点图
5. significance_test.csv — 差异显著性检验结果表
6. brand_concentration.csv — 品牌集中度表（CR3/CR5/HHI）
7. ch05_report.md — 章节分析报告
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
from scipy.stats import mannwhitneyu, pearsonr

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


# ========== 对比参数列表 ==========
COMPARE_PARAMS = [
    "price_usd", "battery_capacity_kwh", "range_miles", "charging_speed_kw",
    "horsepower", "acceleration_0_60_mph", "top_speed_mph", "torque_nm",
    "weight_kg", "customer_rating", "safety_rating", "warranty_years",
]

# 爆款画像参数
PROFILE_PARAMS = [
    "price_usd", "battery_capacity_kwh", "range_miles", "charging_speed_kw",
    "horsepower", "acceleration_0_60_mph", "customer_rating", "safety_rating",
    "warranty_years", "weight_kg",
]


def step1_sales_group_definition(df: pd.DataFrame):
    """Step 1: 销量分组定义 — 三分位分组"""
    print("\n" + "=" * 60)
    print("Step 1: 销量分组定义")
    print("=" * 60)

    q33 = df["annual_sales_units"].quantile(0.33)
    q67 = df["annual_sales_units"].quantile(0.67)
    print(f"\n33% 分位数: {q33:,.0f}")
    print(f"67% 分位数: {q67:,.0f}")

    def assign_sales_group(sales):
        if sales >= q67:
            return "high"
        elif sales >= q33:
            return "medium"
        else:
            return "low"

    df["sales_group"] = df["annual_sales_units"].apply(assign_sales_group)

    group_stats = df.groupby("sales_group").agg(
        count=("annual_sales_units", "size"),
        mean_sales=("annual_sales_units", "mean"),
        median_sales=("annual_sales_units", "median"),
    ).reindex(["high", "medium", "low"])

    print(f"\n分组统计:")
    print(group_stats.to_string())

    # 验证
    counts = group_stats["count"]
    assert all(counts > 250), f"某组样本量过少: {counts.to_dict()}"
    assert group_stats.loc["high", "mean_sales"] > group_stats.loc["low", "mean_sales"]

    print("[OK] Step 1 完成")
    return df


def step2_group_feature_comparison(df: pd.DataFrame, chapter_output: Path):
    """Step 2: 分组特征对比"""
    print("\n" + "=" * 60)
    print("Step 2: 分组特征对比")
    print("=" * 60)

    group_order = ["high", "medium", "low"]
    comparison_records = []

    # 过滤存在的参数
    params = [p for p in COMPARE_PARAMS if p in df.columns]

    for param in params:
        stats = df.groupby("sales_group")[param].agg(["mean", "median"]).reindex(group_order)
        high_mean = stats.loc["high", "mean"]
        low_mean = stats.loc["low", "mean"]
        diff_abs = high_mean - low_mean
        diff_pct = (diff_abs / abs(low_mean)) * 100 if low_mean != 0 else float("inf")

        comparison_records.append({
            "parameter": param,
            "high_mean": round(high_mean, 2),
            "high_median": round(stats.loc["high", "median"], 2),
            "medium_mean": round(stats.loc["medium", "mean"], 2),
            "medium_median": round(stats.loc["medium", "median"], 2),
            "low_mean": round(low_mean, 2),
            "low_median": round(stats.loc["low", "median"], 2),
            "diff_abs": round(diff_abs, 2),
            "diff_pct": round(diff_pct, 2),
        })

    comparison_df = pd.DataFrame(comparison_records)
    print(f"\n分组特征对比 ({len(comparison_df)} 个参数):")
    print(comparison_df.to_string(index=False))

    # 可视化
    setup_plt_style()
    plot_params = params[:8]  # 最多8个参数绘图
    n_plots = len(plot_params)
    n_cols = 4
    n_rows = (n_plots + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, n_rows * 4))
    axes = axes.flatten()

    group_labels = {"high": "High Sales", "medium": "Medium Sales", "low": "Low Sales"}
    group_colors = {"high": "#27ae60", "medium": "#f39c12", "low": "#e74c3c"}

    for idx, param in enumerate(plot_params):
        ax = axes[idx]
        for group in group_order:
            vals = df[df["sales_group"] == group][param].dropna()
            ax.bar(idx + group_order.index(group) * 0.25 - 0.25, vals.mean(), 0.25,
                   color=group_colors[group], label=group_labels[group], alpha=0.8)
        ax.set_title(param.replace("_", " ").title(), fontsize=10, fontweight="bold")
        ax.set_xticks([])
        if idx == 0:
            ax.legend(fontsize=8)

    for idx in range(n_plots, len(axes)):
        axes[idx].set_visible(False)

    plt.suptitle("Feature Comparison by Sales Group", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    save_figure(fig, chapter_output / "sales_group_comparison.png", dpi=150)
    plt.close()

    print("[OK] Step 2 完成")
    return comparison_df


def step3_significance_test(df: pd.DataFrame, chapter_output: Path):
    """Step 3: 差异显著性检验（Mann-Whitney U）"""
    print("\n" + "=" * 60)
    print("Step 3: 差异显著性检验")
    print("=" * 60)

    params = [p for p in COMPARE_PARAMS if p in df.columns]
    alpha = 0.05
    n_tests = len(params)
    bonferroni_alpha = alpha / n_tests

    test_records = []
    for param in params:
        high_vals = df[df["sales_group"] == "high"][param].dropna()
        low_vals = df[df["sales_group"] == "low"][param].dropna()

        if len(high_vals) > 1 and len(low_vals) > 1:
            u_stat, p_value = mannwhitneyu(high_vals, low_vals, alternative="two-sided")
            test_records.append({
                "parameter": param,
                "high_n": len(high_vals),
                "low_n": len(low_vals),
                "u_statistic": round(u_stat, 2),
                "p_value": round(p_value, 6),
                "significant_bonferroni": "Yes" if p_value < bonferroni_alpha else "No",
                "significant_raw": "Yes" if p_value < alpha else "No",
            })

    test_df = pd.DataFrame(test_records)
    print(f"\n显著性检验结果 ({len(test_df)} 个参数):")
    print(test_df.to_string(index=False))

    sig_count = (test_df["significant_bonferroni"] == "Yes").sum()
    print(f"\nBonferroni 校正后显著参数: {sig_count}/{len(test_df)}")

    save_dataframe(test_df, chapter_output / "significance_test.csv")

    # 验证
    assert len(test_df) >= 10, f"检验参数数不足: {len(test_df)}"

    print("[OK] Step 3 完成")
    return test_df


def step4_top10_profile(df: pd.DataFrame, chapter_output: Path):
    """Step 4: TOP10 爆款车型画像"""
    print("\n" + "=" * 60)
    print("Step 4: TOP10 爆款车型画像")
    print("=" * 60)

    # 按 brand + model 聚合
    model_sales = df.groupby(["brand", "model"]).agg(
        avg_sales=("annual_sales_units", "mean"),
        avg_price=("price_usd", "mean"),
        record_count=("annual_sales_units", "size"),
    ).reset_index()

    top10 = model_sales.nlargest(10, "avg_sales").reset_index(drop=True)
    top10["rank"] = range(1, 11)
    top10 = top10[["rank", "brand", "model", "avg_sales", "avg_price", "record_count"]]

    print(f"\nTOP 10 爆款车型:")
    print(top10.to_string(index=False))

    # 验证 TOP10 销量占比
    total_sales = df["annual_sales_units"].sum()
    top10_models = top10[["brand", "model"]].merge(df, on=["brand", "model"], how="left")
    top10_total_sales = top10_models["annual_sales_units"].sum()
    top10_share = (top10_total_sales / total_sales) * 100
    print(f"\nTOP 10 车型销量占比: {top10_share:.1f}%")

    # 爆款画像
    profile_params = [p for p in PROFILE_PARAMS if p in df.columns]
    best_seller_profile = {}
    market_avg = {}
    for param in profile_params:
        best_seller_profile[param] = round(top10_models[param].mean(), 2)
        market_avg[param] = round(df[param].mean(), 2)

    profile_df = pd.DataFrame([
        {"metric": "best_seller_avg", **best_seller_profile},
        {"metric": "market_avg", **market_avg},
    ])
    profile_df = profile_df.set_index("metric").T
    profile_df["diff"] = profile_df["best_seller_avg"] - profile_df["market_avg"]
    profile_df["diff_pct"] = ((profile_df["diff"] / profile_df["market_avg"]) * 100).round(2)
    profile_df = profile_df.reset_index().rename(columns={"index": "parameter"})

    print(f"\n爆款画像:")
    print(profile_df.to_string(index=False))

    save_dataframe(top10, chapter_output / "top10_models.csv")
    save_dataframe(profile_df, chapter_output / "best_seller_profile.csv")

    # 验证
    assert len(top10) == 10, f"TOP10 行数异常: {len(top10)}"

    print("[OK] Step 4 完成")
    return top10, profile_df, top10_share


def step5_bottom10_diagnosis(df: pd.DataFrame, profile_df: pd.DataFrame, chapter_output: Path):
    """Step 5: BOTTOM10 滞销诊断"""
    print("\n" + "=" * 60)
    print("Step 5: BOTTOM10 滞销诊断")
    print("=" * 60)

    model_sales = df.groupby(["brand", "model"]).agg(
        avg_sales=("annual_sales_units", "mean"),
        avg_price=("price_usd", "mean"),
        record_count=("annual_sales_units", "size"),
    ).reset_index()

    bottom10 = model_sales.nsmallest(10, "avg_sales").reset_index(drop=True)
    bottom10["rank"] = range(1, 11)

    print(f"\nBOTTOM 10 滞销车型:")
    print(bottom10[["rank", "brand", "model", "avg_sales", "avg_price"]].to_string(index=False))

    # BOTTOM10 画像
    bottom10_models = bottom10[["brand", "model"]].merge(df, on=["brand", "model"], how="left")
    profile_params = [p for p in PROFILE_PARAMS if p in df.columns]

    worst_profile = {}
    for param in profile_params:
        worst_profile[param] = round(bottom10_models[param].mean(), 2)

    # 爆款 vs 滞销对比
    comparison = pd.DataFrame({
        "parameter": profile_params,
        "best_seller_avg": [profile_df.loc[profile_df["parameter"] == p, "best_seller_avg"].values[0]
                            for p in profile_params],
        "worst_seller_avg": [worst_profile[p] for p in profile_params],
    })
    comparison["gap"] = comparison["best_seller_avg"] - comparison["worst_seller_avg"]
    comparison["gap_pct"] = ((comparison["gap"] / comparison["worst_seller_avg"]) * 100).round(2)

    print(f"\n爆款 vs 滞销差距:")
    print(comparison.sort_values("gap_pct", ascending=False).to_string(index=False))

    save_dataframe(comparison, chapter_output / "bottom10_diagnosis.csv")

    print("[OK] Step 5 完成")
    return bottom10


def step6_price_sales_scatter(df: pd.DataFrame, top10: pd.DataFrame, chapter_output: Path):
    """Step 6: 价格-销量关系分析"""
    print("\n" + "=" * 60)
    print("Step 6: 价格-销量关系分析")
    print("=" * 60)

    setup_plt_style()

    # 计算相关系数
    valid = df[["price_usd", "annual_sales_units"]].dropna()
    r, p = pearsonr(valid["price_usd"], valid["annual_sales_units"])
    print(f"\n价格-销量 Pearson 相关系数: r={r:.4f}, p={p:.6f}")

    # 绘制散点图
    fig, ax = plt.subplots(figsize=(12, 8))

    segment_colors = {
        "Budget": "#2ecc71", "Mid-range": "#3498db",
        "Premium": "#e74c3c", "Luxury": "#9b59b6",
    }

    for segment, color in segment_colors.items():
        subset = df[df["market_segment"] == segment]
        ax.scatter(
            subset["price_usd"], subset["annual_sales_units"],
            alpha=0.5, s=30, color=color, label=segment,
            edgecolors="white", linewidths=0.3,
        )

    # 趋势线
    z = np.polyfit(valid["price_usd"], valid["annual_sales_units"], 1)
    p_line = np.poly1d(z)
    x_range = np.linspace(valid["price_usd"].min(), valid["price_usd"].max(), 100)
    ax.plot(x_range, p_line(x_range), "r--", alpha=0.7, linewidth=2,
            label=f"Trend (r={r:.3f})")

    # 标注 TOP 10
    for _, row in top10.iterrows():
        model_data = df[(df["brand"] == row["brand"]) & (df["model"] == row["model"])]
        if len(model_data) > 0:
            ax.annotate(
                f"{row['brand']} {row['model']}",
                (model_data["price_usd"].mean(), model_data["annual_sales_units"].mean()),
                fontsize=7, alpha=0.8,
                textcoords="offset points", xytext=(5, 5),
            )

    ax.set_xlabel("Price (USD)", fontsize=12)
    ax.set_ylabel("Annual Sales (units)", fontsize=12)
    ax.set_title("Price vs Sales Scatter Plot (by Market Segment)", fontsize=14, fontweight="bold")
    ax.legend(fontsize=10, title="Market Segment")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x/1000:.0f}K"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"{x/1000:.0f}K"))
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    save_figure(fig, chapter_output / "price_sales_scatter.png", dpi=150)
    plt.close()

    # 验证
    assert len(valid) == len(df), "散点图应包含全部数据点"

    print("[OK] Step 6 完成")
    return r


def step7_brand_concentration(df: pd.DataFrame, chapter_output: Path):
    """Step 7: 品牌集中度分析"""
    print("\n" + "=" * 60)
    print("Step 7: 品牌集中度分析")
    print("=" * 60)

    # 整体品牌集中度
    brand_sales = df.groupby("brand")["annual_sales_units"].sum().sort_values(ascending=False)
    brand_share = brand_sales / brand_sales.sum()

    cr3 = brand_share.head(3).sum()
    cr5 = brand_share.head(5).sum()
    hhi = (brand_share ** 2).sum()

    print(f"\n整体市场集中度:")
    print(f"  CR3: {cr3:.4f} ({cr3*100:.1f}%)")
    print(f"  CR5: {cr5:.4f} ({cr5*100:.1f}%)")
    print(f"  HHI: {hhi:.4f}")

    # 年度品牌集中度
    years = sorted(df["year"].unique())
    yearly_concentration = []

    for year in years:
        df_year = df[df["year"] == year]
        brand_sales_year = df_year.groupby("brand")["annual_sales_units"].sum().sort_values(ascending=False)
        share = brand_sales_year / brand_sales_year.sum()

        cr3_y = share.head(3).sum()
        cr5_y = share.head(5).sum()
        hhi_y = (share ** 2).sum()

        yearly_concentration.append({
            "year": year,
            "cr3": round(cr3_y, 4),
            "cr5": round(cr5_y, 4),
            "hhi": round(hhi_y, 4),
            "top_brand": brand_sales_year.index[0],
            "top_brand_share": round(share.iloc[0], 4),
        })

    conc_df = pd.DataFrame(yearly_concentration)
    print(f"\n年度品牌集中度:")
    print(conc_df.to_string(index=False))

    save_dataframe(conc_df, chapter_output / "brand_concentration.csv")

    # 品牌销量排名表
    brand_ranking = pd.DataFrame({
        "brand": brand_share.index,
        "total_sales": brand_sales.values,
        "market_share": (brand_share * 100).round(2).values,
        "cumulative_share": (brand_share.cumsum() * 100).round(2).values,
    })
    save_dataframe(brand_ranking, chapter_output / "brand_sales_ranking.csv")

    print("[OK] Step 7 完成")
    return conc_df, cr3, cr5, hhi


def step8_generate_report(
    chapter_output: Path,
    comparison_df: pd.DataFrame,
    test_df: pd.DataFrame,
    top10: pd.DataFrame,
    conc_df: pd.DataFrame,
    price_corr: float,
    cr3: float, cr5: float, hhi: float,
    top10_share: float,
):
    """Step 8: 章节报告生成"""
    print("\n" + "=" * 60)
    print("Step 8: 章节报告生成")
    print("=" * 60)

    sig_count = (test_df["significant_bonferroni"] == "Yes").sum()

    lines = []
    lines.append("# 第五章：销量归因分析\n")
    lines.append("> **章节编号**: ch05 | **分析类型**: 分析探索型（原型B） | **优先级**: P0\n")
    lines.append("---\n")

    lines.append("## 5.1 研究背景与目标\n")
    lines.append(
        "本章旨在对比高销量车型与低销量车型在价格、技术参数、品牌、市场定位上的差异特征，"
        "识别爆款车型的核心成功因素。通过三分位分组、统计检验和多维度可视化，"
        "揭示影响 EV 销量的关键驱动因素。\n"
    )

    lines.append("## 5.2 分析方法\n")
    lines.append("- **三分位分组**：按销量 33%/67% 分位数分为高/中/低三组（每组约 350 条）")
    lines.append("- **描述性统计对比**：12+ 个参数的组间均值/中位数对比")
    lines.append("- **Mann-Whitney U 检验**：非参数检验，Bonferroni 校正")
    lines.append("- **散点图与趋势线**：价格-销量关系分析")
    lines.append("- **集中度指标**：CR3、CR5、HHI 指数\n")

    lines.append("## 5.3 核心发现\n")

    lines.append("### 5.3.1 分组特征对比\n")
    lines.append("![销量分组对比图](sales_group_comparison.png)\n")
    lines.append("| 参数 | 高销量组均值 | 低销量组均值 | 差异 | 差异% |")
    lines.append("|------|------------|------------|------|-------|")
    for _, row in comparison_df.iterrows():
        lines.append(
            f"| {row['parameter']} | {row['high_mean']} | {row['low_mean']} | "
            f"{row['diff_abs']:+.2f} | {row['diff_pct']:+.2f}% |"
        )
    lines.append("")

    lines.append("### 5.3.2 差异显著性检验\n")
    lines.append("| 参数 | U 统计量 | p-value | Bonferroni 显著 |")
    lines.append("|------|---------|---------|---------------|")
    for _, row in test_df.iterrows():
        lines.append(
            f"| {row['parameter']} | {row['u_statistic']} | {row['p_value']} | {row['significant_bonferroni']} |"
        )
    lines.append(f"\n通过 Bonferroni 校正的显著参数数量: **{sig_count}/{len(test_df)}**\n")

    lines.append("### 5.3.3 TOP 10 爆款画像\n")
    lines.append("| 排名 | 品牌 | 车型 | 平均销量 | 平均价格 |")
    lines.append("|------|------|------|---------|---------|")
    for _, row in top10.iterrows():
        lines.append(
            f"| {int(row['rank'])} | {row['brand']} | {row['model']} | "
            f"{row['avg_sales']:,.0f} | ${row['avg_price']:,.0f} |"
        )
    lines.append(f"\nTOP 10 车型销量占总销量: **{top10_share:.1f}%**\n")

    lines.append("### 5.3.4 价格-销量关系\n")
    lines.append("![价格-销量散点图](price_sales_scatter.png)\n")
    lines.append(f"价格与销量的 Pearson 相关系数: **r = {price_corr:.4f}**\n")

    lines.append("### 5.3.5 品牌集中度分析\n")
    lines.append("| 年份 | CR3 | CR5 | HHI | TOP 品牌 |")
    lines.append("|------|-----|-----|-----|---------|")
    for _, row in conc_df.iterrows():
        lines.append(
            f"| {int(row['year'])} | {row['cr3']:.4f} | {row['cr5']:.4f} | "
            f"{row['hhi']:.4f} | {row['top_brand']} |"
        )
    lines.append(f"\n整体 CR3={cr3:.1f}%, CR5={cr5:.1f}%, HHI={hhi:.4f}\n")

    lines.append("## 5.4 关键洞察与小结\n")
    lines.append(f"1. **高/低销量差异显著**：{sig_count}/{len(test_df)} 个参数通过 Bonferroni 校正的显著性检验")
    lines.append(f"2. **品牌集中度高**：CR3={cr3:.1f}%，TOP 3 品牌占据市场主导地位")
    lines.append(f"3. **价格-销量关系**：相关系数 r={price_corr:.4f}，呈现{'负' if price_corr < 0 else '正'}相关趋势")
    lines.append("4. **爆款特征**：高销量车型通常具备特定的价格-性能组合优势\n")

    lines.append("---\n")
    lines.append(f"*报告生成时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append("*数据来源：cleaned_data.csv（1070行 x 27列）*\n")

    report_content = "\n".join(lines)
    save_markdown(report_content, chapter_output / "ch05_report.md")
    print("[OK] 章节报告已保存: ch05_report.md")


def main():
    """主函数：执行全部8个分析步骤"""
    print("\n" + "=" * 70)
    print("第五章 销量归因分析 - 开始执行")
    print("=" * 70)

    # 创建输出目录
    chapter_output = ensure_dir(OUTPUT_BASE / "ch05_sales_attribution")
    print(f"[INFO] 输出目录: {chapter_output}")

    # 加载数据
    print("\n[INFO] 加载清洗后数据...")
    df = load_preprocessed(chapter="ch01_data_cleaning", filename="cleaned_data.csv")
    print(f"[INFO] 数据形状: {df.shape}")

    # 执行各步骤
    df = step1_sales_group_definition(df)
    comparison_df = step2_group_feature_comparison(df, chapter_output)
    test_df = step3_significance_test(df, chapter_output)
    top10, profile_df, top10_share = step4_top10_profile(df, chapter_output)
    step5_bottom10_diagnosis(df, profile_df, chapter_output)
    price_corr = step6_price_sales_scatter(df, top10, chapter_output)
    conc_df, cr3, cr5, hhi = step7_brand_concentration(df, chapter_output)
    step8_generate_report(
        chapter_output, comparison_df, test_df, top10, conc_df,
        price_corr, cr3, cr5, hhi, top10_share,
    )

    print("\n" + "=" * 70)
    print("第五章 销量归因分析 - 执行完成")
    print("=" * 70)
    print(f"\n输出产物列表 ({chapter_output}):")
    for f in sorted(chapter_output.glob("*")):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
