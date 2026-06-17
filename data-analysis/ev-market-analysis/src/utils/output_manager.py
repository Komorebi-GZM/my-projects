# -*- coding: utf-8 -*-
"""output_manager.py - 输出产物管理器

统一管理数据表、图表、Markdown 报告的保存逻辑，
确保输出目录自动创建和产物格式一致。
"""

from pathlib import Path
from typing import Optional, Union

import pandas as pd

from .config import OUTPUT_BASE, CHAPTER_CONFIG


def ensure_dir(path: Union[str, Path]) -> Path:
    """确保目录存在，不存在则自动创建。

    Parameters
    ----------
    path : str or Path
        目标目录路径。

    Returns
    -------
    Path
        确认存在的目录路径。
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_chapter_dir(chapter_key: str) -> Path:
    """获取章节输出目录的完整路径。

    Parameters
    ----------
    chapter_key : str
        章节标识（如 'ch01', 'ch02' 等）。

    Returns
    -------
    Path
        章节输出目录的完整路径。

    Raises
    ------
    ValueError
        章节标识未在 CHAPTER_CONFIG 中注册。
    """
    # 从 chapter_key 提取章节编号
    chapter_num = int(chapter_key.replace('ch', '').replace('_', '').lstrip('0') or '0')
    
    if chapter_num not in CHAPTER_CONFIG:
        raise ValueError(
            f"未注册的章节标识: {chapter_key}，"
            f"当前已注册: {list(CHAPTER_CONFIG.keys())}"
        )
    
    dir_name = CHAPTER_CONFIG[chapter_num]['dir_name']
    return ensure_dir(OUTPUT_BASE / dir_name)


def save_dataframe(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    index: bool = False,
    encoding: str = "utf-8",
    verbose: bool = True,
) -> Path:
    """保存 DataFrame 到文件（自动根据后缀选择格式）。

    Parameters
    ----------
    df : pd.DataFrame
        要保存的数据表。
    filepath : str or Path
        输出文件路径，支持 .csv / .xlsx / .parquet。
    index : bool
        是否保存索引列。
    encoding : str
        文件编码（仅对 CSV 有效）。
    verbose : bool
        是否打印保存信息。

    Returns
    -------
    Path
        保存后的文件路径。
    """
    filepath = Path(filepath)
    ensure_dir(filepath.parent)

    suffix = filepath.suffix.lower()
    if suffix == ".csv":
        df.to_csv(filepath, index=index, encoding=encoding)
    elif suffix == ".xlsx":
        df.to_excel(filepath, index=index, engine="openpyxl")
    elif suffix == ".parquet":
        df.to_parquet(filepath, index=index)
    else:
        raise ValueError(f"不支持的保存格式: {suffix}，仅支持 csv/xlsx/parquet")

    if verbose:
        print(f"[output_manager] 数据已保存: {filepath} ({df.shape[0]} 行 x {df.shape[1]} 列)")
    return filepath


def save_figure(
    fig,
    filepath: Union[str, Path],
    dpi: int = 300,
    bbox_inches: str = "tight",
    verbose: bool = True,
) -> Path:
    """保存 matplotlib Figure 对象到图片文件。

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        图表对象。
    filepath : str or Path
        输出图片路径，支持 .png / .jpg / .svg / .pdf。
    dpi : int
        图片分辨率。
    bbox_inches : str
        裁剪方式。
    verbose : bool
        是否打印保存信息。

    Returns
    -------
    Path
        保存后的文件路径。
    """
    filepath = Path(filepath)
    ensure_dir(filepath.parent)

    fig.savefig(filepath, dpi=dpi, bbox_inches=bbox_inches)

    if verbose:
        print(f"[output_manager] 图表已保存: {filepath}")
    return filepath


def save_markdown(
    content: str,
    filepath: Union[str, Path],
    encoding: str = "utf-8",
    verbose: bool = True,
) -> Path:
    """保存 Markdown 文本到文件。

    Parameters
    ----------
    content : str
        Markdown 文本内容。
    filepath : str or Path
        输出文件路径。
    encoding : str
        文件编码。
    verbose : bool
        是否打印保存信息。

    Returns
    -------
    Path
        保存后的文件路径。
    """
    filepath = Path(filepath)
    ensure_dir(filepath.parent)

    filepath.write_text(content, encoding=encoding)

    if verbose:
        print(f"[output_manager] Markdown 已保存: {filepath}")
    return filepath
