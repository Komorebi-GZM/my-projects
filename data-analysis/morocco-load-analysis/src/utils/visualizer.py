"""
标准可视化出图器 (Skill-02)
提供项目统一的图表风格和常用绘图函数

使用方式:
    from utils.visualizer import plot_model_forecast

    fig = plot_model_forecast(y_test, y_pred, 'XGBoost - 负荷预测结果',
                              output_path='outputs/ch04/forecast.png')
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 无显示器环境
import matplotlib.pyplot as plt


def _apply_style():
    """应用项目全局样式"""
    plt.rcParams.update({
        'figure.dpi': 150,
        'savefig.dpi': 150,
        'font.size': 12,
        'axes.unicode_minus': False,
        'figure.figsize': (14, 5),
    })


def plot_model_forecast(
    y_true,
    y_pred,
    title: str,
    output_path: str = None,
    figsize: tuple = (14, 5),
    dpi: int = 150,
    show_metrics: bool = True,
    metrics_dict: dict = None,
) -> 'matplotlib.figure.Figure':
    """绘制模型预测结果对比图（真实值 vs 预测值）

    Args:
        y_true: 真实值序列（pd.Series 或 np.ndarray）
        y_pred: 预测值序列（pd.Series 或 np.ndarray）
        title: 图表标题
        output_path: 若非 None，保存图片到指定路径
        figsize: 图表尺寸
        dpi: 分辨率
        show_metrics: 是否在图表上显示 MAE/RMSE/MAPE
        metrics_dict: 若提供，使用其中的指标值；否则自动计算

    Returns:
        matplotlib Figure 对象
    """
    _apply_style()

    y_true = np.asarray(y_true, dtype=np.float64).ravel()
    y_pred = np.asarray(y_pred, dtype=np.float64).ravel()

    # 对齐长度
    min_len = min(len(y_true), len(y_pred))
    y_true = y_true[:min_len]
    y_pred = y_pred[:min_len]

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # 绘制曲线
    ax.plot(y_true, color='#2196F3', linewidth=0.8, alpha=0.9, label='Actual')
    ax.plot(y_pred, color='#F44336', linewidth=0.8, alpha=0.7, linestyle='--', label='Predicted')

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Time Step', fontsize=12)
    ax.set_ylabel('Load (kW)', fontsize=12)
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3)

    # 叠加指标文本框
    if show_metrics:
        if metrics_dict is None:
            from utils.metrics import evaluate_model
            metrics_dict = evaluate_model(y_true, y_pred, '')

        text = (f"MAE  = {metrics_dict['MAE']:.4f}\n"
                f"RMSE = {metrics_dict['RMSE']:.4f}\n"
                f"MAPE = {metrics_dict['MAPE']:.2f}%")
        ax.text(0.02, 0.97, text, transform=ax.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='wheat', alpha=0.8))

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        print(f'  [保存] {output_path}')
    else:
        plt.close(fig)

    return fig
