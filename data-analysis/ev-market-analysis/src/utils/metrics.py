# -*- coding: utf-8 -*-
"""metrics.py - 评估指标计算器

提供常用的回归评估指标计算函数，包括 MAE、RMSE、MAPE 和综合评估。
"""

from typing import Dict, Optional

import numpy as np
import pandas as pd


def calc_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """计算平均绝对误差 (Mean Absolute Error)。

    Parameters
    ----------
    y_true : np.ndarray
        真实值数组。
    y_pred : np.ndarray
        预测值数组。

    Returns
    -------
    float
        MAE 值。
    """
    return float(np.mean(np.abs(y_true - y_pred)))


def calc_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """计算均方根误差 (Root Mean Squared Error)。

    Parameters
    ----------
    y_true : np.ndarray
        真实值数组。
    y_pred : np.ndarray
        预测值数组。

    Returns
    -------
    float
        RMSE 值。
    """
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def calc_mape(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-8) -> float:
    """计算平均绝对百分比误差 (Mean Absolute Percentage Error)。

    Parameters
    ----------
    y_true : np.ndarray
        真实值数组。
    y_pred : np.ndarray
        预测值数组。
    epsilon : float
        防止除零的小常数，默认 1e-8。

    Returns
    -------
    float
        MAPE 值（百分比形式，如 5.23 表示 5.23%）。
    """
    mask = np.abs(y_true) > epsilon
    if mask.sum() == 0:
        return float("inf")
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def evaluate_model(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str = "Model",
    verbose: bool = True,
) -> Dict[str, float]:
    """综合评估模型预测性能。

    Parameters
    ----------
    y_true : np.ndarray
        真实值数组。
    y_pred : np.ndarray
        预测值数组。
    model_name : str
        模型名称，用于输出标识。
    verbose : bool
        是否打印评估结果。

    Returns
    -------
    dict
        包含 mae, rmse, mape 的指标字典。
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    if y_true.shape != y_pred.shape:
        raise ValueError(f"形状不匹配: y_true {y_true.shape} vs y_pred {y_pred.shape}")

    results = {
        "model": model_name,
        "mae": calc_mae(y_true, y_pred),
        "rmse": calc_rmse(y_true, y_pred),
        "mape": calc_mape(y_true, y_pred),
    }

    if verbose:
        print(f"\n{'='*50}")
        print(f"  模型评估报告: {model_name}")
        print(f"{'='*50}")
        print(f"  MAE  : {results['mae']:.4f}")
        print(f"  RMSE : {results['rmse']:.4f}")
        print(f"  MAPE : {results['mape']:.2f}%")
        print(f"{'='*50}\n")

    return results


def compare_models(
    results_list: list,
    sort_by: str = "mape",
    save_path: Optional[str] = None,
) -> pd.DataFrame:
    """多模型对比，生成排序后的 DataFrame。

    Parameters
    ----------
    results_list : list
        evaluate_model() 返回的 dict 列表。
    sort_by : str
        排序依据，可选 'mae' / 'rmse' / 'mape'。
    save_path : str, optional
        若非 None，保存为 CSV。

    Returns
    -------
    pd.DataFrame
        按指定指标排序的模型对比表。
    """
    df = pd.DataFrame(results_list)
    
    # 统一列名格式
    df = df.rename(columns={
        'mae': 'MAE',
        'rmse': 'RMSE', 
        'mape': 'MAPE',
        'model': 'Model'
    })
    
    # 按指定指标排序
    sort_col = sort_by.upper()
    if sort_col not in df.columns:
        sort_col = 'MAPE'  # 默认按 MAPE 排序
    df = df.sort_values(sort_col, ascending=True).reset_index(drop=True)
    
    # 添加排名列
    df.insert(0, 'Rank', range(1, len(df) + 1))
    
    # 添加质量标签
    def _quality_label(mape: float) -> str:
        if mape < 5:
            return 'Outstanding'
        elif mape < 10:
            return 'Excellent'
        elif mape < 15:
            return 'Pass'
        else:
            return 'Needs Improvement'
    
    if 'MAPE' in df.columns:
        df['Quality'] = df['MAPE'].apply(_quality_label)
    
    if save_path:
        df.to_csv(save_path, index=False)
        print(f"[metrics] 模型对比表已保存: {save_path}")
    
    return df


def calc_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """计算决定系数 (R-squared)。

    Parameters
    ----------
    y_true : np.ndarray
        真实值数组。
    y_pred : np.ndarray
        预测值数组。

    Returns
    -------
    float
        R² 值。
    """
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0
