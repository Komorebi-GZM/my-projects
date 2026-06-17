"""
全局配置模块
项目：AB_Test_Analysis
描述：A/B测试点击率数据分析
"""

import os
from pathlib import Path

# ==================== 路径配置 ====================
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
TABLES_DIR = OUTPUTS_DIR / "tables"
DOCS_DIR = PROJECT_ROOT / "docs"

# ==================== 数据配置 ====================
RAW_DATA_FILENAME = "ab_test_click_data.csv"
DATA_FORMAT = "csv"

# ==================== 实体配置 ====================
ENTITY_NAME = "用户"
ENTITY_CONFIG = ["exp", "con"]  # 实验组/对照组

# ==================== 可视化样式 ====================
VISUAL_STYLE = {
    "font_family": "sans-serif",
    "font_size": 12,
    "figure_size": (10, 6),
    "dpi": 150,
    "color_palette": ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"],
    "save_format": "png",
}

# ==================== 章节配置 ====================
CHAPTERS = {
    "ch01": {
        "id": 1,
        "name_cn": "数据清洗",
        "name_en": "data_cleaning",
        "dir_suffix": "data_cleaning",
        "dependencies": [],
    },
    "ch02": {
        "id": 2,
        "name_cn": "核心指标计算与可视化",
        "name_en": "metrics_visualization",
        "dir_suffix": "metrics_visualization",
        "dependencies": ["ch01"],
    },
    "ch03": {
        "id": 3,
        "name_cn": "假设检验与效应量",
        "name_en": "hypothesis_testing",
        "dir_suffix": "hypothesis_testing",
        "dependencies": ["ch01"],
    },
    "ch04": {
        "id": 4,
        "name_cn": "时间趋势分析",
        "name_en": "time_trend_analysis",
        "dir_suffix": "time_trend_analysis",
        "dependencies": ["ch01"],
    },
    "ch05": {
        "id": 5,
        "name_cn": "结论与决策建议",
        "name_en": "conclusion_recommendation",
        "dir_suffix": "conclusion_recommendation",
        "dependencies": ["ch02", "ch03", "ch04"],
    },
}


class Config:
    """项目配置类"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.data_raw_dir = DATA_RAW_DIR
        self.data_processed_dir = DATA_PROCESSED_DIR
        self.outputs_dir = OUTPUTS_DIR
        self.figures_dir = FIGURES_DIR
        self.tables_dir = TABLES_DIR
        self.docs_dir = DOCS_DIR
        self.raw_data_filename = RAW_DATA_FILENAME
        self.data_format = DATA_FORMAT
        self.entity_name = ENTITY_NAME
        self.entity_config = ENTITY_CONFIG
        self.visual_style = VISUAL_STYLE
        self.chapters = CHAPTERS

        # 确保目录存在
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """确保所有必要目录存在"""
        for dir_path in [
            self.data_raw_dir,
            self.data_processed_dir,
            self.outputs_dir,
            self.figures_dir,
            self.tables_dir,
            self.docs_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_raw_data_path(self) -> Path:
        """获取原始数据文件路径"""
        return self.data_raw_dir / self.raw_data_filename
