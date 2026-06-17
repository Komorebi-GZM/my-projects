# gallstone_analysis — 任务分发指南

> 本文档定义了 UCI 胆结石数据集分析项目的任务分发规范。
> **每次派活时，将对应批次的「派活模板」直接发给执行者即可。**

---

## 一、全局依赖图

### 1.1 依赖关系定义

```json
{
  "ch01": [],
  "ch02": ["ch01"],
  "ch03": ["ch01", "ch02"],
  "ch04": ["ch01", "ch02", "ch03"],
  "ch05": ["ch01", "ch04"],
  "ch06": ["ch01", "ch02", "ch03", "ch04", "ch05"]
}
```

### 1.2 ASCII DAG 图

```
Prompt-01 (数据预处理) ─────────────────────────────────── ✅ 已完成
    │
    ▼
Prompt-02 (探索性分析) ─────────────────────────────────── ⬜ 待执行
    │
    ▼
Prompt-03 (统计检验) ───────────────────────────────────── ⬜ 待执行
    │
    ▼
Prompt-04 (特征筛选) ───────────────────────────────────── ⬜ 待执行
    │
    ├──► Prompt-05 (建模预测) ──────────────────────────── ⬜ 待执行
    │         │
    │         ▼
    └─────► Prompt-06 (总结报告) ───────────────────────── ⬜ 待执行
```

### 1.3 依赖关系说明

| 下游章节 | 依赖上游 | 依赖原因 |
|----------|----------|----------|
| ch02 探索性分析 | ch01 | 需要清洗后数据集 |
| ch03 统计检验 | ch01, ch02 | 需要清洗数据 + 效应量参考 |
| ch04 特征筛选 | ch01, ch02, ch03 | 需要清洗数据 + 效应量 + 显著性检验结果 |
| ch05 建模预测 | ch01, ch04 | 需要清洗数据 + 筛选后特征子集 |
| ch06 总结报告 | ch01~ch05 | 需要全部前序章节产物 |

> **注意**：当前依赖关系为严格串行链式结构，无并行执行机会。这是由分析流程的递进逻辑决定的：EDA → 统计检验 → 特征筛选 → 建模，每一步都以前一步的结论为输入。

---

## 二、批次划分

### 2.1 拓扑排序结果

基于上述依赖关系，拓扑排序产生 **6 个批次**，全部为串行执行：

| 批次 | 任务 | 并行度 | 前置依赖 | 状态 |
|------|------|--------|----------|------|
| **Batch-0** | Prompt-01 数据预处理 | 1（串行） | 无 | ✅ 已完成 |
| **Batch-1** | Prompt-02 探索性数据分析 | 1（串行） | ch01 清洗数据 | ⬜ 待执行 |
| **Batch-2** | Prompt-03 统计检验 | 1（串行） | ch01 + ch02 | ⬜ 待执行 |
| **Batch-3** | Prompt-04 特征筛选 | 1（串行） | ch01 + ch02 + ch03 | ⬜ 待执行 |
| **Batch-4** | Prompt-05 建模预测 | 1（串行） | ch01 + ch04 | ⬜ 待执行 |
| **Batch-5** | Prompt-06 总结报告 | 1（串行） | ch01~ch05 全部 | ⬜ 待执行 |

### 2.2 批次执行时间线

```
时间 ──────────────────────────────────────────────────────────►

Batch-0  ████████ ch01 数据预处理                          ✅
Batch-1          ████████████████ ch02 探索性分析           ⬜
Batch-2                          ██████████ ch03 统计检验   ⬜
Batch-3                                  ████████ ch04 特征筛选 ⬜
Batch-4                                          ████████ ch05 建模 ⬜
Batch-5                                                  ████ ch06 总结 ⬜
```

### 2.3 并行优化说明

当前为严格串行，但若未来调整依赖关系，可释放以下并行机会：

| 调整方案 | 变更 | 新批次结构 | 并行度提升 |
|----------|------|-----------|-----------|
| 方案 A | ch05 仅依赖 ch01+ch04（去掉对 ch02/ch03 的间接依赖） | Batch-3: ch04+ch05 并行 | 2 |
| 方案 B | ch03 仅依赖 ch01（去掉对 ch02 的依赖） | Batch-1: ch02+ch03 并行 | 2 |
| 方案 C | A+B 同时生效 | Batch-1: ch02+ch03, Batch-3: ch04+ch05 | 2 |

> **当前选择保持严格串行**，原因是：ch03 的统计检验需要 ch02 的效应量作为输入，ch04 的特征筛选需要 ch03 的显著性结果，保持串行可确保分析逻辑的严谨性。

---

## 三、派活模板

### 模板 A：完整项目启动（从零开始）

```
【UCI 胆结石数据集分析 — 任务分发】

项目路径: gallstone_analysis/
环境: conda activate py310
规范文档: docs/project_convention.md
流程设计: docs/gallstone_analysis_流程设计.md
执行Prompt: docs/gallstone_analysis_Execution_Prompts.md

═══ 阶段 1：串行前置 ═══
▶ Batch-0: Prompt-01 数据预处理                    ✅ 已完成
  - 脚本: src/ch01_preprocessing/preprocess.py
  - 产物: outputs/ch01_preprocessing/ (9个文件)
  - 完成标志: ch01_cleaned_dataset.csv 存在

═══ 阶段 2：逐章串行执行 ═══（Batch-0 完成后依次启动）
▶ Batch-1: Prompt-02 探索性数据分析
  - 依赖: ch01_cleaned_dataset.csv
  - 产物: outputs/ch02_eda/ (10个文件)
  - 完成标志: ch02_effect_sizes.csv 存在

▶ Batch-2: Prompt-03 统计检验
  - 依赖: ch01_cleaned_dataset.csv + ch02_effect_sizes.csv
  - 产物: outputs/ch03_statistical_test/ (6个文件)
  - 完成标志: ch03_significant_features.csv 存在

▶ Batch-3: Prompt-04 特征筛选
  - 依赖: ch01_cleaned_dataset.csv + ch03_significant_features.csv
  - 产物: outputs/ch04_feature_selection/ (9个文件)
  - 完成标志: ch04_final_features.csv + ch04_selected_features_data.csv 存在

▶ Batch-4: Prompt-05 建模预测
  - 依赖: ch04_selected_features_data.csv + ch04_final_features.csv
  - 产物: outputs/ch05_modeling/ (5个文件)
  - 完成标志: ch05_model_comparison.csv + ch05_best_model.pkl 存在

═══ 阶段 3：串行收束 ═══
▶ Batch-5: Prompt-06 总结报告
  - 依赖: ch01~ch05 全部产物
  - 产物: outputs/ch06_summary/ (2个文件)
  - 完成标志: ch06_achievements_summary.md 存在
```

### 模板 B：只派某个批次

#### 派 Batch-1（当前待执行）

```
【UCI 胆结石数据集分析 — Batch-1: 探索性数据分析】

项目路径: gallstone_analysis/
环境: conda activate py310

本批次: Prompt-02 探索性数据分析
前置依赖: outputs/ch01_preprocessing/ch01_cleaned_dataset.csv ✅ 已存在
输入数据: outputs/ch01_preprocessing/ch01_cleaned_dataset.csv
输出产物: outputs/ch02_eda/
完成标志: outputs/ch02_eda/ch02_effect_sizes.csv

执行标准: docs/gallstone_analysis_Execution_Prompts.md 中搜索 "Prompt-02"
产物要求: docs/gallstone_analysis_流程设计.md 第3章 §3.5 产物表
项目规范: docs/project_convention.md

首次执行：先阅读 docs/project_convention.md 了解项目规范，再开始。
```

#### 派 Batch-2

```
【UCI 胆结石数据集分析 — Batch-2: 统计检验】

项目路径: gallstone_analysis/
环境: conda activate py310

本批次: Prompt-03 统计检验
前置依赖:
  - outputs/ch01_preprocessing/ch01_cleaned_dataset.csv
  - outputs/ch02_eda/ch02_effect_sizes.csv
输入数据: outputs/ch01_preprocessing/ch01_cleaned_dataset.csv
输出产物: outputs/ch03_statistical_test/
完成标志: outputs/ch03_statistical_test/ch03_significant_features.csv

执行标准: docs/gallstone_analysis_Execution_Prompts.md 中搜索 "Prompt-03"
产物要求: docs/gallstone_analysis_流程设计.md 第4章 §4.5 产物表
项目规范: docs/project_convention.md
```

#### 派 Batch-3

```
【UCI 胆结石数据集分析 — Batch-3: 特征筛选】

项目路径: gallstone_analysis/
环境: conda activate py310

本批次: Prompt-04 特征筛选
前置依赖:
  - outputs/ch01_preprocessing/ch01_cleaned_dataset.csv
  - outputs/ch03_statistical_test/ch03_significant_features.csv
  - outputs/ch03_statistical_test/ch03_adjusted_p_values.csv
输入数据: outputs/ch01_preprocessing/ch01_cleaned_dataset.csv
输出产物: outputs/ch04_feature_selection/
完成标志: outputs/ch04_feature_selection/ch04_final_features.csv + ch04_selected_features_data.csv

执行标准: docs/gallstone_analysis_Execution_Prompts.md 中搜索 "Prompt-04"
产物要求: docs/gallstone_analysis_流程设计.md 第5章 §5.5 产物表
项目规范: docs/project_convention.md
```

#### 派 Batch-4

```
【UCI 胆结石数据集分析 — Batch-4: 建模预测】

项目路径: gallstone_analysis/
环境: conda activate py310

本批次: Prompt-05 建模预测
前置依赖:
  - outputs/ch04_feature_selection/ch04_selected_features_data.csv
  - outputs/ch04_feature_selection/ch04_final_features.csv
输入数据: outputs/ch04_feature_selection/ch04_selected_features_data.csv
输出产物: outputs/ch05_modeling/
完成标志: outputs/ch05_modeling/ch05_model_comparison.csv + ch05_best_model.pkl

执行标准: docs/gallstone_analysis_Execution_Prompts.md 中搜索 "Prompt-05"
产物要求: docs/gallstone_analysis_流程设计.md 第6章 §6.5 产物表
项目规范: docs/project_convention.md
```

#### 派 Batch-5

```
【UCI 胆结石数据集分析 — Batch-5: 总结报告】

项目路径: gallstone_analysis/
环境: conda activate py310

本批次: Prompt-06 总结报告
前置依赖: outputs/ch01~ch05/ 全部产物
输入数据: outputs/ch01_preprocessing/ ~ outputs/ch05_modeling/
输出产物: outputs/ch06_summary/
完成标志: outputs/ch06_summary/ch06_achievements_summary.md

执行标准: docs/gallstone_analysis_Execution_Prompts.md 中搜索 "Prompt-06"
产物要求: docs/gallstone_analysis_流程设计.md 第7章 §7.5 产物表
项目规范: docs/project_convention.md
```

### 模板 C：检查进度（一句话提醒）

```
检查 UCI 胆结石数据集分析进度：
Batch-0(预处理✅) → Batch-1(EDA⬜) → Batch-2(统计检验⬜) → Batch-3(特征筛选⬜) → Batch-4(建模⬜) → Batch-5(总结⬜)
当前应在 Batch-1。已产出 9 个文件（ch01），预计总产出 39 个文件。
```

---

## 四、每个 Prompt 的关键信息速查

### 4.1 速查表

| Prompt | 名称 | 输入 | 核心产物 | 后续依赖方 | 预计产物数 |
|--------|------|------|----------|-----------|-----------|
| Prompt-01 | 数据预处理 | `data/dataset-uci.xlsx` | `ch01_cleaned_dataset.csv` | 全部 | 9 |
| Prompt-02 | 探索性分析 | `ch01_cleaned_dataset.csv` | `ch02_effect_sizes.csv` | ch03, ch04 | 10 |
| Prompt-03 | 统计检验 | `ch01_cleaned_dataset.csv` + `ch02_effect_sizes.csv` | `ch03_significant_features.csv` | ch04 | 6 |
| Prompt-04 | 特征筛选 | `ch01_cleaned_dataset.csv` + `ch03_significant_features.csv` | `ch04_final_features.csv`, `ch04_selected_features_data.csv` | ch05 | 9 |
| Prompt-05 | 建模预测 | `ch04_selected_features_data.csv` + `ch04_final_features.csv` | `ch05_model_comparison.csv`, `ch05_best_model.pkl` | ch06 | 5 |
| Prompt-06 | 总结报告 | ch01~ch05 全部产物 | `ch06_achievements_summary.md` | 无（最终交付） | 2 |

### 4.2 产物依赖链

```
dataset-uci.xlsx
    │
    ▼ [ch01]
ch01_cleaned_dataset.csv ──────────────────────────────┐
    │                                                  │
    ├──────► [ch02] ──► ch02_effect_sizes.csv          │
    │              │                                    │
    │              └──────► [ch03] ──► ch03_significant_features.csv
    │                              │                    │
    │                              └──────► [ch04] ──► ch04_final_features.csv
    │                                            │       ch04_selected_features_data.csv
    │                                            │
    │                                            └──────► [ch05] ──► ch05_model_comparison.csv
    │                                                          ch05_best_model.pkl
    │                                                          │
    └──────────────────────────────────────────────────────────┘
                                                               │
                                                          [ch06] ──► ch06_achievements_summary.md
```

---

## 五、注意事项

1. **严禁跳批**：每个批次必须等前置依赖全部完成后再启动。例如 ch04 必须等 ch03 的 `ch03_significant_features.csv` 产出后才能开始
2. **数据不覆盖**：每个章节的产物写入独立的 `outputs/chXX_xxx/` 目录，互不干扰
3. **脚本双格式**：每个章节提供 `.py`（批量执行）+ `.ipynb`（交互学习）两种格式
4. **全局配置共享**：所有脚本通过 `src/utils/config.py` 统一路径和参数
5. **ch01 已完成**：Batch-0 的 9 个产物已存在于 `outputs/ch01_preprocessing/`，无需重新执行
6. **产物命名规范**：所有产物文件必须以 `ch{NN}_` 开头，确保归属清晰
7. **环境一致性**：所有章节使用同一 conda 环境 `py310`（Python 3.10），通过 `requirements.txt` 管理依赖

---

## 六、当前状态与下一步

### 6.1 项目进度

| 批次 | 章节 | 状态 | 产物数 |
|------|------|------|--------|
| Batch-0 | ch01 数据预处理 | ✅ 已完成 | 9/9 |
| Batch-1 | ch02 探索性分析 | ⬜ 待执行 | 0/10 |
| Batch-2 | ch03 统计检验 | ⬜ 待执行 | 0/6 |
| Batch-3 | ch04 特征筛选 | ⬜ 待执行 | 0/9 |
| Batch-4 | ch05 建模预测 | ⬜ 待执行 | 0/5 |
| Batch-5 | ch06 总结报告 | ⬜ 待执行 | 0/2 |
| **合计** | | | **9/39** |

### 6.2 下一步行动

**立即执行 Batch-1**：使用「模板 B - 派 Batch-1」将探索性分析任务派发给执行者。

派活话术：
```
【UCI 胆结石数据集分析 — Batch-1: 探索性数据分析】

你现在阅读 docs/gallstone_analysis_Execution_Prompts.md，概览任务状况，
你的任务是 Prompt-02: 探索性数据分析；
执行标准看 docs/gallstone_analysis_流程设计.md 第3章；
产物要求看该文档第3章 §3.5 产物表；
项目规范（文件放哪、怎么命名、脚本结构）看 docs/project_convention.md；
执行前从 src/utils/task_graph.py 检查进度。

环境: conda activate py310

首次执行：先阅读 docs/project_convention.md 了解项目规范，再开始。
```
