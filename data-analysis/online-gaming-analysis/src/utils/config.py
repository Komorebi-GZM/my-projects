"""
全局配置模块 - 在线小游戏数据分析
所有章节脚本共享的路径、参数、常量定义

环境要求:
  - Python 3.10
  - 依赖安装: pip install -r requirements.txt
"""

import os

# === 项目根目录（config.py 在 src/utils/ 下，需上溯两级） ===
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# === 项目标识 ===
PROJECT_NAME = 'online_gaming_analysis'
PROJECT_NAME_CN = '在线小游戏数据分析'

# === 虚拟环境配置 ===
PYTHON_VERSION = '3.10'

# === 路径配置 ===
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_FILE = os.path.join(DATA_DIR, 'online-gaming-14-04-26.csv')
OUTPUT_BASE = os.path.join(PROJECT_ROOT, 'outputs')
DOCS_DIR = os.path.join(PROJECT_ROOT, 'docs')

# === 数据格式 ===
# 注意: 文件扩展名为 .csv，但实际为 Tab 分隔（TSV）
DATA_FORMAT = 'tsv'

# === 实体配置 ===
ENTITY_CONFIG = {
    'poki': {
        'source': 'poki.com',
        'url_pattern': 'https://poki.com/en/g/',
    },
    'newgrounds': {
        'source': 'newgrounds.com',
        'url_pattern': 'https://www.newgrounds.com/portal/view/',
    },
}

# === 领域参数 ===
DOMAIN_PARAMS = {
    'expected_rows': 11406,
    'original_columns': 8,
    'cleaned_columns': 16,
    'tag_special_char_map': {
        "point 'n click": "point and click",
        "run 'n gun": "run and gun",
        "idle / incremental": "idle incremental",
        "casino & gambling": "casino gambling",
        "pet / buddy": "pet buddy",
        "tube / rail": "tube rail",
        "time (rts)": "time rts",
        ".io": "io",
    },
    'tag_synonym_map': {
        "puzzles": "puzzle",
    },
    'output_columns': [
        'game_id', 'name', 'url', 'source', 'likes', 'dislikes',
        'log_likes', 'log_dislikes', 'description', 'tags',
        'like_ratio', 'tag_count',
        'desc_missing', 'tags_missing', 'likes_is_zero', 'dislikes_is_zero'
    ],
}

# === 章节配置 ===
CHAPTER_CONFIG = {
    1: {
        'name_cn': '数据清洗',
        'name_en': 'data_cleaning',
        'dir_name': 'ch01_data_cleaning',
        'script': 'clean.py',
        'notebook': 'clean.ipynb',
    },
    2: {
        'name_cn': '热度分析',
        'name_en': 'popularity_analysis',
        'dir_name': 'ch02_popularity_analysis',
        'script': 'analysis.py',
        'notebook': 'analysis.ipynb',
    },
    3: {
        'name_cn': '标签分析',
        'name_en': 'tag_analysis',
        'dir_name': 'ch03_tag_analysis',
        'script': 'analysis.py',
        'notebook': 'analysis.ipynb',
    },
    4: {
        'name_cn': '跨平台对比',
        'name_en': 'cross_platform',
        'dir_name': 'ch04_cross_platform',
        'script': 'analysis.py',
        'notebook': 'analysis.ipynb',
    },
    5: {
        'name_cn': '可视化报告',
        'name_en': 'visualization',
        'dir_name': 'ch05_visualization',
        'script': 'report.py',
        'notebook': 'report.ipynb',
    },
}

# === 可视化全局样式 ===
PLT_STYLE = {
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'font.size': 12,
    'font.sans-serif': ['Arial Unicode MS', 'Heiti TC', 'PingFang HK', 'STHeiti', 'Apple LiGothic', 'Apple LiSung'],
    'axes.unicode_minus': False,
    'figure.figsize': (14, 5),
}

# === 模块加载时自动创建关键目录 ===
for _dir in [DATA_DIR, OUTPUT_BASE, DOCS_DIR]:
    os.makedirs(_dir, exist_ok=True)
