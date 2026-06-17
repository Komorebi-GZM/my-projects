# 任务分发指南

> 本文档定义了摩洛哥电力负荷分析项目的任务分发规范。
> **每次派活时，将对应批次的「派活模板」直接发给执行者即可。**

---

## 一、全局依赖图

```
Prompt-01 (数据预处理) ───────────────────────────────────── 必须最先完成
    │
    ├──────────────────┬──────────────────┐
    ▼                  ▼                  ▼
Prompt-02          Prompt-04          Prompt-05        ← 三条支线可并行
(用电规律挖掘)      (短期负荷预测)      (中长期趋势)
    │                  │                  │
    ▼                  │                  │
Prompt-03              │                  │
(峰值识别)             │                  │
    │                  │                  │
    ├──────────────────┤                  │
    ▼                  ▼                  ▼
    └──────► Prompt-06 ◄─────────────────┘
            (跨国对比)     ← 需要 02 + 05 完成
                │
                ▼
            Prompt-07
            (配电网优化)   ← 需要 02 + 03 + 04 + 05 全部完成
                │
                ▼
            Prompt-08
            (总结展望)     ← 需要全部章节完成
```

## 二、批次划分

| 批次 | 任务 | 并行度 | 前置依赖 | 数据源 |
|------|------|--------|----------|--------|
| **Batch-0** | Prompt-01 数据预处理 | 串行 | 无 | `data/Data Morocco.xlsx` |
| **Batch-1** | Prompt-02 + 04 + 05 | 3路并行 | Batch-0 | `ch01_feature_engineered_data.csv` |
| **Batch-2** | Prompt-03 峰值识别 | 串行 | Batch-1 支线A | `ch01_cleaned_data.csv` + `ch02_descriptive_stats.csv` |
| **Batch-3** | Prompt-06 跨国对比 | 串行 | Batch-1 支线A+C | ch02~ch05 分析结论 |
| **Batch-4** | Prompt-07 配电网优化 | 串行 | Batch-1~3 全部 | ch03阈值 + ch04预测 + ch05趋势 |
| **Batch-5** | Prompt-08 总结展望 | 串行 | Batch-0~4 全部 | 全部章节产物 |

## 三、派活模板

### 模板 A：完整项目启动（从零开始）

```
【摩洛哥电力负荷分析 — 任务分发】

项目路径: Morocco_Load_Analysis/
环境: conda activate py310
规范文档: docs/摩洛哥多城市电力负荷全流程分析流程设计.md
执行Prompt: docs/Morocco_Load_Analysis_Execution_Prompts.md

═══ 阶段 1：串行前置 ═══
▶ Batch-0: Prompt-01 数据预处理
  - 脚本: src/ch01_preprocessing/preprocess.py
  - 产物: outputs/ch01_data_preprocessing/ (8个文件)
  - 完成标志: ch01_feature_engineered_data.csv 存在且无NaN

═══ 阶段 2：三路并行 ═══（Batch-0 完成后启动）
▶ 支线 A: Prompt-02 用电规律挖掘
  - 依赖: ch01_feature_engineered_data.csv
  - 产物: outputs/ch02_load_pattern_analysis/
▶ 支线 B: Prompt-04 短期负荷预测
  - 依赖: ch01_feature_engineered_data.csv
  - 产物: outputs/ch04_load_forecasting/
▶ 支线 C: Prompt-05 中长期趋势分析
  - 依赖: ch01_cleaned_data.csv
  - 产物: outputs/ch05_midlong_term_trend/

═══ 阶段 3：串行收束 ═══
▶ Batch-2: Prompt-03 峰值识别（支线A完成后）
▶ Batch-3: Prompt-06 跨国对比（支线A+C完成后）
▶ Batch-4: Prompt-07 配电网优化（全部支线完成后）
▶ Batch-5: Prompt-08 总结展望（全部章节完成后）
```

### 模板 B：只派某个批次

```
【摩洛哥电力负荷分析 — Batch-X 任务】

项目路径: Morocco_Load_Analysis/
环境: conda activate py310

本批次: Prompt-XX [章节名称]
前置依赖: [列出需要已完成的产物]
输入数据: [具体文件路径]
输出产物: outputs/chXX_xxx/
完成标志: [关键产物文件名]
```

### 模板 C：检查进度（一句话提醒）

```
检查摩洛哥电力负荷分析进度：
Batch-0(01) → Batch-1(02+04+05并行) → Batch-2(03) → Batch-3(06) → Batch-4(07) → Batch-5(08)
当前应在哪个批次？哪些产物已产出？
```

## 四、每个 Prompt 的关键信息速查

| Prompt | 名称 | 输入 | 核心产物 | 后续依赖方 |
|--------|------|------|----------|-----------|
| 01 | 数据预处理 | `Data Morocco.xlsx` | `ch01_cleaned_data.csv`, `ch01_feature_engineered_data.csv` | 全部 |
| 02 | 用电规律挖掘 | `ch01_feature_engineered_data.csv` | `ch02_descriptive_stats.csv`, `ch02_load_rate_cv.csv` | 03, 06, 07 |
| 03 | 峰值识别 | `ch01_cleaned_data.csv` + ch02统计 | `ch03_peak_thresholds.csv`, `ch03_peak_events.csv` | 07 |
| 04 | 短期负荷预测 | `ch01_feature_engineered_data.csv` | `ch04_model_comparison.csv`, 模型文件 | 07 |
| 05 | 中长期趋势 | `ch01_cleaned_data.csv` | `ch05_seasonal_strength.csv`, `ch05_stl_*.png` | 06, 07 |
| 06 | 跨国对比 | ch02~ch05结论 + 外部爬虫数据 | `ch06_benchmark_cleaned.csv`, 对比图 | 08 |
| 07 | 配电网优化 | ch03阈值 + ch04预测 + ch05趋势 | `ch07_optimization_result.csv`, 策略报告 | 08 |
| 08 | 总结展望 | 全部章节产物 | `ch08_achievements_summary.md` | 无 |

## 五、注意事项

1. **严禁跳批**：每个批次必须等前置依赖全部完成后再启动
2. **数据不覆盖**：每个章节的产物写入独立的 `outputs/chXX_xxx/` 目录，互不干扰
3. **脚本双格式**：每个章节提供 `.py`（批量执行）+ `.ipynb`（交互学习）
4. **全局配置共享**：所有脚本通过 `src/utils/config.py` 统一路径和参数
