# AB_Test_Analysis 任务分发指南

> 项目：A/B测试点击率数据分析
> 生成时间：2026-05-08
> 文档用途：定义任务依赖、批次划分、具体执行话术

---

## 一、全局依赖 DAG 图

```
                    ┌─────────────────────────────────────┐
                    │       Prompt-01: 数据清洗            │
                    │         (ch01_data_cleaning)         │
                    └──────────────┬──────────────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ Prompt-02: 核心指标  │  │ Prompt-03: 假设检验  │  │ Prompt-04: 时间趋势  │
│ (ch02_metrics_viz)  │  │ (ch03_hypothesis)   │  │ (ch04_time_trend)   │
└──────────┬──────────┘  └──────────┬──────────┘  └──────────┬──────────┘
           │                       │                       │
           └───────────────────────┼───────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │    Prompt-05: 结论与决策建议         │
                    │   (ch05_conclusion_recommendation)   │
                    └─────────────────────────────────────┘
```

---

## 二、批次划分

| 批次 | Prompt | 章节 | 依赖 | 并行性 |
|------|--------|------|------|--------|
| Batch-0 | Prompt-01 | ch01_data_cleaning | 无 | 串行前置 |
| Batch-1 | Prompt-02 | ch02_metrics_visualization | Prompt-01 | 可与 03、04 并行 |
| Batch-1 | Prompt-03 | ch03_hypothesis_testing | Prompt-01 | 可与 02、04 并行 |
| Batch-1 | Prompt-04 | ch04_time_trend_analysis | Prompt-01 | 可与 02、03 并行 |
| Batch-2 | Prompt-05 | ch05_conclusion_recommendation | Prompt-02, 03, 04 | 串行收束 |

**并行说明**：Batch-1 中 Prompt-02、Prompt-03、Prompt-04 三条支线可并行执行。

---

## 三、章节关键信息速查表

| Prompt | 章节名称 | 输入数据 | 核心产物 | 后续依赖方 |
|--------|----------|----------|----------|------------|
| Prompt-01 | 数据清洗 | `data/raw/ab_test_click_data.csv` | `cleaned_data.csv`, `report.md` | Prompt-02, 03, 04 |
| Prompt-02 | 核心指标与可视化 | `data/processed/cleaned_data.csv` | `ch02_group_metrics.csv`, `report.md` | Prompt-05 |
| Prompt-03 | 假设检验与效应量 | `data/processed/cleaned_data.csv` | `ch03_hypothesis_test_results.csv`, `report.md` | Prompt-05 |
| Prompt-04 | 时间趋势分析 | `data/processed/cleaned_data.csv` | `ch04_daily_ctr_trend.csv`, `report.md` | Prompt-05 |
| Prompt-05 | 结论与决策建议 | ch02、ch03 结果 | `ch05_decision_report.md`, `report.md` | 无 |

---

## 四、具体执行话术

### Prompt-01: 数据清洗

**具体话术**：
1. 阅读 `docs/execution_prompts.md` 的 Prompt-01 部分，理解数据清洗目标
2. 调用 Skill-01 的 `load_raw()` 加载原始数据 `data/raw/ab_test_click_data.csv`
3. 调用 Skill-03 的 `null_summary()` 检查缺失值，保存结果到 `outputs/ch01_data_cleaning/missing_values_summary.csv`
4. 调用 Skill-03 的 `duplicate_summary()` 检查重复值，保存结果到 `outputs/ch01_data_cleaning/duplicate_summary.json`
5. 验证数据类型，转换 timestamp 为 datetime
6. 调用 Skill-04 的 `save_data()` 保存清洗后数据到 `data/processed/cleaned_data.csv`
7. 生成 `outputs/ch01_data_cleaning/report.md`（四段框架：背景、分析方法、分析发现、小结）
8. 检查标准：`outputs/ch01_data_cleaning/` 目录下已生成 `report.md` + 清洗后数据

**技能调用**：Skill-01 (data_loader), Skill-03 (metrics), Skill-04 (output_manager)

---

### Prompt-02: 核心指标计算与可视化

**具体话术**：
1. 阅读 `docs/execution_prompts.md` 的 Prompt-02 部分，理解核心指标计算目标
2. 调用 Skill-01 的 `load_processed("cleaned_data.csv")` 加载清洗后数据
3. 按 group 分组计算点击率、绝对提升、相对提升
4. 计算 95% 置信区间：`p ± 1.96 × SE`
5. 调用 Skill-02 的 `save_figure()` 保存可视化图表到 `outputs/ch02_metrics_visualization/ctr_comparison_with_ci.png`
6. 调用 Skill-04 的 `save_table()` 保存统计结果到 `outputs/ch02_metrics_visualization/group_metrics_with_ci.csv`
7. 生成 `outputs/ch02_metrics_visualization/report.md`（四段框架）
8. 检查标准：`outputs/ch02_metrics_visualization/` 目录下已生成 `report.md` + 统计表 + 图表

**技能调用**：Skill-01 (data_loader), Skill-02 (visualizer), Skill-04 (output_manager)

---

### Prompt-03: 假设检验与效应量

**具体话术**：
1. 阅读 `docs/execution_prompts.md` 的 Prompt-03 部分，理解假设检验目标
2. 调用 Skill-01 的 `load_processed("cleaned_data.csv")` 加载清洗后数据
3. 执行比例 Z 检验（单尾），计算 Z 统计量和 p 值
4. 计算 Cohen's h 效应量：`h = 2 × (arcsin√p_exp - arcsin√p_con)`
5. 使用 statsmodels 计算统计功效和 MDE
6. 调用 Skill-04 的 `save_table()` 保存检验结果到 `outputs/ch03_hypothesis_testing/hypothesis_test_results.csv`
7. 生成 `outputs/ch03_hypothesis_testing/report.md`（四段框架）
8. 检查标准：`outputs/ch03_hypothesis_testing/` 目录下已生成 `report.md` + 检验结果表

**技能调用**：Skill-01 (data_loader), Skill-03 (metrics), Skill-04 (output_manager)

---

### Prompt-04: 时间趋势分析

**具体话术**：
1. 阅读 `docs/execution_prompts.md` 的 Prompt-04 部分，理解时间趋势分析目标
2. 调用 Skill-01 的 `load_processed("cleaned_data.csv")` 加载清洗后数据
3. 按天分组聚合，计算每日点击率，保存到 `outputs/ch04_time_trend_analysis/daily_ctr_trend.csv`
4. 按小时分组聚合，计算每小时点击率，保存到 `outputs/ch04_time_trend_analysis/hourly_ctr_trend.csv`
5. 调用 Skill-02 的 `save_figure()` 保存趋势图到 `outputs/ch04_time_trend_analysis/`
6. 检测新奇效应：比较实验组前半期 vs 后半期点击率
7. 生成 `outputs/ch04_time_trend_analysis/report.md`（四段框架）
8. 检查标准：`outputs/ch04_time_trend_analysis/` 目录下已生成 `report.md` + 趋势表 + 趋势图

**技能调用**：Skill-01 (data_loader), Skill-02 (visualizer), Skill-04 (output_manager)

---

### Prompt-05: 结论与决策建议

**具体话术**：
1. 阅读 `docs/execution_prompts.md` 的 Prompt-05 部分，理解决策框架
2. 加载 ch02 的 `group_metrics_with_ci.csv` 和 ch03 的 `hypothesis_test_results.csv`
3. 应用严格决策矩阵（p值 + Cohen's h + 统计功效）做出决策
4. 生成决策报告，保存到 `outputs/ch05_conclusion_recommendation/decision_report.md`
5. 生成 `outputs/ch05_conclusion_recommendation/report.md`（四段框架）
6. 检查标准：`outputs/ch05_conclusion_recommendation/` 目录下已生成 `report.md` + 决策报告

**技能调用**：Skill-01 (data_loader), Skill-04 (output_manager)

---

## 五、章节输出规范

每个章节完成标志包含三项必要产出：

| 产出 | 路径 | 说明 |
|------|------|------|
| 执行报告 | `outputs/chXXX/report.md` | 四段框架（背景、分析方法、分析发现、小结） |
| 交互 Notebook | `src/chXXX/notebook.ipynb` | 与 .py 逻辑一致的交互版本 |
| 全部产物 | `outputs/chXXX/` | 所有输出文件统一归档到此目录 |

---

## 六、核心规则

1. **严禁跳批**：每个批次必须等前置依赖全部完成后再启动
2. **数据不覆盖**：每个章节的产物写入独立的 `outputs/chXXX/` 目录
3. **脚本双格式**：每个章节提供 `.py`（批量执行）+ `.ipynb`（交互学习）
4. **全局配置共享**：所有脚本通过 `config.py` 统一路径和参数
5. **章节报告必需**：每个章节执行后必须生成 `outputs/chXXX/report.md`
6. **输出统一归档**：所有产物文件统一放到 `outputs/chXXX/` 目录下

---

## 七、执行命令

```bash
# Batch-0: 串行前置
python src/ch01_data_cleaning/run.py

# Batch-1: 可并行执行
python src/ch02_metrics_visualization/run.py &
python src/ch03_hypothesis_testing/run.py &
python src/ch04_time_trend_analysis/run.py &
wait

# Batch-2: 串行收束
python src/ch05_conclusion_recommendation/run.py
```
