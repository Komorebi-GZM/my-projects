"""
可视化出图器模块 - 产品销售数据分析项目

本模块提供统一的数据可视化接口，封装了常用的图表绘制函数。
所有图表均使用 matplotlib 生成，支持中文显示（SimHei 字体）。
"""

import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
from pathlib import Path

from .config import PLT_CONFIG, CATEGORY_LIST, CITY_LIST

# ============================================================
# 全局绘图设置
# ============================================================
# 设置中文字体
matplotlib.rcParams["font.sans-serif"] = [PLT_CONFIG["font_family"]]
matplotlib.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


def _apply_default_style():
    """应用默认绘图样式配置。"""
    plt.rcParams.update({
        "figure.dpi": PLT_CONFIG["dpi"],
        "font.size": PLT_CONFIG["font_size"],
        "figure.figsize": PLT_CONFIG["figsize"],
    })


def plot_category_sales(
    df: pd.DataFrame,
    category_col: str = "category",
    sales_col: str = "total_price",
    title: str = "各类别销售额对比",
    save_path: str | Path | None = None,
    **kwargs,
) -> plt.Axes:
    """
    按产品类别绘制销售柱状图。

    对 DataFrame 按类别分组求和，绘制柱状图展示各类别的销售额对比。

    Args:
        df: 包含销售数据的 DataFrame。
        category_col: 类别列名，默认为 "category"。
        sales_col: 销售额列名，默认为 "total_price"。
        title: 图表标题。
        save_path: 图片保存路径，为 None 时不保存。
        **kwargs: 传递给 plt.bar 的额外参数。

    Returns:
        plt.Axes: 绑定的 Axes 对象。
    """
    _apply_default_style()

    fig, ax = plt.subplots(figsize=PLT_CONFIG["figsize"])

    # 按类别汇总销售额
    sales_by_category = df.groupby(category_col)[sales_col].sum().sort_values(ascending=False)

    # 绘制柱状图
    colors = plt.cm.Set2(np.linspace(0, 1, len(sales_by_category)))
    bars = ax.bar(sales_by_category.index, sales_by_category.values, color=colors, **kwargs)

    # 在柱子上方添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:,.0f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("产品类别", fontsize=12)
    ax.set_ylabel("销售额", fontsize=12)
    ax.tick_params(axis="x", rotation=30)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=PLT_CONFIG["dpi"], bbox_inches=PLT_CONFIG["bbox_inches"])
        print(f"[可视化] 图表已保存: {save_path}")

    return ax


def plot_city_sales(
    df: pd.DataFrame,
    city_col: str = "city",
    sales_col: str = "total_price",
    title: str = "各城市销售额对比",
    save_path: str | Path | None = None,
    **kwargs,
) -> plt.Axes:
    """
    按城市绘制销售对比柱状图。

    对 DataFrame 按城市分组求和，绘制柱状图展示各城市的销售额对比。

    Args:
        df: 包含销售数据的 DataFrame。
        city_col: 城市列名，默认为 "city"。
        sales_col: 销售额列名，默认为 "total_price"。
        title: 图表标题。
        save_path: 图片保存路径，为 None 时不保存。
        **kwargs: 传递给 plt.bar 的额外参数。

    Returns:
        plt.Axes: 绑定的 Axes 对象。
    """
    _apply_default_style()

    fig, ax = plt.subplots(figsize=PLT_CONFIG["figsize"])

    # 按城市汇总销售额
    sales_by_city = df.groupby(city_col)[sales_col].sum().sort_values(ascending=False)

    # 绘制柱状图
    colors = plt.cm.Pastel1(np.linspace(0, 1, len(sales_by_city)))
    bars = ax.bar(sales_by_city.index, sales_by_city.values, color=colors, **kwargs)

    # 在柱子上方添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:,.0f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("城市", fontsize=12)
    ax.set_ylabel("销售额", fontsize=12)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=PLT_CONFIG["dpi"], bbox_inches=PLT_CONFIG["bbox_inches"])
        print(f"[可视化] 图表已保存: {save_path}")

    return ax


def plot_time_series(
    df: pd.DataFrame,
    date_col: str = "date",
    value_col: str = "total_price",
    title: str = "销售额时间趋势",
    save_path: str | Path | None = None,
    **kwargs,
) -> plt.Axes:
    """
    绘制销售额时序折线图。

    按日期汇总销售额，绘制时间序列折线图，展示销售趋势变化。

    Args:
        df: 包含销售数据的 DataFrame。
        date_col: 日期列名，默认为 "date"。
        value_col: 数值列名，默认为 "total_price"。
        title: 图表标题。
        save_path: 图片保存路径，为 None 时不保存。
        **kwargs: 传递给 plt.plot 的额外参数。

    Returns:
        plt.Axes: 绑定的 Axes 对象。
    """
    _apply_default_style()

    fig, ax = plt.subplots(figsize=PLT_CONFIG["figsize"])

    # 确保日期列为 datetime 类型
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])

    # 按日期汇总
    daily_sales = df_copy.groupby(date_col)[value_col].sum().sort_index()

    ax.plot(daily_sales.index, daily_sales.values, color="#2196F3", linewidth=1.5, **kwargs)
    ax.fill_between(daily_sales.index, daily_sales.values, alpha=0.15, color="#2196F3")

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("日期", fontsize=12)
    ax.set_ylabel("销售额", fontsize=12)
    plt.xticks(rotation=30)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=PLT_CONFIG["dpi"], bbox_inches=PLT_CONFIG["bbox_inches"])
        print(f"[可视化] 图表已保存: {save_path}")

    return ax


def plot_heatmap(
    df: pd.DataFrame,
    title: str = "相关性热力图",
    save_path: str | Path | None = None,
    **kwargs,
) -> plt.Axes:
    """
    绘制数值列相关性热力图。

    计算 DataFrame 中所有数值列的相关系数矩阵，并以热力图形式展示。

    Args:
        df: 包含数值列的 DataFrame。
        title: 图表标题。
        save_path: 图片保存路径，为 None 时不保存。
        **kwargs: 传递给 plt.imshow 的额外参数。

    Returns:
        plt.Axes: 绑定的 Axes 对象。
    """
    _apply_default_style()

    fig, ax = plt.subplots(figsize=(10, 8))

    # 仅选择数值列
    numeric_df = df.select_dtypes(include=[np.number])
    corr_matrix = numeric_df.corr()

    im = ax.imshow(corr_matrix, cmap="RdBu_r", aspect="auto", **kwargs)

    # 添加颜色条
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("相关系数", fontsize=11)

    # 设置坐标轴标签
    labels = corr_matrix.columns.tolist()
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(labels, fontsize=9)

    # 在每个格子中标注相关系数值
    for i in range(len(labels)):
        for j in range(len(labels)):
            val = corr_matrix.iloc[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8)

    ax.set_title(title, fontsize=14, fontweight="bold")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=PLT_CONFIG["dpi"], bbox_inches=PLT_CONFIG["bbox_inches"])
        print(f"[可视化] 图表已保存: {save_path}")

    return ax


def plot_category_distribution(
    df: pd.DataFrame,
    category_col: str = "category",
    title: str = "产品类别分布",
    save_path: str | Path | None = None,
    **kwargs,
) -> plt.Axes:
    """
    绘制产品类别分布饼图。

    统计各类别的数量占比，绘制饼图展示分布情况。

    Args:
        df: 包含类别数据的 DataFrame。
        category_col: 类别列名，默认为 "category"。
        title: 图表标题。
        save_path: 图片保存路径，为 None 时不保存。
        **kwargs: 传递给 plt.pie 的额外参数。

    Returns:
        plt.Axes: 绑定的 Axes 对象。
    """
    _apply_default_style()

    fig, ax = plt.subplots(figsize=(8, 8))

    # 统计各类别数量
    category_counts = df[category_col].value_counts()

    # 绘制饼图
    colors = plt.cm.Set3(np.linspace(0, 1, len(category_counts)))
    wedges, texts, autotexts = ax.pie(
        category_counts.values,
        labels=category_counts.index,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        **kwargs,
    )

    # 设置百分比文字样式
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight("bold")

    ax.set_title(title, fontsize=14, fontweight="bold")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=PLT_CONFIG["dpi"], bbox_inches=PLT_CONFIG["bbox_inches"])
        print(f"[可视化] 图表已保存: {save_path}")

    return ax
