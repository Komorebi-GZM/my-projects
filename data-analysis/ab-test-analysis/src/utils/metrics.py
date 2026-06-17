"""
指标计算工具模块
提供通用的评估指标计算功能
"""

import numpy as np
import pandas as pd
from typing import Optional


class Metrics:
    """指标计算工具"""

    @staticmethod
    def null_summary(df: pd.DataFrame) -> pd.DataFrame:
        """
        计算缺失值汇总

        Args:
            df: 数据框

        Returns:
            pd.DataFrame: 包含缺失值统计的汇总表
        """
        summary = pd.DataFrame({
            "列名": df.columns,
            "非空数量": df.notna().sum().values,
            "缺失数量": df.isnull().sum().values,
            "缺失比例(%)": (df.isnull().sum().values / len(df) * 100).round(2),
            "数据类型": df.dtypes.values,
        })
        return summary

    @staticmethod
    def duplicate_summary(df: pd.DataFrame) -> dict:
        """
        计算重复值汇总

        Args:
            df: 数据框

        Returns:
            dict: 重复值统计信息
        """
        dup_count = df.duplicated().sum()
        return {
            "总行数": len(df),
            "重复行数": int(dup_count),
            "重复比例(%)": round(dup_count / len(df) * 100, 2),
        }

    @staticmethod
    def describe_all(df: pd.DataFrame) -> pd.DataFrame:
        """
        生成全面的描述性统计

        Args:
            df: 数据框

        Returns:
            pd.DataFrame: 描述性统计表
        """
        return df.describe(include="all").round(4)
