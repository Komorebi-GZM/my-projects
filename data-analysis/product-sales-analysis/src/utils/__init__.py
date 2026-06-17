"""
通用工具模块包 - 产品销售数据分析项目

本包导出所有工具子模块，提供统一的数据分析工具接口。
"""

from .config import (
    PROJECT_ROOT,
    DATA_DIR,
    OUTPUT_BASE,
    SRC_DIR,
    DOCS_DIR,
    RAW_DATA_FILENAME,
    RAW_DATA_PATH,
    CATEGORY_LIST,
    CITY_LIST,
    PLT_CONFIG,
    CHAPTERS,
    CHAPTER_NAMES_CN,
    CHAPTER_DIR_SUFFIX,
)

from .data_loader import load_raw_data, load_preprocessed
from .visualizer import (
    plot_category_sales,
    plot_city_sales,
    plot_time_series,
    plot_heatmap,
    plot_category_distribution,
)
from .metrics import (
    calc_total_sales,
    calc_avg_price,
    calc_category_summary,
    calc_city_summary,
    compare_models,
)
from .output_manager import ensure_dir, save_dataframe, save_figure, save_markdown
from .task_graph import TaskGraph, CHAPTER_DEPENDENCIES, CHAPTER_NAMES

__all__ = [
    # config
    "PROJECT_ROOT",
    "DATA_DIR",
    "OUTPUT_BASE",
    "SRC_DIR",
    "DOCS_DIR",
    "RAW_DATA_FILENAME",
    "RAW_DATA_PATH",
    "CATEGORY_LIST",
    "CITY_LIST",
    "PLT_CONFIG",
    "CHAPTERS",
    "CHAPTER_NAMES_CN",
    "CHAPTER_DIR_SUFFIX",
    # data_loader
    "load_raw_data",
    "load_preprocessed",
    # visualizer
    "plot_category_sales",
    "plot_city_sales",
    "plot_time_series",
    "plot_heatmap",
    "plot_category_distribution",
    # metrics
    "calc_total_sales",
    "calc_avg_price",
    "calc_category_summary",
    "calc_city_summary",
    "compare_models",
    # output_manager
    "ensure_dir",
    "save_dataframe",
    "save_figure",
    "save_markdown",
    # task_graph
    "TaskGraph",
    "CHAPTER_DEPENDENCIES",
    "CHAPTER_NAMES",
]
