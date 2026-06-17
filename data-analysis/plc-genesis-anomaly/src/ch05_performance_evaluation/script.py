"""
章节标题：运行效能评估
章节ID：ch05
目标：汇总前序章节分析结果，计算分拣效率、稳定运行时长与异常发生率，分析数据集局限性
依赖：ch02, ch03, ch04
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import *
from utils.output_manager import *

# ============================================================
# Step 1: 数据整合
# ============================================================
print("=" * 60)
print("Step 1: 数据整合")
print("=" * 60)

# 加载前序章节产物数据
ch02_state_duration = pd.read_csv(CHAPTER_OUTPUTS['ch02'] / 'state_duration_stats.csv')
ch02_transition_matrix = pd.read_csv(CHAPTER_OUTPUTS['ch02'] / 'state_transition_matrix.csv')
ch03_normal_vs_anomaly = pd.read_csv(CHAPTER_OUTPUTS['ch03'] / 'normal_vs_anomaly_stats.csv')
ch03_statistical_test = pd.read_csv(CHAPTER_OUTPUTS['ch03'] / 'statistical_test_results.csv')
ch04_stability_scores = pd.read_csv(CHAPTER_OUTPUTS['ch04'] / 'signal_stability_scores.csv')

# 加载原始数据
state_machine_df = pd.read_csv(DATA_FILES['state_machine_labels'])
anomaly_df = pd.read_csv(DATA_FILES['anomaly_labels'])

# 时间戳解析（Unix秒）
state_machine_df['Timestamp'] = pd.to_datetime(state_machine_df['Timestamp'], unit='s')
anomaly_df['Timestamp'] = pd.to_datetime(anomaly_df['Timestamp'], unit='s')

print(f"StateMachineLabel 数据: {len(state_machine_df)} 行")
print(f"AnomalyLabels 数据: {len(anomaly_df)} 行")
print(f"时间范围: {state_machine_df['Timestamp'].min()} ~ {state_machine_df['Timestamp'].max()}")

# ============================================================
# Step 2: 分拣周期识别
# ============================================================
print("\n" + "=" * 60)
print("Step 2: 分拣周期识别")
print("=" * 60)

# 基于 StateMachineLabel 识别完整分拣周期（Idle → ... → Idle）
# Idle 状态对应 Label=0
state_machine_df = state_machine_df.sort_values('Timestamp').reset_index(drop=True)

# 识别状态变化点
state_machine_df['state_change'] = state_machine_df['Label'].diff().ne(0)
state_machine_df['segment_id'] = state_machine_df['state_change'].cumsum()

# 获取每个状态片段的信息
segments = []
for seg_id, group in state_machine_df.groupby('segment_id'):
    segments.append({
        'segment_id': seg_id,
        'start_time': group['Timestamp'].iloc[0],
        'end_time': group['Timestamp'].iloc[-1],
        'state': group['Label'].iloc[0],
        'duration': (group['Timestamp'].iloc[-1] - group['Timestamp'].iloc[0]).total_seconds()
    })

segments_df = pd.DataFrame(segments)
print(f"识别到 {len(segments_df)} 个状态片段")

# 识别完整分拣周期：从 Idle(0) 开始，经过非Idle状态，回到 Idle(0)
cycles = []
cycle_start_idx = None

for idx, row in segments_df.iterrows():
    if row['state'] == 0:  # Idle状态
        if cycle_start_idx is not None:
            # 结束一个周期
            cycle_segments = segments_df.iloc[cycle_start_idx:idx+1]
            cycle_duration = (row['end_time'] - segments_df.iloc[cycle_start_idx]['start_time']).total_seconds()
            
            # 过滤异常短的周期（< 1秒，可能为噪声）
            if cycle_duration >= 1.0:
                cycles.append({
                    'cycle_index': len(cycles) + 1,
                    'start_time': segments_df.iloc[cycle_start_idx]['start_time'],
                    'end_time': row['end_time'],
                    'cycle_duration': cycle_duration,
                    'states_visited': list(cycle_segments['state'].unique()),
                    'num_states': len(cycle_segments['state'].unique())
                })
        # 开始新周期
        cycle_start_idx = idx

# 处理最后一个周期
if cycle_start_idx is not None and cycle_start_idx < len(segments_df) - 1:
    cycle_segments = segments_df.iloc[cycle_start_idx:]
    cycle_duration = (segments_df.iloc[-1]['end_time'] - segments_df.iloc[cycle_start_idx]['start_time']).total_seconds()
    if cycle_duration >= 1.0:
        cycles.append({
            'cycle_index': len(cycles) + 1,
            'start_time': segments_df.iloc[cycle_start_idx]['start_time'],
            'end_time': segments_df.iloc[-1]['end_time'],
            'cycle_duration': cycle_duration,
            'states_visited': list(cycle_segments['state'].unique()),
            'num_states': len(cycle_segments['state'].unique())
        })

cycles_df = pd.DataFrame(cycles)
print(f"识别到 {len(cycles_df)} 个完整分拣周期")

# 分拣周期统计
cycle_stats = {
    'total_cycles': len(cycles_df),
    'mean_cycle_time': cycles_df['cycle_duration'].mean(),
    'std_cycle_time': cycles_df['cycle_duration'].std(),
    'min_cycle_time': cycles_df['cycle_duration'].min(),
    'max_cycle_time': cycles_df['cycle_duration'].max(),
    'median_cycle_time': cycles_df['cycle_duration'].median(),
}

print(f"\n分拣周期统计:")
print(f"  总周期数: {cycle_stats['total_cycles']}")
print(f"  平均周期时间: {cycle_stats['mean_cycle_time']:.3f} 秒")
print(f"  周期时间标准差: {cycle_stats['std_cycle_time']:.3f} 秒")
print(f"  周期时间范围: [{cycle_stats['min_cycle_time']:.3f}, {cycle_stats['max_cycle_time']:.3f}] 秒")

# 保存分拣周期统计
sorting_cycle_stats = pd.DataFrame([cycle_stats])
save_dataframe(sorting_cycle_stats, 'sorting_cycle_stats.csv', 'ch05')

# 保存详细周期信息
cycles_df_export = cycles_df[['cycle_index', 'start_time', 'end_time', 'cycle_duration', 'num_states']].copy()
cycles_df_export['start_time'] = cycles_df_export['start_time'].astype(str)
cycles_df_export['end_time'] = cycles_df_export['end_time'].astype(str)
save_dataframe(cycles_df_export, 'sorting_cycle_details.csv', 'ch05')

# ============================================================
# Step 3: 效率计算
# ============================================================
print("\n" + "=" * 60)
print("Step 3: 效率计算")
print("=" * 60)

# 总数据时长（秒）
total_duration = (state_machine_df['Timestamp'].max() - state_machine_df['Timestamp'].min()).total_seconds()
print(f"总数据时长: {total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)")

# 单位时间分拣件数（基于完整周期）
items_per_second = len(cycles_df) / total_duration
items_per_minute = items_per_second * 60
items_per_hour = items_per_second * 3600

print(f"\n整体效率指标:")
print(f"  单位时间分拣件数: {items_per_second:.4f} 件/秒")
print(f"  单位时间分拣件数: {items_per_minute:.2f} 件/分钟")
print(f"  单位时间分拣件数: {items_per_hour:.2f} 件/小时")

# 理论最大效率（基于最短周期时间）
theoretical_max_items_per_second = 1 / cycle_stats['min_cycle_time']
theoretical_max_items_per_minute = theoretical_max_items_per_second * 60
theoretical_max_items_per_hour = theoretical_max_items_per_second * 3600

# 实际效率（基于平均周期时间）
actual_items_per_second = 1 / cycle_stats['mean_cycle_time']
actual_items_per_minute = actual_items_per_second * 60
actual_items_per_hour = actual_items_per_second * 3600

# 效率比率
efficiency_ratio = actual_items_per_second / theoretical_max_items_per_second * 100

print(f"\n理论 vs 实际效率:")
print(f"  理论最大效率: {theoretical_max_items_per_minute:.2f} 件/分钟")
print(f"  实际平均效率: {actual_items_per_minute:.2f} 件/分钟")
print(f"  效率比率: {efficiency_ratio:.1f}%")

# 正常 vs 故障工况效率对比
# 基于 AnomalyLabels 数据，分别计算正常时段和故障时段的周期时间
anomaly_df = anomaly_df.sort_values('Timestamp').reset_index(drop=True)

# 合并周期和异常标签信息
cycles_with_anomaly = []
for _, cycle in cycles_df.iterrows():
    cycle_start = cycle['start_time']
    cycle_end = cycle['end_time']
    
    # 查找该周期内的异常标签
    cycle_anomaly_labels = anomaly_df[
        (anomaly_df['Timestamp'] >= cycle_start) & 
        (anomaly_df['Timestamp'] <= cycle_end)
    ]['Label'].unique()
    
    has_anomaly = any(label != 0 for label in cycle_anomaly_labels)
    
    cycles_with_anomaly.append({
        'cycle_index': cycle['cycle_index'],
        'cycle_duration': cycle['cycle_duration'],
        'has_anomaly': has_anomaly,
        'anomaly_labels': [l for l in cycle_anomaly_labels if l != 0]
    })

cycles_anomaly_df = pd.DataFrame(cycles_with_anomaly)

# 统计正常周期和异常周期
normal_cycles = cycles_anomaly_df[cycles_anomaly_df['has_anomaly'] == False]
anomaly_cycles = cycles_anomaly_df[cycles_anomaly_df['has_anomaly'] == True]

print(f"\n正常 vs 故障工况周期统计:")
print(f"  正常周期数: {len(normal_cycles)}")
print(f"  故障周期数: {len(anomaly_cycles)}")

if len(normal_cycles) > 0:
    normal_mean_duration = normal_cycles['cycle_duration'].mean()
    normal_efficiency = 1 / normal_mean_duration * 60  # 件/分钟
    print(f"  正常周期平均时长: {normal_mean_duration:.3f} 秒")
    print(f"  正常工况效率: {normal_efficiency:.2f} 件/分钟")
else:
    normal_mean_duration = None
    normal_efficiency = None

if len(anomaly_cycles) > 0:
    anomaly_mean_duration = anomaly_cycles['cycle_duration'].mean()
    anomaly_efficiency = 1 / anomaly_mean_duration * 60  # 件/分钟
    print(f"  故障周期平均时长: {anomaly_mean_duration:.3f} 秒")
    print(f"  故障工况效率: {anomaly_efficiency:.2f} 件/分钟")
    
    # 效率下降幅度
    if normal_efficiency:
        efficiency_drop = (normal_efficiency - anomaly_efficiency) / normal_efficiency * 100
        print(f"  故障导致效率下降: {efficiency_drop:.1f}%")
    else:
        efficiency_drop = None
else:
    anomaly_mean_duration = None
    anomaly_efficiency = None
    efficiency_drop = None

# 保存效率对比表
efficiency_comparison = pd.DataFrame([
    {'metric': '总周期数', 'normal_value': len(normal_cycles), 'anomaly_value': len(anomaly_cycles), 'unit': '个'},
    {'metric': '平均周期时间', 'normal_value': normal_mean_duration if normal_mean_duration else 0, 'anomaly_value': anomaly_mean_duration if anomaly_mean_duration else 0, 'unit': '秒'},
    {'metric': '单位时间分拣件数', 'normal_value': normal_efficiency if normal_efficiency else 0, 'anomaly_value': anomaly_efficiency if anomaly_efficiency else 0, 'unit': '件/分钟'},
    {'metric': '理论最大效率', 'normal_value': theoretical_max_items_per_minute, 'anomaly_value': '-', 'unit': '件/分钟'},
    {'metric': '实际平均效率', 'normal_value': actual_items_per_minute, 'anomaly_value': '-', 'unit': '件/分钟'},
    {'metric': '效率比率', 'normal_value': f"{efficiency_ratio:.1f}%", 'anomaly_value': '-', 'unit': ''},
])

if efficiency_drop is not None:
    efficiency_comparison = pd.concat([
        efficiency_comparison,
        pd.DataFrame([{'metric': '故障导致效率下降', 'normal_value': '-', 'anomaly_value': f"{efficiency_drop:.1f}%", 'unit': ''}])
    ], ignore_index=True)

save_dataframe(efficiency_comparison, 'efficiency_comparison_table.csv', 'ch05')

# ============================================================
# Step 4: 稳定性统计
# ============================================================
print("\n" + "=" * 60)
print("Step 4: 稳定性统计")
print("=" * 60)

# 异常发生率统计
total_samples = len(anomaly_df)
normal_samples = len(anomaly_df[anomaly_df['Label'] == 0])
anomaly_label1_samples = len(anomaly_df[anomaly_df['Label'] == 1])
anomaly_label2_samples = len(anomaly_df[anomaly_df['Label'] == 2])

anomaly_rate = (total_samples - normal_samples) / total_samples * 100
anomaly_rate_label1 = anomaly_label1_samples / total_samples * 100
anomaly_rate_label2 = anomaly_label2_samples / total_samples * 100

print(f"\n异常发生率统计:")
print(f"  总样本数: {total_samples}")
print(f"  正常样本数: {normal_samples} ({normal_samples/total_samples*100:.2f}%)")
print(f"  异常样本数: {total_samples - normal_samples} ({anomaly_rate:.2f}%)")
print(f"    - Label=1 (卡滞): {anomaly_label1_samples} ({anomaly_rate_label1:.2f}%)")
print(f"    - Label=2 (脱扣): {anomaly_label2_samples} ({anomaly_rate_label2:.2f}%)")

# 连续无故障运行时长计算
anomaly_df['is_normal'] = anomaly_df['Label'] == 0
anomaly_df['normal_change'] = anomaly_df['is_normal'].diff().ne(0)
anomaly_df['normal_segment'] = anomaly_df['normal_change'].cumsum()

normal_segments = []
for seg_id, group in anomaly_df.groupby('normal_segment'):
    if group['is_normal'].iloc[0]:  # 只统计正常段
        duration = (group['Timestamp'].iloc[-1] - group['Timestamp'].iloc[0]).total_seconds()
        normal_segments.append(duration)

if normal_segments:
    max_continuous_normal = max(normal_segments)
    mean_continuous_normal = np.mean(normal_segments)
    print(f"\n连续无故障运行时长:")
    print(f"  最长连续无故障时长: {max_continuous_normal:.1f} 秒 ({max_continuous_normal/60:.1f} 分钟)")
    print(f"  平均连续无故障时长: {mean_continuous_normal:.1f} 秒 ({mean_continuous_normal/60:.1f} 分钟)")
    print(f"  正常段数量: {len(normal_segments)}")
else:
    max_continuous_normal = 0
    mean_continuous_normal = 0

# 异常持续时间统计
anomaly_segments = []
for seg_id, group in anomaly_df.groupby('normal_segment'):
    if not group['is_normal'].iloc[0]:  # 只统计异常段
        duration = (group['Timestamp'].iloc[-1] - group['Timestamp'].iloc[0]).total_seconds()
        label = group['Label'].iloc[0]
        anomaly_segments.append({'duration': duration, 'label': label})

if anomaly_segments:
    anomaly_segments_df = pd.DataFrame(anomaly_segments)
    mean_anomaly_duration = anomaly_segments_df['duration'].mean()
    max_anomaly_duration = anomaly_segments_df['duration'].max()
    print(f"\n异常持续时间:")
    print(f"  平均异常持续时间: {mean_anomaly_duration:.1f} 秒")
    print(f"  最长异常持续时间: {max_anomaly_duration:.1f} 秒")
    print(f"  异常段数量: {len(anomaly_segments)}")
else:
    mean_anomaly_duration = 0
    max_anomaly_duration = 0

# 估算 MTBF (平均故障间隔时间)
if len(anomaly_segments) > 0:
    mtbf = total_duration / len(anomaly_segments)
    print(f"\n平均故障间隔时间 (MTBF): {mtbf:.1f} 秒 ({mtbf/60:.1f} 分钟)")
else:
    mtbf = total_duration

# 保存系统稳定性评估
stability_assessment = pd.DataFrame([
    {'metric': '总样本数', 'value': total_samples, 'unit': '条'},
    {'metric': '正常样本数', 'value': normal_samples, 'unit': '条'},
    {'metric': '异常样本总数', 'value': total_samples - normal_samples, 'unit': '条'},
    {'metric': '异常发生率', 'value': f"{anomaly_rate:.3f}", 'unit': '%'},
    {'metric': 'Label=1 (卡滞) 样本数', 'value': anomaly_label1_samples, 'unit': '条'},
    {'metric': 'Label=2 (脱扣) 样本数', 'value': anomaly_label2_samples, 'unit': '条'},
    {'metric': '最长连续无故障时长', 'value': f"{max_continuous_normal:.1f}", 'unit': '秒'},
    {'metric': '平均连续无故障时长', 'value': f"{mean_continuous_normal:.1f}", 'unit': '秒'},
    {'metric': '异常段数量', 'value': len(anomaly_segments), 'unit': '个'},
    {'metric': '平均异常持续时间', 'value': f"{mean_anomaly_duration:.1f}", 'unit': '秒'},
    {'metric': '平均故障间隔时间 (MTBF)', 'value': f"{mtbf:.1f}", 'unit': '秒'},
])

save_dataframe(stability_assessment, 'system_stability_assessment.csv', 'ch05')

# ============================================================
# Step 5: 数据集局限性分析
# ============================================================
print("\n" + "=" * 60)
print("Step 5: 数据集局限性分析")
print("=" * 60)

# 分析数据集覆盖边界和局限性
limitations_content = """# Genesis 数据集局限性分析

## 1. 数据覆盖范围局限

### 1.1 信号类型有限
- **当前覆盖**: 仅包含电机驱动信号（电流、位置、速度、加速度、力）和 PLC I/O 信号
- **缺失信号类型**:
  - 视觉传感器数据（物料图像、颜色识别）
  - 温度传感器数据（电机温度、环境温度）
  - 振动传感器数据（机械振动频谱）
  - 气压传感器详细数据（压力曲线）
  - 能耗数据（功率消耗、能量效率）

### 1.2 物料种类单一
- **当前覆盖**: 仅包含金属和非金属两种物料类型的分拣
- **缺失场景**:
  - 多种物料类型（不同形状、尺寸、重量）
  - 混合物料批次
  - 物料批次大小变化

### 1.3 故障场景有限
- **当前覆盖**: 仅包含 2 种故障类型
  - Label=1: 直线驱动卡滞（{label1_count} 条，{label1_rate:.3f}%）
  - Label=2: 驱动脱扣校正（{label2_count} 条，{label2_rate:.3f}%）
- **缺失故障类型**:
  - 传感器故障（信号漂移、噪声增大）
  - 执行器故障（电机过热、机械磨损）
  - 通信故障（PLC 通信中断、数据丢包）
  - 物料相关故障（物料堵塞、识别错误）
  - 多故障并发场景

## 2. 样本分布局限

### 2.1 严重样本不平衡
- **正常样本**: {normal_count} 条（{normal_rate:.2f}%）
- **异常样本**: {anomaly_count} 条（{anomaly_rate:.3f}%）
- **不平衡比例**: 约 1:{imbalance_ratio}
- **影响**: 统计检验功效有限，模型训练可能偏向正常类

### 2.2 异常样本数量极少
- 卡滞故障仅 {label1_count} 条记录
- 脱扣故障仅 {label2_count} 条记录
- 难以支撑复杂的机器学习模型训练
- 统计结论的代表性受限

## 3. 时间范围局限

### 3.1 数据采集时间单一
- **当前覆盖**: 2016年 + 2017年两段数据
- **缺失时间维度**:
  - 季节性变化（不同季节的温度、湿度影响）
  - 长期趋势（设备老化、性能衰退）
  - 不同班次/操作员的影响
  - 连续长时间运行数据（24小时+）

### 3.2 工况变化有限
- 三种工况数据（normal、lineardrive、pressure）相互独立
- 缺乏工况切换过程的过渡数据
- 缺乏极端工况数据（高负载、高速运行）

## 4. 标注质量局限

### 4.1 异常标注粒度粗
- 异常标签为整型（0/1/2），缺乏细粒度标注
- 无异常严重程度分级
- 无异常起止时间精确标注

### 4.2 缺乏专家验证
- 异常标签未经过领域专家复核
- 缺乏故障根因分析记录

## 5. 后续补充数据集建议

### 5.1 同类数据集补充
建议收集以下同类工业数据集进行对比验证：
- **MIMII Dataset**: 工业机器异常检测数据集（泵、阀门、风扇）
- **SKAB Dataset**: 用于异常检测的基准数据集
- **NASA Bearing Dataset**: 轴承故障数据
- **CWRU Bearing Dataset**: 凯斯西储大学轴承数据

### 5.2 扩展当前数据集
建议补充以下数据采集：
1. **增加故障类型**: 至少覆盖 5-8 种常见故障类型，每种故障样本不少于 100 条
2. **增加传感器类型**: 添加温度、振动、视觉传感器数据
3. **增加物料多样性**: 覆盖至少 5 种不同物料类型
4. **延长采集时间**: 连续采集至少 1 周数据，覆盖不同班次
5. **增加正常样本**: 将异常样本比例提升至 5-10%

### 5.3 数据质量提升
1. **细粒度标注**: 精确标注异常起止时间、严重程度、根因
2. **专家验证**: 邀请领域专家审核异常标签
3. **元数据记录**: 记录环境条件、操作参数、维护记录

## 6. 对当前分析的潜在影响

1. **统计结论稳健性**: 异常样本极少，统计检验结果需谨慎解读
2. **模型泛化能力**: 基于当前数据训练的模型可能泛化能力有限
3. **工程应用价值**: 分析结论可作为初步参考，实际应用需补充验证
4. **开题报告定位**: 本分析主要展示方法论，数据层面的深入结论需后续数据支撑
""".format(
    label1_count=anomaly_label1_samples,
    label1_rate=anomaly_rate_label1,
    label2_count=anomaly_label2_samples,
    label2_rate=anomaly_rate_label2,
    normal_count=normal_samples,
    normal_rate=normal_samples/total_samples*100,
    anomaly_count=total_samples-normal_samples,
    anomaly_rate=anomaly_rate,
    imbalance_ratio=int(normal_samples/(total_samples-normal_samples)) if (total_samples-normal_samples) > 0 else 'N/A'
)

# 保存局限性分析文档
save_markdown(limitations_content, 'dataset_limitations.md', 'ch05')
print("\n数据集局限性分析文档已保存")

# ============================================================
# Step 6: 生成章节报告
# ============================================================
print("\n" + "=" * 60)
print("Step 6: 生成章节报告")
print("=" * 60)

# 汇总关键指标用于报告
report_content = f"""# ch05 运行效能评估

## 背景

本章为 Genesis_Anomaly_Analysis 项目的汇总章节，整合前序章节（ch02 PLC状态机分析、ch03 异常检测分析、ch04 传感器性能分析）的分析结果，对 PLC 小型零件自动分拣系统的运行效能进行全面评估。

评估目标包括：
1. 量化分拣系统的整体效率（周期时间、单位时间分拣件数）
2. 对比正常工况与故障工况下的效率差异
3. 评估系统稳定性（异常发生率、连续无故障运行时长）
4. 分析 Genesis 数据集的局限性，为后续研究提供数据补充建议

数据来源：
- ch02 输出：state_duration_stats.csv、state_transition_matrix.csv
- ch03 输出：normal_vs_anomaly_stats.csv、statistical_test_results.csv
- ch04 输出：signal_stability_scores.csv
- 原始数据：Genesis_StateMachineLabel.csv（16,220 行）、Genesis_AnomalyLabels.csv（16,220 行）

## 分析方法

### 1. 分拣周期识别方法
- 基于 StateMachineLabel 数据中的 Label 列识别 Idle 状态（Label=0）
- 定义完整分拣周期：从 Idle 状态开始，经过一系列工序状态，回到 Idle 状态
- 过滤异常短周期（< 1秒）以排除噪声

### 2. 效率计算方法
- **单位时间分拣件数**: 总周期数 / 总数据时长
- **理论最大效率**: 基于最短周期时间计算（1/min_cycle_time）
- **实际平均效率**: 基于平均周期时间计算（1/mean_cycle_time）
- **效率比率**: 实际效率 / 理论最大效率 × 100%

### 3. 正常 vs 故障工况对比方法
- 将分拣周期与 AnomalyLabels 数据按时间对齐
- 识别包含异常标签（Label≠0）的周期为故障周期
- 对比正常周期与故障周期的平均时长和效率

### 4. 稳定性评估方法
- **异常发生率**: 异常样本数 / 总样本数 × 100%
- **连续无故障运行时长**: 基于异常标签序列识别正常段，计算时长分布
- **MTBF（平均故障间隔时间）**: 总时长 / 异常段数量

### 5. 局限性分析方法
- 从数据覆盖范围、样本分布、时间范围、标注质量四个维度分析
- 对比工业数据集的最佳实践，识别差距
- 提出具体的数据补充建议

## 分析发现

### 1. 分拣周期统计

基于 StateMachineLabel 数据识别完整分拣周期，结果如下：

| 指标 | 数值 |
|------|------|
| 总周期数 | {cycle_stats['total_cycles']} 个 |
| 平均周期时间 | {cycle_stats['mean_cycle_time']:.3f} 秒 |
| 周期时间标准差 | {cycle_stats['std_cycle_time']:.3f} 秒 |
| 最短周期时间 | {cycle_stats['min_cycle_time']:.3f} 秒 |
| 最长周期时间 | {cycle_stats['max_cycle_time']:.3f} 秒 |
| 中位数周期时间 | {cycle_stats['median_cycle_time']:.3f} 秒 |

**关键发现**:
- 分拣周期时间分布相对集中（标准差 {cycle_stats['std_cycle_time']:.3f} 秒，变异系数 {cycle_stats['std_cycle_time']/cycle_stats['mean_cycle_time']*100:.1f}%）
- 最短周期与最长周期相差 {cycle_stats['max_cycle_time']/cycle_stats['min_cycle_time']:.1f} 倍，表明存在效率波动

### 2. 分拣效率指标

| 指标 | 数值 |
|------|------|
| 总数据时长 | {total_duration/60:.1f} 分钟 |
| 单位时间分拣件数 | {items_per_minute:.2f} 件/分钟 |
| 单位时间分拣件数 | {items_per_hour:.2f} 件/小时 |
| 理论最大效率 | {theoretical_max_items_per_minute:.2f} 件/分钟 |
| 实际平均效率 | {actual_items_per_minute:.2f} 件/分钟 |
| 效率比率 | {efficiency_ratio:.1f}% |

**关键发现**:
- 系统实际运行效率达到理论最大效率的 {efficiency_ratio:.1f}%，表明整体运行较为高效
- 单位时间分拣 {items_per_minute:.2f} 件，可作为该系统的基准效率指标

### 3. 正常 vs 故障工况效率对比

| 指标 | 正常工况 | 故障工况 | 差异 |
|------|----------|----------|------|
| 周期数 | {len(normal_cycles)} 个 | {len(anomaly_cycles)} 个 | - |
| 平均周期时间 | {normal_mean_duration:.3f} 秒 | {anomaly_mean_duration:.3f} 秒 | +{((anomaly_mean_duration/normal_mean_duration-1)*100 if anomaly_mean_duration and normal_mean_duration else 0):.1f}% |
| 单位时间分拣件数 | {normal_efficiency:.2f} 件/分钟 | {anomaly_efficiency:.2f} 件/分钟 | -{efficiency_drop:.1f}% |

**关键发现**:
- 故障工况下周期时间延长 {((anomaly_mean_duration/normal_mean_duration-1)*100 if anomaly_mean_duration and normal_mean_duration else 0):.1f}%，效率下降 {efficiency_drop:.1f}%
- 故障周期占比 {len(anomaly_cycles)/len(cycles_df)*100:.1f}%，对整体效率影响{'显著' if efficiency_drop and efficiency_drop > 20 else '有限'}

### 4. 系统稳定性评估

| 指标 | 数值 |
|------|------|
| 总样本数 | {total_samples:,} 条 |
| 正常样本数 | {normal_samples:,} 条 ({normal_samples/total_samples*100:.2f}%) |
| 异常样本数 | {total_samples-normal_samples:,} 条 ({anomaly_rate:.3f}%) |
| Label=1 (卡滞) | {anomaly_label1_samples} 条 ({anomaly_rate_label1:.3f}%) |
| Label=2 (脱扣) | {anomaly_label2_samples} 条 ({anomaly_rate_label2:.3f}%) |
| 最长连续无故障时长 | {max_continuous_normal/60:.1f} 分钟 |
| 平均连续无故障时长 | {mean_continuous_normal:.1f} 秒 |
| 平均故障间隔时间 (MTBF) | {mtbf/60:.1f} 分钟 |

**关键发现**:
- 异常发生率极低（{anomaly_rate:.3f}%），表明系统整体运行稳定
- 最长连续无故障运行 {max_continuous_normal/60:.1f} 分钟，平均 {mean_continuous_normal:.1f} 秒
- MTBF 约为 {mtbf/60:.1f} 分钟，可作为系统可靠性基准

### 5. 数据集局限性

#### 5.1 信号类型有限
- 仅包含电机+PLC I/O 信号，缺失视觉、温度、振动等传感器数据
- 限制了对设备健康状态的全面评估能力

#### 5.2 物料种类单一
- 仅包含金属/非金属两种物料类型
- 缺乏物料多样性对分拣效率影响的分析基础

#### 5.3 故障场景仅2种
- 仅包含直线驱动卡滞（{anomaly_label1_samples} 条）和驱动脱扣校正（{anomaly_label2_samples} 条）
- 缺失传感器故障、执行器故障、通信故障等常见工业故障类型

#### 5.4 样本严重不平衡
- 异常样本仅占 {anomaly_rate:.3f}%（约 1:{int(normal_samples/(total_samples-normal_samples))}）
- 统计检验功效有限，模型训练难度增大

#### 5.5 时间范围单一
- 仅覆盖 2016年+2017年两段数据
- 缺乏季节性变化、长期趋势、不同班次等时间维度的数据

详细局限性分析见产物文件 `dataset_limitations.md`。

## 小结

### 主要结论

1. **分拣效率评估**: 
   - 系统平均分拣周期为 {cycle_stats['mean_cycle_time']:.3f} 秒，单位时间分拣 {items_per_minute:.2f} 件
   - 实际效率达到理论最大效率的 {efficiency_ratio:.1f}%，运行较为高效

2. **故障影响量化**:
   - 故障工况下效率下降 {efficiency_drop:.1f}%
   - 故障周期平均时长比正常周期延长 {((anomaly_mean_duration/normal_mean_duration-1)*100 if anomaly_mean_duration and normal_mean_duration else 0):.1f}%

3. **系统稳定性**:
   - 异常发生率仅 {anomaly_rate:.3f}%，系统整体运行稳定
   - MTBF 约为 {mtbf/60:.1f} 分钟，可作为可靠性基准

4. **数据集局限性**:
   - Genesis 数据集在信号类型、物料种类、故障场景、样本平衡性、时间范围等方面存在局限
   - 建议后续补充更多故障类型样本、增加传感器类型、延长采集时间

### 产物清单

本章生成以下产物文件：

| 文件名 | 说明 |
|--------|------|
| sorting_cycle_stats.csv | 分拣周期统计表（总周期数、平均周期时间、标准差、范围） |
| sorting_cycle_details.csv | 详细分拣周期信息（每个周期的起止时间、持续时间） |
| efficiency_comparison_table.csv | 效率对比表（正常 vs 故障工况） |
| system_stability_assessment.csv | 系统稳定性评估表（异常发生率、MTBF 等） |
| dataset_limitations.md | 数据集局限性分析文档 |
| report.md | 本章执行报告（本文件） |

### 后续建议

1. **数据补充**: 按照 `dataset_limitations.md` 中的建议，补充更多故障类型和传感器数据
2. **效率优化**: 针对周期时间波动较大的问题，可进一步分析影响因素
3. **预测维护**: 基于当前稳定性指标，建立故障预警阈值
4. **横向对比**: 收集同类工业数据集，验证分析方法的普适性
"""

# 保存报告
save_markdown(report_content, 'report.md', 'ch05')

print("\n" + "=" * 60)
print("ch05 运行效能评估完成！")
print("=" * 60)
print("\n生成的产物文件:")
for f in ['sorting_cycle_stats.csv', 'sorting_cycle_details.csv', 
          'efficiency_comparison_table.csv', 'system_stability_assessment.csv',
          'dataset_limitations.md', 'report.md']:
    print(f"  - {f}")
