"""
章节：ch01 数据清洗
描述：对A/B测试点击数据进行清洗和质量检查
"""

import pandas as pd
import sys
import os

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from src.utils.config import Config
from src.utils.data_loader import DataLoader
from src.utils.metrics import Metrics
from src.utils.output_manager import OutputManager
from src.utils.visualizer import Visualizer


def step01_load_data(config: Config, loader: DataLoader) -> pd.DataFrame:
    """
    步骤1：加载原始数据
    """
    print("=" * 60)
    print("步骤1：加载原始数据")
    print("=" * 60)

    df = loader.load_raw()

    # 打印基本信息
    info = loader.get_data_info(df)
    print(f"\n数据形状: {info['shape']}")
    print(f"列名: {info['columns']}")
    print(f"内存占用: {info['memory_usage_mb']:.2f} MB")
    print(f"\n数据类型:")
    for col, dtype in info["dtypes"].items():
        print(f"  {col}: {dtype}")

    print(f"\n前5行预览:")
    print(df.head())

    return df


def step02_check_missing(df: pd.DataFrame, metrics: Metrics, output: OutputManager) -> pd.DataFrame:
    """
    步骤2：缺失值检查
    """
    print("\n" + "=" * 60)
    print("步骤2：缺失值检查")
    print("=" * 60)

    null_summary = metrics.null_summary(df)
    print(f"\n缺失值汇总:")
    print(null_summary.to_string(index=False))

    # 保存缺失值报告
    output.save_table(null_summary, "missing_values_summary", chapter_prefix="ch01")

    total_null = df.isnull().sum().sum()
    print(f"\n总缺失值数量: {total_null}")

    if total_null > 0:
        print("⚠ 发现缺失值，需要进行处理")
    else:
        print("✓ 无缺失值")

    return df


def step03_check_duplicates(df: pd.DataFrame, metrics: Metrics, output: OutputManager) -> pd.DataFrame:
    """
    步骤3：重复值检查
    """
    print("\n" + "=" * 60)
    print("步骤3：重复值检查")
    print("=" * 60)

    dup_info = metrics.duplicate_summary(df)
    print(f"\n重复值汇总:")
    for k, v in dup_info.items():
        print(f"  {k}: {v}")

    output.save_json(dup_info, "duplicate_summary", chapter_prefix="ch01")

    if dup_info["重复行数"] > 0:
        print(f"\n⚠ 发现 {dup_info['重复行数']} 行重复数据")
        # 删除重复行
        before_count = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        after_count = len(df)
        print(f"已删除重复行: {before_count - after_count} 行")
        print(f"删除后剩余: {after_count} 行")
    else:
        print("✓ 无重复数据")

    return df


def step04_check_types(df: pd.DataFrame, output: OutputManager) -> pd.DataFrame:
    """
    步骤4：数据类型验证与转换
    """
    print("\n" + "=" * 60)
    print("步骤4：数据类型验证与转换")
    print("=" * 60)

    print(f"\n原始数据类型:")
    print(df.dtypes)

    # 转换 timestamp 为 datetime
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        print(f"\n✓ timestamp 已转换为 datetime 类型")

    # 验证 click 是否为 0/1
    if "click" in df.columns:
        unique_clicks = sorted(df["click"].unique())
        print(f"\nclick 唯一值: {unique_clicks}")
        if set(unique_clicks).issubset({0, 1}):
            print("✓ click 字段值合法（0/1）")
        else:
            print(f"⚠ click 字段存在异常值: {set(unique_clicks) - {0, 1}}")

    # 验证 group 是否为 exp/con
    if "group" in df.columns:
        unique_groups = sorted(df["group"].unique())
        print(f"\ngroup 唯一值: {unique_groups}")
        if set(unique_groups).issubset({"exp", "con"}):
            print("✓ group 字段值合法（exp/con）")
        else:
            print(f"⚠ group 字段存在异常值: {set(unique_groups) - {'exp', 'con'}}")

    # 验证 user_id 唯一性
    if "user_id" in df.columns:
        unique_users = df["user_id"].nunique()
        total_rows = len(df)
        print(f"\nuser_id 唯一值数量: {unique_users}")
        print(f"总行数: {total_rows}")
        if unique_users == total_rows:
            print("✓ user_id 无重复，每个用户一条记录")
        else:
            print(f"⚠ user_id 存在重复，{total_rows - unique_users} 条多余记录")

    print(f"\n转换后数据类型:")
    print(df.dtypes)

    return df


def step05_descriptive_stats(df: pd.DataFrame, metrics: Metrics, output: OutputManager) -> pd.DataFrame:
    """
    步骤5：描述性统计
    """
    print("\n" + "=" * 60)
    print("步骤5：描述性统计")
    print("=" * 60)

    desc = metrics.describe_all(df)
    print(f"\n描述性统计:")
    print(desc.to_string())

    output.save_table(desc.reset_index(), "descriptive_stats", chapter_prefix="ch01")

    # 按组统计点击率
    if "group" in df.columns and "click" in df.columns:
        print(f"\n按组统计:")
        group_stats = df.groupby("group")["click"].agg(["count", "sum", "mean"])
        group_stats.columns = ["总用户数", "点击数", "点击率"]
        group_stats["点击率"] = (group_stats["点击率"] * 100).round(2)
        group_stats["点击率(%)"] = group_stats["点击率"].astype(str) + "%"
        print(group_stats.to_string())
        output.save_table(group_stats.reset_index(), "group_click_stats", chapter_prefix="ch01")

    return df


def step06_save_cleaned(df: pd.DataFrame, output: OutputManager) -> None:
    """
    步骤6：保存清洗后数据
    """
    print("\n" + "=" * 60)
    print("步骤6：保存清洗后数据")
    print("=" * 60)

    save_path = output.save_data(df, "cleaned_data.csv", index=False)
    print(f"\n✓ 清洗后数据已保存: {save_path}")
    print(f"最终数据形状: {df.shape}")


def main():
    """主函数：执行完整数据清洗流程"""
    print("╔" + "═" * 58 + "╗")
    print("║" + "  AB_Test_Analysis - ch01 数据清洗".center(52) + "║")
    print("╚" + "═" * 58 + "╝")

    # 初始化工具
    config = Config()
    loader = DataLoader(config)
    visualizer = Visualizer(config)
    metrics = Metrics()
    output = OutputManager(config)

    # 执行清洗流程
    df = step01_load_data(config, loader)
    df = step02_check_missing(df, metrics, output)
    df = step03_check_duplicates(df, metrics, output)
    df = step04_check_types(df, output)
    df = step05_descriptive_stats(df, metrics, output)
    step06_save_cleaned(df, output)

    print("\n" + "=" * 60)
    print("✓ 数据清洗流程全部完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
