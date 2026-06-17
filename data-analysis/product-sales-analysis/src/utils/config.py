"""
全局配置模块 - 产品销售数据分析项目

本模块定义了项目中使用的所有全局配置常量，包括路径、类别列表、城市列表、
绘图配置等。所有模块应从本模块导入共享配置，避免硬编码。
"""

import os
from pathlib import Path

# ============================================================
# 项目根目录（自动检测）
# ============================================================
# 从当前文件（src/utils/config.py）向上两级定位项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ============================================================
# 路径常量
# ============================================================
DATA_DIR = PROJECT_ROOT / "data"                          # 原始数据目录
OUTPUT_BASE = PROJECT_ROOT / "outputs"                    # 输出产物根目录
SRC_DIR = PROJECT_ROOT / "src"                            # 源代码目录
DOCS_DIR = PROJECT_ROOT / "docs"                          # 文档目录

# ============================================================
# 数据配置
# ============================================================
RAW_DATA_FILENAME = "product_sales_dataset.csv"            # 原始数据文件名
RAW_DATA_PATH = DATA_DIR / RAW_DATA_FILENAME               # 原始数据完整路径

# ============================================================
# 业务实体配置
# ============================================================
# 产品类别列表
CATEGORY_LIST = ["Beauty", "Books", "Electronics", "Fashion", "Home", "Sports"]

# 城市列表
CITY_LIST = ["Islamabad", "Karachi", "Lahore", "Peshawar", "Quetta"]

# ============================================================
# 绘图全局配置
# ============================================================
PLT_CONFIG = {
    "dpi": 150,                # 图像分辨率
    "font_size": 12,           # 默认字体大小
    "figsize": (10, 6),        # 默认图像尺寸
    "font_family": "SimHei",   # 中文字体
    "save_format": "png",      # 默认保存格式
    "bbox_inches": "tight",    # 保存时去除空白边距
}

# ============================================================
# 章节配置
# ============================================================
CHAPTERS = [
    "ch01_data_cleaning",
    "ch02_descriptive_analysis",
    "ch03_sales_forecasting",
    "ch04_price_elasticity",
    "ch05_conclusions_and_recommendations",
]

# 章节中文名称映射
CHAPTER_NAMES_CN = {
    "ch01_data_cleaning": "数据清洗",
    "ch02_descriptive_analysis": "描述性统计与可视化",
    "ch03_sales_forecasting": "销售趋势预测",
    "ch04_price_elasticity": "价格弹性分析",
    "ch05_conclusions_and_recommendations": "结论与业务建议",
}

# 章节目录后缀映射
CHAPTER_DIR_SUFFIX = {
    "ch01_data_cleaning": "data_cleaning",
    "ch02_descriptive_analysis": "descriptive_analysis",
    "ch03_sales_forecasting": "sales_forecasting",
    "ch04_price_elasticity": "price_elasticity",
    "ch05_conclusions_and_recommendations": "conclusions_and_recommendations",
}

# 章节依赖关系
CHAPTER_DEPENDENCIES = {
    "ch01": [],
    "ch02": ["ch01"],
    "ch03": ["ch01", "ch02"],
    "ch04": ["ch01", "ch02"],
    "ch05": ["ch02", "ch03", "ch04"]
}
