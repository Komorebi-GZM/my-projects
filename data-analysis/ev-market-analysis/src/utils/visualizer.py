# -*- coding: utf-8 -*-
"""visualizer.py - 通用可视化出图器

提供时间序列图、热力图和多组对比图等常用可视化函数，
统一管理图表样式和保存逻辑。
"""

from pathlib import Path
from typing import Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .config import PLT_STYLE


def _apply_style():
    """应用全局可视化样式。"""
    try:
        plt.style.use(PLT_STYLE["style"])
    except OSError:
        # 某些环境可能缺少特定样式，使用默认样式
        plt.style.use("seaborn-v0_8-whitegrid")
    sns.set_palette(PLT_STYLE["color_palette"])
    plt.rcParams.update({
        "font.size": PLT_STYLE["font_size"],
        "figure.dpi": PLT_STYLE["figure_dpi"],
        "savefig.dpi": PLT_STYLE["save_dpi"],
        "savefig.bbox_inches": PLT_STYLE["save_bbox_inches"],
    })


def plot_time_series(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    group_col: Optional[str] = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    figsize: Optional[tuple] = None,
    save_path: Optional[Union[str, Path]] = None,
    **kwargs,
) -> plt.Axes:
    """绘制时间序列折线图。

    Parameters
    ----------
    df : pd.DataFrame
        输入数据。
    x_col : str
        X 轴列名（通常为时间列）。
    y_col : str
        Y 轴列名（数值列）。
    group_col : str, optional
        分组列名，用于绘制多条折线。
    title : str
        图表标题。
    xlabel : str
        X 轴标签。
    ylabel : str
        Y 轴标签。
    figsize : tuple, optional
        图表尺寸，默认使用配置值。
    save_path : str or Path, optional
        图片保存路径，为 None 则不保存。
    **kwargs
        传递给 seaborn.lineplot 的额外参数。

    Returns
    -------
    plt.Axes
        绑定的坐标轴对象。
    """
    _apply_style()
    fig, ax = plt.subplots(figsize=figsize or PLT_STYLE["figure_size"])

    if group_col:
        sns.lineplot(data=df, x=x_col, y=y_col, hue=group_col,
                     marker="o", ax=ax, **kwargs)
        ax.legend(title=group_col, bbox_to_anchor=(1.02, 1), loc="upper left")
    else:
        sns.lineplot(data=df, x=x_col, y=y_col, marker="o", ax=ax, **kwargs)

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, format=PLT_STYLE["save_format"])
        print(f"[visualizer] 图表已保存: {save_path}")

    return ax


def plot_model_forecast(
    y_true,
    y_pred,
    title: str = "预测结果对比",
    xlabel: str = "样本序号",
    ylabel: str = "数值",
    figsize: Optional[tuple] = None,
    save_path: Optional[Union[str, Path]] = None,
    show_metrics: bool = True,
) -> plt.Axes:
    """绘制模型预测结果对比图（真实值 vs 预测值）。

    Parameters
    ----------
    y_true : array-like
        真实值序列。
    y_pred : array-like
        预测值序列。
    title : str
        图表标题。
    xlabel : str
        X 轴标签。
    ylabel : str
        Y 轴标签。
    figsize : tuple, optional
        图表尺寸。
    save_path : str or Path, optional
        图片保存路径。
    show_metrics : bool
        是否在图表上显示 MAE/RMSE/MAPE 指标。

    Returns
    -------
    plt.Axes
        绑定的坐标轴对象。
    """
    from .metrics import calc_mae, calc_rmse, calc_mape

    _apply_style()
    fig, ax = plt.subplots(figsize=figsize or PLT_STYLE["figure_size"])

    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()

    ax.plot(y_true, color="#2196F3", linewidth=0.8, alpha=0.9, label="真实值")
    ax.plot(y_pred, color="#F44336", linewidth=0.8, alpha=0.7, linestyle="--", label="预测值")

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)

    if show_metrics:
        mae = calc_mae(y_true, y_pred)
        rmse = calc_rmse(y_true, y_pred)
        mape = calc_mape(y_true, y_pred)
        text = f"MAE  = {mae:.4f}\nRMSE = {rmse:.4f}\nMAPE = {mape:.2f}%"
        ax.text(0.02, 0.97, text, transform=ax.transAxes,
                fontsize=10, verticalalignment="top",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="wheat", alpha=0.8))

    plt.tight_layout()

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, format=PLT_STYLE["save_format"])
        print(f"[visualizer] 图表已保存: {save_path}")

    return ax


def plot_grouped_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    group_col: Optional[str] = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    figsize: Optional[tuple] = None,
    save_path: Optional[Union[str, Path]] = None,
    **kwargs,
) -> plt.Axes:
    """绘制分组柱状图。

    Parameters
    ----------
    df : pd.DataFrame
        输入数据。
    x_col : str
        X 轴列名（分类列）。
    y_col : str
        Y 轴列名（数值列）。
    group_col : str, optional
        分组列名（用于 hue 分组）。
    title : str
        图表标题。
    xlabel : str
        X 轴标签。
    ylabel : str
        Y 轴标签。
    figsize : tuple, optional
        图表尺寸。
    save_path : str or Path, optional
        图片保存路径。
    **kwargs
        传递给 seaborn.barplot 的额外参数。

    Returns
    -------
    plt.Axes
        绑定的坐标轴对象。
    """
    _apply_style()
    fig, ax = plt.subplots(figsize=figsize or PLT_STYLE["figure_size"])

    sns.barplot(data=df, x=x_col, y=y_col, hue=group_col, ax=ax, **kwargs)

    if group_col:
        ax.legend(title=group_col, bbox_to_anchor=(1.02, 1), loc="upper left")

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, format=PLT_STYLE["save_format"])
        print(f"[visualizer] 图表已保存: {save_path}")

    return ax


def plot_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    hue_col: Optional[str] = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    figsize: Optional[tuple] = None,
    save_path: Optional[Union[str, Path]] = None,
    **kwargs,
) -> plt.Axes:
    """绘制散点图。

    Parameters
    ----------
    df : pd.DataFrame
        输入数据。
    x_col : str
        X 轴列名。
    y_col : str
        Y 轴列名。
    hue_col : str, optional
        颜色分组列名。
    title : str
        图表标题。
    xlabel : str
        X 轴标签。
    ylabel : str
        Y 轴标签。
    figsize : tuple, optional
        图表尺寸。
    save_path : str or Path, optional
        图片保存路径。
    **kwargs
        传递给 seaborn.scatterplot 的额外参数。

    Returns
    -------
    plt.Axes
        绑定的坐标轴对象。
    """
    _apply_style()
    fig, ax = plt.subplots(figsize=figsize or PLT_STYLE["figure_size"])

    sns.scatterplot(data=df, x=x_col, y=y_col, hue=hue_col, ax=ax, **kwargs)

    if hue_col:
        ax.legend(title=hue_col, bbox_to_anchor=(1.02, 1), loc="upper left")

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, format=PLT_STYLE["save_format"])
        print(f"[visualizer] 图表已保存: {save_path}")

    return ax


def plot_heatmap(
    data: Union[pd.DataFrame, np.ndarray],
    title: str = "",
    annot: bool = True,
    cmap: Optional[str] = None,
    figsize: Optional[tuple] = None,
    save_path: Optional[Union[str, Path]] = None,
    **kwargs,
) -> plt.Axes:
    """绘制热力图。

    Parameters
    ----------
    data : pd.DataFrame or np.ndarray
        输入数据（二维矩阵或 DataFrame）。
    title : str
        图表标题。
    annot : bool
        是否显示数值标注。
    cmap : str, optional
        颜色映射，默认使用配置值。
    figsize : tuple, optional
        图表尺寸。
    save_path : str or Path, optional
        图片保存路径。
    **kwargs
        传递给 seaborn.heatmap 的额外参数。

    Returns
    -------
    plt.Axes
        绑定的坐标轴对象。
    """
    _apply_style()
    fig, ax = plt.subplots(figsize=figsize or (10, 8))

    cmap = cmap or PLT_STYLE["cmap_sequential"]
    sns.heatmap(data, annot=annot, cmap=cmap, ax=ax,
                fmt=".2f" if annot else None, **kwargs)

    ax.set_title(title, fontsize=14, fontweight="bold")
    plt.tight_layout()

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, format=PLT_STYLE["save_format"])
        print(f"[visualizer] 图表已保存: {save_path}")

    return ax


def plot_multi_comparison(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    group_col: Optional[str] = None,
    plot_type: str = "bar",
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    figsize: Optional[tuple] = None,
    save_path: Optional[Union[str, Path]] = None,
    **kwargs,
) -> plt.Axes:
    """绘制多组对比图（柱状图/箱线图/小提琴图）。

    Parameters
    ----------
    df : pd.DataFrame
        输入数据。
    x_col : str
        X 轴列名（分类列）。
    y_col : str
        Y 轴列名（数值列）。
    group_col : str, optional
        分组列名（用于 hue 分组）。
    plot_type : str
        图表类型，支持 'bar' / 'box' / 'violin'。
    title : str
        图表标题。
    xlabel : str
        X 轴标签。
    ylabel : str
        Y 轴标签。
    figsize : tuple, optional
        图表尺寸。
    save_path : str or Path, optional
        图片保存路径。
    **kwargs
        传递给绑图函数的额外参数。

    Returns
    -------
    plt.Axes
        绑定的坐标轴对象。
    """
    _apply_style()
    fig, ax = plt.subplots(figsize=figsize or PLT_STYLE["figure_size"])

    plot_func_map = {
        "bar": sns.barplot,
        "box": sns.boxplot,
        "violin": sns.violinplot,
    }
    if plot_type not in plot_func_map:
        raise ValueError(f"不支持的图表类型: {plot_type}，可选: {list(plot_func_map.keys())}")

    plot_func = plot_func_map[plot_type]
    plot_func(data=df, x=x_col, y=y_col, hue=group_col, ax=ax, **kwargs)

    if group_col:
        ax.legend(title=group_col, bbox_to_anchor=(1.02, 1), loc="upper left")

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, format=PLT_STYLE["save_format"])
        print(f"[visualizer] 图表已保存: {save_path}")

    return ax
