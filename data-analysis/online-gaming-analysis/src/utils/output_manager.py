"""
通用输出产物管理器
确保输出目录存在，统一保存 DataFrame、图片和 Markdown 文件

使用方式:
    from utils.output_manager import get_chapter_dir, save_dataframe, save_figure, save_report

    output_dir = get_chapter_dir('ch01')
    save_dataframe(df, 'ch01_cleaned_data.csv', output_dir)
    save_figure(fig, 'ch01_distribution.png', output_dir)
    save_report(report, 'ch01_report.md', output_dir)
"""

import os
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def _get_output_base():
    """获取输出根目录（延迟导入，避免循环依赖）"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.config import OUTPUT_BASE
    return OUTPUT_BASE


def ensure_dir(dirpath):
    """确保目录存在，不存在则创建

    Args:
        dirpath: 目录路径

    Returns:
        目录路径
    """
    os.makedirs(dirpath, exist_ok=True)
    return dirpath


def get_chapter_dir(chapter_key):
    """获取章节输出目录的完整路径

    Args:
        chapter_key: 章节标识（如 'ch01' 或 1）

    Returns:
        完整目录路径
    """
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.config import CHAPTER_CONFIG

    if isinstance(chapter_key, int):
        ch_num = chapter_key
    else:
        ch_num = int(chapter_key.replace('ch', ''))

    if ch_num not in CHAPTER_CONFIG:
        raise ValueError(
            f"未注册的章节: {chapter_key}，"
            f"当前已注册: {list(CHAPTER_CONFIG.keys())}"
        )

    output_base = _get_output_base()
    dir_name = CHAPTER_CONFIG[ch_num]['dir_name']
    return ensure_dir(os.path.join(output_base, dir_name))


def save_dataframe(df, filename, output_dir, index=False, **kwargs):
    """保存 DataFrame 为 CSV

    Args:
        df: DataFrame
        filename: 文件名（建议 chXX_ 前缀）
        output_dir: 输出目录
        index: 是否保存索引，默认 False
        **kwargs: 传递给 to_csv 的额外参数

    Returns:
        完整文件路径
    """
    ensure_dir(output_dir)
    filepath = os.path.join(output_dir, filename)
    encoding = kwargs.pop('encoding', 'utf-8-sig')
    df.to_csv(filepath, index=index, encoding=encoding, **kwargs)
    logger.info("DataFrame 已保存: %s (%d 行)", filepath, len(df))
    return filepath


def save_figure(fig, filename, output_dir, dpi=150):
    """保存 matplotlib 图表

    Args:
        fig: matplotlib Figure 对象
        filename: 文件名（建议 chXX_ 前缀）
        output_dir: 输出目录
        dpi: 图片分辨率

    Returns:
        完整文件路径
    """
    import matplotlib.pyplot as plt
    ensure_dir(output_dir)
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    logger.info("图表已保存: %s", filepath)
    return filepath


def save_report(content, filename, output_dir, encoding='utf-8'):
    """保存 Markdown 报告

    Args:
        content: Markdown 文本
        filename: 文件名（建议 chXX_ 前缀）
        output_dir: 输出目录
        encoding: 文件编码

    Returns:
        完整文件路径
    """
    ensure_dir(output_dir)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding=encoding) as f:
        f.write(content)
    logger.info("报告已保存: %s", filepath)
    return filepath
