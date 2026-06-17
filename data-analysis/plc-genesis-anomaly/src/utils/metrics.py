"""
Genesis_Anomaly_Analysis - 评估指标计算模块
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional


def calc_descriptive_stats(series: pd.Series) -> Dict:
    """
    计算描述性统计量
    
    Args:
        series: 数值序列
    
    Returns:
        统计量字典
    """
    return {
        'count': series.count(),
        'mean': series.mean(),
        'std': series.std(),
        'min': series.min(),
        '25%': series.quantile(0.25),
        '50%': series.median(),
        '75%': series.quantile(0.75),
        'max': series.max(),
        'skewness': series.skew(),
        'kurtosis': series.kurtosis(),
    }


def calc_cohens_d(group1: pd.Series, group2: pd.Series) -> float:
    """
    计算 Cohen's d 效应量
    
    Args:
        group1: 第一组数据
        group2: 第二组数据
    
    Returns:
        Cohen's d 值
    """
    n1, n2 = len(group1), len(group2)
    pooled_std = np.sqrt(((n1 - 1) * group1.var() + (n2 - 1) * group2.var()) / (n1 + n2 - 2))
    return (group1.mean() - group2.mean()) / pooled_std


def perform_ttest(group1: pd.Series, 
                  group2: pd.Series,
                  alternative: str = 'two-sided') -> Dict:
    """
    执行独立样本 t 检验
    
    Args:
        group1: 第一组数据
        group2: 第二组数据
        alternative: 检验类型 ('two-sided', 'less', 'greater')
    
    Returns:
        检验结果字典
    """
    t_stat, p_value = stats.ttest_ind(group1.dropna(), group2.dropna(), alternative=alternative)
    
    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < 0.05,
        'cohens_d': calc_cohens_d(group1, group2),
    }


def perform_ks_test(group1: pd.Series, group2: pd.Series) -> Dict:
    """
    执行 Kolmogorov-Smirnov 检验
    
    Args:
        group1: 第一组数据
        group2: 第二组数据
    
    Returns:
        检验结果字典
    """
    ks_stat, p_value = stats.ks_2samp(group1.dropna(), group2.dropna())
    
    return {
        'ks_statistic': ks_stat,
        'p_value': p_value,
        'significant': p_value < 0.05,
    }


def calc_correlation_matrix(df: pd.DataFrame, 
                            method: str = 'pearson') -> pd.DataFrame:
    """
    计算相关系数矩阵
    
    Args:
        df: DataFrame（数值列）
        method: 'pearson', 'spearman', 'kendall'
    
    Returns:
        相关系数矩阵
    """
    return df.corr(method=method)


def calc_stability_score(series: pd.Series, window: int = 100) -> Dict:
    """
    计算信号稳定性评分
    
    Args:
        series: 数值序列
        window: 滑动窗口大小
    
    Returns:
        稳定性指标字典
    """
    rolling_std = series.rolling(window=window).std()
    rolling_mean = series.rolling(window=window).mean()
    cv = rolling_std / rolling_mean  # 变异系数
    
    return {
        'mean_std': rolling_std.mean(),
        'max_std': rolling_std.max(),
        'mean_cv': cv.mean(),
        'stability_score': 1 / (1 + rolling_std.mean()),  # 标准差越小，稳定性越高
    }


def extract_time_features(series: pd.Series) -> Dict:
    """
    提取时域特征
    
    Args:
        series: 数值序列
    
    Returns:
        特征字典
    """
    series_clean = series.dropna()
    
    return {
        'mean': series_clean.mean(),
        'std': series_clean.std(),
        'max': series_clean.max(),
        'min': series_clean.min(),
        'peak_to_peak': series_clean.max() - series_clean.min(),
        'rms': np.sqrt(np.mean(series_clean ** 2)),
        'skewness': series_clean.skew(),
        'kurtosis': series_clean.kurtosis(),
    }


def compare_groups(df: pd.DataFrame,
                   value_col: str,
                   group_col: str,
                   groups: List) -> pd.DataFrame:
    """
    多组对比统计
    
    Args:
        df: DataFrame
        value_col: 数值列
        group_col: 分组列
        groups: 分组值列表
    
    Returns:
        对比统计表
    """
    results = []
    
    for group in groups:
        group_data = df[df[group_col] == group][value_col]
        stats_dict = calc_descriptive_stats(group_data)
        stats_dict['group'] = group
        stats_dict['count'] = len(group_data)
        results.append(stats_dict)
    
    return pd.DataFrame(results).set_index('group')
