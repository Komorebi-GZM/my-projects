# ch03 文本挖掘与情感分析 — 一键启动说明

> **Batch-2 | Prompt-03 | TDD Workflow**
> 本文档是 ch03 章节的完整操作手册，包含环境要求、输入输出明细、一键启动步骤。

---

## 一、快速开始（3 步搞定）

```bash
# 第 1 步：将整个项目文件夹复制到目标电脑
# （确保 financial_news_sentiment_analysis/ 完整复制）

# 第 2 步：打开终端，进入项目目录
cd financial_news_sentiment_analysis

# 第 3 步：一键启动
bash run_ch03.sh
```

脚本会自动完成：**环境检查 → 依赖安装 → 模型训练 → 产物验证**。

---

## 二、输入明细

| 项目 | 说明 |
|------|------|
| **输入数据** | `outputs/ch01_data_preprocessing/ch01_cleaned_data.csv` |
| **数据规模** | 139,919 行 × 24 列 |
| **关键列** | `full_text`（新闻全文）、`date`（日期）、`categories_list`（分类列表） |
| **前置依赖** | ch01 数据预处理已完成（文件已存在） |
| **参考文档** | `outputs/ch02_descriptive_stats/ch02_descriptive_stats_report.md` |

### 输入数据列说明（与本章节相关的列）

| 列名 | 类型 | 用途 |
|------|------|------|
| `full_text` | str | FinBERT 情感分析的输入文本 |
| `date` | str (YYYY-MM-DD) | 情感时序分析的时间轴 |
| `categories_list` | list[str] | 行业情感交叉分析的分组依据 |
| `year` / `month` | int | 时间维度聚合 |

---

## 三、输出明细（10 个产物）

所有产物输出到 `outputs/ch03_text_mining_sentiment/` 目录。

### 3.1 数据文件（2 个 CSV）

| # | 文件名 | 格式 | 说明 | 后续使用 |
|---|--------|------|------|----------|
| 1 | `ch03_sentiment_labels.csv` | CSV | 每条新闻的情感标签、置信度、情感得分 | ch04, ch05 |
| 2 | `ch03_topic_model_results.csv` | CSV | 每条新闻的主题 ID 和概率 | ch04 |

**ch03_sentiment_labels.csv 列定义：**

| 列名 | 类型 | 取值范围 | 说明 |
|------|------|----------|------|
| `sentiment` | str | positive / negative / neutral | FinBERT 情感标签 |
| `confidence` | float | 0.0 ~ 1.0 | 模型置信度 |
| `sentiment_score` | int | -1 / 0 / 1 | 数值化情感（positive=1, neutral=0, negative=-1） |

**ch03_topic_model_results.csv 列定义：**

| 列名 | 类型 | 取值范围 | 说明 |
|------|------|----------|------|
| `topic_id` | int | -1, 0, 1, ..., N | 主题编号（-1 = outlier） |
| `topic_prob` | float | 0.0 ~ 1.0 | 属于该主题的概率 |

### 3.2 图表文件（5 个 PNG）

| # | 文件名 | 尺寸 | DPI | 说明 |
|---|--------|------|-----|------|
| 3 | `ch03_sentiment_distribution.png` | 8×6 in | 300 | 情感分布饼图（positive/neutral/negative 占比） |
| 4 | `ch03_sentiment_by_category.png` | 16×6 in | 300 | Top10 行业情感得分箱线图 |
| 5 | `ch03_sentiment_timeline.png` | 14×10 in | 300 | 月度情感趋势 + 事件窗口标注 |
| 6 | `ch03_event_window_sentiment.png` | 14×6 in | 300 | COVID-19 / 俄乌战争事件窗口情感变化 |
| 7 | `ch03_topic_timeline_heatmap.png` | 16×8 in | 300 | 主题热度月度时序热力图 |

### 3.3 交互式可视化（1 个 HTML）

| # | 文件名 | 说明 |
|---|--------|------|
| 8 | `ch03_topic_visualization.html` | BERTopic 交互式主题距离可视化（浏览器打开） |

### 3.4 分析报告（2 个 Markdown）

| # | 文件名 | 说明 |
|---|--------|------|
| 9 | `ch03_sentiment_analysis_report.md` | 情感分析完整报告（分布、行业对比、时序、事件窗口、置信度） |
| 10 | `ch03_topic_analysis_report.md` | 主题分析完整报告（BERTopic 主题详情、LDA 对比、Coherence Score） |

---

## 四、输出规范与质量标准

### 4.1 文件命名规范
- 所有产物文件以 `ch03_` 为前缀
- 数据文件: `ch03_{描述}.csv`
- 图片文件: `ch03_{描述}.png`
- 报告文件: `ch03_{描述}.md`

### 4.2 图片规范
- DPI >= 150（实际输出 300 DPI 高清）
- 格式: PNG
- 配色: 专业学术风格

### 4.3 质量标准

| 指标 | 标准 | 验证方式 |
|------|------|----------|
| 情感标签覆盖率 | = 100% | test_ch03.py 自动验证 |
| 情感分布合理性 | 任一类别占比 < 80% | test_ch03.py 自动验证 |
| 主题数量 | 8 ~ 15 个 | test_ch03.py 自动验证 |
| LDA Coherence Score | >= 0.4（理想值） | 报告中记录 |
| 产物总数 | >= 10 个 | test_ch03.py 自动验证 |

---

## 五、运行方式详解

### 5.1 完整执行（推荐首次使用）

```bash
bash run_ch03.sh
```

自动完成 4 个阶段：
1. **Phase 0**: 环境检查（Python 版本、GPU、磁盘空间、输入数据）
2. **Phase 1**: 依赖安装（torch, transformers, bertopic, spacy 等）
3. **Phase 2**: 模型训练（FinBERT 情感分析 + BERTopic 主题建模 + LDA 对比）
4. **Phase 3**: 产物验证（自动运行 test_ch03.py 检查全部 10 个产物）

### 5.2 跳过依赖安装（已安装过依赖时）

```bash
bash run_ch03.sh --skip-deps
```

### 5.3 仅验证产物（训练完成后检查）

```bash
bash run_ch03.sh --test-only
```

### 5.4 手动执行（调试用）

```bash
# 直接运行 Python 脚本
python src/ch03_text_mining_sentiment/sentiment.py

# 仅运行测试
python src/ch03_text_mining_sentiment/test_ch03.py
```

### 5.5 环境变量控制

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `CH03_SAMPLE_FRACTION` | 1.0 | 采样比例（0.5 = 50% 数据，加速调试） |
| `HF_ENDPOINT` | https://huggingface.co | HuggingFace 模型下载地址 |
| `TMPDIR` | /tmp | 临时文件目录 |

**示例 — 使用 50% 采样快速测试：**
```bash
CH03_SAMPLE_FRACTION=0.5 bash run_ch03.sh --skip-deps
```

---

## 六、训练流程与耗时预估

### 6.1 六步训练流程

```
Step 1: FinBERT 模型加载        →  首次需下载模型 (~420MB)
Step 2: 全量情感标签生成        →  139,919 条新闻逐批推理
Step 3: 情感分布统计 + 行业分析 →  生成饼图 + 箱线图
Step 4: 情感时序演变 + 事件分析 →  生成趋势图 + 事件窗口图
Step 5: BERTopic 主题建模       →  文本预处理 + 自动主题聚类
Step 6: LDA 对比 + 报告生成     →  LDA 训练 + Coherence 评估 + 报告
```

### 6.2 耗时预估

| 环境 | batch_size | FinBERT 推理 | BERTopic | 总计 |
|------|-----------|-------------|----------|------|
| **GPU (推荐)** | 32 | ~15 分钟 | ~10 分钟 | **~30 分钟** |
| **CPU** | 8 | ~2 小时 | ~30 分钟 | **~3 小时** |
| CPU + 50% 采样 | 8 | ~1 小时 | ~20 分钟 | ~1.5 小时 |

### 6.3 资源需求

| 资源 | 最低要求 | 推荐配置 |
|------|----------|----------|
| 内存 | 8 GB | 16 GB |
| 磁盘 | 5 GB | 10 GB（含模型缓存） |
| GPU | 无（CPU 可运行） | NVIDIA GPU + CUDA |

---

## 七、目录结构

```
financial_news_sentiment_analysis/
├── run_ch03.sh                              # 一键启动脚本（入口）
├── README_CH03.md                           # 本说明文档
│
├── src/
│   ├── utils/
│   │   ├── config.py                        # 全局配置（路径、图表参数）
│   │   ├── data_loader.py                   # 数据加载器
│   │   ├── output_manager.py                # 输出管理器
│   │   └── task_graph.py                    # 任务依赖图
│   └── ch03_text_mining_sentiment/
│       ├── __init__.py                      # 包初始化
│       ├── sentiment.py                     # 主分析脚本（6 步训练）
│       └── test_ch03.py                     # 产物验证测试（TDD）
│
├── outputs/
│   ├── ch01_data_preprocessing/             # [输入] 清洗后数据
│   │   └── ch01_cleaned_data.csv
│   ├── ch02_descriptive_stats/              # [参考] 描述统计报告
│   │   └── ch02_descriptive_stats_report.md
│   └── ch03_text_mining_sentiment/          # [输出] 本章产物
│       ├── ch03_sentiment_labels.csv        #   情感标签
│       ├── ch03_topic_model_results.csv     #   主题分类
│       ├── ch03_sentiment_distribution.png  #   情感饼图
│       ├── ch03_sentiment_by_category.png   #   行业情感图
│       ├── ch03_sentiment_timeline.png      #   时序趋势图
│       ├── ch03_event_window_sentiment.png  #   事件窗口图
│       ├── ch03_topic_visualization.html    #   主题可视化
│       ├── ch03_topic_timeline_heatmap.png  #   主题热力图
│       ├── ch03_sentiment_analysis_report.md #  情感报告
│       └── ch03_topic_analysis_report.md    #  主题报告
│
├── data/
│   └── stock_news_2016 to 2026.csv          # 原始数据（只读）
│
├── docs/                                     # 项目文档
│   ├── project_convention.md                # 项目规范
│   ├── flow_design.md                       # 研究设计
│   └── financial_news_sentiment_analysis_Execution_Prompts.md
│
└── requirements.txt                         # Python 依赖清单
```

---

## 八、常见问题

### Q1: HuggingFace 模型下载失败怎么办？
脚本会自动检测网络连通性，如果直连超时会自动切换到镜像站 `hf-mirror.com`。
也可手动设置：
```bash
export HF_ENDPOINT=https://hf-mirror.com
bash run_ch03.sh --skip-deps
```

### Q2: 训练中断了怎么办？
重新运行 `bash run_ch03.sh --skip-deps` 即可。脚本会覆盖已有产物重新生成。

### Q3: 如何验证训练结果是否正确？
```bash
bash run_ch03.sh --test-only
```
测试通过 = 全部 10 个产物合格。

### Q4: GPU 内存不足怎么办？
脚本会自动检测 GPU 并设置 batch_size=32。如果仍然 OOM，可手动降低：
```bash
# 编辑 src/ch03_text_mining_sentiment/sentiment.py
# 将 batch_size = 32 改为 batch_size = 16 或 8
```

### Q5: 如何查看训练进度？
训练过程中终端会显示：
- FinBERT 推理进度条（tqdm）
- BERTopic 训练日志
- LDA Coherence Score 实时输出
- 日志文件：`logs/ch03_sentiment.log`

---

## 九、训练完成后

1. **检查产物**: 运行 `bash run_ch03.sh --test-only` 确认全部通过
2. **查看报告**: 用任意 Markdown 阅读器打开 `outputs/ch03_text_mining_sentiment/` 下的两个 `.md` 报告
3. **查看可视化**: 浏览器打开 `ch03_topic_visualization.html`
4. **下一步**: 将产物目录 `outputs/ch03_text_mining_sentiment/` 复制回原项目，继续执行 Batch-3 (ch04 特征工程)
