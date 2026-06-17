"""
标准时序数据加载器 (Skill-01)
支持加载原始数据、预处理后数据、全城市合并数据
"""

import pandas as pd
import sys
import os

# 确保可以导入 config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import RAW_DATA_FILE, CITIES


def load_raw_city_data(city: str) -> pd.DataFrame:
    """加载指定城市的原始数据

    Args:
        city: 城市名称（Laayoune/Boujdour/Foum eloued/Marrakech）

    Returns:
        DataFrame，DateTime为索引，含 city 列
    """
    if city not in CITIES:
        raise ValueError(f"未知城市: {city}，可选: {list(CITIES.keys())}")

    config = CITIES[city]
    df = pd.read_excel(RAW_DATA_FILE, sheet_name=config['sheet'], engine='openpyxl')
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df = df.set_index('DateTime').sort_index()
    df['city'] = city
    return df


def load_all_cities() -> dict:
    """加载全部城市原始数据

    Returns:
        {"Laayoune": DataFrame, "Boujdour": DataFrame, ...}
    """
    return {city: load_raw_city_data(city) for city in CITIES}


def load_preprocessed(filepath: str) -> pd.DataFrame:
    """加载预处理后的统一数据集

    Args:
        filepath: 预处理后的CSV文件路径

    Returns:
        DataFrame
    """
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    return df
