"""全局配置模块.

本模块定义了金融新闻舆情分析项目的所有全局配置项，包括：
- 项目目录路径（动态计算，不硬编码）
- 原始数据文件名
- 图表样式与字体配置
- 章节配置列表
- 日志配置

Example:
    >>> from src.utils.config import PROJECT_ROOT, RAW_DATA_PATH
    >>> print(PROJECT_ROOT)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, List

# =============================================================================
# 项目基本信息
# =============================================================================
PROJECT_NAME: str = "financial_news_sentiment_analysis"
PROJECT_DESCRIPTION: str = "金融新闻舆情分析与市场预测"
PYTHON_VERSION: str = "3.10"
ENV_NAME: str = "py310"

# =============================================================================
# 路径配置（基于本文件位置动态计算）
# =============================================================================
# 本文件位于 src/utils/config.py，项目根目录为其上三级
_PROJECT_CONFIG_DIR: Path = Path(__file__).resolve().parent  # src/utils/
_SRC_DIR: Path = _PROJECT_CONFIG_DIR.parent  # src/
PROJECT_ROOT: Path = _SRC_DIR.parent  # 项目根目录

# 数据目录
DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_PATH: Path = DATA_DIR / "stock_news_2016 to 2026.csv"

# 输出目录
OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"

# 文档目录
DOCS_DIR: Path = PROJECT_ROOT / "docs"

# =============================================================================
# 原始数据配置
# =============================================================================
RAW_DATA_FILENAME: str = "stock_news_2016 to 2026.csv"
DATA_FORMAT: str = "csv"
ENTITY_NAME: str = "新闻"

# 日期列名称（根据实际数据调整）
DATE_COLUMNS: List[str] = ["date", "published_at", "created_at"]

# 编码配置
CSV_ENCODING: str = "utf-8"
CSV_ENCODING_FALLBACK: str = "latin-1"

# =============================================================================
# 图表配置
# =============================================================================
FIGURE_DPI: int = 150
FIGURE_DPI_HIGH: int = 300  # 高清图（用于论文/报告）
FIGURE_FORMAT: str = "png"  # 默认图表格式，可选 png / pdf / svg
FIGURE_SIZE_DEFAULT: tuple = (12, 6)
FIGURE_SIZE_WIDE: tuple = (16, 8)

# 字体配置（中文支持）
FONT_FAMILY: str = "sans-serif"
FONT_SANS_SERIF: List[str] = [
    "SimHei",
    "DejaVu Sans",
    "Arial",
    "Helvetica",
]
MATPLOTLIB_RC_PARAMS: Dict[str, object] = {
    "figure.dpi": FIGURE_DPI,
    "savefig.dpi": FIGURE_DPI_HIGH,
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.figsize": FIGURE_SIZE_DEFAULT,
    "font.family": FONT_FAMILY,
    "font.sans-serif": FONT_SANS_SERIF,
    "axes.unicode_minus": False,  # 正常显示负号
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
}

# =============================================================================
# 章节配置
# =============================================================================
CHAPTERS: List[Dict[str, str]] = [
    {
        "id": "ch01",
        "name": "ch01_data_preprocessing",
        "title": "数据预处理",
        "description": "数据清洗、类型转换、去重、异常值检测",
        "script": "preprocess.py",
        "notebook": "preprocess.ipynb",
    },
    {
        "id": "ch02",
        "name": "ch02_descriptive_stats",
        "title": "描述性统计分析",
        "description": "新闻数量趋势、分类分布、来源统计、关键词频率",
        "script": "analysis.py",
        "notebook": "analysis.ipynb",
    },
    {
        "id": "ch03",
        "name": "ch03_text_mining_sentiment",
        "title": "文本挖掘与情感分析",
        "description": "文本预处理、情感词典、BERT情感模型、情感时序分析",
        "script": "sentiment.py",
        "notebook": "sentiment.ipynb",
    },
    {
        "id": "ch04",
        "name": "ch04_feature_engineering",
        "title": "特征工程",
        "description": "情感特征、文本统计特征、时间特征、技术指标特征",
        "script": "features.py",
        "notebook": "features.ipynb",
    },
    {
        "id": "ch05",
        "name": "ch05_event_driven_strategy",
        "title": "事件驱动策略分析",
        "description": "事件信号生成、影响力评估、舆情扩散分析",
        "script": "strategy.py",
        "notebook": "strategy.ipynb",
    },
    {
        "id": "ch06",
        "name": "ch06_dashboard_summary",
        "title": "可视化看板与总结报告",
        "description": "交互式看板、综合分析报告",
        "script": "dashboard.py",
        "notebook": "dashboard.ipynb",
    },
]

# 章节ID到名称的映射
CHAPTER_ID_MAP: Dict[str, Dict[str, str]] = {
    ch["id"]: ch for ch in CHAPTERS
}

# =============================================================================
# 日志配置
# =============================================================================
LOG_LEVEL: int = logging.INFO
LOG_FORMAT: str = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

# 日志文件路径
LOG_DIR: Path = PROJECT_ROOT / "logs"


def setup_logging(
    name: str = PROJECT_NAME,
    level: int = LOG_LEVEL,
    log_to_file: bool = False,
) -> logging.Logger:
    """初始化日志记录器.

    Args:
        name: 日志记录器名称，默认为项目名称.
        level: 日志级别，默认为 INFO.
        log_to_file: 是否同时输出到文件，默认为 False.

    Returns:
        配置好的 Logger 实例.

    Example:
        >>> logger = setup_logging("my_module")
        >>> logger.info("初始化完成")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件输出（可选）
    if log_to_file:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            LOG_DIR / f"{name}.log",
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_chapter_output_dir(chapter_name: str) -> Path:
    """获取指定章节的输出目录路径.

    Args:
        chapter_name: 章节目录名，如 'ch01_data_preprocessing'.

    Returns:
        对应章节的输出目录 Path 对象.
    """
    return OUTPUTS_DIR / chapter_name


def get_chapter_dir(chapter_name: str) -> Path:
    """获取指定章节的源代码目录路径.

    Args:
        chapter_name: 章节目录名，如 'ch01_data_preprocessing'.

    Returns:
        对应章节的源代码目录 Path 对象.
    """
    return _SRC_DIR / chapter_name
