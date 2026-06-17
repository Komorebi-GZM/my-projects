"""
输出产物管理器模块 - 产品销售数据分析项目

本模块提供统一的输出文件管理接口，包括目录创建、DataFrame 保存、
图表保存和 Markdown 文件生成等功能。确保所有输出产物存放于
统一的目录结构中。
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    """
    确保目录存在，不存在则创建。

    支持多级目录创建（类似 mkdir -p）。

    Args:
        path: 目标目录路径。

    Returns:
        Path: 确认存在的目录 Path 对象。
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def save_dataframe(
    df: pd.DataFrame,
    file_path: str | Path,
    index: bool = False,
    encoding: str = "utf-8",
) -> Path:
    """
    保存 DataFrame 为 CSV 文件。

    自动创建目标目录（如果不存在），然后将 DataFrame 保存为 CSV。

    Args:
        df: 待保存的 DataFrame。
        file_path: 目标文件路径。
        index: 是否保存索引，默认为 False。
        encoding: 文件编码，默认为 utf-8。

    Returns:
        Path: 保存后的文件路径。
    """
    file_path = Path(file_path)
    ensure_dir(file_path.parent)
    df.to_csv(file_path, index=index, encoding=encoding)
    print(f"[输出] DataFrame 已保存: {file_path}")
    return file_path


def save_figure(
    fig: plt.Figure,
    file_path: str | Path,
    dpi: int = 150,
    bbox_inches: str = "tight",
) -> Path:
    """
    保存 matplotlib 图表为图片文件。

    自动创建目标目录（如果不存在），然后将 Figure 保存为图片。

    Args:
        fig: matplotlib Figure 对象。
        file_path: 目标文件路径。
        dpi: 图像分辨率，默认为 150。
        bbox_inches: 边距控制，默认为 "tight"。

    Returns:
        Path: 保存后的文件路径。
    """
    file_path = Path(file_path)
    ensure_dir(file_path.parent)
    fig.savefig(file_path, dpi=dpi, bbox_inches=bbox_inches)
    print(f"[输出] 图表已保存: {file_path}")
    return file_path


def save_markdown(
    content: str,
    file_path: str | Path,
    encoding: str = "utf-8",
) -> Path:
    """
    保存 Markdown 内容为 .md 文件。

    自动创建目标目录（如果不存在），然后将 Markdown 文本写入文件。

    Args:
        content: Markdown 格式的文本内容。
        file_path: 目标文件路径。
        encoding: 文件编码，默认为 utf-8。

    Returns:
        Path: 保存后的文件路径。
    """
    file_path = Path(file_path)
    ensure_dir(file_path.parent)
    with open(file_path, "w", encoding=encoding) as f:
        f.write(content)
    print(f"[输出] Markdown 文件已保存: {file_path}")
    return file_path
