"""
Genesis_Anomaly_Analysis - 数据加载器模块
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, List
import sys

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import DATA_FILES, SIGNAL_COLUMNS


def load_raw_data(file_key: str, parse_timestamp: bool = True) -> pd.DataFrame:
    """
    加载原始数据文件
    
    Args:
        file_key: 文件标识 ('anomaly_labels', 'state_machine_labels', 'lineardrive', 'normal', 'pressure')
        parse_timestamp: 是否解析时间戳
    
    Returns:
        DataFrame
    """
    file_path = DATA_FILES.get(file_key)
    if not file_path or not file_path.exists():
        raise FileNotFoundError(f"数据文件不存在: {file_key} -> {file_path}")
    
    df = pd.read_csv(file_path)
    
    if parse_timestamp and 'Timestamp' in df.columns:
        # 根据文件名判断时间戳格式
        if file_key in ['anomaly_labels', 'state_machine_labels']:
            # Unix 秒格式
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')
        else:
            # Unix 毫秒格式
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df.set_index('Timestamp', inplace=True)
    
    return df


def load_all_data(parse_timestamp: bool = True) -> Dict[str, pd.DataFrame]:
    """
    批量加载所有数据文件
    
    Args:
        parse_timestamp: 是否解析时间戳
    
    Returns:
        Dict[str, DataFrame]
    """
    data_dict = {}
    for key in DATA_FILES.keys():
        try:
            data_dict[key] = load_raw_data(key, parse_timestamp)
            print(f"✓ 加载成功: {key} ({len(data_dict[key])} 行)")
        except Exception as e:
            print(f"✗ 加载失败: {key} - {e}")
    return data_dict


def load_anomaly_data() -> pd.DataFrame:
    """加载异常标签数据（含 Label 0/1/2）"""
    return load_raw_data('anomaly_labels')


def load_state_machine_data() -> pd.DataFrame:
    """加载状态机标签数据（含 Label 0-8）"""
    return load_raw_data('state_machine_labels')


def load_condition_data(condition: str) -> pd.DataFrame:
    """
    加载特定工况数据
    
    Args:
        condition: 'lineardrive', 'normal', 'pressure'
    """
    return load_raw_data(condition)


def get_signal_columns(signal_type: str = 'all') -> List[str]:
    """
    获取信号列名
    
    Args:
        signal_type: 'analog', 'digital', 'setpoint', 'timing', 'all'
    
    Returns:
        列名列表
    """
    if signal_type == 'all':
        columns = []
        for cols in SIGNAL_COLUMNS.values():
            columns.extend(cols)
        return columns
    return SIGNAL_COLUMNS.get(signal_type, [])


def split_by_label(df: pd.DataFrame, label_col: str = 'Label') -> Dict[int, pd.DataFrame]:
    """
    按标签分组数据
    
    Args:
        df: 含标签列的 DataFrame
        label_col: 标签列名
    
    Returns:
        Dict[label_value, DataFrame]
    """
    return {label: group for label, group in df.groupby(label_col)}


def get_common_columns(df_list: List[pd.DataFrame]) -> List[str]:
    """获取多个 DataFrame 的共同列"""
    if not df_list:
        return []
    common = set(df_list[0].columns)
    for df in df_list[1:]:
        common &= set(df.columns)
    return list(common)
