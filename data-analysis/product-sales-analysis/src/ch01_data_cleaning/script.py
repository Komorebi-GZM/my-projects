"""
ch01 数据清洗脚本 - 产品销售数据分析项目

本脚本执行数据清洗流程，包括：
1. 加载原始 CSV 数据
2. 检查缺失值和重复值
3. 数据类型转换
4. 保存清洗后的数据
5. 生成数据清洗报告（report.md）

执行方式:
    cd Product_Sales_Analysis
    python -m src.ch01_data_cleaning.script
"""

import sys
from pathlib import Path

# 将项目根目录添加到 sys.path，确保可以导入 src.utils
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils import (
    load_raw_data,
    save_dataframe,
    save_markdown,
    OUTPUT_BASE,
    CATEGORY_LIST,
    CITY_LIST,
)


def main():
    """执行数据清洗主流程。"""
    print("=" * 60)
    print("ch01 数据清洗 - 开始执行")
    print("=" * 60)

    # ============================================================
    # 步骤 1: 加载原始数据
    # ============================================================
    print("\n--- 步骤 1: 加载原始数据 ---")
    df = load_raw_data()
    print(f"原始数据列名: {df.columns.tolist()}")
    print(f"原始数据形状: {df.shape}")

    # ============================================================
    # 步骤 2: 检查缺失值
    # ============================================================
    print("\n--- 步骤 2: 检查缺失值 ---")
    missing_summary = df.isnull().sum()
    missing_total = missing_summary.sum()
    print(f"缺失值总数: {missing_total}")
    if missing_total > 0:
        print("各列缺失值统计:")
        print(missing_summary[missing_summary > 0])
        # 填充或删除缺失值（根据实际情况选择策略）
        df = df.dropna()
        print(f"删除缺失值后数据形状: {df.shape}")
    else:
        print("数据中无缺失值。")

    # ============================================================
    # 步骤 3: 检查重复值
    # ============================================================
    print("\n--- 步骤 3: 检查重复值 ---")
    duplicate_count = df.duplicated().sum()
    print(f"重复行数: {duplicate_count}")
    if duplicate_count > 0:
        df = df.drop_duplicates()
        print(f"删除重复值后数据形状: {df.shape}")
    else:
        print("数据中无重复行。")

    # ============================================================
    # 步骤 4: 数据类型转换
    # ============================================================
    print("\n--- 步骤 4: 数据类型转换 ---")
    print("转换前数据类型:")
    print(df.dtypes)

    # 转换日期列
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        print("已将 'date' 列转换为 datetime 类型。")

    # 转换数值列
    numeric_cols = ["price", "quantity", "total_price"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            print(f"已将 '{col}' 列转换为数值类型。")

    # 转换类别列为 category 类型
    if "category" in df.columns:
        valid_categories = set(CATEGORY_LIST)
        df["category"] = df["category"].astype(str).str.strip()
        # 过滤无效类别
        df = df[df["category"].isin(valid_categories)]
        df["category"] = df["category"].astype("category")
        print(f"已将 'category' 列转换为 category 类型（有效类别: {CATEGORY_LIST}）。")

    if "city" in df.columns:
        valid_cities = set(CITY_LIST)
        df["city"] = df["city"].astype(str).str.strip()
        df = df[df["city"].isin(valid_cities)]
        df["city"] = df["city"].astype("category")
        print(f"已将 'city' 列转换为 category 类型（有效城市: {CITY_LIST}）。")

    print("\n转换后数据类型:")
    print(df.dtypes)

    # ============================================================
    # 步骤 5: 保存清洗后的数据
    # ============================================================
    print("\n--- 步骤 5: 保存清洗后的数据 ---")
    output_dir = OUTPUT_BASE / "data_cleaning"
    output_dir.mkdir(parents=True, exist_ok=True)
    cleaned_path = save_dataframe(df, output_dir / "product_preprocessed.csv")
    print(f"清洗后数据已保存至: {cleaned_path}")

    # ============================================================
    # 步骤 6: 生成数据清洗报告
    # ============================================================
    print("\n--- 步骤 6: 生成数据清洗报告 ---")
    report_content = f"""# 数据清洗报告

## 背景

本报告记录了产品销售数据集（product_sales_dataset.csv）的数据清洗过程。
数据清洗是数据分析流程的第一步，旨在确保后续分析基于高质量、一致的数据。

## 分析方法

数据清洗流程包括以下步骤：

1. **加载原始数据**：从 CSV 文件加载产品销售数据集。
2. **缺失值检查**：统计各列缺失值数量，对含有缺失值的行进行删除处理。
3. **重复值检查**：检测并删除重复记录。
4. **数据类型转换**：
   - 日期列转换为 datetime 类型
   - 数值列（price, quantity, total_price）转换为数值类型
   - 类别列（category, city）转换为 category 类型，并过滤无效值
5. **数据验证**：确保类别和城市字段仅包含预定义的有效值。

## 分析发现

### 原始数据概况
- 原始数据形状：加载后进行清洗
- 缺失值总数：{missing_total}
- 重复行数：{duplicate_count}

### 清洗后数据概况
- 清洗后数据形状：{df.shape[0]} 行 x {df.shape[1]} 列
- 数据列：{df.columns.tolist()}
- 有效产品类别：{CATEGORY_LIST}
- 有效城市：{CITY_LIST}

### 数据类型
清洗后各列数据类型已统一，确保数值列可用于计算，日期列可用于时序分析。

## 小结

数据清洗流程已完成。原始数据经过缺失值处理、重复值删除、数据类型转换和
有效性验证后，输出为清洗后的数据文件（product_preprocessed.csv），
可供后续探索性分析和销售模式挖掘使用。
"""
    report_path = save_markdown(report_content, output_dir / "report.md")
    print(f"数据清洗报告已保存至: {report_path}")

    print("\n" + "=" * 60)
    print("ch01 数据清洗 - 执行完成")
    print("=" * 60)


if __name__ == "__main__":
    import pandas as pd
    main()
