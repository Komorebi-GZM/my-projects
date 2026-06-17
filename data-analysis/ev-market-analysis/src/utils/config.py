# -*- coding: utf-8 -*-
"""config.py - 全局配置模块

集中管理项目路径、实体配置、领域参数、分类映射和可视化样式。
所有模块通过导入本文件获取全局配置，确保参数一致性。
"""

from pathlib import Path

# ============================================================================
# 项目路径配置
# ============================================================================

# 项目根目录：从本文件位置向上推导
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"

# 原始数据文件
RAW_DATA_FILE = DATA_DIR / "ev_market_2026.csv"

# 输出根目录
OUTPUT_BASE = PROJECT_ROOT / "outputs"

# ============================================================================
# 项目元信息
# ============================================================================

PROJECT_NAME = "ev_market_analysis"
PROJECT_NAME_CN = "电动汽车市场数据分析"
PROJECT_SLUG = "ev_market_analysis"
PROJECT_DESCRIPTION = "电动汽车市场数据分析项目"
RAW_DATA_FILENAME = "ev_market_2026.csv"
DATA_FORMAT = "csv"
ENTITY_NAME = "品牌 (brand)"
PYTHON_VERSION = "3.10"
ENV_NAME = "py310"
ENV_TYPE = "conda"
DELIVERY_DATE = "2026-05-07"

# ============================================================================
# 实体配置 - 品牌
# ============================================================================

# 数据中实际存在的全部品牌（20个）
ENTITY_CONFIG = {
    "brands": [
        "Audi", "BMW", "BYD", "Fisker", "Ford",
        "GM/Chevrolet", "Honda", "Hyundai", "Kia", "Lucid",
        "Mercedes", "NIO", "Polestar", "Porsche", "Rivian",
        "Tesla", "Toyota", "Volkswagen", "Volvo", "Xiaomi",
    ],
    "brand_column": "brand",
    # 重点分析品牌（用户指定）
    "focus_brands": [
        "Tesla", "BYD", "Volkswagen", "Kia", "Hyundai",
        "Mercedes", "BMW", "Audi", "Toyota", "Ford",
        "GM/Chevrolet", "Fisker",
    ],
}

# ============================================================================
# 领域参数 - EV 相关
# ============================================================================

DOMAIN_PARAMS = {
    "price_unit": "USD",
    "range_unit": "miles",
    "battery_unit": "kWh",
    "charging_unit": "kW",
    "power_unit": "hp",
    "torque_unit": "Nm",
    "weight_unit": "kg",
    "speed_unit": "mph",
    "volume_unit": "cubic_ft",
    "year_range": (2022, 2026),
    "safety_rating_range": (1, 5),
    "autopilot_levels": {0: "无", 1: "基础", 2: "高级", 3: "完全"},
    "warranty_years_range": (1, 10),
    "customer_rating_range": (1.0, 5.0),
}

# ============================================================================
# 分类映射
# ============================================================================

# 市场细分映射
CATEGORY_MAP = {
    "market_segment": {
        "Budget": "经济型",
        "Mid-range": "中端",
        "Premium": "高端",
        "Luxury": "豪华",
    },
    # 驱动类型映射
    "drive_type": {
        "FWD": "前驱",
        "RWD": "后驱",
        "AWD": "全驱",
    },
    # 车身类型映射
    "body_type": {
        "Sedan": "轿车",
        "SUV": "SUV",
        "Truck": "皮卡",
        "Van": "MPV",
        "Hatchback": "两厢车",
        "Coupe": "轿跑",
    },
}

# ============================================================================
# 数据列配置（24列）
# ============================================================================

COLUMN_CONFIG = {
    # 标识列
    "id_columns": ["brand", "model", "year", "variant"],
    # 数值列
    "numeric_columns": [
        "price_usd", "battery_capacity_kwh", "range_miles",
        "charging_speed_kw", "acceleration_0_60_mph", "top_speed_mph",
        "horsepower", "torque_nm", "seating_capacity",
        "cargo_volume_cubic_ft", "weight_kg", "safety_rating",
        "autopilot_level", "annual_sales_units", "customer_rating",
        "warranty_years",
    ],
    # 分类列
    "categorical_columns": [
        "drive_type", "body_type", "country_of_origin", "market_segment",
    ],
    # 全部列（按原始顺序）
    "all_columns": [
        "brand", "model", "year", "variant", "price_usd",
        "battery_capacity_kwh", "range_miles", "charging_speed_kw",
        "acceleration_0_60_mph", "top_speed_mph", "horsepower",
        "torque_nm", "drive_type", "seating_capacity", "body_type",
        "cargo_volume_cubic_ft", "weight_kg", "safety_rating",
        "autopilot_level", "country_of_origin", "market_segment",
        "annual_sales_units", "customer_rating", "warranty_years",
    ],
}

# ============================================================================
# 可视化样式配置
# ============================================================================

PLT_STYLE = {
    # 全局样式
    "style": "seaborn-v0_8-whitegrid",
    "font_family": "sans-serif",
    "font_size": 12,
    "figure_dpi": 150,
    "figure_size": (12, 6),
    "save_format": "png",
    "save_dpi": 300,
    "save_bbox_inches": "tight",
    # 配色方案
    "color_palette": "Set2",
    "cmap_sequential": "YlOrRd",
    "cmap_diverging": "RdBu_r",
    "cmap_categorical": "Set2",
    # 品牌配色（重点品牌）
    "brand_colors": {
        "Tesla": "#E31937",
        "BYD": "#003DA5",
        "Volkswagen": "#001E50",
        "Kia": "#05141F",
        "Hyundai": "#002C5F",
        "Mercedes": "#333333",
        "BMW": "#0066B1",
        "Audi": "#BB0A30",
        "Toyota": "#EB0A1E",
        "Ford": "#003478",
        "GM/Chevrolet": "#C8102E",
        "Fisker": "#1A1A2E",
    },
}

# ============================================================================
# 章节配置
# ============================================================================

CHAPTER_CONFIG = {
    1: {'name_cn': '数据清洗', 'name_en': 'data_cleaning', 'dir_name': 'ch01_data_cleaning', 'status': 'completed'},
    2: {'name_cn': '市场格局分析', 'name_en': 'market_landscape', 'dir_name': 'ch02_market_landscape', 'status': 'completed'},
    3: {'name_cn': '价格机制分析', 'name_en': 'price_mechanism', 'dir_name': 'ch03_price_mechanism', 'status': 'completed'},
    4: {'name_cn': '技术趋势分析', 'name_en': 'tech_trends', 'dir_name': 'ch04_tech_trends', 'status': 'completed'},
    5: {'name_cn': '销量归因分析', 'name_en': 'sales_attribution', 'dir_name': 'ch05_sales_attribution', 'status': 'completed'},
    6: {'name_cn': '时序趋势分析', 'name_en': 'temporal_trends', 'dir_name': 'ch06_temporal_trends', 'status': 'completed'},
    7: {'name_cn': '竞品对标分析', 'name_en': 'competitive_benchmark', 'dir_name': 'ch07_competitive_benchmark', 'status': 'completed'},
    8: {'name_cn': '量化建模', 'name_en': 'quantitative_modeling', 'dir_name': 'ch08_quantitative_modeling', 'status': 'completed'},
    9: {'name_cn': '商业决策建议', 'name_en': 'business_recommendations', 'dir_name': 'ch09_business_recommendations', 'status': 'completed'},
}

# ============================================================================
# 批次配置
# ============================================================================

BATCH_CONFIG = {
    0: {'name': '数据基础', 'chapters': [1], 'parallel': False},
    1: {'name': '核心描述分析', 'chapters': [2, 3, 4], 'parallel': True},
    2: {'name': '深度诊断分析', 'chapters': [5, 6, 7], 'parallel': True},
    3: {'name': '建模与总结', 'chapters': [8, 9], 'parallel': False},
}

# ============================================================================
# 章节依赖关系
# ============================================================================

CHAPTER_DEPENDENCIES = {
    1: [],
    2: [1],
    3: [1],
    4: [1],
    5: [1],
    6: [1],
    7: [1],
    8: [1],
    9: [2, 3, 4, 5, 6, 7, 8],
}
