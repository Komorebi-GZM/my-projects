"""
评估指标计算器模块 - 产品销售数据分析项目

本模块提供常用的数据统计和指标计算函数，包括销售额汇总、
价格统计、类别/城市维度的汇总分析，以及多模型对比功能。
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def calc_total_sales(df: pd.DataFrame, sales_col: str = "total_price") -> float:
    """
    计算总销售额。

    对指定列求和，返回总销售额。

    Args:
        df: 包含销售数据的 DataFrame。
        sales_col: 销售额列名，默认为 "total_price"。

    Returns:
        float: 总销售额。
    """
    total = df[sales_col].sum()
    print(f"[指标] 总销售额: {total:,.2f}")
    return total


def calc_avg_price(df: pd.DataFrame, price_col: str = "price") -> float:
    """
    计算平均价格。

    对指定列求均值，返回平均价格。

    Args:
        df: 包含价格数据的 DataFrame。
        price_col: 价格列名，默认为 "price"。

    Returns:
        float: 平均价格。
    """
    avg = df[price_col].mean()
    print(f"[指标] 平均价格: {avg:,.2f}")
    return avg


def calc_category_summary(
    df: pd.DataFrame,
    category_col: str = "category",
    sales_col: str = "total_price",
    quantity_col: str = "quantity",
) -> pd.DataFrame:
    """
    按产品类别汇总统计。

    对 DataFrame 按类别分组，计算销售额总和、平均销售额、
    总销量和订单数量。

    Args:
        df: 包含销售数据的 DataFrame。
        category_col: 类别列名，默认为 "category"。
        sales_col: 销售额列名，默认为 "total_price"。
        quantity_col: 销量列名，默认为 "quantity"。

    Returns:
        pd.DataFrame: 按类别汇总的统计结果 DataFrame。
    """
    summary = df.groupby(category_col).agg(
        total_sales=(sales_col, "sum"),
        avg_sales=(sales_col, "mean"),
        total_quantity=(quantity_col, "sum"),
        order_count=(sales_col, "count"),
    ).reset_index()

    summary = summary.sort_values("total_sales", ascending=False).reset_index(drop=True)
    print(f"[指标] 类别汇总统计完成，共 {len(summary)} 个类别")
    return summary


def calc_city_summary(
    df: pd.DataFrame,
    city_col: str = "city",
    sales_col: str = "total_price",
    quantity_col: str = "quantity",
) -> pd.DataFrame:
    """
    按城市汇总统计。

    对 DataFrame 按城市分组，计算销售额总和、平均销售额、
    总销量和订单数量。

    Args:
        df: 包含销售数据的 DataFrame。
        city_col: 城市列名，默认为 "city"。
        sales_col: 销售额列名，默认为 "total_price"。
        quantity_col: 销量列名，默认为 "quantity"。

    Returns:
        pd.DataFrame: 按城市汇总的统计结果 DataFrame。
    """
    summary = df.groupby(city_col).agg(
        total_sales=(sales_col, "sum"),
        avg_sales=(sales_col, "mean"),
        total_quantity=(quantity_col, "sum"),
        order_count=(sales_col, "count"),
    ).reset_index()

    summary = summary.sort_values("total_sales", ascending=False).reset_index(drop=True)
    print(f"[指标] 城市汇总统计完成，共 {len(summary)} 个城市")
    return summary


def compare_models(
    results: Dict[str, Dict[str, Any]],
) -> pd.DataFrame:
    """
    多模型对比表。

    将多个模型或方法的评估指标整理为对比表格。

    Args:
        results: 字典结构，键为模型名称，值为包含各项指标的字典。
                  例如: {"模型A": {"accuracy": 0.95, "f1": 0.92}}

    Returns:
        pd.DataFrame: 模型对比结果表格。
    """
    comparison_df = pd.DataFrame(results).T
    comparison_df.index.name = "模型/方法"
    print(f"[指标] 模型对比表生成完成，共 {len(comparison_df)} 个模型")
    return comparison_df
