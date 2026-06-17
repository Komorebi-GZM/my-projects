# 金融新闻舆情分析与市场预测 — 流程设计文档

> **版本**: v1.0 | **更新日期**: 2026-05-04 | **配套执行文档**: `docs/financial_news_sentiment_analysis_Execution_Prompts.md`
> **目标依据**: `docs/analysis_goals.md`（本文档为该目标文档的下位设计，所有研究目标均源自该文档）

---

## 文档说明

本文档为**全流程标准化金融新闻舆情分析研究框架**，严格遵循金融文本挖掘、情感分析、主题建模、特征工程、事件分析的学术规范。每一章节明确：**研究目标 → 数据输入 → 技术方法 → 实施步骤 → 阶段产物 → 质量标准**，可直接作为课程论文、实训报告、数据分析结题文档原稿使用。

**与执行Prompt文档的关系**：本文档定义"做什么、为什么、用什么方法"；配套的Prompt文档定义"怎么做——精确到函数、参数、代码级别"。两份文档配合使用：先阅读本文档理解全貌，再参照Prompt文档逐步执行。

**与 task_dispatch_guide.md 的关系**：
- 本文档（flow_design.md）= **研究设计文档**，面向读者/评审者，描述"做什么、为什么、用什么方法"
- task_dispatch_guide.md = **执行操作手册**，面向执行者，描述"怎么做、按什么顺序、怎么派活"
- 修改本文档的章节目标或方法后，需同步检查 execution_prompts.md 和 task_dispatch_guide.md 是否需要更新

**关于 ch05（股价预测建模）**：因数据集不含 OHLCV 行情数据，ch05 已在 `analysis_goals.md` 中明确移除。本文档不包含 ch05 章节，依赖关系为 ch04 → ch05。详见附录A。

---

## 第一章 研究概述

### 1.1 研究背景

金融新闻是市场情绪的重要载体，系统化挖掘新闻舆情有助于理解市场行为。本数据集收录 2016-2026 年印度金融市场每日财经新闻，覆盖宏观经济、行业动态、公司财报、地缘政治等多个维度。数据适用于金融文本挖掘、舆情监控、事件驱动分析等研究场景。

当前数据集时间跨度长（10年）、覆盖面广（17个分类、414个关键词），具备深度挖掘价值。需要建立标准化的金融新闻分析流程，为后续量化研究奠定基础。

本次研究采用**印度金融市场新闻数据集**，数据覆盖**17个行业/事件分类**和**414个核心财经关键词**，具备**10年跨度、多维度标签、多来源覆盖**特征，可真实反映**印度金融市场的新闻舆情生态**。

### 1.2 数据集基础概况

| 维度 | 值 |
|------|-----|
| 数据量(行) | 139,919 |
| 列数 | 24 |
| 时间范围 | 2016-01-01 ~ 2026-04-15 |
| 采样间隔 | 日频（新闻发布日期） |
| 分析实体数 | 17个行业/事件分类 |
| 数据类型 | 文本（title, description, full_text）、分类（categories, impact_tier）、数值（relevance_score）、布尔（has_negation） |
| 缺失率 | 0%（全量无缺失） |
| 数值量级 | relevance_score: 1-11; text_length: 21-623字符 |
| 特殊说明 | 2021年数据量骤降（仅3,548条），时序分析需注意 |

**数据特征**：
- 全量无缺失值、无重复记录
- 多标签分类（categories 字段可含多个分类，原始组合366种）
- 多关键词标注（matched_keywords 字段可含多个关键词）
- 影响等级三级分布（LOW 41.0%、MEDIUM 56.8%、HIGH 2.2%）
- 7个数据来源，主来源占47.1%
- 英文文本，平均长度156.8字符/条

### 1.3 整体研究逻辑

以**139,919条印度金融新闻**为核心，依次完成**6大分析环节**：

```
ch01 数据预处理 → ch02 描述性统计分析 → ch03 文本挖掘与情感分析 → ch04 特征工程 → ch05 事件驱动分析 → ch06 看板与总结
       ↓                    ↓                       ↓                      ↓                 ↓                    ↓
   清洗数据集          统计图表+报告          情感标签+主题分类          日频特征表        事件日历+评分        看板+综合报告
```

**章节间数据依赖关系**：
- 第一章（ch01 数据预处理）是全部后续章节的基础，必须最先完成 ✅ 已完成
- ch02（描述性统计）依赖 ch01 清洗后数据
- ch03（文本挖掘与情感分析）依赖 ch01 清洗后数据 + ch02 描述统计报告
- ch04（特征工程）依赖 ch01 清洗后数据 + ch03 情感标签 + ch03 主题分类
- ch05（事件驱动分析）依赖 ch01-ch04 全部产物（注意：不依赖已移除的 ch05）
- ch06（看板与总结）依赖 ch01-ch04、ch05 全部产物

### 1.4 整体研究产出总览

| 序号 | 产出类别 | 具体内容 | 产出形式 |
|------|----------|----------|----------|
| 1 | 数据产物 | 清洗后数据集、情感标签表、主题分类结果、日频特征表、事件日历、影响力评分 | CSV |
| 2 | 可视化产物 | 描述统计图表(10+)、情感分析图表(6+)、主题可视化、特征相关性图、事件分析图表(4+) | PNG/HTML |
| 3 | 文档产物 | 数据质量报告、描述统计报告、情感分析报告、主题分析报告、特征字典、事件分析报告、综合报告 | Markdown |
| 4 | 工程产物 | Streamlit 可视化看板、可复用特征工程模块 | Python |

**预计总产出**：50+ 个文件（15 数据 + 25 图片 + 8 报告 + 2 工程）

### 1.5 技术环境与依赖

- **Python**: 3.10（conda 环境 `py310`，激活命令 `conda activate py310`）
- **执行方式**: 每个章节均提供 **.py + .ipynb** 双格式脚本，按章节编号命名（如 `preprocess.py`、`analysis.py`），支持批量执行和交互式调试
- **环境管理**: 使用 conda 环境 `py310`，通过 `pip install -r requirements.txt` 安装全部依赖
- **核心依赖**: pandas, numpy, matplotlib, seaborn, scikit-learn, nltk, transformers, torch, tqdm, openpyxl
- **完整依赖清单**: 见 `requirements.txt` 及附录F

---

## 第二章 ch01 数据预处理（已完成 ✅）

> **章节原型**: A — 数据预处理型
> **对应分析目标**: 无独立目标，为全部后续章节的数据基础
> **状态**: ✅ 已完成

### 2.1 研究目标

对原始金融新闻数据进行全面的清洗和预处理，包括日期解析、多标签字段拆分、文本清洗、数据类型优化、重复检测与去重、异常值检测，输出干净的结构化数据集，为后续所有分析章节提供可靠的数据基础。

### 2.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 原始新闻数据 | `data/stock_news_2016 to 2026.csv` | CSV | 174.7MB，含日期、标题、描述、分类、关键词等字段 |

### 2.3 技术方法

| 处理环节 | 方法 | 公式/参数 | 选择理由 |
|----------|------|-----------|----------|
| 日期解析 | `pd.to_datetime(errors='coerce')` | 删除无效日期行 | 确保时间序列完整性 |
| 多标签拆分 | 字符串分割 `split('\|')` | `categories_list`, `keywords_list` | 便于分类统计和关键词分析 |
| 文本清洗 | 正则替换（HTML标签、URL、多余空格） | `full_text = title + ' . ' + description` | 统一文本输入格式 |
| 类型优化 | `pd.CategoricalDtype` + `downcast='integer'` | impact_tier 有序 category | 减少内存占用（174.7MB→142MB） |
| 去重 | `df.duplicated(subset=['title','date','source_file'])` | keep='first' | 消除跨来源重复 |
| 异常检测 | IQR 方法 + 分布统计 | relevance_score 上界 = Q3 + 1.5*IQR | 标记但不删除异常值 |

**替代方法**：
- 去重：基于全文相似度（TF-IDF + cosine）— 更精确但计算量大，当前基于标题+日期+来源已足够
- 类型优化：PyArrow 后端 — 更快但兼容性待验证

### 2.4 实施步骤

1. **数据读取与结构探查** — 读取原始 CSV，检查行数、列数、数据类型、缺失值、数值范围
2. **日期解析与验证** — 转为 datetime 类型，删除无效日期行，提取 year/month/day/day_of_week/is_weekend 特征
3. **categories 字段处理** — 拆分为 categories_list 列表，新增 category_count 列
4. **matched_keywords 字段处理** — 拆分为 keywords_list 列表，新增 keyword_count 列
5. **文本清洗** — 合并 title + description 为 full_text，去除 HTML 标签、URL、多余空格
6. **数据类型优化** — impact_tier 转有序 category，source_file/categories 转 category，relevance_score 降精度
7. **重复检测与去重** — 基于 title + date + source_file 去重
8. **异常值检测** — IQR 方法检测 relevance_score 异常，统计 impact_tier 分布
9. **数据质量报告生成** — 汇总全部处理结果，生成 Markdown 报告

### 2.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | **清洗后统一数据集** | `ch01_cleaned_data.csv` | CSV | ch02-ch04, ch05, ch06 全部后续章节 |
| 2 | 数据质量报告 | `ch01_data_quality_report.md` | Markdown | 参考 |
| 3 | 缺失值统计表 | `ch01_missing_values_summary.csv` | CSV | 参考 |
| 4 | 分类统计表 | `ch01_category_statistics.csv` | CSV | ch02 行业分布分析 |
| 5 | 关键词统计表 | `ch01_keyword_statistics.csv` | CSV | ch02 关键词分析 |

### 2.6 质量验证标准

- [x] 全量 139,919 条记录，缺失率 = 0%
- [x] 重复记录 = 0（已去重）
- [x] 日期字段已解析为 datetime64[ns]，范围覆盖 2016-01-01 ~ 2026-04-15
- [x] full_text 字段已生成，平均长度 156.8 字符，无空文本
- [x] categories_list 和 keywords_list 列表字段完整
- [x] impact_tier 为有序 category（LOW < MEDIUM < HIGH）
- [x] 内存优化至 142 MB

---

## 第三章 ch02 描述性统计分析

> **章节原型**: B — 分析探索型
> **对应分析目标**: 目标-1 (P0) — 新闻全景描述性统计分析
> **回答研究问题**: RQ-Sub-1（新闻发布时间分布规律）、RQ-Sub-2（行业分类热度分布）
> **详细目标定义见**: `docs/analysis_goals.md` 第3节 目标-1

### 3.1 研究目标

对 139,919 条新闻完成**时间趋势、行业分布、影响等级、关键词热度、来源分布**的多维度可视化统计分析，输出 10+ 张高质量图表和 1 份描述性统计报告，为后续文本挖掘和建模提供数据理解基础。

**SMART 表述**: 对 139,919 条新闻完成时间趋势、行业分布、影响等级、关键词热度、来源分布的多维度可视化统计，输出 10+ 张高质量图表和 1 份描述性统计报告。

### 3.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 清洗后数据 | `outputs/ch01_data_preprocessing/ch01_cleaned_data.csv` | CSV | 139,919行 x 24列，ch01 输出 |
| 分类统计表 | `outputs/ch01_data_preprocessing/ch01_category_statistics.csv` | CSV | ch01 输出，可直接使用 |
| 关键词统计表 | `outputs/ch01_data_preprocessing/ch01_keyword_statistics.csv` | CSV | ch01 输出，可直接使用 |

### 3.3 技术方法

| 分析维度 | 方法 | 关键函数/公式 |
|----------|------|---------------|
| 时间分布 | 年度/月度/星期频次统计 + 折线图/柱状图 | `df.groupby('year').size()`, `df['day_of_week'].value_counts()` |
| 行业分布 | 频次统计 + 排名柱状图 + 堆叠面积图 | `categories_list.explode().value_counts()` |
| 影响等级 | 占比饼图 + 时间演变折线图 | `df['impact_tier'].value_counts(normalize=True)` |
| 否定表述 | 行业交叉统计 + 分组柱状图 | `df[df['has_negation']==True].groupby('categories')` |
| 关键词热度 | Top50 词频柱状图 + 词云图 | `keywords_list.explode().value_counts().head(50)` |
| 来源偏差 | 来源覆盖度统计 + 年度分布对比 | `df.groupby(['source_file','year']).size()` |
| 文本长度 | 直方图 + 箱线图 + 分位数统计 | `df['text_length'].describe()` |
| 交叉分析 | 行业×影响等级热力图、行业×年度堆叠图 | `pd.crosstab()`, `sns.heatmap()` |

**替代方法**：
- 词云：wordcloud（Python）— 主选，支持中英文；pyecharts 词云 — 备选，交互式但配置复杂
- 热力图：seaborn.heatmap — 主选；plotly — 备选，交互式

### 3.4 实施步骤

1. **新闻发布时间分布分析** — 按年度、月度、星期、工作日vs周末统计新闻数量，绘制多子图时间分布图（折线图+柱状图组合）
2. **17个行业分类热度排名与占比** — 展开 categories_list 统计各分类新闻数量，绘制水平柱状图（按数量降序），标注占比百分比
3. **影响等级分布与时间演变** — 统计 HIGH/MEDIUM/LOW 数量与占比（饼图），绘制各等级月度数量时序图（堆叠面积图）
4. **含否定表述新闻的行业分布** — 筛选 has_negation=True 的新闻，按 categories 统计分布，绘制分组柱状图
5. **Top 50 高频关键词词频统计** — 展开 keywords_list 统计词频，绘制 Top50 水平柱状图，生成词云图
6. **7个数据来源覆盖度与偏差分析** — 统计各来源的新闻数量与占比，绘制来源×年度热力图，分析来源偏差
7. **新闻文本长度分布特征** — 绘制 text_length 直方图（含KDE曲线）和箱线图，统计分位数
8. **交叉分析** — 行业×影响等级交叉表热力图、Top5行业年度趋势堆叠面积图
9. **描述性统计报告撰写** — 汇总全部统计结果，生成 `ch02_descriptive_stats_report.md`

### 3.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | 新闻年度趋势图 | `ch02_yearly_trend.png` | PNG | 报告配图 |
| 2 | 新闻月度分布图 | `ch02_monthly_distribution.png` | PNG | 报告配图 |
| 3 | 星期分布图 | `ch02_weekday_distribution.png` | PNG | 报告配图 |
| 4 | 行业分类热度排名图 | `ch02_category_ranking.png` | PNG | 报告配图 |
| 5 | 行业年度趋势堆叠图 | `ch02_category_yearly_trend.png` | PNG | 报告配图 |
| 6 | 影响等级分布饼图 | `ch02_impact_tier_distribution.png` | PNG | 报告配图 |
| 7 | 影响等级时序演变图 | `ch02_impact_tier_timeline.png` | PNG | 报告配图 |
| 8 | Top50关键词词频图 | `ch02_top50_keywords.png` | PNG | 报告配图 |
| 9 | 关键词词云图 | `ch02_keyword_wordcloud.png` | PNG | 报告配图 |
| 10 | 数据来源偏差分析图 | `ch02_source_bias_analysis.png` | PNG | 报告配图 |
| 11 | 文本长度分布图 | `ch02_text_length_distribution.png` | PNG | 报告配图 |
| 12 | 行业×影响等级热力图 | `ch02_category_impact_heatmap.png` | PNG | 报告配图 |
| 13 | 描述统计汇总表 | `ch02_descriptive_stats.csv` | CSV | ch03 参考 |
| 14 | **描述性统计报告** | `ch02_descriptive_stats_report.md` | Markdown | ch03 参考、最终交付 |

### 3.6 质量验证标准

- [ ] 产出 `ch02_*` 前缀的可视化图表 ≥ 10 张
- [ ] 所有图表 DPI ≥ 150，含中文标题、坐标轴标签、图例
- [ ] 产出 `ch02_descriptive_stats_report.md` 统计报告
- [ ] 报告覆盖全部7个分析维度
- [ ] 17个行业分类均出现在统计中
- [ ] 2021年数据稀疏区间在分析中有明确说明

### 3.7 待优化方向

| 类别 | 现有局限 | 优化建议 |
|------|----------|----------|
| 词云可视化 | 基于简单词频，高频通用词占比过大 | 改用 TF-IDF 加权词云，突出行业区分性关键词 |
| 交叉分析维度 | 仅覆盖行业×影响等级二维 | 新增"行业×来源×时间"三维交叉分析，识别来源的行业偏好和时间演变 |
| 数据稀疏处理 | 2021年数据量骤降（3,548条）仅做标注 | 对稀疏区间做线性插值补全时序图，或标注为独立分析区间 |

---

## 第四章 ch03 文本挖掘与情感分析

> **章节原型**: B — 分析探索型
> **对应分析目标**: 目标-2 (P0) — 金融文本情感分析与舆情挖掘 + 目标-3 (P1) — 新闻主题聚类与事件分类
> **回答研究问题**: RQ-Sub-3（FinBERT情感判别效果）、RQ-Sub-4（新闻主题自动聚类）
> **详细目标定义见**: `docs/analysis_goals.md` 第3节 目标-2、目标-3

### 4.1 研究目标

本章节包含两大核心模块：

**模块一：情感分析** — 基于 FinBERT 对全量 139,919 条新闻的 full_text 进行情感判别（positive/negative/neutral），输出每条新闻的情感标签与置信度，并分析情感时序演变规律。

**模块二：主题建模** — 对新闻文本进行主题建模（BERTopic + LDA），自动划分为 8-15 个金融主题簇，并与现有 17 个 categories 分类进行对比分析。

### 4.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 清洗后数据 | `outputs/ch01_data_preprocessing/ch01_cleaned_data.csv` | CSV | 139,919行 x 24列 |
| 描述统计报告 | `outputs/ch02_descriptive_stats/ch02_descriptive_stats_report.md` | Markdown | ch02 输出，参考数据分布特征 |

### 4.3 技术方法

**模块一：情感分析**

| 分析维度 | 方法 | 关键函数/公式 |
|----------|------|---------------|
| 情感判别 | FinBERT (ProsusAI/finbert) 预训练模型推理 | `pipeline('sentiment-analysis', model='ProsusAI/finbert')` |
| 批量推理 | 分批处理（batch_size=32/64） | GPU 优先，CPU 备选 |
| 情感分布 | 频次统计 + 饼图/柱状图 | `df['sentiment'].value_counts(normalize=True)` |
| 行业交叉 | 分组情感均值 + 箱线图 | `df.groupby('categories')['sentiment_score'].mean()` |
| 时序演变 | 月度/季度情感均值折线图 | `df.resample('M')['sentiment_score'].mean()` |
| 事件窗口 | 事件前后N天情感变化 | 定义窗口 [t-N, t+N]，计算差值 |

**模块二：主题建模**

| 分析维度 | 方法 | 关键函数/公式 |
|----------|------|---------------|
| 文本预处理 | NLTK 去停用词 + spaCy lemmatization | `nlp = spacy.load('en_core_web_sm')` |
| 主题建模(主) | BERTopic | `BERTopic(nr_topics='auto')` |
| 主题建模(对比) | LDA (gensim) | `LdaModel(corpus, num_topics=N, id2word=dictionary)` |
| 主题评估 | Coherence Score (c_v) | `CoherenceModel(model, texts, dictionary, coherence='c_v')` |
| 主题可视化 | pyLDAvis / BERTopic 可视化 | 交互式 HTML 图 |
| 交叉验证 | 主题×categories 混淆矩阵 | `pd.crosstab(topic_label, category)` |

**替代方法**：
- 情感分析：VADER（规则方法，速度快但精度低）、TextBlob（简单但金融领域效果差）— FinBERT 为金融领域专用，效果最佳
- 主题建模：NMF（非负矩阵分解）— 速度快但可解释性不如 LDA/BERTopic

### 4.4 实施步骤

**情感分析模块（Step 3.1 - 3.8）**

1. **FinBERT 模型加载与环境配置** — 检测 GPU 可用性，加载 ProsusAI/finbert 模型，配置批量推理参数（batch_size=32 for GPU, 8 for CPU）
2. **全量新闻情感标签生成** — 对 full_text 列逐批推理，输出 sentiment（positive/negative/neutral）和 confidence（置信度），添加 sentiment_score 数值列（positive=1, neutral=0, negative=-1）
3. **情感分布整体统计** — 统计三种情感的占比，绘制饼图和柱状图，检查分布合理性（非极端偏斜）
4. **行业维度情感交叉分析** — 按主分类统计情感均值和分布，绘制行业情感对比箱线图
5. **情感时序演变分析** — 计算月度/季度情感均值，绘制时序折线图，识别趋势和突变点
6. **高影响等级（HIGH）新闻情感特征** — 筛选 impact_tier=HIGH 的新闻，分析其情感分布特征
7. **含否定表述新闻情感准确性验证** — 筛选 has_negation=True 的新闻，检查 FinBERT 是否正确处理否定语义
8. **重大事件窗口情感突变分析** — 定义 COVID-19（2020-03）、俄乌战争（2022-02）等事件窗口，分析事件前后情感变化

**主题建模模块（Step 3.9 - 3.14）**

9. **文本预处理** — 对 full_text 进行小写转换、去停用词、lemmatization，构建词袋和 TF-IDF 矩阵
10. **BERTopic 主题建模** — 使用 BERTopic 自动确定主题数（nr_topics='auto'），训练模型，输出主题-关键词映射
11. **LDA 主题建模（对比）** — 使用 gensim LDA 训练模型，通过 Coherence Score 确定最优主题数（8-15范围），与 BERTopic 结果对比
12. **主题-关键词映射与标签生成** — 提取每个主题的 Top10 关键词，基于关键词人工/半自动生成主题标签
13. **主题时序演变分析** — 计算各主题的月度新闻数量，绘制主题热度时序热力图
14. **主题与categories交叉验证 + 报告撰写** — 计算主题标签与 categories 分类的对应关系，生成 `ch03_sentiment_analysis_report.md` 和 `ch03_topic_analysis_report.md`

### 4.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | **情感标签数据** | `ch03_sentiment_labels.csv` | CSV | ch04 特征工程、ch05 事件分析 |
| 2 | **主题分类结果** | `ch03_topic_model_results.csv` | CSV | ch04 特征工程 |
| 3 | 情感分布饼图 | `ch03_sentiment_distribution.png` | PNG | 报告配图 |
| 4 | 行业情感对比箱线图 | `ch03_sentiment_by_category.png` | PNG | 报告配图 |
| 5 | 情感时序趋势图 | `ch03_sentiment_timeline.png` | PNG | 报告配图 |
| 6 | 高影响新闻情感特征图 | `ch03_high_impact_sentiment.png` | PNG | 报告配图 |
| 7 | 事件窗口情感变化图 | `ch03_event_window_sentiment.png` | PNG | 报告配图 |
| 8 | 主题可视化（交互式） | `ch03_topic_visualization.html` | HTML | 报告配图 |
| 9 | 主题热度时序热力图 | `ch03_topic_timeline_heatmap.png` | PNG | 报告配图 |
| 10 | **情感分析报告** | `ch03_sentiment_analysis_report.md` | Markdown | ch05 参考、最终交付 |
| 11 | **主题分析报告** | `ch03_topic_analysis_report.md` | Markdown | ch05 参考、最终交付 |

### 4.6 质量验证标准

- [ ] 全量 139,919 条数据情感标签覆盖率 = 100%
- [ ] 情感分布合理（非极端偏斜，任一类别占比 < 80%）
- [ ] 产出 `ch03_sentiment_labels.csv`（含 sentiment, confidence, sentiment_score 列）
- [ ] 产出 `ch03_topic_model_results.csv`（含 topic_id, topic_label, top_keywords）
- [ ] 主题数量在 8-15 范围内
- [ ] Coherence Score (c_v) ≥ 0.4（可接受水平）
- [ ] 情感分析图表 ≥ 6 张，主题可视化 ≥ 2 张
- [ ] 产出 `ch03_sentiment_analysis_report.md` 和 `ch03_topic_analysis_report.md`

### 4.7 待优化方向

| 类别 | 现有局限 | 优化建议 |
|------|----------|----------|
| 否定句处理 | FinBERT 对含否定表述新闻的情感判别可能翻转 | 加入后处理规则修正：检测否定词（not, no, never）后翻转情感标签 |
| 训练性能 | 14万条文本在 CPU 下 BERTopic 训练耗时数小时 | 预计算文本 Embedding（sentence-transformers）加速 BERTopic；或降采样至 50% 数据 |
| 模型精度 | FinBERT-base 在金融领域精度有限 | 替换为 FinBERT-large 或 FinGPT（清华金融大模型）提升精度 |
| 主题评估 | 仅使用 Coherence Score 单一指标 | 增加 Silhouette Score、主题多样性指标等多维评估 |

---

## 第五章 ch04 特征工程

> **章节原型**: B — 分析探索型（偏数据工程）
> **对应分析目标**: 目标-4 (P1) — 新闻舆情特征工程
> **回答研究问题**: RQ-Sub-5（如何构建标准化日频舆情特征集）
> **详细目标定义见**: `docs/analysis_goals.md` 第3节 目标-4

### 5.1 研究目标

基于情感标签、主题分类、关键词统计、时间特征等维度，构建标准化的新闻舆情特征集，输出按日期聚合的**日频特征表**（目标 ≥ 30 个特征），为后续事件驱动分析和看板展示提供可直接使用的特征输入。

**SMART 表述**: 基于情感标签、主题分类、关键词统计、时间特征等维度，构建标准化的新闻舆情特征集，输出按日期聚合的日频特征表，为后续建模和策略分析提供可直接使用的特征输入。

### 5.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 清洗后数据 | `outputs/ch01_data_preprocessing/ch01_cleaned_data.csv` | CSV | 基础字段（date, categories, impact_tier, relevance_score 等） |
| 情感标签 | `outputs/ch03_text_mining_sentiment/ch03_sentiment_labels.csv` | CSV | sentiment, confidence, sentiment_score |
| 主题分类 | `outputs/ch03_text_mining_sentiment/ch03_topic_model_results.csv` | CSV | topic_id, topic_label |

### 5.3 技术方法

| 特征类别 | 方法 | 关键函数/公式 |
|----------|------|---------------|
| 情感特征 | 日频聚合统计 | `df.groupby('date')['sentiment_score'].agg(['mean','std'])` |
| 主题特征 | 各主题日频计数 + Shannon熵 | `-sum(p * ln(p))` |
| 关键词特征 | Top关键词日频出现次数 | `df.groupby('date')['keyword_count'].sum()` |
| 影响等级特征 | 各等级日频占比 + 加权得分 | `HIGH*3 + MEDIUM*2 + LOW*1` |
| 文本统计特征 | 日均长度、日总量、否定占比 | `df.groupby('date')['text_length'].mean()` |
| 时间特征 | 星期效应、月份效应、工作日/周末 | `df['day_of_week'].astype(int)`, `df['is_weekend']` |
| 交叉特征 | 行业×情感、影响等级×情感 | `pd.crosstab(date, category)` |
| 共线性检测 | VIF (方差膨胀因子) | `statsmodels.stats.outliers_influence.variance_inflation_factor` |

**替代方法**：
- 特征选择：基于树模型的特征重要性（RandomForest/XGBoost feature_importances_）— 可与 VIF 互补
- 缺失值处理：前向填充（ffill）— 主选；线性插值 — 备选

### 5.4 实施步骤

1. **情感特征构造** — 按日期聚合：日均情感得分、情感标准差（波动率）、正面新闻占比、负面新闻占比、情感极化指数（|正面占比 - 负面占比|）
2. **主题特征构造** — 各主题日频新闻计数（N列）、主题多样性指数（Shannon熵）、当日热门主题ID、热门主题切换频率（与前日热门主题不同的天数占比）
3. **关键词特征构造** — Top 10 关键词日频出现次数（10列）、日关键词总数、日均关键词数
4. **影响等级特征构造** — HIGH/MEDIUM/LOW 新闻日频占比（3列）、影响等级加权得分（HIGH=3, MEDIUM=2, LOW=1）
5. **文本统计特征构造** — 日均文本长度、日新闻总量、含否定表述新闻占比、日均分类数
6. **时间特征构造** — 星期几（0-6 one-hot 或 sin/cos 编码）、月份（1-12）、是否月末、是否季度末、工作日/周末标识
7. **交叉特征构造** — Top5行业×情感均值（5列）、影响等级×情感均值（3列）
8. **特征合并与日频聚合** — 将所有特征按日期合并为统一 DataFrame，填充缺失日期（全量日期范围）
9. **缺失值处理与特征覆盖率检查** — 检查各列缺失率，对缺失值使用前向填充（ffill），确保无全缺失列
10. **特征相关性分析与VIF检测** — 计算特征间 Pearson 相关系数矩阵，绘制热力图；计算 VIF，标记高共线性特征（VIF > 10）
11. **特征字典文档撰写** — 生成 `ch04_feature_catalog.md`，记录每个特征的名称、定义、计算方式、数据类型、预期范围

### 5.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | **日频舆情特征表** | `ch04_daily_features.csv` | CSV | ch05 事件分析、ch06 看板 |
| 2 | **特征字典** | `ch04_feature_catalog.md` | Markdown | ch05/ch06 参考、最终交付 |
| 3 | 特征相关性热力图 | `ch04_feature_correlation_heatmap.png` | PNG | 报告配图 |
| 4 | VIF 共线性检测结果 | `ch04_vif_results.csv` | CSV | 参考 |

### 5.6 质量验证标准

- [ ] 特征总数 ≥ 30 个
- [ ] 日频特征表行数 = 数据集日期跨度天数（约3,182天）
- [ ] 无全缺失列（每列缺失率 < 5%）
- [ ] 产出 `ch04_daily_features.csv` 和 `ch04_feature_catalog.md`
- [ ] 特征字典覆盖所有特征，含定义、计算方式、类型
- [ ] 相关性热力图已生成

### 5.7 待优化方向

| 类别 | 现有局限 | 优化建议 |
|------|----------|----------|
| 滞后特征 | 仅当日聚合，无时间滞后信息 | 补充滞后特征（如 sentiment_mean_lag1/3/7、news_count_lag7） |
| 滚动窗口 | 无滚动统计特征 | 补充 7/14 天滚动均值、滚动标准差（波动率）特征 |
| 特征字典 | 特征定义仅标注"见代码"，缺乏业务含义 | 每个特征补充业务定义（如 polarization_idx：正负情感占比差值，反映舆情极化程度） |
| 共线性处理 | VIF > 10 仅标记未处理 | 对高 VIF 特征执行 PCA 降维或删除冗余特征 |

---

## 第六章 ch05 事件驱动策略分析

> **章节原型**: B — 分析探索型
> **对应分析目标**: 目标-5 (P1) — 新闻影响力评估与事件驱动分析
> **回答研究问题**: RQ-Sub-6（高影响力新闻事件共性特征与舆情扩散）
> **详细目标定义见**: `docs/analysis_goals.md` 第3节 目标-5
> **重要说明**: 因数据集不含股价数据，本章聚焦**舆情层面的事件影响力分析**，不涉及交易策略回测

### 6.1 研究目标

基于 impact_tier、relevance_score、情感标签等维度，构建新闻影响力评估体系，识别高影响力新闻事件，分析事件发布后的舆情扩散模式，输出事件日历与影响力评分。

### 6.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 清洗后数据 | `outputs/ch01_data_preprocessing/ch01_cleaned_data.csv` | CSV | impact_tier, relevance_score, categories, date |
| 情感标签 | `outputs/ch03_text_mining_sentiment/ch03_sentiment_labels.csv` | CSV | sentiment, sentiment_score |
| 日频特征 | `outputs/ch04_feature_engineering/ch04_daily_features.csv` | CSV | 日频舆情特征 |

### 6.3 技术方法

| 分析环节 | 方法 | 关键函数/公式 |
|----------|------|---------------|
| 事件识别 | 多条件筛选（impact_tier=HIGH + relevance_score≥阈值） | `df[(df['impact_tier']=='HIGH') & (df['relevance_score']>=7)]` |
| 事件分类 | 基于 categories + keywords 规则分类 | 政策类/财报类/地缘类/行业类/其他 |
| 窗口分析 | 事件前后N天情感/特征变化 | `df[t-N:t+N]` 差值和均值对比 |
| 行业对比 | 分行业事件影响力统计 | `df.groupby('categories')['influence_score'].describe()` |
| 舆情扩散 | 跨行业情感变化相关性 | 事件日前后各行业情感变化的相关系数 |
| 影响力评分 | 多维度加权评分 | `score = w1*relevance + w2*impact + w3*sentiment_change + w4*breadth` |

**替代方法**：
- 事件聚类：DBSCAN 密度聚类 — 基于时间+行业+情感的多维聚类
- 影响力评分：AHP 层次分析法 — 更系统但需要专家打分

### 6.4 实施步骤

1. **高影响力新闻事件筛选与识别** — 筛选 impact_tier=HIGH 且 relevance_score≥7 的新闻，统计事件数量和行业分布
2. **事件类型分类** — 基于 categories 和 keywords 规则，将事件分为政策类、财报类、地缘类、行业类、其他五大类
3. **事件窗口定义** — 定义事件窗口为前后7天（[t-7, t+7]），对密集事件进行合并（7天内同类事件合并为一个事件）
4. **事件前后情感变化分析** — 计算每个事件窗口内的日均情感得分，与窗口外基线对比，量化情感突变幅度
5. **行业维度事件影响力对比** — 分行业统计事件数量、平均影响力评分、情感变化幅度
6. **舆情传染效应分析** — 对每个重大事件，计算事件日前后各行业的情感变化，识别跨行业影响扩散模式
7. **事件影响力评分体系构建** — 基于 relevance_score、impact_tier、情感变化幅度、影响行业广度四个维度构建综合评分
8. **事件日历生成** — 按时间排列全部识别到的事件，生成事件日历 CSV，标注事件类型、影响行业、影响力评分
9. **事件分析报告撰写** — 汇总全部分析结果，生成 `ch05_event_analysis_report.md`

### 6.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | **事件日历** | `ch05_event_calendar.csv` | CSV | ch06 看板 |
| 2 | **影响力评分表** | `ch05_influence_score.csv` | CSV | ch06 看板 |
| 3 | 事件类型分布图 | `ch05_event_type_distribution.png` | PNG | 报告配图 |
| 4 | 事件窗口情感变化图 | `ch05_event_sentiment_change.png` | PNG | 报告配图 |
| 5 | 行业事件影响力对比图 | `ch05_industry_impact_comparison.png` | PNG | 报告配图 |
| 6 | 舆情传染效应热力图 | `ch05_contagion_heatmap.png` | PNG | 报告配图 |
| 7 | **事件分析报告** | `ch05_event_analysis_report.md` | Markdown | ch06 参考、最终交付 |

### 6.6 质量验证标准

- [ ] 事件日历非空（识别到的高影响力事件 ≥ 10 个）
- [ ] 影响力评分分布合理（非全部相同值）
- [ ] 事件分析图表 ≥ 4 张
- [ ] 产出 `ch05_event_calendar.csv` 和 `ch05_influence_score.csv`
- [ ] 产出 `ch05_event_analysis_report.md`
- [ ] 五大事件类型均有覆盖

### 6.7 待优化方向

| 类别 | 现有局限 | 优化建议 |
|------|----------|----------|
| 市场关联验证 | 无股价/指数数据，无法验证舆情与市场波动相关性 | 后续接入金融市场数据（NIFTY 50 指数、个股 OHLCV），计算舆情特征与收益率的相关系数 |
| 事件聚类 | 基于规则分类，未利用文本语义 | 使用 DBSCAN 对事件文本 Embedding 做密度聚类，自动发现事件群 |
| 传播网络 | 仅统计跨行业影响，未构建传播路径 | 构建事件传播有向图（行业A→行业B），分析舆情传染链 |

---

## 第七章 ch06 可视化看板与总结报告

> **章节原型**: C — 总结报告型
> **对应分析目标**: 目标-6 (P2) — 可视化看板与综合报告
> **详细目标定义见**: `docs/analysis_goals.md` 第3节 目标-6

### 7.1 研究目标

系统完成**金融新闻舆情分析全链条研究**的成果汇总与可视化展示，构建交互式 Streamlit 看板，整合行业新闻热度、舆情情绪时序、主题演变、事件影响力等核心指标，并输出综合分析报告。

### 7.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 全部前序章节产物 | `outputs/ch01~ch04, ch05/*/` | 混合格式 | 各章节分析结论与数据 |

### 7.3 技术方法

| 环节 | 方法 | 说明 |
|------|------|------|
| 看板框架 | Streamlit 多页面布局 | `st.tabs()` 或 `st.sidebar` 导航 |
| 概览页 | KPI 卡片 + 指标总览 | `st.metric()` 展示核心指标 |
| 时序页 | Plotly 交互式折线图 | 支持缩放、悬停查看详情 |
| 行业页 | Plotly 交互式柱状图/热力图 | 支持行业筛选 |
| 事件页 | 事件日历表格 + 影响力排名 | `st.dataframe()` + `st.data_editor()` |
| 词云页 | 动态词云 + 关键词趋势 | wordcloud + plotly |
| 综合报告 | Markdown 结构化撰写 | 汇总各章节核心发现 |

### 7.4 实施步骤

1. **Streamlit 项目框架搭建** — 创建 `src/ch06_dashboard_summary/dashboard.py`，配置多页面布局（侧边栏导航），加载全局配置和样式
2. **全局概览页** — KPI 卡片展示：新闻总量（139,919）、情感分布（正/负/中占比）、活跃行业数（17）、分析时间跨度（10年）
3. **时间趋势页** — 新闻量时序图、情感时序图、影响力时序图的多轴展示，支持日期范围筛选
4. **行业分析页** — 行业热度排名柱状图、行业情感对比箱线图，支持行业多选筛选
5. **事件分析页** — 事件日历表格（按时间排列）、影响力 Top 20 事件排名、事件类型分布饼图
6. **关键词云页** — 动态词云图（基于全量关键词）、Top 20 关键词趋势折线图
7. **看板交互功能** — 全局日期范围选择器、行业多选筛选器、数据刷新按钮
8. **综合分析报告撰写** — 整合各章节核心发现，生成 `ch06_comprehensive_report.md`，包含研究背景、方法总结、关键发现、局限性分析、未来展望

### 7.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | **Streamlit 看板代码** | `dashboard.py` + `pages/` | Python | 本地运行 |
| 2 | **综合分析报告** | `ch06_comprehensive_report.md` | Markdown | 最终交付 |
| 3 | 关键指标总览表 | `ch06_key_metrics_table.csv` | CSV | 最终交付 |

### 7.6 质量验证标准

- [ ] 看板可本地运行（`streamlit run src/ch06_dashboard_summary/dashboard.py`）
- [ ] 包含 ≥ 5 个页面/标签（概览、趋势、行业、事件、词云）
- [ ] 支持日期范围和行业筛选交互
- [ ] 产出 `ch06_comprehensive_report.md` 综合报告
- [ ] 全部前序章节的核心发现均已纳入总结
- [ ] 局限性分析覆盖数据、方法、范围三个维度

### 7.7 待优化方向

| 类别 | 现有局限 | 优化建议 |
|------|----------|----------|
| 交互性 | Streamlit 基础组件，非技术人员操作门槛较高 | 补充 Plotly/Dash 交互式图表，增加拖拽筛选、联动高亮等高级交互 |
| 部署 | 仅支持本地运行 | 部署到 Streamlit Cloud / AWS，支持在线访问 |
| 实时性 | 静态数据，无实时更新能力 | 接入新闻 API 实现实时舆情监控和预警推送 |

---

## 附录A: 股价预测建模移除决策记录（原 ch05）

### 决策背景

原始项目设计包含 7 个章节（ch01-ch07），其中 ch05 为"股价预测建模"。在数据分析目标设定阶段（`docs/analysis_goals.md`），发现数据集存在以下关键缺口：

| 缺口项 | 说明 |
|--------|------|
| 股票 OHLCV 行情数据 | 数据集不含任何股价数据（开盘价、收盘价、最高价、最低价、成交量） |
| 个股/实体关联字段 | 原始数据集说明中提及 stock 字段但实际未包含 |

### 决策内容

- **决策**: 移除 ch05（股价预测建模）章节
- **决策时间**: 2026-05-04
- **决策依据**: `docs/analysis_goals.md` 第1节数据缺口说明
- **影响范围**: 项目从 7 章缩减为 6 章（ch01, ch02, ch03, ch04, ch05, ch06），依赖关系从 ch04→ch05(已移除)→ch06(现ch05) 简化为 ch04→ch05

### 待同步更新的文件

以下文件仍保留 ch05 引用，需要同步更新：

| 文件 | 需更新位置 | 更新内容 |
|------|-----------|---------|
| `docs/project_convention.md` | 一、项目结构总览 | 移除或标注 ch05 目录为已弃用 |
| `docs/project_convention.md` | 七、7.2 派活话术 | 移除 Prompt-05 行 |
| `docs/project_convention.md` | 八、8.2 ch05 检查项 | 移除 ch05 检查项 |
| `docs/project_convention.md` | 附录参数速查 | 更新 CHAPTER_LIST 和 CHAPTER_DEPENDENCIES |
| `docs/task_dispatch_guide.md` | 第1节依赖关系图 | 移除 ch05 节点 |
| `docs/task_dispatch_guide.md` | 第2节批次划分 | Batch-4 改为 ch05，后续批次号前移 |
| `docs/task_dispatch_guide.md` | Batch-4 模板 | 替换为 ch05 内容 |
| `docs/task_dispatch_guide.md` | 第4节进度检查 | 移除 ch05 相关检查 |
| `src/utils/config.py` | CHAPTERS 列表 | 移除 ch05 条目 |
| `src/utils/task_graph.py` | dependency_map | ch05 依赖改为 `["ch01","ch02","ch03","ch04"]` |
| `src/utils/task_graph.py` | expected_outputs_map | 移除 ch05 条目 |

---

## 附录B: 文档一致性检查清单

### 术语一致性

| 术语 | 统一用法 | 出现位置 |
|------|----------|----------|
| 章节名称 | ch02 描述性统计分析 | 全部文档 |
| 章节名称 | ch03 文本挖掘与情感分析 | 全部文档 |
| 章节名称 | ch04 特征工程 | 全部文档 |
| 章节名称 | ch05 事件驱动策略分析 | 全部文档 |
| 章节名称 | ch06 可视化看板与总结报告 | 全部文档 |
| 数据字段 | full_text（标题+描述合并文本） | 全部文档 |
| 数据字段 | impact_tier（LOW/MEDIUM/HIGH） | 全部文档 |
| 数据字段 | relevance_score（1-11） | 全部文档 |
| 数据字段 | categories_list（分类列表） | 全部文档 |
| 数据字段 | keywords_list（关键词列表） | 全部文档 |

### 数据规模一致性

| 指标 | 统一值 |
|------|--------|
| 总记录数 | 139,919 |
| 总列数 | 24 |
| 时间范围 | 2016-01-01 ~ 2026-04-15 |
| 行业分类数 | 17（原始组合 366 种） |
| 关键词数 | 414 |
| 数据来源数 | 7 |
| 内存占用 | 142 MB（优化后） |

### 目标编号一致性

| flow_design 章节 | 对应 analysis_goals.md 目标 | 对应研究问题 |
|------------------|---------------------------|-------------|
| ch02 | 目标-1 (P0) | RQ-Sub-1, RQ-Sub-2 |
| ch03 | 目标-2 (P0) + 目标-3 (P1) | RQ-Sub-3, RQ-Sub-4 |
| ch04 | 目标-4 (P1) | RQ-Sub-5 |
| ch05 | 目标-5 (P1) | RQ-Sub-6 |
| ch06 | 目标-6 (P2) | — |

---

## 附录C: 项目文件目录结构

```
financial_news_sentiment_analysis/
├── data/                              # 原始数据（只读）
│   └── stock_news_2016 to 2026.csv    #    唯一数据源
├── src/                               # 源代码
│   ├── utils/                         #    通用工具模块
│   │   ├── config.py                  #      全局配置
│   │   ├── data_loader.py             #      Skill-01: 数据加载器
│   │   ├── output_manager.py          #      Skill-04: 输出产物管理器
│   │   └── task_graph.py              #      任务依赖图 + 进度检查
│   ├── ch01_data_preprocessing/       #    Ch01: 数据预处理 ✓
│   ├── ch02_descriptive_stats/        #    Ch02: 描述性统计与可视化
│   ├── ch03_text_mining_sentiment/    #    Ch03: 文本挖掘与情感分析
│   ├── ch04_feature_engineering/      #    Ch04: 特征工程
│   ├── ch05_event_driven_strategy/    #    Ch05: 事件驱动策略分析
│   └── ch06_dashboard_summary/        #    Ch06: 可视化看板与总结报告
├── outputs/                           # 输出产物
│   ├── ch01_data_preprocessing/       #    ✓ 已完成
│   ├── ch02_descriptive_stats/
│   ├── ch03_text_mining_sentiment/
│   ├── ch04_feature_engineering/
│   ├── ch05_event_driven_strategy/
│   └── ch06_dashboard_summary/
├── docs/                              # 项目文档
│   ├── flow_design.md                 #    本文档（研究设计）
│   ├── analysis_goals.md              #    分析目标文档
│   ├── project_convention.md          #    项目规范
│   ├── task_dispatch_guide.md         #    任务分发指南
│   └── financial_news_sentiment_analysis_Execution_Prompts.md  # 执行Prompt
├── logs/                              # 日志
├── requirements.txt                   # Python 依赖清单
└── README.md                          # 项目说明
```

---

## 附录D: 文件命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 数据文件 | `ch{NN}_{描述}.csv` | `ch01_cleaned_data.csv`, `ch03_sentiment_labels.csv` |
| 图片文件 | `ch{NN}_{描述}.png` | `ch02_category_ranking.png`, `ch03_sentiment_distribution.png` |
| 交互图 | `ch{NN}_{描述}.html` | `ch03_topic_visualization.html` |
| 报告文件 | `ch{NN}_{描述}.md` | `ch02_descriptive_stats_report.md` |
| 配置文件 | `ch{NN}_{描述}.json` | — |
| 看板代码 | `dashboard.py` | `src/ch06_dashboard_summary/dashboard.py` |

**前缀 `ch{NN}_` 是强制的**，确保产物归属清晰。

---

## 附录E: 全局可复用Skill库

| Skill | 名称 | 适用章节 | 核心功能 |
|-------|------|----------|----------|
| Skill-01 | 标准数据加载器 | 全部6章 | `load_raw_data()`, `load_preprocessed()` |
| Skill-02 | 标准可视化出图器 | ch02, ch03, ch04, ch05 | `plot_time_series()`, `plot_heatmap()`, `plot_distribution()` |
| Skill-03 | 标准评估指标计算器 | ch03, ch04 | `calc_coherence()`, `calc_vif()`, `compare_models()` |
| Skill-04 | 标准输出产物管理器 | 全部6章 | `save_dataframe()`, `save_figure()`, `save_markdown()` |

---

## 附录F: 完整依赖清单

```
pandas>=2.0              # 数据处理核心
numpy                     # 数值计算
matplotlib                # 静态可视化
seaborn                   # 统计可视化
scikit-learn              # 机器学习工具（特征选择、评估指标）
nltk                      # 自然语言处理（分词、停用词）
transformers              # HuggingFace 模型（FinBERT）
torch                     # 深度学习框架（FinBERT 后端）
tqdm                      # 进度条
openpyxl                  # Excel 文件支持
```

### 建议新增依赖

```
spacy                     # 高性能 NLP（lemmatization）
en_core_web_sm            # spaCy 英文模型
bertopic                  # 主题建模
gensim                    # LDA 主题建模
pyLDAvis                  # 主题可视化
wordcloud                 # 词云生成
plotly                    # 交互式可视化（看板）
streamlit                 # 可视化看板框架
statsmodels               # 统计检验（VIF）
```

### 已知版本兼容性约束

| 约束 | 说明 | 推荐处理 |
|------|------|----------|
| torch + numpy | torch 2.x 通常需要 numpy < 2.0 | 先装 numpy 再装 torch |
| transformers + torch | 版本需兼容 | 使用 requirements.txt 锁定版本 |
| spacy 模型 | 需单独下载 | `python -m spacy download en_core_web_sm` |
| BERTopic | 依赖 sentence-transformers | 自动安装，注意磁盘空间 |

---

*本文档由 flow_design Skill 生成，基于 `docs/analysis_goals.md` 的分析目标展开。*
*如需调整研究目标，请先修改 `docs/analysis_goals.md`，再同步更新本文档。*
