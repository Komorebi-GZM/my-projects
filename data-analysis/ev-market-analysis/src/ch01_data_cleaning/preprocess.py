# -*- coding: utf-8 -*-
"""preprocess.py - 数据清洗脚本

对电动汽车市场原始数据进行全面清洗，包括：
- Step 1.1: 数据加载与结构探查
- Step 1.2: 缺失值检测与处理
- Step 1.3: 重复值检测与处理
- Step 1.4: 数据类型验证与转换
- Step 1.5: 异常值检测与处理
- Step 1.6: 清洗后数据保存与报告生成

Usage:
    python -m src.ch01_data_cleaning.preprocess
"""

import sys
from pathlib import Path

# 将项目根目录加入 sys.path，确保可以导入 src.utils
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np

from src.utils.config import (
    RAW_DATA_FILE, OUTPUT_BASE, COLUMN_CONFIG,
    ENTITY_CONFIG, DOMAIN_PARAMS, CATEGORY_MAP,
)
from src.utils.data_loader import load_raw_data
from src.utils.output_manager import save_dataframe, save_figure, save_markdown, ensure_dir
from src.utils.visualizer import plot_heatmap
from src.utils.task_graph import TaskGraph


# ============================================================================
# Step 1.1: 数据加载与结构探查
# ============================================================================

def step_1_1_load_and_explore(df: pd.DataFrame) -> dict:
    """Step 1.1: 数据加载与结构探查。

    检查数据形状、列信息、数据类型、基本统计量和前 N 行预览。

    Parameters
    ----------
    df : pd.DataFrame
        原始数据。

    Returns
    -------
    dict
        探查结果摘要。
    """
    print("\n" + "=" * 60)
    print("  Step 1.1: 数据加载与结构探查")
    print("=" * 60)

    # 基本形状
    print(f"\n数据形状: {df.shape[0]} 行 x {df.shape[1]} 列")
    print(f"列名列表: {list(df.columns)}")

    # 数据类型概览
    print(f"\n数据类型分布:")
    print(df.dtypes.value_counts().to_string())

    # 基本统计量
    print(f"\n数值列描述统计:")
    print(df.describe().to_string())

    # 前 5 行预览
    print(f"\n前 5 行预览:")
    print(df.head().to_string())

    # 品牌分布
    brand_counts = df["brand"].value_counts()
    print(f"\n品牌分布 (共 {brand_counts.shape[0]} 个品牌):")
    print(brand_counts.to_string())

    # 年份分布
    year_counts = df["year"].value_counts().sort_index()
    print(f"\n年份分布:")
    print(year_counts.to_string())

    summary = {
        "shape": df.shape,
        "n_brands": df["brand"].nunique(),
        "n_years": df["year"].nunique(),
        "year_range": (int(df["year"].min()), int(df["year"].max())),
        "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
    }
    print(f"\n探查摘要: {summary}")
    return summary


# ============================================================================
# Step 1.2: 缺失值检测与处理
# ============================================================================

def step_1_2_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Step 1.2: 缺失值检测与处理。

    检测各列缺失值数量和比例，根据业务规则制定处理策略。

    Parameters
    ----------
    df : pd.DataFrame
        输入数据。

    Returns
    -------
    pd.DataFrame
        处理缺失值后的数据。
    """
    print("\n" + "=" * 60)
    print("  Step 1.2: 缺失值检测与处理")
    print("=" * 60)

    # 缺失值统计
    null_counts = df.isnull().sum()
    null_pct = (null_counts / len(df) * 100).round(2)
    null_summary = pd.DataFrame({
        "缺失数量": null_counts,
        "缺失比例(%)": null_pct,
    })
    null_summary = null_summary[null_summary["缺失数量"] > 0]

    if null_summary.empty:
        print("\n未检测到缺失值，数据完整。")
    else:
        print(f"\n缺失值统计 (共 {len(null_summary)} 列存在缺失):")
        print(null_summary.to_string())

        # TODO: 根据业务需求制定缺失值处理策略
        # - 数值列: 填充均值/中位数/众数，或删除
        # - 分类列: 填充众数或 "Unknown"
        # - 缺失比例 > 50%: 考虑删除该列
        print("\n[TODO] 请根据业务需求补充缺失值处理逻辑。")

    return df


# ============================================================================
# Step 1.3: 重复值检测与处理
# ============================================================================

def step_1_3_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Step 1.3: 重复值检测与处理。

    检测完全重复记录和基于业务键的部分重复记录。

    Parameters
    ----------
    df : pd.DataFrame
        输入数据。

    Returns
    -------
    pd.DataFrame
        去重后的数据。
    """
    print("\n" + "=" * 60)
    print("  Step 1.3: 重复值检测与处理")
    print("=" * 60)

    # 完全重复检测
    n_full_dup = df.duplicated().sum()
    print(f"\n完全重复记录数: {n_full_dup}")

    # 基于业务键的部分重复（品牌+型号+年份+变体）
    business_key = ["brand", "model", "year", "variant"]
    n_key_dup = df.duplicated(subset=business_key).sum()
    print(f"业务键重复记录数 ({' + '.join(business_key)}): {n_key_dup}")

    if n_full_dup > 0:
        df = df.drop_duplicates()
        print(f"已删除 {n_full_dup} 条完全重复记录。")

    if n_key_dup > 0:
        # TODO: 业务键重复的处理策略（保留最新/均值聚合/人工审核）
        print(f"\n[TODO] 存在 {n_key_dup} 条业务键重复，请确认处理策略。")

    print(f"去重后数据形状: {df.shape}")
    return df


# ============================================================================
# Step 1.4: 数据类型验证与转换
# ============================================================================

def step_1_4_dtype_validation(df: pd.DataFrame) -> pd.DataFrame:
    """Step 1.4: 数据类型验证与转换。

    验证各列数据类型是否符合预期，进行必要的类型转换。

    Parameters
    ----------
    df : pd.DataFrame
        输入数据。

    Returns
    -------
    pd.DataFrame
        类型转换后的数据。
    """
    print("\n" + "=" * 60)
    print("  Step 1.4: 数据类型验证与转换")
    print("=" * 60)

    # 预期类型映射
    expected_types = {
        "brand": "object",
        "model": "object",
        "year": "int64",
        "variant": "object",
        "price_usd": "float64",
        "battery_capacity_kwh": "float64",
        "range_miles": "float64",
        "charging_speed_kw": "float64",
        "acceleration_0_60_mph": "float64",
        "top_speed_mph": "float64",
        "horsepower": "float64",
        "torque_nm": "float64",
        "drive_type": "object",
        "seating_capacity": "int64",
        "body_type": "object",
        "cargo_volume_cubic_ft": "float64",
        "weight_kg": "float64",
        "safety_rating": "int64",
        "autopilot_level": "int64",
        "country_of_origin": "object",
        "market_segment": "object",
        "annual_sales_units": "int64",
        "customer_rating": "float64",
        "warranty_years": "int64",
    }

    print("\n数据类型验证结果:")
    type_issues = []
    for col, expected in expected_types.items():
        if col in df.columns:
            actual = str(df[col].dtype)
            match = "OK" if actual == expected else f"MISMATCH (预期: {expected})"
            if actual != expected:
                type_issues.append((col, actual, expected))
            print(f"  {col:30s} -> {actual:15s} [{match}]")
        else:
            print(f"  {col:30s} -> MISSING")
            type_issues.append((col, "MISSING", expected))

    if type_issues:
        print(f"\n发现 {len(type_issues)} 个类型问题，需要处理。")
        # TODO: 根据实际问题补充类型转换逻辑
    else:
        print("\n所有列数据类型验证通过。")

    # 将分类列转换为 category 类型以节省内存
    categorical_cols = COLUMN_CONFIG["categorical_columns"]
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    print(f"\n分类列已转换为 category 类型: {categorical_cols}")
    print(f"转换后内存占用: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    return df


# ============================================================================
# Step 1.5: 异常值检测与处理
# ============================================================================

def step_1_5_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Step 1.5: 异常值检测与处理。

    使用 IQR 方法检测数值列中的异常值。

    Parameters
    ----------
    df : pd.DataFrame
        输入数据。

    Returns
    -------
    pd.DataFrame
        处理异常值后的数据。
    """
    print("\n" + "=" * 60)
    print("  Step 1.5: 异常值检测与处理")
    print("=" * 60)

    numeric_cols = COLUMN_CONFIG["numeric_columns"]
    outlier_summary = []

    for col in numeric_cols:
        if col not in df.columns:
            continue

        series = df[col].dropna()
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        n_outliers = ((series < lower_bound) | (series > upper_bound)).sum()
        outlier_summary.append({
            "列名": col,
            "Q1": round(q1, 2),
            "Q3": round(q3, 2),
            "IQR": round(iqr, 2),
            "下界": round(lower_bound, 2),
            "上界": round(upper_bound, 2),
            "异常值数量": n_outliers,
            "异常值比例(%)": round(n_outliers / len(series) * 100, 2),
        })

    outlier_df = pd.DataFrame(outlier_summary)
    outlier_df = outlier_df[outlier_df["异常值数量"] > 0].sort_values(
        "异常值比例(%)", ascending=False
    )

    if outlier_df.empty:
        print("\n未检测到异常值。")
    else:
        print(f"\n异常值检测结果 (共 {len(outlier_df)} 列存在异常值):")
        print(outlier_df.to_string(index=False))

        # TODO: 根据业务需求制定异常值处理策略
        # - 保留: 如果异常值有业务意义（如豪华车高价）
        # - 裁剪: 使用上下界截断
        # - 删除: 如果确认是数据录入错误
        print("\n[TODO] 请根据业务需求确认异常值处理策略。")

    return df


# ============================================================================
# Step 1.6: 清洗后数据保存与报告生成
# ============================================================================

def step_1_6_save_and_report(
    df: pd.DataFrame,
    explore_summary: dict,
    output_dir: Path,
) -> Path:
    """Step 1.6: 清洗后数据保存与报告生成。

    保存清洗后的数据集，生成数据清洗报告 Markdown 文件。

    Parameters
    ----------
    df : pd.DataFrame
        清洗后的数据。
    explore_summary : dict
        Step 1.1 的探查摘要。
    output_dir : Path
        输出目录。

    Returns
    -------
    Path
        清洗后数据文件路径。
    """
    print("\n" + "=" * 60)
    print("  Step 1.6: 清洗后数据保存与报告生成")
    print("=" * 60)

    ensure_dir(output_dir)

    # 保存清洗后的数据
    cleaned_path = save_dataframe(df, output_dir / "cleaned_data.csv")
    print(f"清洗后数据已保存: {cleaned_path}")

    # 生成清洗报告
    report = f"""# 数据清洗报告 - {ENTITY_CONFIG["brand_column"]}分析

## 1. 数据概览

| 指标 | 值 |
|------|------|
| 原始数据形状 | {explore_summary['shape'][0]} 行 x {explore_summary['shape'][1]} 列 |
| 清洗后数据形状 | {df.shape[0]} 行 x {df.shape[1]} 列 |
| 品牌数量 | {explore_summary['n_brands']} |
| 年份范围 | {explore_summary['year_range'][0]} - {explore_summary['year_range'][1]} |
| 内存占用 | {explore_summary['memory_usage_mb']:.2f} MB |

## 2. 清洗步骤

### Step 1.1: 数据加载与结构探查
- 数据成功加载，共 {explore_summary['shape'][0]} 行 x {explore_summary['shape'][1]} 列
- 包含 {explore_summary['n_brands']} 个品牌，{explore_summary['n_years']} 个年份

### Step 1.2: 缺失值检测与处理
- 检测结果: 见运行日志

### Step 1.3: 重复值检测与处理
- 检测结果: 见运行日志

### Step 1.4: 数据类型验证与转换
- 分类列已转换为 category 类型

### Step 1.5: 异常值检测与处理
- 检测结果: 见运行日志

## 3. 清洗后数据预览

{df.head(10).to_markdown(index=False)}

## 4. 数据列说明

| 列名 | 类型 | 说明 |
|------|------|------|
| brand | 分类 | 汽车品牌 |
| model | 文本 | 车型名称 |
| year | 整数 | 年份 |
| variant | 文本 | 变体/配置 |
| price_usd | 浮点 | 价格 (USD) |
| battery_capacity_kwh | 浮点 | 电池容量 (kWh) |
| range_miles | 浮点 | 续航里程 (miles) |
| charging_speed_kw | 浮点 | 充电功率 (kW) |
| acceleration_0_60_mph | 浮点 | 0-60mph 加速时间 (s) |
| top_speed_mph | 浮点 | 最高速度 (mph) |
| horsepower | 浮点 | 马力 (hp) |
| torque_nm | 浮点 | 扭矩 (Nm) |
| drive_type | 分类 | 驱动类型 |
| seating_capacity | 整数 | 座位数 |
| body_type | 分类 | 车身类型 |
| cargo_volume_cubic_ft | 浮点 | 货箱容积 (cubic ft) |
| weight_kg | 浮点 | 整备质量 (kg) |
| safety_rating | 整数 | 安全评级 (1-5) |
| autopilot_level | 整数 | 自动驾驶等级 (0-3) |
| country_of_origin | 分类 | 原产国 |
| market_segment | 分类 | 市场细分 |
| annual_sales_units | 整数 | 年销量 |
| customer_rating | 浮点 | 客户评分 (1.0-5.0) |
| warranty_years | 整数 | 保修年限 |
"""

    report_path = save_markdown(report, output_dir / "cleaning_report.md")
    print(f"清洗报告已保存: {report_path}")

    return cleaned_path


# ============================================================================
# 主函数
# ============================================================================

def main():
    """数据清洗主流程。

    按顺序执行 Step 1.1 ~ Step 1.6，完成数据清洗并保存结果。
    """
    print("=" * 60)
    print("  电动汽车市场数据分析 - 数据清洗 (Chapter 01)")
    print("=" * 60)

    # 初始化任务图
    tg = TaskGraph()
    print(f"\n任务依赖图:\n{tg.summary()}")

    # 输出目录
    output_dir = OUTPUT_BASE / "ch01_data_cleaning"
    ensure_dir(output_dir)

    # Step 1.1: 数据加载与结构探查
    tg.tasks["ch01_step1.1"].status = "running"
    df = load_raw_data()
    explore_summary = step_1_1_load_and_explore(df)
    tg.mark_completed("ch01_step1.1")

    # Step 1.2: 缺失值检测与处理
    tg.tasks["ch01_step1.2"].status = "running"
    df = step_1_2_missing_values(df)
    tg.mark_completed("ch01_step1.2")

    # Step 1.3: 重复值检测与处理
    tg.tasks["ch01_step1.3"].status = "running"
    df = step_1_3_duplicates(df)
    tg.mark_completed("ch01_step1.3")

    # Step 1.4: 数据类型验证与转换
    tg.tasks["ch01_step1.4"].status = "running"
    df = step_1_4_dtype_validation(df)
    tg.mark_completed("ch01_step1.4")

    # Step 1.5: 异常值检测与处理
    tg.tasks["ch01_step1.5"].status = "running"
    df = step_1_5_outliers(df)
    tg.mark_completed("ch01_step1.5")

    # Step 1.6: 清洗后数据保存与报告生成
    tg.tasks["ch01_step1.6"].status = "running"
    cleaned_path = step_1_6_save_and_report(df, explore_summary, output_dir)
    tg.mark_completed("ch01_step1.6")

    # 最终摘要
    print("\n" + "=" * 60)
    print("  数据清洗完成!")
    print("=" * 60)
    print(f"\n最终任务状态:\n{tg.summary()}")
    print(f"\n清洗后数据: {cleaned_path}")
    print(f"清洗报告: {output_dir / 'cleaning_report.md'}")


if __name__ == "__main__":
    main()
