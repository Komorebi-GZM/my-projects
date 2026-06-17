"""
标准评估指标计算器 (Skill-03)
支持时序预测模型和优化模型的评估

使用方式:
    from utils.metrics import evaluate_model, compare_models

    result = evaluate_model(y_true, y_pred, "XGBoost")
    # {'model': 'XGBoost', 'MAE': 1.23, 'RMSE': 1.56, 'MAPE': 5.67}

    df = compare_models([result1, result2, ...])
"""

import numpy as np
import pandas as pd


# === 低负荷过滤阈值 ===
# 夜间低谷负荷可能降至 0.01~0.1 kW 量级，
# 1e-8 阈值几乎不起作用，因此设为 0.5 kW
MAPE_LOW_LOAD_THRESHOLD = 0.5


def calc_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """平均绝对误差 (Mean Absolute Error)

    Args:
        y_true: 真实值
        y_pred: 预测值

    Returns:
        MAE 值
    """
    y_true = np.asarray(y_true, dtype=np.float64).ravel()
    y_pred = np.asarray(y_pred, dtype=np.float64).ravel()
    return float(np.mean(np.abs(y_true - y_pred)))


def calc_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """均方根误差 (Root Mean Square Error)

    Args:
        y_true: 真实值
        y_pred: 预测值

    Returns:
        RMSE 值
    """
    y_true = np.asarray(y_true, dtype=np.float64).ravel()
    y_pred = np.asarray(y_pred, dtype=np.float64).ravel()
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def calc_mape(y_true: np.ndarray, y_pred: np.ndarray,
              threshold: float = MAPE_LOW_LOAD_THRESHOLD) -> float:
    """平均绝对百分比误差 (Mean Absolute Percentage Error, %)

    跳过 |y_true| < threshold 的点，避免低负荷时段除零导致 MAPE 爆炸。

    Args:
        y_true: 真实值
        y_pred: 预测值
        threshold: 低负荷过滤阈值，默认 0.5 kW

    Returns:
        MAPE 百分比数值（如 5.23 表示 5.23%）
    """
    y_true = np.asarray(y_true, dtype=np.float64).ravel()
    y_pred = np.asarray(y_pred, dtype=np.float64).ravel()

    # 过滤低负荷点
    mask = np.abs(y_true) >= threshold
    if mask.sum() == 0:
        return float('inf')

    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def evaluate_model(y_true, y_pred, model_name: str,
                   threshold: float = MAPE_LOW_LOAD_THRESHOLD) -> dict:
    """综合评估单个模型

    Args:
        y_true: 真实值 (np.ndarray 或 pd.Series)
        y_pred: 预测值 (np.ndarray 或 pd.Series)
        model_name: 模型名称
        threshold: MAPE 低负荷过滤阈值

    Returns:
        dict: {'model': str, 'MAE': float, 'RMSE': float, 'MAPE': float}
    """
    y_true = np.asarray(y_true, dtype=np.float64).ravel()
    y_pred = np.asarray(y_pred, dtype=np.float64).ravel()

    return {
        'model': model_name,
        'MAE': round(calc_mae(y_true, y_pred), 4),
        'RMSE': round(calc_rmse(y_true, y_pred), 4),
        'MAPE': round(calc_mape(y_true, y_pred, threshold), 2),
    }


def _quality_label(mape: float) -> str:
    """根据 MAPE 值返回质量标签

    <5%   Outstanding (卓越)
    <10%  Excellent (优秀)
    <15%  Pass (合格)
    >=15% Needs Improvement (需改进)
    """
    if mape < 5:
        return 'Outstanding'
    elif mape < 10:
        return 'Excellent'
    elif mape < 15:
        return 'Pass'
    else:
        return 'Needs Improvement'


def compare_models(results: list, output_path: str = None) -> pd.DataFrame:
    """多模型对比，生成排序后的 DataFrame

    Args:
        results: evaluate_model() 返回的 dict 列表
        output_path: 若非 None，保存为 CSV

    Returns:
        DataFrame 按 MAPE 升序排列，含 model/MAE/RMSE/MAPE/quality 列
    """
    df = pd.DataFrame(results)
    df = df.sort_values('MAPE', ascending=True).reset_index(drop=True)
    df.insert(0, 'rank', range(1, len(df) + 1))
    df['quality'] = df['MAPE'].apply(_quality_label)

    if output_path:
        df.to_csv(output_path, index=False)
        print(f'  [保存] {output_path}')

    return df
