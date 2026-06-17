# online_gaming_analysis — 任务分发指南

> 本文档定义了 online_gaming_analysis 项目的任务分发规范。
> **每次派活时，将对应批次的「派活模板」直接发给执行者即可。**

---

## 一、全局依赖图

### 1.1 ASCII DAG 图

```
Prompt-01 (数据清洗) ───────────────────────────────────── 必须最先完成
    │
    ├──────────────────┬──────────────────┐
    ▼                  ▼                  ▼
Prompt-02          Prompt-03          Prompt-04        ← ch01 完成后可并行
(热度分析)          (标签分析)          (跨平台对比)
    │                  │                  │
    └──────────────────┼──────────────────┘
                       ▼
                  Prompt-05
                  (可视化报告)         ← 全部分析章节完成后
```

> **说明**：当前全部章节（ch01-ch05）均已开发完成。ch01（数据清洗）→ ch02（热度分析）+ ch03（标签分析）+ ch04（跨平台对比）→ ch05（可视化报告）。

### 1.2 DAG 参数说明

| 参数 | 含义 | 本项目值 |
|------|------|----------|
| `Prompt-01` | 第一章：数据清洗 | 已定义 |
| `Prompt-02` | 第二章：热度分析 | 待补充 |
| `Prompt-03` | 第三章：标签分析 | 待补充 |
| `Prompt-04` | 第四章：跨平台对比 | 待补充 |
| `Prompt-05` | 第五章：可视化报告 | 待补充 |

---

## 二、批次划分

### 2.1 批次划分算法说明

批次划分基于**拓扑排序（Topological Sort）**算法：

1. **构建依赖图**：以每个 Prompt 为节点，以数据依赖关系为有向边
2. **计算入度**：统计每个节点的入度（前置依赖数量）
3. **逐层展开**：
   - 入度为 0 的节点归入当前批次
   - 移除已分配节点及其出边
   - 重复以上过程直到所有节点分配完毕
4. **并行度标注**：同一批次内的节点可并行执行，标注最大并行度
5. **批次编号**：从 Batch-0 开始顺序编号

### 2.2 批次表格

| 批次 | 任务 | 并行度 | 前置依赖 | 数据源 |
|------|------|--------|----------|--------|
| Batch-0 | Prompt-01 数据清洗 | 1（串行） | 无 | `data/online-gaming-14-04-26.csv` |
| Batch-1 | Prompt-02 热度分析 + Prompt-03 标签分析 + Prompt-04 跨平台对比 | 3（并行） | Batch-0 | `outputs/ch01_data_cleaning/ch01_cleaned_online_gaming.csv` |
| Batch-2 | Prompt-05 可视化报告 | 1（串行） | Batch-1 | 全部前序章节产物 |

> **说明**：全部章节（ch01-ch05）均已开发完成。按 Batch-0 → Batch-1 → Batch-2 顺序执行。

---

## 三、派活模板

### 模板 A：完整项目启动（从零开始）

```
【online_gaming_analysis — 任务分发】

项目路径: online_gaming_analysis/
环境: conda activate py310
规范文档: docs/flow_design.md
执行Prompt: docs/online_gaming_analysis_Execution_Prompts.md

═══ 阶段 1：串行前置 ═══
▶ Batch-0: Prompt-01 数据清洗
  - 脚本: src/ch01_data_cleaning/clean.py
  - 产物: outputs/ch01_data_cleaning/ (3个文件)
  - 完成标志: outputs/ch01_data_cleaning/ch01_cleaned_online_gaming.csv

═══ 阶段 2：3路并行 ═══（Batch-0 完成后启动）
▶ 支线 A: Prompt-02 热度分析（已开发完成）
  - 脚本: src/ch02_popularity_analysis/analysis.py
  - 依赖: ch01_cleaned_online_gaming.csv
  - 产物: outputs/ch02_popularity_analysis/ (8个文件)
▶ 支线 B: Prompt-03 标签分析（已开发完成）
  - 脚本: src/ch03_tag_analysis/analysis.py
  - 依赖: ch01_cleaned_online_gaming.csv
  - 产物: outputs/ch03_tag_analysis/ (10个文件)
▶ 支线 C: Prompt-04 跨平台对比（已开发完成）
  - 脚本: src/ch04_cross_platform/analysis.py
  - 依赖: ch01_cleaned_online_gaming.csv
  - 产物: outputs/ch04_cross_platform/ (8个文件)

═══ 阶段 3：串行收束 ═══
▶ Batch-2: Prompt-05 可视化报告（已开发完成）
  - 脚本: src/ch05_visualization/report.py
  - 依赖: 全部前序章节产物
  - 产物: outputs/ch05_visualization/ (3个文件)
```

### 模板 B：只派某个批次

```
【online_gaming_analysis — Batch-0 任务】

项目路径: online_gaming_analysis/
环境: conda activate py310

本批次: Prompt-01 [数据清洗]
前置依赖: 无（本章为起始章节）
输入数据: data/online-gaming-14-04-26.csv（TSV 格式，Tab 分隔）
输出产物: outputs/ch01_data_cleaning/
完成标志: outputs/ch01_data_cleaning/ch01_cleaned_online_gaming.csv
```

**使用说明**：
- 将 `Batch-0` 替换为实际批次编号
- 将 `Prompt-01` 替换为实际 Prompt 编号
- `前置依赖` 必须逐项列出该批次所需的全部上游产物文件
- `完成标志` 应为该批次最关键的 1~2 个产物文件名

### 模板 C：检查进度（一句话提醒）

```
检查 online_gaming_analysis 进度：
Batch-0(01) → Batch-1(02+03+04并行) → Batch-2(05)
当前应在哪个批次？哪些产物已产出？
```

---

## 四、每个 Prompt 的关键信息速查

### 4.1 速查表

| Prompt | 名称 | 输入 | 核心产物 | 后续依赖方 |
|--------|------|------|----------|-----------|
| Prompt-01 | 数据清洗 | `data/online-gaming-14-04-26.csv` | `ch01_cleaned_online_gaming.csv`, `ch01_cleaning_report.md`, `ch01_cleaning.log` | 全部后续章节 |
| Prompt-02 | 热度分析 | `ch01_cleaned_online_gaming.csv` | `ch02_popularity_stats.csv`, `ch02_popularity_analysis_report.md`, 6 PNG | ch05 |
| Prompt-03 | 标签分析 | `ch01_cleaned_online_gaming.csv` | `ch03_tag_frequency.csv`, `ch03_tag_analysis_report.md`, 7 PNG | ch05 |
| Prompt-04 | 跨平台对比 | `ch01_cleaned_online_gaming.csv` | `ch04_platform_comparison.csv`, `ch04_platform_analysis_report.md`, 5 PNG | ch05 |
| Prompt-05 | 可视化报告 | ch02-ch04 产物 | `ch05_summary_report.md`, `ch05_dashboard.png` | 无（最终产章节） |

### 4.2 速查表填写规范

| 列名 | 填写规则 |
|------|----------|
| **Prompt** | 两位数字编号，与流程设计文档章节编号对应 |
| **名称** | 章节简称（3~8字），用于快速识别 |
| **输入** | 该章节所需的全部输入数据文件，用 `+` 连接多个文件 |
| **核心产物** | 该章节最重要的 1~3 个产物文件名，用 `,` 分隔 |
| **后续依赖方** | 依赖该章节产物的下游 Prompt 编号，"全部"表示所有后续章节均依赖 |

---

## 五、注意事项

1. **严禁跳批**：每个批次必须等前置依赖全部完成后再启动
2. **数据不覆盖**：每个章节的产物写入独立的 `outputs/ch01_data_cleaning/` 目录，互不干扰
3. **脚本双格式**：每个章节提供 `.py`（批量执行）+ `.ipynb`（交互学习）
4. **全局配置共享**：所有脚本通过 `src/utils/config.py` 统一路径和参数
5. **数据格式注意**：原始数据文件扩展名为 `.csv`，但实际使用 Tab 分隔（TSV 格式），读取时需指定 `sep='\t'`
6. **编码注意**：输出 CSV 文件统一使用 UTF-8 BOM 编码，确保中文在 Excel 中正确显示
