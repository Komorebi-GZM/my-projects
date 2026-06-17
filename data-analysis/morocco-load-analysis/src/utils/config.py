"""
全局配置模块 - 摩洛哥电力负荷分析项目
所有章节脚本共享的路径、参数、常量定义

环境要求:
  - Python 3.10 (本地 conda 虚拟环境 py310)
  - 激活方式: conda activate py310
  - 依赖安装: pip install -r requirements.txt

脚本规范:
  - 每个章节提供两种脚本:
    1. src/chXX_xxx/preprocess.py  — 可直接运行的 .py 脚本
    2. src/chXX_xxx/preprocess.ipynb — Jupyter Notebook 交互式脚本（学习用）
  - 运行 .py 脚本: cd Morocco_Load_Analysis && python src/chXX_xxx/preprocess.py
  - 运行 .ipynb: 在 Jupyter 中打开，确保 kernel 为 py310
"""

import os

# === 项目根目录（config.py 在 src/utils/ 下，需上溯两级） ===
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# === 虚拟环境配置（使用本地 conda 环境） ===
VENV_PYTHON = os.path.expanduser('~/anaconda3/envs/py310/bin/python')
PYTHON_VERSION = '3.10'

# === 路径配置 ===
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_FILE = os.path.join(DATA_DIR, 'Data Morocco.xlsx')
OUTPUT_BASE = os.path.join(PROJECT_ROOT, 'outputs')

# === 城市配置 ===
CITIES = {
    'Laayoune':    {'sheet': 'Laayoune',    'sampling': '10min', 'unit': 'A',  'zones': 5},
    'Boujdour':    {'sheet': 'Boujdour',    'sampling': '10min', 'unit': 'A',  'zones': 3},
    'Foum eloued': {'sheet': 'Foum eloued', 'sampling': '10min', 'unit': 'A',  'zones': 7},
    'Marrakech':   {'sheet': 'Marrakech',   'sampling': '30min', 'unit': 'kW', 'zones': 2},
}

# === 量纲转换参数 ===
VOLTAGE = 220          # 市电标准电压 V
POWER_FACTOR = 0.9     # 平均功率因数

# === 季节映射（北半球） ===
SEASON_MAP = {
    12: 'Winter', 1: 'Winter', 2: 'Winter',
    3: 'Spring',  4: 'Spring',  5: 'Spring',
    6: 'Summer',  7: 'Summer',  8: 'Summer',
    9: 'Autumn',  10: 'Autumn', 11: 'Autumn'
}

# === 可视化全局样式 ===
PLT_STYLE = {
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'font.size': 12,
    'axes.unicode_minus': False,
    'figure.figsize': (14, 5),
}
