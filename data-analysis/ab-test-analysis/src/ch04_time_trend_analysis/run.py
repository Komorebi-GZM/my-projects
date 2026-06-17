"""
章节：ch04 时间趋势分析
描述：按天/按小时分析点击率趋势，检测新奇效应
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


def step01_daily_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    步骤1：按天分析点击率趋势
    """
    print("=" * 60)
    print("步骤1：按天点击率趋势")
    print("=" * 60)

    # 确保 timestamp 是 datetime 类型
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # 提取日期
    df["date"] = df["timestamp"].dt.date

    # 按天和分组统计
    daily_stats = df.groupby(["date", "group"]).agg({
        "click": ["count", "sum", "mean"]
    }).reset_index()
    daily_stats.columns = ["date", "group", "users", "clicks", "ctr"]

    # 透视表
    daily_pivot = daily_stats.pivot(index="date", columns="group", values=["users", "clicks", "ctr"])
    daily_pivot.columns = [f"{col[1]}_{col[0]}" for col in daily_pivot.columns]

    print(f"\n按天点击率统计:")
    print(daily_pivot.to_string())

    return daily_stats, daily_pivot


def step02_hourly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    步骤2：按小时分析点击率趋势
    """
    print("\n" + "=" * 60)
    print("步骤2：按小时点击率趋势")
    print("=" * 60)

    # 提取小时
    df["hour"] = df["timestamp"].dt.hour

    # 按小时和分组统计
    hourly_stats = df.groupby(["hour", "group"]).agg({
        "click": ["count", "sum", "mean"]
    }).reset_index()
    hourly_stats.columns = ["hour", "group", "users", "clicks", "ctr"]

    print(f"\n按小时点击率统计（前10行）:")
    print(hourly_stats.head(10).to_string(index=False))

    return hourly_stats


def step03_visualize_trends(daily_stats: pd.DataFrame, hourly_stats: pd.DataFrame,
                            visualizer: Visualizer, output: OutputManager) -> None:
    """
    步骤3：绘制时间趋势图
    """
    print("\n" + "=" * 60)
    print("步骤3：绘制时间趋势图")
    print("=" * 60)

    import matplotlib.pyplot as plt

    # 图1：按天趋势
    fig, ax = plt.subplots(figsize=visualizer.style["figure_size"])

    for group, color in zip(["con", "exp"], ["#DD8452", "#4C72B0"]):
        data = daily_stats[daily_stats["group"] == group]
        ax.plot(data["date"], data["ctr"], marker="o", label=f"{group.upper()}",
                color=color, linewidth=2, markersize=8)

    ax.set_xlabel("日期", fontsize=12)
    ax.set_ylabel("点击率 (CTR)", fontsize=12)
    ax.set_title("A/B测试点击率按天趋势", fontsize=14, fontweight="bold")
    ax.legend(title="分组")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    save_path1 = visualizer.save_figure(fig, "daily_ctr_trend", chapter_prefix="ch04")
    print(f"\n✓ 按天趋势图已保存: {save_path1}")

    # 图2：按小时趋势
    fig, ax = plt.subplots(figsize=visualizer.style["figure_size"])

    for group, color in zip(["con", "exp"], ["#DD8452", "#4C72B0"]):
        data = hourly_stats[hourly_stats["group"] == group]
        ax.plot(data["hour"], data["ctr"], marker="o", label=f"{group.upper()}",
                color=color, linewidth=2, markersize=6)

    ax.set_xlabel("小时", fontsize=12)
    ax.set_ylabel("点击率 (CTR)", fontsize=12)
    ax.set_title("A/B测试点击率按小时趋势", fontsize=14, fontweight="bold")
    ax.legend(title="分组")
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(0, 24, 2))
    plt.tight_layout()

    save_path2 = visualizer.save_figure(fig, "hourly_ctr_trend", chapter_prefix="ch04")
    print(f"✓ 按小时趋势图已保存: {save_path2}")


def step04_novelty_effect_check(daily_pivot: pd.DataFrame) -> None:
    """
    步骤4：新奇效应检测
    """
    print("\n" + "=" * 60)
    print("步骤4：新奇效应检测")
    print("=" * 60)

    if "exp_ctr" not in daily_pivot.columns or len(daily_pivot) < 2:
        print("数据不足，无法检测新奇效应")
        return

    exp_ctrs = daily_pivot["exp_ctr"].values

    # 简单检测：前两天 vs 后几天的差异
    first_half = np.mean(exp_ctrs[:len(exp_ctrs)//2])
    second_half = np.mean(exp_ctrs[len(exp_ctrs)//2:])

    diff = first_half - second_half
    diff_pct = diff / first_half * 100 if first_half > 0 else 0

    print(f"\n实验组点击率:")
    print(f"  前半期平均: {first_half:.4f} ({first_half*100:.2f}%)")
    print(f"  后半期平均: {second_half:.4f} ({second_half*100:.2f}%)")
    print(f"  差异: {diff:.4f} ({diff_pct:.1f}%)")

    if diff_pct > 10:
        print(f"\n⚠ 可能存在新奇效应（Novelty Effect）")
        print(f"   实验初期点击率较高，随后下降")
        print(f"   建议：考虑延长实验时间或分段分析")
    elif diff_pct < -10:
        print(f"\n○ 相反趋势：实验初期点击率较低，随后上升")
        print(f"   可能存在学习效应")
    else:
        print(f"\n✓ 无明显新奇效应，点击率趋势稳定")


def main():
    """主函数"""
    print("╔" + "═" * 58 + "╗")
    print("║" + "  ch04 时间趋势分析".center(46) + "║")
    print("╚" + "═" * 58 + "╝")

    # 初始化工具
    config = Config()
    loader = DataLoader(config)
    visualizer = Visualizer(config)
    output = OutputManager(config)

    # 加载清洗后数据
    df = loader.load_processed("cleaned_data.csv")

    # 执行分析步骤
    daily_stats, daily_pivot = step01_daily_trend(df)
    hourly_stats = step02_hourly_trend(df)
    step03_visualize_trends(daily_stats, hourly_stats, visualizer, output)
    step04_novelty_effect_check(daily_pivot)

    # 保存结果
    output.save_table(daily_pivot.reset_index(), "daily_ctr_trend", chapter_prefix="ch04")
    output.save_table(hourly_stats, "hourly_ctr_trend", chapter_prefix="ch04")

    print("\n" + "=" * 60)
    print("✓ ch04 完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
