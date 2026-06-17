"""
通用数据加载器
支持加载 CSV / Excel / JSON 格式的原始数据和已处理数据

使用方式:
    from utils.data_loader import load_raw_data, load_processed_data, load_cleaned_data

    df = load_raw_data()                    # 加载原始数据（默认 TSV）
    df = load_processed_data(1, 'xxx.csv')  # 加载 ch01 输出
    df = load_cleaned_data()                # 便捷加载 ch01 清洗后数据
"""

import sys
import os
import logging

import pandas as pd

# 确保可以导入 config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import DATA_DIR, OUTPUT_BASE, RAW_DATA_FILE, CHAPTER_CONFIG

logger = logging.getLogger(__name__)

# === 编码回退列表 ===
_FALLBACK_ENCODINGS = ['utf-8', 'gbk', 'gb18030', 'latin1']


def _try_read_csv(filepath, encoding='utf-8', **kwargs):
    """尝试多种编码读取 CSV 文件"""
    encodings = [encoding] + [e for e in _FALLBACK_ENCODINGS if e != encoding]
    last_error = None
    for enc in encodings:
        try:
            df = pd.read_csv(filepath, encoding=enc, **kwargs)
            logger.info("成功读取 CSV: %s (编码: %s, 行数: %d)", filepath, enc, len(df))
            return df
        except UnicodeDecodeError as e:
            last_error = e
            logger.warning("编码 %s 读取失败: %s", enc, filepath)
            continue
    raise UnicodeDecodeError(
        last_error.encoding, last_error.object,
        last_error.start, last_error.end,
        f"所有编码尝试均失败，文件: {filepath}",
    )


def load_raw_data(filename=None, **kwargs):
    """加载原始数据文件

    默认加载 RAW_DATA_FILE，使用 TSV 格式（sep='\\t'）。
    支持自动编码回退。

    Args:
        filename: 文件名（相对于 data/），默认使用 RAW_DATA_FILE
        **kwargs: 传递给 pd.read_csv 的额外参数

    Returns:
        DataFrame
    """
    if filename is None:
        filepath = RAW_DATA_FILE
    else:
        filepath = os.path.join(DATA_DIR, filename)

    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"数据文件不存在: {filepath}")

    logger.info("正在加载数据: %s", filepath)

    # 默认 TSV 格式
    kwargs.setdefault('sep', '\t')
    kwargs.setdefault('keep_default_na', False)

    ext = os.path.splitext(filepath)[1].lower()
    if ext in ('.xlsx', '.xls'):
        df = pd.read_excel(filepath, **kwargs)
    elif ext == '.json':
        df = pd.read_json(filepath, **kwargs)
    else:
        encoding = kwargs.pop('encoding', 'utf-8')
        df = _try_read_csv(filepath, encoding=encoding, **kwargs)

    return df


def load_processed_data(chapter_key, filename, **kwargs):
    """从 outputs/chXX_xxx/ 加载已处理数据

    Args:
        chapter_key: 章节编号（int 或 str，如 1 或 'ch01'）
        filename: 文件名
        **kwargs: 传递给读取函数的额外参数

    Returns:
        DataFrame
    """
    if isinstance(chapter_key, int):
        ch_num = chapter_key
    else:
        ch_num = int(chapter_key.replace('ch', ''))

    if ch_num not in CHAPTER_CONFIG:
        raise ValueError(f"未注册的章节: {chapter_key}，可选: {list(CHAPTER_CONFIG.keys())}")

    dir_name = CHAPTER_CONFIG[ch_num]['dir_name']
    filepath = os.path.join(OUTPUT_BASE, dir_name, filename)

    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"已处理数据不存在: {filepath}")

    logger.info("正在加载已处理数据: %s (章节: ch%02d)", filepath, ch_num)

    ext = os.path.splitext(filepath)[1].lower()
    if ext in ('.xlsx', '.xls'):
        return pd.read_excel(filepath, **kwargs)
    elif ext == '.json':
        return pd.read_json(filepath, **kwargs)
    else:
        encoding = kwargs.pop('encoding', 'utf-8-sig')
        return _try_read_csv(filepath, encoding=encoding, **kwargs)


def load_cleaned_data(**kwargs):
    """便捷函数：加载 ch01 清洗后数据

    Returns:
        DataFrame
    """
    return load_processed_data(1, 'ch01_cleaned_online_gaming.csv', **kwargs)


def list_data_files(pattern='*'):
    """列出 data/ 目录下所有数据文件

    Args:
        pattern: 文件匹配模式

    Returns:
        list of Path
    """
    if not os.path.isdir(DATA_DIR):
        logger.warning("数据目录不存在: %s", DATA_DIR)
        return []
    files = sorted([f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))])
    if pattern != '*':
        from fnmatch import fnmatch
        files = [f for f in files if fnmatch(f, pattern)]
    return [os.path.join(DATA_DIR, f) for f in files]
