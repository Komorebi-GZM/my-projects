# online_gaming_analysis — 流程设计文档

> **版本**: v1.0 | **更新日期**: 2026-04-25 | **配套执行文档**: `online_gaming_analysis_Execution_Prompts.md`

---

## 文档说明

本文档为**全流程标准化数据分析研究框架**，严格遵循在线小游戏数据分析、热度挖掘、标签体系规范化、跨平台差异分析的学术规范。每一章节明确：**研究目标 → 数据输入 → 技术方法 → 实施步骤 → 阶段产物 → 质量标准**，可直接作为课程论文、实训报告、数据分析结题文档原稿使用。

**与执行Prompt文档的关系**：本文档定义"做什么、为什么、用什么方法"；配套的Prompt文档定义"怎么做——精确到函数、参数、代码级别"。两份文档配合使用：先阅读本文档理解全貌，再参照Prompt文档逐步执行。

**与 task_dispatch_guide.md 的关系**：
- 本文档（flow_design.md）= **研究设计文档**，面向读者/评审者，描述"做什么、为什么、用什么方法"
- task_dispatch_guide.md = **执行操作手册**，面向执行者，描述"怎么做、按什么顺序、怎么派活"
- 修改本文档的章节目标或方法后，需同步检查 execution_prompts.md 和 dispatch_guide.md 是否需要更新

---

## 第一章 研究概述

### 1.1 研究背景

在线小游戏（Online Games）已成为全球互联网娱乐生态的重要组成部分。Poki 和 Newgrounds 作为两大知名在线小游戏平台，汇聚了大量来自独立开发者和小型工作室的游戏作品。对这些平台上的游戏数据进行系统化分析，能够揭示以下关键问题：

1. **游戏热度挖掘**：哪些游戏最受欢迎？热度指标（播放量、点赞数、评分等）的分布特征如何？是否存在"头部效应"？
2. **标签体系规范化**：不同平台、不同开发者使用的游戏标签（tags）存在命名不统一、大小写混杂、分隔符不一致等问题。构建统一的标签体系是后续分类分析、推荐系统的基础。
3. **跨平台差异分析**：Poki 和 Newgrounds 两个平台在游戏类型分布、用户偏好、评分机制等方面是否存在显著差异？这些差异对游戏开发者有何启示？

本次研究采用 **Poki + Newgrounds 双平台在线小游戏数据集**，数据覆盖两个主流在线小游戏平台，具备 **多平台、多维度、真实用户行为** 特征，可真实反映在线小游戏市场的竞争格局和用户偏好。

### 1.2 数据集基础概况

| 维度 | 说明 |
|------|------|
| 数据量(行) | 11,406 条 |
| 数据列数 | 8 列 |
| 数据格式 | TSV（Tab 分隔，扩展名 .csv） |
| 数据来源 | Poki.com + Newgrounds.com 双平台 |
| 分析实体 | 游戏（game） |
| 编码 | 待确认（清洗阶段检测） |
| 缺失情况 | 待清洗阶段检测 |

**数据特征**：
- 双平台数据合并，source 列标识来源平台（poki / newgrounds）
- 包含游戏描述（description）和标签（tags）等文本字段
- 包含用户互动指标（播放量、点赞数等），可计算衍生指标（如 like_ratio）
- 数据可能存在重复行、缺失值、标签格式不统一等质量问题

### 1.3 整体研究逻辑

以 Poki + Newgrounds 双平台在线小游戏数据为核心，依次完成以下分析环节：

```
数据清洗(ch01) → 热度分析(ch02) → 标签分析(ch03) → 跨平台对比(ch04) → 可视化报告(ch05)
     ↓               ↓               ↓               ↓               ↓
  清洗后数据集     热度统计表       标签体系         平台差异         最终报告
```

**章节间数据依赖关系**：
- 第一章（数据清洗）是全部后续章节的基础，必须最先完成
- 第二章（热度分析）依赖第一章的清洗后数据集
- 第三章（标签分析）依赖第一章的清洗后数据集
- 第四章（跨平台对比）依赖第一至三章的分析结果
- 第五章（可视化报告）依赖全部前序章节的产物

### 1.4 整体研究产出总览

| 序号 | 产出类别 | 具体内容 | 产出形式 |
|------|----------|----------|----------|
| 1 | 清洗后数据集 | 统一格式、高质量的分析数据集 | CSV |
| 2 | 数据质量报告 | 清洗过程记录与质量验证 | Markdown |
| 3 | 热度分析 | 游戏热度统计与分布特征 | CSV + PNG |
| 4 | 标签分析 | 标签体系构建与分类统计 | CSV + PNG |
| 5 | 跨平台对比 | Poki vs Newgrounds 差异分析 | CSV + PNG |
| 6 | 可视化报告 | 综合分析报告与图表 | Markdown + PNG |

**预计总产出**：15+ 个文件（6 数据 + 6 图片 + 3 报告）

### 1.5 技术环境与依赖

- **Python**: 3.10（conda 环境 `py310`）
- **执行方式**: 每个章节均提供 **Python 脚本 (.py) + Jupyter Notebook (.ipynb)** 两种格式，按章节编号命名（如 `src/ch01_data_cleaning/clean.py`、`src/ch01_data_cleaning/clean.ipynb`），支持批量执行和交互式调试
- **环境管理**: 使用 conda 环境 `py310`，激活命令 `conda activate py310`，通过 `pip install -r requirements.txt` 安装全部依赖。**禁止创建 venv 目录**
- **核心依赖**: pandas, numpy, matplotlib, seaborn
- **完整依赖清单**: 见 `requirements.txt`

---

## 第二章 数据集概况与数据清洗预处理（ch01）

> **章节类型**: 原型 A — 数据预处理型
> **对应 Prompt**: Prompt-01

### 2.1 研究目标

厘清 Poki + Newgrounds 双平台在线小游戏原始数据的基本属性，解决以下核心问题：

1. **重复数据问题**：原始数据中可能存在完全重复的行，需要检测并去除
2. **缺失值问题**：description、tags 等关键字段可能存在缺失，需要检测并处理
3. **文本清洗问题**：description 和 tags 字段可能包含多余空格、特殊字符、大小写不统一等问题
4. **标签规范化问题**：tags 字段的格式可能不一致（分隔符、大小写、空格等），需要统一规范化
5. **异常值问题**：数值型字段（如播放量、点赞数）可能存在异常值，需要检测和校验
6. **特征工程**：基于现有字段计算衍生指标（如 like_ratio = likes / plays），为后续分析提供更多维度

最终目标是构建一份统一格式、高质量、可直接用于后续分析的标准数据集。

### 2.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 原始游戏数据 | `data/online-gaming-14-04-26.csv` | TSV（Tab 分隔） | Poki + Newgrounds 双平台合并数据，11,406 行，8 列 |

### 2.3 技术方法

| 处理环节 | 方法 | 公式/参数 | 选择理由 |
|----------|------|-----------|----------|
| 重复值处理 | 完全重复行检测与去除 | `df.duplicated()` | 确保每条游戏记录唯一 |
| 缺失值处理 | description/tags 缺失值填充 | 填充为 "unknown" / 空列表 | 保留记录完整性，避免丢失数据 |
| 文本清洗 | 去除前后空格、统一大小写 | `str.strip()`, `str.lower()` | 消除格式不一致问题 |
| 标签规范化 | 统一分隔符、小写、去空格 | `str.split()`, `str.lower()` | 构建统一标签体系的基础 |
| 异常值校验 | 数值范围检查、逻辑一致性验证 | `df.describe()`, 条件过滤 | 确保数据质量 |
| 特征工程 | like_ratio 计算 | `like_ratio = likes / plays` | 量化游戏用户满意度 |

**替代方法**：
- 缺失值处理：删除缺失行（可能丢失过多数据）、KNN 填充（对文本字段不适用）
- 标签规范化：TF-IDF 向量化（适合机器学习，不适合标签体系构建）
- 异常值检测：IQR 方法（对偏态分布更鲁棒）、孤立森林（无监督方法）

### 2.4 实施步骤

1. **数据读取与结构探查** — 读取 TSV 格式原始数据，检查行数、列数、数据类型、缺失值分布、数值范围，形成对数据的整体认知
2. **重复值检测与处理** — 使用 `df.duplicated()` 检测完全重复行，统计重复数量，去除重复后验证行数变化
3. **缺失值检测与处理** — 统计每列缺失率，对 description 字段缺失值填充为 "unknown"，对 tags 字段缺失值填充为空列表
4. **文本字段清洗** — 对 description 字段去除前后空格、统一换行符；对 tags 字段去除前后空格
5. **标签规范化** — 将 tags 统一转换为小写、使用逗号分隔、去除标签内前后空格和特殊字符
6. **异常值校验** — 检查数值型字段的范围是否合理（如播放量、点赞数不应为负值），检查 like_ratio 是否在 [0, 1] 范围内
7. **特征工程** — 计算 like_ratio（likes / plays），处理除零情况（plays=0 时 like_ratio 设为 NaN）
8. **数据质量报告生成** — 汇总全部处理结果，生成清洗报告和日志文件

### 2.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | **清洗后数据集** | `ch01_cleaned_online_gaming.csv` | CSV (UTF-8 BOM) | Prompt-02, 03, 04, 05 |
| 2 | **数据清洗报告** | `ch01_cleaning_report.md` | Markdown | 参考 |
| 3 | **清洗日志** | `ch01_cleaning.log` | LOG | 调试参考 |

### 2.6 质量验证标准

- [ ] 清洗后数据无完全重复行
- [ ] 所有 description 和 tags 字段无 NaN
- [ ] 所有标签均为小写、无特殊字符（已规范化）
- [ ] game_id 唯一且连续（1~N）
- [ ] source 列值仅为 'poki' 或 'newgrounds'
- [ ] like_ratio 在 [0, 1] 范围内（NaN 除外）
- [ ] 输出 CSV 编码为 UTF-8 BOM
- [ ] 脚本可在 `conda activate py310` 下无报错运行

---

## 第三章 热度分析（ch02）

> **章节类型**: 原型 B — 统计描述型
> **对应 Prompt**: Prompt-02

### 3.1 研究目标

揭示 Poki + Newgrounds 双平台游戏热度分布特征，识别头部效应，发现关键热度指标之间的关系。

### 3.2 数据输入

清洗后的标准数据集 `outputs/ch01_data_cleaning/ch01_cleaned_online_gaming.csv`。

### 3.3 技术方法

| 分析环节 | 方法 | 说明 |
|----------|------|------|
| 基本统计 | 描述性统计 | 均值、中位数、标准差、分位数 |
| 分布分析 | 直方图 + 箱线图 | 平台分布对比（对数坐标） |
| 头部效应 | Pareto 分析 | 累计占比曲线、Gini 系数 |
| 排名分析 | Top N 排序 | 按点赞数排序 |
| 相关性 | Pearson 相关系数 | 热度指标间相关性矩阵 |

### 3.4 阶段产物

| 序号 | 产物名称 | 文件名 |
|------|----------|--------|
| 1 | 热度统计表 | `ch02_popularity_stats.csv` |
| 2 | Top 20 游戏排名 | `ch02_top20_games.csv` |
| 3 | 分平台统计表 | `ch02_platform_stats.csv` |
| 4 | 点赞数分布图 | `ch02_likes_distribution.png` |
| 5 | 点赞率分布图 | `ch02_like_ratio_distribution.png` |
| 6 | 点赞 vs 踩散点图 | `ch02_likes_vs_dislikes.png` |
| 7 | 头部效应分析图 | `ch02_head_effect.png` |
| 8 | 热度分析报告 | `ch02_popularity_analysis_report.md` |

---

## 第四章 标签分析（ch03）

> **章节类型**: 原型 C — 文本分析型
> **对应 Prompt**: Prompt-03

### 4.1 研究目标

对游戏标签进行系统化分析，包括标签频率统计、共现关系挖掘、平台标签偏好对比，构建标签体系的完整画像。

### 4.2 数据输入

清洗后的标准数据集 `outputs/ch01_data_cleaning/ch01_cleaned_online_gaming.csv`。

### 4.3 技术方法

| 分析环节 | 方法 | 说明 |
|----------|------|------|
| 频率统计 | Counter | 标签出现次数统计 |
| 长尾分析 | 累计占比曲线 | 标签集中度分析 |
| 共现分析 | 共现矩阵 | 标签共同出现频次 |
| 热力图 | 矩阵可视化 | Top N 标签共现热力图 |
| 平台对比 | 分组统计 | Poki vs Newgrounds 标签偏好 |

### 4.4 阶段产物

| 序号 | 产物名称 | 文件名 |
|------|----------|--------|
| 1 | 标签频率统计表 | `ch03_tag_frequency.csv` |
| 2 | Poki 标签表 | `ch03_tags_poki.csv` |
| 3 | Newgrounds 标签表 | `ch03_tags_newgrounds.csv` |
| 4 | Top 20 标签柱状图 | `ch03_top20_tags.png` |
| 5 | 标签长尾分布图 | `ch03_tag_long_tail.png` |
| 6 | 共现热力图 | `ch03_cooccurrence_top20.png` |
| 7 | 共现对柱状图 | `ch03_top20_cooccurrence_pairs.png` |
| 8 | 标签数量分布图 | `ch03_tag_count_distribution.png` |
| 9 | 平台标签偏好对比 | `ch03_platform_tag_comparison.png` |
| 10 | 标签分析报告 | `ch03_tag_analysis_report.md` |

---

## 第五章 跨平台对比（ch04）

> **章节类型**: 原型 D — 对比分析型
> **对应 Prompt**: Prompt-04

### 5.1 研究目标

系统对比 Poki 和 Newgrounds 两个平台在热度指标、标签体系、用户互动等方面的差异，通过统计检验验证差异显著性。

### 5.2 数据输入

清洗后的标准数据集 `outputs/ch01_data_cleaning/ch01_cleaned_online_gaming.csv`。

### 5.3 技术方法

| 分析环节 | 方法 | 说明 |
|----------|------|------|
| 描述性对比 | 分组统计 | 各平台指标均值、中位数 |
| 统计检验 | Mann-Whitney U | 非参数检验，验证差异显著性 |
| 分布对比 | 重叠直方图 | 同一指标两平台分布对比 |
| 相关性对比 | 散点图 | 分平台的指标关系 |

### 5.4 阶段产物

| 序号 | 产物名称 | 文件名 |
|------|----------|--------|
| 1 | 平台对比统计表 | `ch04_platform_comparison.csv` |
| 2 | 统计检验结果表 | `ch04_statistical_tests.csv` |
| 3 | 指标对比箱线图 | `ch04_metric_comparison.png` |
| 4 | 点赞率分布对比 | `ch04_like_ratio_comparison.png` |
| 5 | 点赞数分布对比 | `ch04_likes_dist_comparison.png` |
| 6 | 标签数量分布对比 | `ch04_tag_count_comparison.png` |
| 7 | 相关性散点图 | `ch04_platform_correlation.png` |
| 8 | 跨平台分析报告 | `ch04_platform_analysis_report.md` |

---

## 第六章 可视化报告（ch05）

> **章节类型**: 原型 E — 综合报告型
> **对应 Prompt**: Prompt-05

### 6.1 研究目标

汇总全部前序章节的分析结果，生成综合可视化仪表板和总结性报告，为项目交付提供一站式文档。

### 6.2 数据输入

全部前序章节分析产物。

### 6.3 技术方法

| 分析环节 | 方法 | 说明 |
|----------|------|------|
| 综合仪表板 | 9 宫格 GridSpec | 关键图表集中展示 |
| 汇总图表 | 分组柱状图 | 平台关键指标对比 |
| 综合分析 | 多维度总结 | 热度 + 标签 + 跨平台 |

### 6.4 阶段产物

| 序号 | 产物名称 | 文件名 |
|------|----------|--------|
| 1 | 综合仪表板 | `ch05_dashboard.png` |
| 2 | 汇总图表 | `ch05_summary_chart.png` |
| 3 | 综合报告 | `ch05_summary_report.md` |

---

## 附录

### 附录A: 项目文件目录结构

```
online_gaming_analysis/
├── data/                              # 原始数据
│   └── online-gaming-14-04-26.csv
├── src/                               # Python 源代码
│   ├── utils/                         # 通用工具模块
│   │   ├── __init__.py
│   │   ├── config.py                  # 全局配置
│   │   ├── data_loader.py             # 数据加载器
│   │   ├── output_manager.py          # 输出产物管理器
│   │   └── task_graph.py              # 任务依赖图
│   └── ch01_data_cleaning/            # 第一章：数据清洗
│       ├── __init__.py
│       ├── clean.py                   # Python 脚本
│       └── clean.ipynb                # Jupyter Notebook
├── outputs/                           # 全部输出产物
│   └── ch01_data_cleaning/            # 第一章产物
│       ├── ch01_cleaned_online_gaming.csv
│       ├── ch01_cleaning_report.md
│       └── ch01_cleaning.log
├── docs/                              # 文档
│   ├── project_convention.md          # 项目规范
│   ├── flow_design.md                 # 本文档
│   ├── task_dispatch_guide.md         # 任务分发指南
│   └── online_gaming_analysis_Execution_Prompts.md  # 执行Prompt文档
└── requirements.txt                   # 依赖清单
```

### 附录B: 文件命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 数据文件 | `ch{NN}_{描述}.csv` | `ch01_cleaned_online_gaming.csv` |
| 图片文件 | `ch{NN}_{描述}.png` | `ch02_popularity_distribution.png` |
| 报告文件 | `ch{NN}_{描述}.md` | `ch01_cleaning_report.md` |
| 日志文件 | `ch{NN}_{描述}.log` | `ch01_cleaning.log` |

### 附录C: 全局可复用Skill库

| Skill | 名称 | 适用章节 | 核心功能 |
|-------|------|----------|----------|
| Skill-01 | 标准数据加载器 | 全部章节 | `load_raw_data()`, `load_preprocessed()` |
| Skill-02 | 标准可视化出图器 | ch02~ch05 | `plot_bar()`, `plot_heatmap()`, `plot_distribution()` |
| Skill-03 | 标准评估指标计算器 | ch02~ch04 | `calc_statistics()`, `compare_groups()` |
| Skill-04 | 标准输出产物管理器 | 全部章节 | `save_dataframe()`, `save_figure()`, `save_markdown()` |

### 附录D: 完整依赖清单

```
pandas              # 数据处理与分析
numpy               # 数值计算
matplotlib          # 基础可视化
seaborn             # 高级统计可视化
```

### 已知版本兼容性约束

| 约束 | 说明 | 推荐处理 |
|------|------|----------|
| pandas + numpy | pandas 2.x 需要 numpy >= 1.20 | 使用 requirements.txt 锁定版本 |
| matplotlib 中文显示 | 默认不支持中文 | 配置 `plt.rcParams['font.sans-serif']` 或安装中文字体 |
| seaborn + matplotlib | seaborn 依赖 matplotlib 版本 | 使用 requirements.txt 锁定版本 |
