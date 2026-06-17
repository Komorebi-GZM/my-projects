"""
Genesis_Anomaly_Analysis - 可视化工具模块
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import PLT_CONFIG, ensure_output_dir

# 设置默认样式
plt.style.use(PLT_CONFIG['style'])
plt.rcParams['figure.dpi'] = PLT_CONFIG['dpi']
plt.rcParams['font.size'] = PLT_CONFIG['font_size']


def save_figure(fig: plt.Figure, filename: str, chapter_id: str, dpi: int = 150) -> str:
    """
    保存图表到章节输出目录
    
    Args:
        fig: matplotlib Figure 对象
        filename: 文件名（不含路径）
        chapter_id: 章节ID（如 'ch01'）
        dpi: 分辨率
    
    Returns:
        保存的文件路径
    """
    output_dir = ensure_output_dir(chapter_id)
    figures_dir = output_dir / 'figures'
    filepath = figures_dir / filename
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return str(filepath)


def plot_time_series(df: pd.DataFrame, 
                     columns: List[str],
                     title: str = 'Time Series',
                     figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
    """
    绘制时序图
    
    Args:
        df: DataFrame（含时间索引）
        columns: 要绘制的列名列表
        title: 图表标题
        figsize: 图表尺寸
    
    Returns:
        Figure 对象
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    for col in columns:
        if col in df.columns:
            ax.plot(df.index, df[col], label=col, alpha=0.8)
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.set_title(title)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    return fig


def plot_distribution(df: pd.DataFrame,
                      column: str,
                      title: str = None,
                      bins: int = 50) -> plt.Figure:
    """
    绘制分布直方图
    
    Args:
        df: DataFrame
        column: 列名
        title: 图表标题
        bins: 分箱数
    
    Returns:
        Figure 对象
    """
    if title is None:
        title = f'Distribution of {column}'
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df[column].dropna(), bins=bins, alpha=0.7, edgecolor='black')
    ax.set_xlabel(column)
    ax.set_ylabel('Frequency')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    
    return fig


def plot_boxplot(df: pd.DataFrame,
                 column: str,
                 by: Optional[str] = None,
                 title: str = None) -> plt.Figure:
    """
    绘制箱线图
    
    Args:
        df: DataFrame
        column: 数值列名
        by: 分组列名
        title: 图表标题
    
    Returns:
        Figure 对象
    """
    if title is None:
        title = f'Boxplot of {column}'
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if by and by in df.columns:
        df.boxplot(column=column, by=by, ax=ax)
        ax.set_title(title)
    else:
        df[column].dropna().plot.box(ax=ax)
        ax.set_title(title)
        ax.set_ylabel(column)
    
    return fig


def plot_heatmap(df: pd.DataFrame,
                 title: str = 'Correlation Heatmap',
                 figsize: Tuple[int, int] = (10, 8),
                 cmap: str = 'RdBu_r') -> plt.Figure:
    """
    绘制相关性热力图
    
    Args:
        df: DataFrame（数值列）
        title: 图表标题
        figsize: 图表尺寸
        cmap: 颜色映射
    
    Returns:
        Figure 对象
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # 计算相关系数
    corr = df.corr()
    
    # 绘制热力图
    sns.heatmap(corr, annot=True, fmt='.2f', cmap=cmap, 
                center=0, square=True, ax=ax,
                cbar_kws={'shrink': 0.8})
    ax.set_title(title)
    
    return fig


def plot_comparison(dfs: List[pd.DataFrame],
                    column: str,
                    labels: List[str],
                    title: str = 'Comparison',
                    figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
    """
    绘制多组数据对比图
    
    Args:
        dfs: DataFrame 列表
        column: 要对比的列名
        labels: 每组数据的标签
        title: 图表标题
        figsize: 图表尺寸
    
    Returns:
        Figure 对象
    """
    fig, axes = plt.subplots(1, len(dfs), figsize=figsize, sharey=True)
    
    if len(dfs) == 1:
        axes = [axes]
    
    for ax, df, label in zip(axes, dfs, labels):
        if column in df.columns:
            ax.plot(df.index, df[column], alpha=0.7)
            ax.set_title(f'{label} (n={len(df)})')
            ax.set_xlabel('Time')
            ax.grid(True, alpha=0.3)
    
    axes[0].set_ylabel(column)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    return fig


def plot_state_timeline(df: pd.DataFrame,
                        state_col: str = 'Label',
                        signal_cols: List[str] = None,
                        title: str = 'State Timeline') -> plt.Figure:
    """
    绘制状态时间轴图（带状态背景色）
    
    Args:
        df: DataFrame（含时间索引和状态列）
        state_col: 状态列名
        signal_cols: 要绘制的信号列
        title: 图表标题
    
    Returns:
        Figure 对象
    """
    if signal_cols is None:
        signal_cols = ['MotorData.ActCurrent']
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # 绘制信号
    for col in signal_cols:
        if col in df.columns:
            ax.plot(df.index, df[col], label=col, linewidth=1)
    
    # 添加状态背景色
    states = df[state_col].unique()
    colors = plt.cm.Set3(np.linspace(0, 1, len(states)))
    state_colors = dict(zip(states, colors))
    
    # 标记状态变化点
    state_changes = df[state_col].diff().ne(0)
    change_points = df.index[state_changes]
    
    for i, point in enumerate(change_points[:-1]):
        next_point = change_points[i + 1]
        state = df.loc[point, state_col]
        ax.axvspan(point, next_point, alpha=0.2, color=state_colors.get(state, 'gray'))
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Signal Value')
    ax.set_title(title)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    return fig
