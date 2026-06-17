# -*- coding: utf-8 -*-
"""data_loader.py - 通用数据加载器

支持 CSV / Excel / Parquet 格式的数据加载，
提供原始数据和预处理数据的统一加载接口。
"""

from pathlib import Path
from typing import Optional, Union

import pandas as pd

from .config import RAW_DATA_FILE, OUTPUT_BASE, DATA_DIR


def load_raw_data(
    filepath: Optional[Union[str, Path]] = None,
    encoding: str = "utf-8",
    **kwargs,
) -> pd.DataFrame:
    """加载原始数据文件。

    Parameters
    ----------
    filepath : str or Path, optional
        数据文件路径，默认使用 config.py 中配置的 RAW_DATA_FILE。
    encoding : str
        文件编码，默认 utf-8。
    **kwargs
        传递给 pandas 读取函数的额外参数。

    Returns
    -------
    pd.DataFrame
        加载的数据表。

    Raises
    ------
    FileNotFoundError
        指定的数据文件不存在。
    ValueError
        不支持的文件格式。
    """
    if filepath is None:
        filepath = RAW_DATA_FILE
    else:
        filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"数据文件不存在: {filepath}")

    suffix = filepath.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(filepath, encoding=encoding, **kwargs)
    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(filepath, engine="openpyxl", **kwargs)
    elif suffix == ".parquet":
        df = pd.read_parquet(filepath, **kwargs)
    else:
        raise ValueError(f"不支持的文件格式: {suffix}，仅支持 csv/xlsx/xls/parquet")

    print(f"[data_loader] 已加载数据: {filepath}")
    print(f"[data_loader] 数据形状: {df.shape[0]} 行 x {df.shape[1]} 列")
    return df


def load_preprocessed(
    chapter: str = "ch01_data_cleaning",
    filename: str = "cleaned_data.csv",
    **kwargs,
) -> pd.DataFrame:
    """加载预处理后的数据文件。

    Parameters
    ----------
    chapter : str
        章节目录名，如 'ch01_data_cleaning'。
    filename : str
        预处理后的文件名。
    **kwargs
        传递给 load_raw_data 的额外参数。

    Returns
    -------
    pd.DataFrame
        预处理后的数据表。
    """
    filepath = OUTPUT_BASE / chapter / filename
    return load_raw_data(filepath=filepath, **kwargs)
