"""
章节：ch02 核心指标计算与可视化
描述：计算分组点击率、绝对提升、相对提升，并绘制带95%置信区间的可视化图表
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from src.utils.config import Config
from src.utils.data_loader import DataLoader
from src.utils.visualizer import Visualizer
from src.utils.output_manager import OutputManager


def step01_calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    步骤1：计算分组核心指标
    """
    print("=" * 60)
    print("步骤1：计算分组核心指标")
    print("=" * 60)

    # 按组统计
    group_stats = df.groupby("group")["click"].agg(["count", "sum", "mean"])
    group_stats.columns = ["总用户数", "点击数", "点击率"]

    # 计算绝对提升和相对提升
    ctr_con = group_stats.loc["con", "点击率"]
    ctr_exp = group_stats.loc["exp", "点击率"]

    absolute_lift = ctr_exp - ctr_con
    relative_lift = (ctr_exp - ctr_con) / ctr_con * 100

    print(f"\n分组点击率:")
    print(f"  对照组 (con): {ctr_con:.4f} ({ctr_con*100:.2f}%)")
    print(f"  实验组 (exp): {ctr_exp:.4f} ({ctr_exp*100:.2f}%)")

    print(f"\n提升分析:")
    print(f"  绝对提升: {absolute_lift:.4f} ({absolute_lift*100:.2f} pp)")
    print(f"  相对提升: {relative_lift:.2f}%")

    return group_stats, absolute_lift, relative_lift


def step02_calculate_ci(df: pd.DataFrame) -> pd.DataFrame:
    """
    步骤2：计算95%置信区间
    """
    print("\n" + "=" * 60)
    print("步骤2：计算95%置信区间")
    print("=" * 60)

    results = []
    for group in ["con", "exp"]:
        group_data = df[df["group"] == group]["click"]
        n = len(group_data)
        p = group_data.mean()

        # 比例的标准误
        se = np.sqrt(p * (1 - p) / n)

        # 95% CI
        z = 1.96
        ci_lower = p - z * se
        ci_upper = p + z * se

        results.append({
            "group": group,
            "n": n,
            "clicks": group_data.sum(),
            "ctr": p,
            "ctr_pct": f"{p*100:.2f}%",
            "se": se,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "ci_95": f"[{ci_lower*100:.2f}%, {ci_upper*100:.2f}%]"
        })

    ci_df = pd.DataFrame(results)
    print(f"\n带95%置信区间的分组统计:")
    print(ci_df[["group", "n", "clicks", "ctr_pct", "ci_95"]].to_string(index=False))

    return ci_df


def step03_visualize(ci_df: pd.DataFrame, visualizer: Visualizer, output: OutputManager) -> None:
    """
    步骤3：绘制带置信区间的可视化图表
    """
    print("\n" + "=" * 60)
    print("步骤3：绘制可视化图表")
    print("=" * 60)

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=visualizer.style["figure_size"])

    groups = ci_df["group"].values
    ctrs = ci_df["ctr"].values
    errors = [
        ctrs - ci_df["ci_lower"].values,
        ci_df["ci_upper"].values - ctrs
    ]

    colors = ["#DD8452", "#4C72B0"]  # con: 橙色, exp: 蓝色
    bars = ax.bar(groups, ctrs, yerr=errors, capsize=10, color=colors, edgecolor="black", linewidth=1.2)

    # 添加数值标签
    for bar, ctr in zip(bars, ctrs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f"{ctr*100:.2f}%",
                ha="center", va="bottom", fontsize=12, fontweight="bold")

    ax.set_ylabel("点击率 (CTR)", fontsize=12)
    ax.set_xlabel("分组", fontsize=12)
    ax.set_title("A/B测试点击率对比（含95%置信区间）", fontsize=14, fontweight="bold")
    ax.set_ylim(0, max(ci_df["ci_upper"]) * 1.2)

    # 添加图例说明
    ax.text(0.5, 0.95, "con = 对照组（旧版本）\nexp = 实验组（新版本）",
            transform=ax.transAxes, fontsize=10, verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()

    # 保存图表
    save_path = visualizer.save_figure(fig, "ctr_comparison_with_ci", chapter_prefix="ch02")
    print(f"\n✓ 图表已保存: {save_path}")


def main():
    """主函数"""
    print("╔" + "═" * 58 + "╗")
    print("║" + "  ch02 核心指标计算与可视化".center(46) + "║")
    print("╚" + "═" * 58 + "╝")

    # 初始化工具
    config = Config()
    loader = DataLoader(config)
    visualizer = Visualizer(config)
    output = OutputManager(config)

    # 加载清洗后数据
    df = loader.load_processed("cleaned_data.csv")

    # 执行分析步骤
    group_stats, abs_lift, rel_lift = step01_calculate_metrics(df)
    ci_df = step02_calculate_ci(df)
    step03_visualize(ci_df, visualizer, output)

    # 保存结果表
    output.save_table(group_stats.reset_index(), "group_metrics", chapter_prefix="ch02")
    output.save_table(ci_df, "group_metrics_with_ci", chapter_prefix="ch02")

    print("\n" + "=" * 60)
    print("✓ ch02 完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
