"""
数据加载器模块 - 产品销售数据分析项目

本模块提供统一的数据加载接口，支持加载原始 CSV 数据和各章节预处理后的数据。
所有数据加载操作均通过本模块完成，确保编码和路径的一致性。
"""

import pandas as pd
from pathlib import Path

from .config import RAW_DATA_PATH, OUTPUT_BASE, CHAPTER_DIR_SUFFIX


def load_raw_data() -> pd.DataFrame:
    """
    加载原始 CSV 数据。

    从 data/ 目录读取 product_sales_dataset.csv 文件，
    返回 pandas DataFrame 对象。

    Returns:
        pd.DataFrame: 包含原始产品销售数据的 DataFrame。

    Raises:
        FileNotFoundError: 当原始数据文件不存在时抛出。
        pd.errors.EmptyDataError: 当数据文件为空时抛出。
    """
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"原始数据文件不存在: {RAW_DATA_PATH}")

    df = pd.read_csv(RAW_DATA_PATH, encoding="utf-8")
    print(f"[数据加载] 成功加载原始数据: {RAW_DATA_PATH}")
    print(f"[数据加载] 数据形状: {df.shape[0]} 行 x {df.shape[1]} 列")
    return df


def load_preprocessed(chapter: str, entity: str = "product") -> pd.DataFrame:
    """
    加载指定章节预处理后的数据。

    根据章节名称和实体名称，从 outputs/ 对应目录中加载
    预处理后的 CSV 文件。

    Args:
        chapter: 章节标识符，例如 "ch01_data_cleaning"。
        entity: 实体名称，默认为 "product"。

    Returns:
        pd.DataFrame: 预处理后的数据 DataFrame。

    Raises:
        FileNotFoundError: 当预处理数据文件不存在时抛出。
    """
    dir_suffix = CHAPTER_DIR_SUFFIX.get(chapter, chapter)
    file_path = OUTPUT_BASE / dir_suffix / f"{entity}_preprocessed.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"预处理数据文件不存在: {file_path}")

    df = pd.read_csv(file_path, encoding="utf-8")
    print(f"[数据加载] 成功加载预处理数据: {file_path}")
    print(f"[数据加载] 数据形状: {df.shape[0]} 行 x {df.shape[1]} 列")
    return df
