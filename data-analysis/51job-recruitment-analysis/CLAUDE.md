# 51job招聘数据分析项目 - CLAUDE.md

## 项目概述

本项目基于51job平台295条Python开发岗位招聘数据，进行人才市场全维度分析。通过对招聘数据的深入挖掘，揭示Python开发岗位的市场需求、薪资水平、技能要求等关键洞察，为求职者和招聘方提供数据驱动的决策支持。

---

## 关键文件索引

### 项目文档

| 文件路径 | 说明 |
|---------|------|
| `docs/project_convention.md` | 项目规范文档 - 定义目录结构、命名规范、脚本规范、环境配置等 |
| `docs/flow_design.md` | 研究设计文档 - 各章节研究目标、数据输入、技术方法、实施步骤、质量标准 |
| `docs/51job_recruitment_analysis_Execution_Prompts.md` | 执行Prompt文档 - 五段式可执行指令（任务概述→执行步骤→产物总览→优化方向→异常处理） |
| `docs/task_dispatch_guide.md` | 任务分发指南 - 全局依赖DAG图、并行批次划分、派活模板 |

### 核心代码

| 文件路径 | 说明 |
|---------|------|
| `src/utils/task_graph.py` | 任务依赖图 - 定义章节间依赖关系，支持拓扑排序和并行批次生成 |

---

## 代码规范

### 格式规范
- **行长度**: 每行代码不超过88个字符
- **文档字符串**: 采用Google风格docstring

### 文件命名规范
- **产物文件前缀**: 所有产物文件必须添加 `ch{NN}_` 前缀（如 `ch01_data_overview.py`）
- **双格式要求**: 每章节必须同时提供 `.py` 和 `.ipynb` 两种格式

### 编码规范
- **禁止硬编码参数**: 所有可配置参数必须通过配置文件或命令行参数传入
- **禁止使用绝对路径**: 使用相对路径或配置化的路径管理

---

## 禁止事项

1. **禁止修改 `data/` 目录** - 原始数据为只读，不得修改
2. **禁止跨章节写入产物** - 各章节产物只能写入本章节目录
3. **禁止根目录散落文件** - 所有文件必须按规范存放在对应目录
4. **禁止跳过依赖执行** - 必须按依赖顺序执行章节任务
5. **禁止硬编码参数** - 参数必须通过配置传入
6. **禁止使用绝对路径** - 使用相对路径或配置化路径

---

## 薪资单位约定

**重要**: 所有薪资相关字段统一使用 `"万/月"` 作为单位。

- 数据字段: `salary_min`, `salary_max`, `salary_avg` 单位均为 "万/月"
- 图表标签: 必须使用 "万/月" 而非 "千/月"
- 报告文本: 统一使用 "万/月" 描述薪资水平

---

## 环境信息

- **Python版本**: Python 3.10
- **Conda环境**: `py310`
- **依赖安装**:
  ```bash
  pip install -r requirements.txt
  ```

---

## 快速开始

1. 激活conda环境:
   ```bash
   conda activate py310
   ```

2. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

3. 查看任务依赖图:
   ```bash
   python src/utils/task_graph.py
   ```

4. 按章节顺序执行分析任务（参考 `docs/task_dispatch_guide.md`）

---

## 项目结构

```
51job_recruitment_analysis/
├── CLAUDE.md              # 本文件 - 项目指南
├── docs/                  # 项目文档
│   ├── project_convention.md
│   ├── flow_design.md
│   ├── 51job_recruitment_analysis_Execution_Prompts.md
│   └── task_dispatch_guide.md
├── src/                   # 源代码
│   └── utils/
│       └── task_graph.py
├── data/                  # 原始数据（只读）
├── chapters/              # 各章节产物
├── requirements.txt       # 依赖列表
└── README.md             # 项目说明
```

---

*最后更新: 2026-05-05*
