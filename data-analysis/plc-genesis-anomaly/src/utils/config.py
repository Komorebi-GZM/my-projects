"""
Genesis_Anomaly_Analysis - 全局配置模块
"""
import os
from pathlib import Path

# ============================================================
# 项目基本信息
# ============================================================
PROJECT_NAME = 'Genesis_Anomaly_Analysis'
PROJECT_NAME_CN = 'PLC小型零件自动分拣系统数据分析'
PROJECT_SLUG = 'Genesis_Anomaly_Analysis'

# ============================================================
# 路径配置
# ============================================================
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data' / '原始数据1'
OUTPUT_BASE = PROJECT_ROOT / 'outputs'
SRC_DIR = PROJECT_ROOT / 'src'

# ============================================================
# 数据文件配置
# ============================================================
DATA_FILES = {
    'anomaly_labels': DATA_DIR / 'Genesis_AnomalyLabels.csv',
    'state_machine_labels': DATA_DIR / 'Genesis_StateMachineLabel.csv',
    'lineardrive': DATA_DIR / 'Genesis_lineardrive.csv',
    'normal': DATA_DIR / 'Genesis_normal.csv',
    'pressure': DATA_DIR / 'Genesis_pressure.csv',
}

# ============================================================
# 实体配置（PLC状态）
# ============================================================
ENTITY_CONFIG = {
    'state_0': {'name': 'Idle', 'desc': '待机'},
    'state_1': {'name': 'Homing', 'desc': '回零'},
    'state_2': {'name': 'Pickup', 'desc': '取料'},
    'state_3': {'name': 'Inspection', 'desc': '检测'},
    'state_4': {'name': 'Sorting_Metal', 'desc': '金属分拣'},
    'state_5': {'name': 'Sorting_NonMetal', 'desc': '非金属分拣'},
    'state_6': {'name': 'Return', 'desc': '返回'},
    'state_7': {'name': 'Error', 'desc': '错误'},
    'state_8': {'name': 'Unknown', 'desc': '未知'},
}

# ============================================================
# 异常标签配置
# ============================================================
ANOMALY_LABELS = {
    0: {'name': 'Normal', 'desc': '正常运行', 'count': 16170},
    1: {'name': 'Jammed', 'desc': '直线驱动卡滞', 'count': 39},
    2: {'name': 'BreakFree', 'desc': '驱动脱扣校正', 'count': 11},
}

# ============================================================
# 信号列配置
# ============================================================
SIGNAL_COLUMNS = {
    'analog': [
        'MotorData.ActCurrent',
        'MotorData.ActPosition',
        'MotorData.ActSpeed',
        'MotorData.IsAcceleration',
        'MotorData.IsForce',
    ],
    'digital': [
        'MotorData.Motor_Pos1reached',
        'MotorData.Motor_Pos2reached',
        'MotorData.Motor_Pos3reached',
        'MotorData.Motor_Pos4reached',
        'NVL_Recv_Ind.GL_Metall',
        'NVL_Recv_Ind.GL_NonMetall',
        'NVL_Recv_Storage.GL_I_ProcessStarted',
        'NVL_Recv_Storage.GL_I_Slider_IN',
        'NVL_Recv_Storage.GL_I_Slider_OUT',
        'NVL_Recv_Storage.GL_LightBarrier',
        'NVL_Send_Storage.ActivateStorage',
        'PLC_PRG.Gripper',
        'PLC_PRG.MaterialIsMetal',
    ],
    'setpoint': [
        'MotorData.SetAcceleration',
        'MotorData.SetCurrent',
        'MotorData.SetForce',
        'MotorData.SetSpeed',
    ],
    'timing': [
        'NVL_Recv_Storage.GL_X_TimeSlideIn',
        'NVL_Recv_Storage.GL_X_TimeSlideOut',
    ]
}

# ============================================================
# 章节输出目录配置
# ============================================================
CHAPTER_OUTPUTS = {
    'ch01': OUTPUT_BASE / 'ch01_data_overview_and_cleaning',
    'ch02': OUTPUT_BASE / 'ch02_plc_state_machine_analysis',
    'ch03': OUTPUT_BASE / 'ch03_anomaly_detection_analysis',
    'ch04': OUTPUT_BASE / 'ch04_sensor_performance_analysis',
    'ch05': OUTPUT_BASE / 'ch05_performance_evaluation',
}

# ============================================================
# 可视化配置
# ============================================================
PLT_CONFIG = {
    'dpi': 150,
    'font_size': 10,
    'figsize': (12, 6),
    'style': 'seaborn-v0_8-whitegrid',
}

# ============================================================
# 分析参数配置
# ============================================================
ANALYSIS_PARAMS = {
    'sampling_interval_ms': 50,  # 采样间隔约 50ms
    'outlier_threshold': 3,       # 异常值阈值（3sigma）
    'rolling_window': 100,        # 滑动窗口大小
    'significance_level': 0.05,   # 统计显著性水平
}

# ============================================================
# 辅助函数
# ============================================================
def get_chapter_output_dir(chapter_id: str) -> Path:
    """获取章节输出目录"""
    return CHAPTER_OUTPUTS.get(chapter_id, OUTPUT_BASE / chapter_id)


def ensure_output_dir(chapter_id: str) -> Path:
    """确保章节输出目录存在"""
    output_dir = get_chapter_output_dir(chapter_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'figures').mkdir(exist_ok=True)
    return output_dir
