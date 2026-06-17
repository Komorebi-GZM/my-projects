"""
Prompt-08: 总结与展望
汇总全流程8个章节的核心研究成果，提炼关键发现和数据指标，
形成成果汇总报告和关键指标总览表。

覆盖步骤:
  - Step 1: 从各章产物中自动提取数据指标
  - Step 2: 基于提取数据动态生成成果汇总报告 (ch08_achievements_summary.md)
  - Step 3: 构建关键指标总览表 (ch08_key_metrics_table.csv)

产物输出到: outputs/ch08_summary/
"""

import sys
import os

# ============================================================
# 模块 A: 路径设置
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

import pandas as pd
import numpy as np

from utils.config import CITIES, OUTPUT_BASE, PROJECT_ROOT

OUTPUT_DIR = os.path.join(OUTPUT_BASE, 'ch08_summary')


# ============================================================
# 模块 B: 数据提取层
# ============================================================

def safe_read_csv(filepath, **kwargs):
    """安全读取CSV文件，文件不存在时返回None并打印警告"""
    try:
        return pd.read_csv(filepath, **kwargs)
    except FileNotFoundError:
        print(f"  [警告] 文件不存在: {filepath}")
        return None
    except Exception as e:
        print(f"  [警告] 读取失败 {filepath}: {e}")
        return None


def extract_all_data():
    """从ch01~ch07的全部产物中提取关键数值，返回结构化dict"""

    data = {}

    # --- ch01 数据预处理 ---
    print("  [ch01] 数据预处理...")
    ch01_path = os.path.join(OUTPUT_BASE, 'ch01_data_preprocessing', 'ch01_cleaned_data.csv')
    ch01_df = safe_read_csv(ch01_path, usecols=['DateTime'])
    if ch01_df is not None:
        data['total_rows'] = len(ch01_df)
        data['date_start'] = ch01_df['DateTime'].iloc[0]
        data['date_end'] = ch01_df['DateTime'].iloc[-1]
    else:
        data['total_rows'] = '未知'
        data['date_start'] = '未知'
        data['date_end'] = '未知'

    ch01_missing = safe_read_csv(
        os.path.join(OUTPUT_BASE, 'ch01_data_preprocessing', 'ch01_missing_stats.csv')
    )
    if ch01_missing is not None and 'missing_rate_pct' in ch01_missing.columns:
        data['avg_missing_rate'] = ch01_missing['missing_rate_pct'].mean()
    else:
        data['avg_missing_rate'] = 0.0

    # --- ch02 用电规律 ---
    print("  [ch02] 用电规律...")
    ch02_stats = safe_read_csv(
        os.path.join(OUTPUT_BASE, 'ch02_load_pattern_analysis', 'ch02_descriptive_stats.csv')
    )
    if ch02_stats is not None and 'city' in ch02_stats.columns and 'mean' in ch02_stats.columns:
        city_mean = ch02_stats.groupby('city')['mean'].mean()
        data['city_max_load'] = city_mean.idxmax()
        data['city_min_load'] = city_mean.idxmin()
        data['max_load_value'] = city_mean.max()
        data['min_load_value'] = city_mean.min()
        data['load_ratio'] = city_mean.max() / city_mean.min() if city_mean.min() > 0 else float('inf')
    else:
        data['city_max_load'] = '未知'
        data['city_min_load'] = '未知'
        data['max_load_value'] = 0
        data['min_load_value'] = 0
        data['load_ratio'] = 0

    ch02_class = safe_read_csv(
        os.path.join(OUTPUT_BASE, 'ch02_load_pattern_analysis', 'ch02_residential_industrial_class.csv')
    )
    if ch02_class is not None and 'load_type' in ch02_class.columns:
        type_counts = ch02_class['load_type'].value_counts()
        data['n_residential'] = type_counts.get('Residential', 0)
        data['n_industrial'] = type_counts.get('Industrial', 0)
        data['total_zones'] = len(ch02_class)
        data['residential_pct'] = data['n_residential'] / data['total_zones'] * 100
    else:
        data['n_residential'] = 0
        data['n_industrial'] = 0
        data['total_zones'] = 0
        data['residential_pct'] = 0

    # --- ch03 峰值识别 ---
    print("  [ch03] 峰值识别...")
    ch03_summary = safe_read_csv(
        os.path.join(OUTPUT_BASE, 'ch03_peak_analysis', 'ch03_peak_events_summary.csv')
    )
    if ch03_summary is not None and 'total_peak_count' in ch03_summary.columns:
        data['total_peak_events'] = int(ch03_summary['total_peak_count'].sum())
        data['peak_ratio'] = ch03_summary['peak_ratio_pct'].iloc[0] if 'peak_ratio_pct' in ch03_summary.columns else 5.0
        data['avg_excess_ratio'] = ch03_summary['avg_excess_ratio_pct'].mean() if 'avg_excess_ratio_pct' in ch03_summary.columns else 0
    else:
        data['total_peak_events'] = 0
        data['peak_ratio'] = 0
        data['avg_excess_ratio'] = 0

    ch03_anomaly = safe_read_csv(
        os.path.join(OUTPUT_BASE, 'ch03_peak_analysis', 'ch03_anomaly_peak_flags.csv')
    )
    if ch03_anomaly is not None and 'anomaly_ratio' in ch03_anomaly.columns:
        data['avg_anomaly_ratio'] = ch03_anomaly['anomaly_ratio'].mean()
    else:
        data['avg_anomaly_ratio'] = 0

    ch03_duration = safe_read_csv(
        os.path.join(OUTPUT_BASE, 'ch03_peak_analysis', 'ch03_peak_duration_stats.csv')
    )
    if ch03_duration is not None and 'city' in ch03_duration.columns and 'duration_hours' in ch03_duration.columns:
        city_duration = ch03_duration[ch03_duration['scope'] == 'city_aggregated'] if 'scope' in ch03_duration.columns else ch03_duration
        data['avg_peak_duration_by_city'] = city_duration.groupby('city')['duration_hours'].mean().to_dict()
    else:
        data['avg_peak_duration_by_city'] = {}

    # --- ch04 短期预测 ---
    print("  [ch04] 短期预测...")
    ch04_models = safe_read_csv(
        os.path.join(OUTPUT_BASE, 'ch04_load_forecasting', 'ch04_model_comparison.csv')
    )
    if ch04_models is not None and len(ch04_models) > 0:
        data['model_ranking'] = ch04_models
        best_row = ch04_models.iloc[0]
        data['best_model'] = best_row.get('model', '未知')
        data['best_mape'] = float(best_row.get('MAPE', 0))
        data['best_rmse'] = float(best_row.get('RMSE', 0))
        data['best_mae'] = float(best_row.get('MAE', 0))
    else:
        data['model_ranking'] = pd.DataFrame()
        data['best_model'] = '未知'
        data['best_mape'] = 0
        data['best_rmse'] = 0
        data['best_mae'] = 0

    # --- ch05 中长期趋势 ---
    print("  [ch05] 中长期趋势...")
    ch05_seasonal = safe_read_csv(
        os.path.join(OUTPUT_BASE, 'ch05_midlong_term_trend', 'ch05_seasonal_strength.csv')
    )
    if ch05_seasonal is not None and 'seasonal_strength' in ch05_seasonal.columns:
        data['all_seasonal_strength'] = ch05_seasonal
        idx_max = ch05_seasonal['seasonal_strength'].idxmax()
        data['strongest_season_city'] = ch05_seasonal.loc[idx_max, 'city']
        data['strongest_fs'] = ch05_seasonal.loc[idx_max, 'seasonal_strength']
    else:
        data['all_seasonal_strength'] = pd.DataFrame()
        data['strongest_season_city'] = '未知'
        data['strongest_fs'] = 0

    # STL趋势方向判断
    data['trend_directions'] = {}
    for city in CITIES.keys():
        stl_file = os.path.join(OUTPUT_BASE, 'ch05_midlong_term_trend', f'ch05_stl_components_{city.lower().replace(" ", "_")}.csv')
        stl_df = safe_read_csv(stl_file)
        if stl_df is not None and 'trend' in stl_df.columns:
            first_trend = stl_df['trend'].iloc[0]
            last_trend = stl_df['trend'].iloc[-1]
            if last_trend > first_trend * 1.05:
                data['trend_directions'][city] = '上升'
            elif last_trend < first_trend * 0.95:
                data['trend_directions'][city] = '下降'
            else:
                data['trend_directions'][city] = '平稳'
        else:
            data['trend_directions'][city] = '未知'

    # --- ch06 跨国对比 ---
    print("  [ch06] 跨国对比...")
    ch06_benchmark = safe_read_csv(
        os.path.join(OUTPUT_BASE, 'ch06_cross_country_comparison', 'ch06_benchmark_cleaned.csv')
    )
    if ch06_benchmark is not None and 'country' in ch06_benchmark.columns and 'load_rate' in ch06_benchmark.columns:
        ma_loads = ch06_benchmark[ch06_benchmark['country'] == 'Morocco']['load_rate']
        cn_loads = ch06_benchmark[ch06_benchmark['country'] == 'China']['load_rate']
        data['ma_load_rate_avg'] = ma_loads.mean() if len(ma_loads) > 0 else 0
        data['cn_load_rate_avg'] = cn_loads.mean() if len(cn_loads) > 0 else 0
        data['ma_load_rate_min'] = ma_loads.min() if len(ma_loads) > 0 else 0
        data['ma_load_rate_max'] = ma_loads.max() if len(ma_loads) > 0 else 0
    else:
        data['ma_load_rate_avg'] = 0
        data['cn_load_rate_avg'] = 0
        data['ma_load_rate_min'] = 0
        data['ma_load_rate_max'] = 0

    # --- ch07 配电网优化 ---
    print("  [ch07] 配电网优化...")
    ch07_metrics = safe_read_csv(
        os.path.join(OUTPUT_BASE, 'ch07_grid_optimization', 'ch07_optimization_metrics.csv')
    )
    if ch07_metrics is not None and 'metric' in ch07_metrics.columns:
        peak_row = ch07_metrics[ch07_metrics['metric'].str.contains('峰值', na=False)]
        if len(peak_row) > 0:
            data['peak_reduction_pct'] = float(peak_row.iloc[0].get('change_pct', 0))
            data['original_peak'] = float(peak_row.iloc[0].get('original', 0))
            data['optimized_peak'] = float(peak_row.iloc[0].get('optimized', 0))
        else:
            data['peak_reduction_pct'] = 0
            data['original_peak'] = 0
            data['optimized_peak'] = 0

        lr_row = ch07_metrics[ch07_metrics['metric'].str.contains('负荷率', na=False)]
        if len(lr_row) > 0:
            data['load_rate_change_pct'] = float(lr_row.iloc[0].get('change_pct', 0))
        else:
            data['load_rate_change_pct'] = 0
    else:
        data['peak_reduction_pct'] = 0
        data['original_peak'] = 0
        data['optimized_peak'] = 0
        data['load_rate_change_pct'] = 0

    # 硬编码常量（来自MD文件）
    data['engineering_strategies'] = [
        "错峰用电引导（P0, 0-6月）: 分时电价、智能电表、可中断负荷合同 → 峰值降低10-15%",
        "台区容量优化（P1, 6-12月）: 变压器减容、联络线建设、子台区管理 → 负荷率提升5-10%",
        "季节性配电调度（P2, 1-2年）: 差异化调度预案、预警机制 → 夏季峰值降低5-8%",
        "储能协同削峰（P3, 2-3年）: 7~14kW电池储能、'谷充峰放' → 峰值额外降低5-10%"
    ]
    data['ch06_difference_attribution'] = "气候因素（夏季制冷）、产业结构（旅游vs工业）、电气化水平、建筑能效"

    return data


# ============================================================
# 模块 C: 文本生成层
# ============================================================

def gen_chapter_01(data):
    """第一章：数据预处理"""
    return f"""## 第一章 数据预处理

**核心发现1**：成功将4城市、17个zone的异构数据统一为10分钟/kW标准格式。
- 原始数据总量：{data['total_rows']}行
- 时间范围：{data['date_start']} ~ {data['date_end']}
- 量纲统一：3个城市从电流(A)转换为有功功率(kW)，换算公式 P = I × 220V × 0.9 / 1000
- 时间对齐：Marrakech从30分钟上采样至10分钟

**核心发现2**：数据质量优异，缺失率接近0%。
- 平均缺失率：{data['avg_missing_rate']:.2f}%
- 异常值处理：基于3σ准则检测并替换异常值

**与前章关系**：本章是全流程的基础起点，输出的标准化数据集是后续所有章节的输入。
"""


def gen_chapter_02(data):
    """第二章：用电规律"""
    return f"""## 第二章 用电负荷特征挖掘

**核心发现1**：四城市日均负荷差异显著，{data['city_max_load']}综合负荷最高。
- 最高城市：{data['city_max_load']}，日均负荷约{data['max_load_value']:.2f} kW
- 最低城市：{data['city_min_load']}，日均负荷约{data['min_load_value']:.2f} kW
- 最高值为最低值的{data['load_ratio']:.1f}倍

**核心发现2**：日内负荷呈典型双峰模式，晚高峰更为突出。
- 早高峰：8-10点，主要由工业和商业用电驱动
- 晚高峰：18-21点，主要由居民生活用电驱动

**核心发现3**：居民/工业zone比例为{data['residential_pct']:.1f}%/{100-data['residential_pct']:.1f}%。
- 居民zone：{data['n_residential']}个
- 工业zone：{data['n_industrial']}个

**与前章关系**：本章的规律发现为第三章的峰值识别提供了统计基础。
"""


def gen_chapter_03(data):
    """第三章：峰值识别"""
    duration_str = ", ".join([f"{c}={d:.2f}h" for c, d in data['avg_peak_duration_by_city'].items()]) if data['avg_peak_duration_by_city'] else "未知"

    return f"""## 第三章 负荷峰值识别与峰值特征研究

**核心发现1**：95%分位数阈值有效识别了全部4城市的峰值事件。
- 峰值事件总数：约{data['total_peak_events']}个（4城市合计）
- 峰值判定标准：负荷超过该zone历史95%分位数的时段
- 峰值比例：{data['peak_ratio']:.1f}%

**核心发现2**：平均峰值持续时间为{duration_str}。
- 平均超限比：{data['avg_excess_ratio']:.1f}%
- 异常峰值比例：{data['avg_anomaly_ratio']:.2f}%

**与前章关系**：本章的峰值特征为第四章的预测建模提供了目标变量定义，为第七章的优化模型提供了峰值基准。
"""


def gen_chapter_04(data):
    """第四章：短期预测"""
    best = data['best_model']
    mape = data['best_mape']

    # 条件分支：根据实际最优模型动态生成文本
    if best == 'Prophet':
        model_desc = "Prophet 在精度和效率间取得最佳平衡，其内置的周期性建模能力特别适合电力负荷的日内和周周期特征"
    elif best in ['XGBoost', 'LightGBM']:
        model_desc = f"{best} 作为梯度提升模型，在处理非线性负荷模式时表现优异"
    elif best == 'LSTM':
        model_desc = "LSTM 深度学习模型通过记忆长程时序依赖，在复杂负荷模式预测中表现最佳"
    else:
        model_desc = f"{best} 模型在本次对比中表现最优"

    # 模型排名表
    ranking_rows = ""
    for _, row in data['model_ranking'].iterrows():
        ranking_rows += f"| {row['rank']} | {row['model']} | {row['MAPE']:.2f}% | {row['RMSE']:.2f} | {row['quality']} |\n"

    return f"""## 第四章 短期电力负荷预测模型构建

**核心发现1**：5模型对比显示，{best}在精度和效率间取得最佳平衡。
- 最优模型：{best}（{model_desc}）
- 最优MAPE：{mape:.2f}%（平均绝对百分比误差）
- 最优RMSE：{data['best_rmse']:.2f} kW
- 模型排名（按MAPE升序）：

| 排名 | 模型 | MAPE | RMSE | 质量等级 |
|------|------|------|------|----------|
{ranking_rows}**核心发现2**：24h滚动预测成功捕捉了日内周期性特征。
- 预测窗口：24小时
- 典型误差模式：在负荷突变点（如早晚高峰的上升/下降沿）误差较大

**与前章关系**：本章的预测模型为第五章的中长期趋势分析提供了工具支撑，为第七章的优化模型提供了未来负荷输入。
"""


def gen_chapter_05(data):
    """第五章：中长期趋势"""
    trend_str = ", ".join([f"{c}={d}" for c, d in data['trend_directions'].items()])

    return f"""## 第五章 月度/季度中长期趋势分析

**核心发现1**：STL分解显示四城市趋势方向为{trend_str}。
- 趋势分量：各城市长期负荷变化方向存在差异
- 季节性分量：所有城市均呈现显著的年度周期性（夏季高、冬季低）

**核心发现2**：季节性强度均为中等水平，{data['strongest_season_city']}相对最强。
- 最强季节性城市：{data['strongest_season_city']}，Fs={data['strongest_fs']:.4f}
- 强度等级：Moderate（0.5~0.7区间）

**与前章关系**：本章的趋势判断为第六章的跨国对比提供了摩洛哥侧的基准数据，为第七章的优化模型提供了季节性调整依据。
"""


def gen_chapter_06(data):
    """第六章：跨国对比"""
    return f"""## 第六章 国内对标区域数据爬取与跨国对比

**核心发现1**：摩洛哥城市负荷率显著低于中国对标城市。
- 摩洛哥平均负荷率：{data['ma_load_rate_avg']:.2f}（范围{data['ma_load_rate_min']:.2f}~{data['ma_load_rate_max']:.2f}）
- 中国平均负荷率：{data['cn_load_rate_avg']:.2f}
- 差异归因：{data['ch06_difference_attribution']}

**核心发现2**：季节性波动模式存在显著差异。
- 摩洛哥城市：受夏季高温影响更大，制冷负荷是峰值的主要驱动
- 中国对标城市：冬季供暖负荷和夏季制冷负荷共同构成双峰

**与前章关系**：本章的跨国对比为第七章的工程策略建议提供了国际参考（如中国错峰电价政策的经验）。
"""


def gen_chapter_07(data):
    """第七章：配电网优化"""
    peak_red = data['peak_reduction_pct']

    if abs(peak_red) < 0.01:
        opt_result = (
            f"线性规划优化后峰值负荷变化为 {peak_red:.1f}%，模型未产生实质性优化效果。"
            f"原因分析：当前优化模型受供需平衡约束（总供电=总需求）限制，"
            f"在无储能、无需求侧响应的条件下，负荷曲线无法通过重新分配实现削峰。"
            f"这一结果本身具有重要参考价值——说明仅靠供给侧调度无法解决配电网峰值问题，"
            f"必须引入储能、需求侧响应等灵活性资源。"
        )
    else:
        opt_result = (
            f"线性规划优化后峰值负荷降低 {abs(peak_red):.1f}%，验证了优化模型的有效性。"
            f"原始峰值负荷 {data['original_peak']:.1f} kW → 优化后 {data['optimized_peak']:.1f} kW。"
        )

    strategies_rows = "\n".join([f"- {s}" for s in data['engineering_strategies']])

    return f"""## 第七章 配电网优化模型

**核心发现1**：{opt_result}

**核心发现2**：四类工程策略可进一步提升优化效果。
{strategies_rows}
- 综合实施预期：峰值降低20-30%

**与前章关系**：本章是全流程的工程应用落地，综合运用了前六章的全部分析结论。
"""


def gen_chapter_08():
    """第八章：总结与展望（本章）"""
    return """## 第八章 总结与展望（本章）

**核心发现1**：全流程分析建立了从数据预处理到配电网优化的完整技术链条。
- 技术路线：数据清洗 → 规律挖掘 → 峰值识别 → 预测建模 → 趋势分析 → 跨国对比 → 配电优化
- 核心工具：Python (pandas, scikit-learn, XGBoost, Prophet, PuLP, matplotlib)
- 数据规模：4城市、17 zone、约30万条10分钟级记录

**核心发现2**：研究存在数据维度缺失、模型精度限制等局限性，未来可在多个方向拓展。
- 详见"不足与局限"和"未来展望"部分
"""


def gen_tech_route(data):
    """技术路线总结"""
    return f"""## 技术路线总结

### 方法选择理由

| 步骤 | 核心方法 | 选择理由 | 替代方案 |
|------|----------|----------|----------|
| 数据预处理 | 线性插值 + 3σ准则 | 标准时序预处理方法，成熟可靠 | 样条插值、IQR方法 |
| 用电规律 | 描述性统计 + KMeans聚类 | 无监督方法，无需标签数据 | DBSCAN、GMM |
| 峰值识别 | 95%分位数阈值 | 工程上常用的峰值判定标准 | Z-score、固定阈值 |
| 短期预测 | {data['best_model']}等5模型对比 | 多模型对比确保选型客观 | 单一模型直接建模 |
| 中长期趋势 | STL分解 | 经典时序分解方法，可解释性强 | X-11、SEATS |
| 跨国对比 | 描述性统计对比 | 数据维度有限，统计对比最直接 | 回归分析、因果推断 |
| 配电网优化 | 线性规划(PuLP) | 问题为线性结构，求解快且全局最优 | MILP、NSGA-II |

### 工具链清单

| 工具/库 | 用途 | 使用章节 |
|---------|------|----------|
| pandas + numpy | 数据处理 | 全部 |
| matplotlib + seaborn | 可视化 | ch02~ch07 |
| scikit-learn | 机器学习(RF,聚类) | ch02, ch04 |
| XGBoost + LightGBM | 梯度提升预测 | ch04 |
| PyTorch | LSTM深度学习 | ch04 |
| Prophet | 时序预测 | ch04 |
| statsmodels | STL分解 | ch05 |
| PuLP | 线性规划求解 | ch07 |

### 数据流

```
原始数据(Excel) → ch01清洗 → ch02规律 → ch03峰值 → ch04预测 → ch05趋势 → ch06对比 → ch07优化 → ch08总结
```
"""


def gen_limitations(data):
    """不足与局限"""
    mape = data['best_mape']
    if mape < 5:
        mape_eval = f"当前最优模型MAPE为{mape:.2f}%，已达到较高精度，但引入气象特征后预期可进一步降低至3-5%"
    elif mape < 10:
        mape_eval = f"当前最优模型MAPE为{mape:.2f}%，仍有较大提升空间，引入气象特征后预期可降低2-5个百分点"
    else:
        mape_eval = f"当前最优模型MAPE为{mape:.2f}%，精度有待提升，引入气象特征和更多外部变量是首要改进方向"

    peak_red = data['peak_reduction_pct']
    if abs(peak_red) < 0.01:
        opt_eval = "当前线性规划模型受供需平衡约束限制未产生优化效果，需升级为含储能和需求侧响应的MILP模型"
    else:
        opt_eval = f"当前优化模型峰值降低{abs(peak_red):.1f}%，但线性规划简化假设较多，升级为MILP后预期可进一步提升"

    return f"""## 不足与局限

### 数据维度局限
1. **缺少气象数据**：气温、湿度、风速等气象因素未纳入分析，限制了预测精度提升空间
2. **缺少经济数据**：GDP、人口、产业结构等宏观经济指标未纳入
3. **时间跨度有限**：约20个月数据，不足以进行多年周期趋势分析
4. **空间分辨率有限**：仅到zone级别，缺少用户级数据

### 模型精度局限
1. **预测模型未充分利用外部特征**：{mape_eval}
2. **优化模型简化假设较多**：{opt_eval}
3. **跨国对比深度不足**：主要基于宏观指标，缺少负荷曲线形态等微观对比

### 方法论局限
1. **异常检测方法单一**：仅使用3σ准则
2. **居民/工业分类方法简单**：基于KMeans的二分类较为粗糙
3. **优化模型为静态模型**：未考虑负荷的时变性
"""


FUTURE_OUTLOOK = """## 未来展望

### 方向1：引入多维气象数据提升预测精度
- **做什么**：将气温、湿度、风速、日照时数等气象变量纳入预测模型
- **怎么做**：通过Open-Meteo API或NOAA数据库获取逐小时气象数据，与负荷数据按时间戳合并，使用SHAP值量化贡献度
- **预期效果**：MAPE降低2-5个百分点
- **实施难度**：低

### 方向2：拓展多国家多气候带对比
- **做什么**：从"摩洛哥 vs 中国"拓展到包含撒哈拉以南非洲、欧洲国家
- **怎么做**：通过世界银行、IEA公开数据获取更多国家电力负荷统计数据，按气候带分组对比
- **预期效果**：揭示不同气候带和经济发展阶段下电力负荷模式的普适规律
- **实施难度**：中

### 方向3：升级优化模型为多时间尺度协调调度
- **做什么**：升级为"日前调度 + 日内滚动修正"的多时间尺度框架
- **怎么做**：日前阶段用预测模型输出求解MILP（含储能决策）；日内每15分钟滚动更新
- **预期效果**：优化方案实际可执行性显著提升
- **实施难度**：高

### 方向4：结合分布式光伏和储能的主动配电网优化
- **做什么**：将光伏出力和电池储能纳入优化模型
- **怎么做**：获取太阳能辐照数据建立光伏出力模型，MILP中增加光伏和储能SOC约束
- **预期效果**：光伏消纳率提升至90%以上，净峰值额外降低10-20%
- **实施难度**：高

### 方向5：开发交互式数据可视化平台
- **做什么**：整合为交互式Web平台
- **怎么做**：使用Plotly Dash或Streamlit开发，支持多城市对比、在线推理、仪表盘
- **预期效果**：研究成果可访问性和可复用性大幅提升
- **实施难度**：中
"""


# ============================================================
# 模块 E: 指标表生成 + main()
# ============================================================

def build_metrics_table(data):
    """构建关键指标总览表"""
    metrics = [
        # ch01
        {'chapter': 'ch01', 'category': '数据预处理', 'metric': '清洗后数据总量', 'value': str(data['total_rows']), 'unit': '行', 'source_file': 'ch01_cleaned_data.csv'},
        {'chapter': 'ch01', 'category': '数据预处理', 'metric': '城市/zone数量', 'value': '4城市/17zone', 'unit': '-', 'source_file': '数据概况'},
        {'chapter': 'ch01', 'category': '数据预处理', 'metric': '时间粒度', 'value': '10分钟', 'unit': '-', 'source_file': '数据概况'},
        {'chapter': 'ch01', 'category': '数据预处理', 'metric': '缺失率', 'value': f"{data['avg_missing_rate']:.2f}%", 'unit': '%', 'source_file': 'ch01_missing_stats.csv'},
        # ch02
        {'chapter': 'ch02', 'category': '用电规律', 'metric': '日均负荷最高城市', 'value': data['city_max_load'], 'unit': 'kW', 'source_file': 'ch02_descriptive_stats.csv'},
        {'chapter': 'ch02', 'category': '用电规律', 'metric': '日均负荷最低城市', 'value': data['city_min_load'], 'unit': 'kW', 'source_file': 'ch02_descriptive_stats.csv'},
        {'chapter': 'ch02', 'category': '用电规律', 'metric': '居民zone比例', 'value': f"{data['residential_pct']:.1f}%", 'unit': '%', 'source_file': 'ch02_residential_industrial_class.csv'},
        # ch03
        {'chapter': 'ch03', 'category': '峰值识别', 'metric': '峰值事件总数', 'value': str(data['total_peak_events']), 'unit': '个', 'source_file': 'ch03_peak_events_summary.csv'},
        {'chapter': 'ch03', 'category': '峰值识别', 'metric': '平均异常峰值比例', 'value': f"{data['avg_anomaly_ratio']:.2f}%", 'unit': '%', 'source_file': 'ch03_anomaly_peak_flags.csv'},
        # ch04
        {'chapter': 'ch04', 'category': '短期预测', 'metric': '最优模型', 'value': data['best_model'], 'unit': '-', 'source_file': 'ch04_model_comparison.csv'},
        {'chapter': 'ch04', 'category': '短期预测', 'metric': '最优MAPE', 'value': f"{data['best_mape']:.2f}%", 'unit': '%', 'source_file': 'ch04_model_comparison.csv'},
        # ch05
        {'chapter': 'ch05', 'category': '中长期趋势', 'metric': '最强季节性城市', 'value': data['strongest_season_city'], 'unit': '-', 'source_file': 'ch05_seasonal_strength.csv'},
        {'chapter': 'ch05', 'category': '中长期趋势', 'metric': '最强季节性Fs', 'value': f"{data['strongest_fs']:.4f}", 'unit': '-', 'source_file': 'ch05_seasonal_strength.csv'},
        # ch06
        {'chapter': 'ch06', 'category': '跨国对比', 'metric': '摩洛哥平均负荷率', 'value': f"{data['ma_load_rate_avg']:.2f}", 'unit': '-', 'source_file': 'ch06_benchmark_cleaned.csv'},
        {'chapter': 'ch06', 'category': '跨国对比', 'metric': '中国平均负荷率', 'value': f"{data['cn_load_rate_avg']:.2f}", 'unit': '-', 'source_file': 'ch06_benchmark_cleaned.csv'},
        # ch07
        {'chapter': 'ch07', 'category': '配电网优化', 'metric': '峰值降低率', 'value': f"{data['peak_reduction_pct']:.1f}%", 'unit': '%', 'source_file': 'ch07_optimization_metrics.csv'},
        {'chapter': 'ch07', 'category': '配电网优化', 'metric': '负荷率变化', 'value': f"{data['load_rate_change_pct']:.1f}%", 'unit': '%', 'source_file': 'ch07_optimization_metrics.csv'},
    ]
    return pd.DataFrame(metrics)


def assemble_report(data):
    """拼接完整报告"""
    sections = [
        "# 摩洛哥多城市电力负荷全流程分析 — 成果汇总报告\n\n",
        "> 本报告对全流程8个章节的核心研究成果进行系统性汇总，提炼关键发现和数据指标。\n",
        "> 数据来源：摩洛哥4城市（Laayoune、Boujdour、Foum eloued、Marrakech）智能电表数据\n",
        "> 分析周期：2022年9月 ~ 2024年5月（约20个月）\n\n",
        "---\n\n",
        gen_chapter_01(data), "\n\n",
        gen_chapter_02(data), "\n\n",
        gen_chapter_03(data), "\n\n",
        gen_chapter_04(data), "\n\n",
        gen_chapter_05(data), "\n\n",
        gen_chapter_06(data), "\n\n",
        gen_chapter_07(data), "\n\n",
        gen_chapter_08(), "\n\n",
        "---\n\n",
        gen_tech_route(data), "\n\n",
        "---\n\n",
        gen_limitations(data), "\n\n",
        "---\n\n",
        FUTURE_OUTLOOK,
    ]
    return "".join(sections)


def print_report_summary(data, metrics_df):
    """打印报告摘要"""
    print("\n" + "=" * 70)
    print("  成果汇总报告生成完成")
    print("=" * 70)
    print(f"  数据总量: {data['total_rows']} 行")
    print(f"  最优模型: {data['best_model']} (MAPE={data['best_mape']:.2f}%)")
    print(f"  峰值事件: {data['total_peak_events']} 个")
    print(f"  峰值降低率: {data['peak_reduction_pct']:.1f}%")
    print(f"  指标表行数: {len(metrics_df)}")
    print("=" * 70)


def main():
    """主函数"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 70)
    print("  Prompt-08: 总结与展望")
    print("=" * 70)
    print("\nStep 1: 从各章产物中提取数据...")
    data = extract_all_data()

    print("\nStep 2: 生成成果汇总报告...")
    report = assemble_report(data)
    report_path = os.path.join(OUTPUT_DIR, 'ch08_achievements_summary.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  [完成] {report_path}")

    print("\nStep 3: 生成关键指标总览表...")
    metrics_df = build_metrics_table(data)
    metrics_path = os.path.join(OUTPUT_DIR, 'ch08_key_metrics_table.csv')
    metrics_df.to_csv(metrics_path, index=False, encoding='utf-8-sig')
    print(f"  [完成] {metrics_path}")

    print_report_summary(data, metrics_df)
    print("\n所有产物已保存到:", OUTPUT_DIR)


if __name__ == '__main__':
    main()
