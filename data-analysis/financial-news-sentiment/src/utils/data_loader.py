"""数据加载器模块.

提供统一的数据加载接口，支持：
- 原始CSV数据加载
- 预处理后数据加载
- 数据类型自动推断
- 日期列自动解析

Example:
    >>> from src.utils.data_loader import load_raw_data
    >>> df = load_raw_data()
    >>> print(df.shape)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd

from src.utils.config import (
    CSV_ENCODING,
    CSV_ENCODING_FALLBACK,
    DATA_DIR,
    DATE_COLUMNS,
    OUTPUTS_DIR,
    RAW_DATA_FILENAME,
    setup_logging,
)

logger = logging.getLogger(__name__)


def _try_read_csv(
    filepath: Path,
    encoding: str = CSV_ENCODING,
    **kwargs,
) -> Optional[pd.DataFrame]:
    """尝试以指定编码读取CSV文件.

    Args:
        filepath: CSV文件路径.
        encoding: 文件编码，默认为 utf-8.
        **kwargs: 传递给 pd.read_csv 的额外参数.

    Returns:
        成功返回 DataFrame，失败返回 None.
    """
    try:
        df = pd.read_csv(filepath, encoding=encoding, **kwargs)
        logger.info("成功加载文件: %s (编码: %s, 行数: %d)",
                     filepath.name, encoding, len(df))
        return df
    except UnicodeDecodeError:
        logger.warning("编码 %s 失败，尝试备用编码 %s",
                       encoding, CSV_ENCODING_FALLBACK)
        return None
    except FileNotFoundError:
        logger.error("文件不存在: %s", filepath)
        return None
    except Exception as e:
        logger.error("读取文件失败: %s, 错误: %s", filepath, e)
        return None


def load_raw_data(
    nrows: Optional[int] = None,
    date_columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """加载原始CSV数据.

    自动处理文件名中的空格，支持编码回退，并尝试解析日期列.

    Args:
        nrows: 限制加载的行数，用于快速调试. None 表示加载全部.
        date_columns: 需要解析为日期的列名列表.
            None 表示使用配置中的 DATE_COLUMNS 自动检测.

    Returns:
        加载的 DataFrame.

    Raises:
        FileNotFoundError: 当原始数据文件不存在时抛出.

    Example:
        >>> df = load_raw_data(nrows=100)
        >>> print(df.columns.tolist())
    """
    filepath = DATA_DIR / RAW_DATA_FILENAME

    if not filepath.exists():
        raise FileNotFoundError(
            f"原始数据文件不存在: {filepath}\n"
            f"请将数据文件放置到 {DATA_DIR} 目录下."
        )

    # 构建读取参数
    read_kwargs: Dict = {}
    if nrows is not None:
        read_kwargs["nrows"] = nrows

    # 尝试主编码读取
    df = _try_read_csv(filepath, **read_kwargs)

    # 编码回退
    if df is None:
        df = _try_read_csv(filepath, encoding=CSV_ENCODING_FALLBACK, **read_kwargs)

    if df is None:
        raise RuntimeError(f"无法读取文件: {filepath}")

    # 日期列解析
    _parse_date_columns(df, date_columns)

    # 数据类型自动推断与优化
    _optimize_dtypes(df)

    logger.info("原始数据加载完成: %d 行 x %d 列", df.shape[0], df.shape[1])
    return df


def load_preprocessed(
    chapter_name: str = "ch01_data_preprocessing",
    filename: str = "cleaned_data.csv",
    nrows: Optional[int] = None,
) -> pd.DataFrame:
    """加载预处理后的数据.

    Args:
        chapter_name: 章节目录名，默认为 'ch01_data_preprocessing'.
        filename: 预处理后的文件名，默认为 'cleaned_data.csv'.
        nrows: 限制加载的行数. None 表示加载全部.

    Returns:
        加载的 DataFrame.

    Raises:
        FileNotFoundError: 当预处理文件不存在时抛出.

    Example:
        >>> df = load_preprocessed("ch01_data_preprocessing")
    """
    filepath = OUTPUTS_DIR / chapter_name / filename

    if not filepath.exists():
        raise FileNotFoundError(
            f"预处理数据文件不存在: {filepath}\n"
            f"请先运行 {chapter_name} 的预处理脚本."
        )

    read_kwargs: Dict = {}
    if nrows is not None:
        read_kwargs["nrows"] = nrows

    df = _try_read_csv(filepath, **read_kwargs)

    if df is None:
        df = _try_read_csv(filepath, encoding=CSV_ENCODING_FALLBACK, **read_kwargs)

    if df is None:
        raise RuntimeError(f"无法读取预处理文件: {filepath}")

    # 日期列解析
    _parse_date_columns(df)

    logger.info("预处理数据加载完成: %d 行 x %d 列",
                df.shape[0], df.shape[1])
    return df


def _parse_date_columns(
    df: pd.DataFrame,
    date_columns: Optional[List[str]] = None,
) -> None:
    """尝试将检测到的日期列转换为 datetime 类型.

    在 DataFrame 上原地修改.

    Args:
        df: 目标 DataFrame.
        date_columns: 指定日期列名. None 则自动检测.
    """
    if date_columns is None:
        date_columns = DATE_COLUMNS

    detected: List[str] = []
    for col in date_columns:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                valid_count = df[col].notna().sum()
                logger.debug("日期列 '%s' 解析成功，有效值: %d/%d",
                             col, valid_count, len(df))
                detected.append(col)
            except Exception as e:
                logger.warning("日期列 '%s' 解析失败: %s", col, e)

    if detected:
        logger.info("已解析日期列: %s", detected)


def _optimize_dtypes(df: pd.DataFrame) -> None:
    """自动优化 DataFrame 的内存占用.

    将 object 类型中低基数的列转为 category 类型，
    将整数列转为最小可表示类型.
    注意：categories 和 matched_keywords 列不转为 category，
    因为后续需要拆分为列表.

    在 DataFrame 上原地修改.

    Args:
        df: 目标 DataFrame.
    """
    # 不转为 category 的列（后续需要字符串操作）
    SKIP_CATEGORY_COLS = {"categories", "matched_keywords", "title", "description"}

    original_mem = df.memory_usage(deep=True).sum() / 1024**2

    for col in df.columns:
        col_type = df[col].dtype

        # 整数类型优化
        if col_type in ("int64", "int32"):
            df[col] = pd.to_numeric(df[col], downcast="integer")

        # 浮点类型优化
        elif col_type in ("float64", "float32"):
            df[col] = pd.to_numeric(df[col], downcast="float")

        # object -> category（基数低于50%时转换，排除文本列）
        elif col_type == "object" and col not in SKIP_CATEGORY_COLS:
            nunique = df[col].nunique()
            if nunique / len(df) < 0.5:
                df[col] = df[col].astype("category")

    optimized_mem = df.memory_usage(deep=True).sum() / 1024**2
    reduction = (1 - optimized_mem / original_mem) * 100 if original_mem > 0 else 0
    logger.info("内存优化: %.2f MB -> %.2f MB (节省 %.1f%%)",
                original_mem, optimized_mem, reduction)
