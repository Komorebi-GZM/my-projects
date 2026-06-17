"""
标准输出产物管理器 (Skill-04)
确保输出目录存在，统一保存DataFrame和图片
"""

import os
import pandas as pd
import matplotlib.pyplot as plt


def ensure_dir(dirpath: str) -> str:
    """确保目录存在，不存在则创建

    Args:
        dirpath: 目录路径

    Returns:
        目录路径（确认存在）
    """
    os.makedirs(dirpath, exist_ok=True)
    return dirpath


def save_dataframe(df: pd.DataFrame, filename: str, output_dir: str, index: bool = True) -> str:
    """保存DataFrame为CSV

    Args:
        df: 要保存的DataFrame
        filename: 文件名（如 ch01_cleaned_data.csv）
        output_dir: 输出目录
        index: 是否保存索引

    Returns:
        完整文件路径
    """
    ensure_dir(output_dir)
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=index)
    print(f'  [保存] {filepath}')
    return filepath


def save_figure(fig, filename: str, output_dir: str, dpi: int = 150) -> str:
    """保存matplotlib图表

    Args:
        fig: matplotlib Figure对象
        filename: 文件名（如 ch02_daily_load_curve.png）
        output_dir: 输出目录
        dpi: 图片分辨率

    Returns:
        完整文件路径
    """
    ensure_dir(output_dir)
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print(f'  [保存] {filepath}')
    return filepath


def save_markdown(content: str, filename: str, output_dir: str) -> str:
    """保存Markdown文本

    Args:
        content: Markdown文本内容
        filename: 文件名
        output_dir: 输出目录

    Returns:
        完整文件路径
    """
    ensure_dir(output_dir)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  [保存] {filepath}')
    return filepath
