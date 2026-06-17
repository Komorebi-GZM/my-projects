# 金融新闻舆情分析与市场预测 — 任务分发指南

> **项目名称**: financial_news_sentiment_analysis
> **项目描述**: 基于印度金融新闻数据集（139,919条，2016-2026）的舆情分析项目
> **原始数据**: `data/stock_news_2016 to 2026.csv`（174.7MB）
> **章节数量**: 6章（ch01 已完成，ch02-ch06 待执行）
> **生成日期**: 2026-05-04

---

## 一、全局依赖图

```
ch01 数据预处理 ✅ 已完成
  │
  ▼
ch02 描述性统计分析 ────────────────────────────── 串行
  │ 依赖: ch01
  ▼
ch03 文本挖掘与情感分析 ────────────────────────── 串行
  │ 依赖: ch01, ch02
  ▼
ch04 特征工程 ──────────────────────────────────── 串行
  │ 依赖: ch01, ch02, ch03
  ▼
ch05 事件驱动策略分析 ──────────────────────────── 串行
  │ 依赖: ch01, ch02, ch03, ch04
  ▼
ch06 可视化看板与总结报告 ──────────────────────── 串行
  │ 依赖: ch01, ch02, ch03, ch04, ch05
  ▼
项目交付
```

### 依赖关系汇总

| 章节 | 代码名 | 依赖 | 状态 |
|------|--------|------|------|
| ch01 | data_preprocessing | 无 | ✅ 已完成 |
| ch02 | descriptive_stats | ch01 | 待执行 |
| ch03 | text_mining_sentiment | ch01, ch02 | 待执行 |
| ch04 | feature_engineering | ch01, ch02, ch03 | 待执行 |
| ch05 | event_driven_strategy | ch01, ch02, ch03, ch04 | 待执行 |
| ch06 | dashboard_summary | ch01, ch02, ch03, ch04, ch05 | 待执行 |

> **说明**: 本项目存在严格线性依赖链（每章依赖前面所有章节），因此全部采用串行批次。

---

## 二、批次划分

| 批次 | Prompt | 章节 | 并行度 | 说明 |
|------|--------|------|--------|------|
| Batch-0 | — | ch01 数据预处理 | — | ✅ 已完成 |
| Batch-1 | Prompt-02 | ch02 描述性统计分析 | 串行 | ch03 的输入依赖 |
| Batch-2 | Prompt-03 | ch03 文本挖掘与情感分析 | 串行 | ch04 的输入依赖（GPU 推理，耗时较长） |
| Batch-3 | Prompt-04 | ch04 特征工程 | 串行 | ch05 的输入依赖 |
| Batch-4 | Prompt-05 | ch05 事件驱动策略分析 | 串行 | ch06 的输入依赖 |
| Batch-5 | Prompt-06 | ch06 可视化看板与总结报告 | 串行 | 全流程收尾 |

### 批次执行流程

```
Batch-0 (ch01) ✅ ──完成──> Batch-1 (ch02) ──完成──> Batch-2 (ch03) ──完成──>
    Batch-3 (ch04) ──完成──> Batch-4 (ch05) ──完成──> Batch-5 (ch06) ──完成──>
    项目交付
```

### 各批次预估耗时

| 批次 | 预估耗时 | 说明 |
|------|----------|------|
| Batch-1 (ch02) | 5-10 分钟 | 纯统计+可视化，CPU 即可 |
| Batch-2 (ch03) | 1-4 小时 | FinBERT 推理 + BERTopic 训练，GPU 约 30 分钟，CPU 数小时 |
| Batch-3 (ch04) | 5-15 分钟 | 特征聚合 + VIF 计算 |
| Batch-4 (ch05) | 10-20 分钟 | 事件筛选 + 窗口分析 |
| Batch-5 (ch06) | 15-30 分钟 | Streamlit 看板 + 综合报告 |

---

## 三、派活模板

### 通用环境激活指令

```bash
cd /path/to/financial_news_sentiment_analysis
conda activate py310
pip install -r requirements.txt   # 首次执行时
```

### 通用规范文档引用

派发每个批次时，需提醒执行者遵循：
- **项目规范**: `docs/project_convention.md` — 目录结构、命名规范、脚本规范
- **研究设计**: `docs/flow_design.md` — 各章节研究目标、数据输入、技术方法、质量标准
- **执行 Prompt**: `docs/financial_news_sentiment_analysis_Execution_Prompts.md` — 可执行指令

---

### Batch-1: Prompt-02 ch02 描述性统计分析

**章节目标简述**:
对 139,919 条清洗后新闻完成时间趋势、行业分布、影响等级、关键词热度、来源偏差、文本长度的多维度可视化统计分析，输出 10+ 张图表和 1 份描述性统计报告。

**输入数据**:
- `outputs/ch01_data_preprocessing/ch01_cleaned_data.csv` — 139,919行 x 24列
- `outputs/ch01_data_preprocessing/ch01_category_statistics.csv` — 分类统计
- `outputs/ch01_data_preprocessing/ch01_keyword_statistics.csv` — 关键词统计

**预期产物**:
1. `outputs/ch02_descriptive_stats/ch02_time_distribution.png`
2. `outputs/ch02_descriptive_stats/ch02_category_ranking.png`
3. `outputs/ch02_descriptive_stats/ch02_impact_tier_analysis.png`
4. `outputs/ch02_descriptive_stats/ch02_top50_keywords.png`
5. `outputs/ch02_descriptive_stats/ch02_keyword_wordcloud.png`
6. `outputs/ch02_descriptive_stats/ch02_source_bias_analysis.png`
7. `outputs/ch02_descriptive_stats/ch02_text_length_and_cross.png`
8. `outputs/ch02_descriptive_stats/ch02_category_yearly_trend.png`
9. `outputs/ch02_descriptive_stats/ch02_descriptive_stats.csv`
10. `outputs/ch02_descriptive_stats/ch02_descriptive_stats_report.md`

**完成标志**:
- [ ] 图表 ≥ 10 张，DPI ≥ 150
- [ ] 17 个行业分类均出现在统计中
- [ ] 2021 年数据稀疏区间有明确说明
- [ ] `ch02_descriptive_stats_report.md` 已生成

---

### Batch-2: Prompt-03 ch03 文本挖掘与情感分析

**章节目标简述**:
基于 FinBERT 对全量新闻进行情感判别（positive/negative/neutral），使用 BERTopic + LDA 进行主题建模（8-15 个主题），分析情感时序演变和主题分布规律。

**输入数据**:
- `outputs/ch01_data_preprocessing/ch01_cleaned_data.csv`
- `outputs/ch02_descriptive_stats/ch02_descriptive_stats_report.md`（参考）

**预期产物**:
1. `outputs/ch03_text_mining_sentiment/ch03_sentiment_labels.csv` — 情感标签（sentiment, confidence, sentiment_score）
2. `outputs/ch03_text_mining_sentiment/ch03_topic_model_results.csv` — 主题分类
3. `outputs/ch03_text_mining_sentiment/ch03_sentiment_distribution.png`
4. `outputs/ch03_text_mining_sentiment/ch03_sentiment_by_category.png`
5. `outputs/ch03_text_mining_sentiment/ch03_sentiment_timeline.png`
6. `outputs/ch03_text_mining_sentiment/ch03_event_window_sentiment.png`
7. `outputs/ch03_text_mining_sentiment/ch03_topic_visualization.html`
8. `outputs/ch03_text_mining_sentiment/ch03_topic_timeline_heatmap.png`
9. `outputs/ch03_text_mining_sentiment/ch03_sentiment_analysis_report.md`
10. `outputs/ch03_text_mining_sentiment/ch03_topic_analysis_report.md`

**完成标志**:
- [ ] 情感标签覆盖率 = 100%
- [ ] 情感分布合理（任一类别占比 < 80%）
- [ ] 主题数量在 8-15 范围内
- [ ] Coherence Score (c_v) ≥ 0.4
- [ ] `ch03_sentiment_labels.csv` 和 `ch03_topic_model_results.csv` 已生成

**性能提示**:
- GPU 可用: batch_size=32, 预计 30 分钟
- CPU only: batch_size=8, 预计 2-4 小时（可降采样至 50%）
- BERTopic embedding 缓存约 2-3GB，需确保磁盘空间

---

### Batch-3: Prompt-04 ch04 特征工程

**章节目标简述**:
基于情感标签、主题分类、关键词统计等维度，构建日频舆情特征表（目标 ≥ 30 个特征），输出特征字典和相关性分析。

**输入数据**:
- `outputs/ch01_data_preprocessing/ch01_cleaned_data.csv`
- `outputs/ch03_text_mining_sentiment/ch03_sentiment_labels.csv`
- `outputs/ch03_text_mining_sentiment/ch03_topic_model_results.csv`

**预期产物**:
1. `outputs/ch04_feature_engineering/ch04_daily_features.csv` — 日频特征表
2. `outputs/ch04_feature_engineering/ch04_feature_catalog.md` — 特征字典
3. `outputs/ch04_feature_engineering/ch04_feature_correlation_heatmap.png`
4. `outputs/ch04_feature_engineering/ch04_vif_results.csv`

**完成标志**:
- [ ] 特征总数 ≥ 30 个
- [ ] 日频特征表行数 ≈ 3,182 天
- [ ] 无全缺失列（每列缺失率 < 5%）
- [ ] 特征字典覆盖所有特征，含业务定义

---

### Batch-4: Prompt-05 ch05 事件驱动策略分析

**章节目标简述**:
基于 impact_tier、relevance_score、情感标签构建影响力评估体系，识别高影响力新闻事件，分析舆情扩散模式，输出事件日历与影响力评分。因无股价数据，聚焦舆情层面分析。

**输入数据**:
- `outputs/ch01_data_preprocessing/ch01_cleaned_data.csv`
- `outputs/ch03_text_mining_sentiment/ch03_sentiment_labels.csv`
- `outputs/ch04_feature_engineering/ch04_daily_features.csv`

**预期产物**:
1. `outputs/ch05_event_driven_strategy/ch05_event_calendar.csv`
2. `outputs/ch05_event_driven_strategy/ch05_influence_score.csv`
3. `outputs/ch05_event_driven_strategy/ch05_event_analysis.png`
4. `outputs/ch05_event_driven_strategy/ch05_event_analysis_report.md`

**完成标志**:
- [ ] 事件日历非空（高影响力事件 ≥ 10 个）
- [ ] 影响力评分分布合理（非全部相同值）
- [ ] 五大事件类型均有覆盖
- [ ] `ch05_event_calendar.csv` 和 `ch05_influence_score.csv` 已生成

---

### Batch-5: Prompt-06 ch06 可视化看板与总结报告

**章节目标简述**:
构建 Streamlit 交互式看板（概览、趋势、行业、事件、词云 5 个标签页），汇总全部章节核心发现，输出综合分析报告。

**输入数据**:
- ch01-ch05 全部输出产物

**预期产物**:
1. `src/ch06_dashboard_summary/dashboard.py` — Streamlit 看板代码
2. `outputs/ch06_dashboard_summary/ch06_comprehensive_report.md`
3. `outputs/ch06_dashboard_summary/ch06_key_metrics_table.csv`

**完成标志**:
- [ ] 看板可本地运行（`streamlit run src/ch06_dashboard_summary/dashboard.py`）
- [ ] 包含 ≥ 5 个标签页
- [ ] 支持日期范围和行业筛选
- [ ] `ch06_comprehensive_report.md` 已生成
- [ ] 局限性分析覆盖数据、方法、范围三个维度

---

## 四、进度检查

### 4.1 一键进度总览

```bash
cd /path/to/financial_news_sentiment_analysis

echo "========================================="
echo "  金融新闻舆情分析 — 项目进度"
echo "========================================="
printf "%-10s %-35s %-10s\n" "批次" "章节" "状态"
printf "%-10s %-35s %-10s\n" "----" "----" "----"

# Batch-0: ch01
if [ -f "outputs/ch01_data_preprocessing/ch01_cleaned_data.csv" ]; then
    printf "Batch-0    %-35s [DONE]\n" "ch01 数据预处理"
else
    printf "Batch-0    %-35s [TODO]\n" "ch01 数据预处理"
fi

# Batch-1: ch02
if [ -f "outputs/ch02_descriptive_stats/ch02_descriptive_stats_report.md" ]; then
    printf "Batch-1    %-35s [DONE]\n" "ch02 描述性统计分析"
else
    printf "Batch-1    %-35s [TODO]\n" "ch02 描述性统计分析"
fi

# Batch-2: ch03
if [ -f "outputs/ch03_text_mining_sentiment/ch03_sentiment_labels.csv" ]; then
    printf "Batch-2    %-35s [DONE]\n" "ch03 文本挖掘与情感分析"
else
    printf "Batch-2    %-35s [TODO]\n" "ch03 文本挖掘与情感分析"
fi

# Batch-3: ch04
if [ -f "outputs/ch04_feature_engineering/ch04_daily_features.csv" ]; then
    printf "Batch-3    %-35s [DONE]\n" "ch04 特征工程"
else
    printf "Batch-3    %-35s [TODO]\n" "ch04 特征工程"
fi

# Batch-4: ch05
if [ -f "outputs/ch05_event_driven_strategy/ch05_event_calendar.csv" ]; then
    printf "Batch-4    %-35s [DONE]\n" "ch05 事件驱动策略分析"
else
    printf "Batch-4    %-35s [TODO]\n" "ch05 事件驱动策略分析"
fi

# Batch-5: ch06
if [ -f "outputs/ch06_dashboard_summary/ch06_comprehensive_report.md" ]; then
    printf "Batch-5    %-35s [DONE]\n" "ch06 可视化看板与总结报告"
else
    printf "Batch-5    %-35s [TODO]\n" "ch06 可视化看板与总结报告"
fi

echo "========================================="
```

### 4.2 数据产物链检查

```bash
echo "=== Data Pipeline Check ==="
[ -f "outputs/ch01_data_preprocessing/ch01_cleaned_data.csv" ] && echo "[OK] ch01 cleaned_data" || echo "[FAIL] ch01"
[ -f "outputs/ch02_descriptive_stats/ch02_descriptive_stats.csv" ] && echo "[OK] ch02 descriptive_stats" || echo "[FAIL] ch02"
[ -f "outputs/ch03_text_mining_sentiment/ch03_sentiment_labels.csv" ] && echo "[OK] ch03 sentiment_labels" || echo "[FAIL] ch03"
[ -f "outputs/ch03_text_mining_sentiment/ch03_topic_model_results.csv" ] && echo "[OK] ch03 topic_results" || echo "[FAIL] ch03"
[ -f "outputs/ch04_feature_engineering/ch04_daily_features.csv" ] && echo "[OK] ch04 daily_features" || echo "[FAIL] ch04"
[ -f "outputs/ch05_event_driven_strategy/ch05_event_calendar.csv" ] && echo "[OK] ch05 event_calendar" || echo "[FAIL] ch05"
[ -f "outputs/ch06_dashboard_summary/ch06_comprehensive_report.md" ] && echo "[OK] ch06 comprehensive_report" || echo "[FAIL] ch06"
```

### 4.3 文档产物检查

```bash
echo "=== Document Check ==="
for doc in ch01_data_quality_report ch02_descriptive_stats_report ch03_sentiment_analysis_report \
           ch03_topic_analysis_report ch05_event_analysis_report ch06_comprehensive_report; do
    found=$(find outputs/ -name "${doc}.md" 2>/dev/null | head -1)
    if [ -n "$found" ]; then
        echo "[OK] ${doc}.md"
    else
        echo "[FAIL] ${doc}.md"
    fi
done
```

---

## 五、派活话术模板

### 模板 A：完整项目启动

```
【金融新闻舆情分析 — 任务分发】

项目路径: financial_news_sentiment_analysis/
环境: conda activate py310
规范: docs/project_convention.md
设计: docs/flow_design.md
执行: docs/financial_news_sentiment_analysis_Execution_Prompts.md

═══ Batch-0: ch01 数据预处理 ✅ 已完成 ═══

═══ Batch-1: Prompt-02 ch02 描述性统计分析 ═══
  依赖: outputs/ch01_data_preprocessing/ch01_cleaned_data.csv
  产物: outputs/ch02_descriptive_stats/ (10个文件)
  耗时: 5-10分钟

═══ Batch-2: Prompt-03 ch03 文本挖掘与情感分析 ═══
  依赖: ch01 + ch02 全部产物
  产物: outputs/ch03_text_mining_sentiment/ (10个文件)
  耗时: 1-4小时（GPU 30分钟，CPU 数小时）

═══ Batch-3: Prompt-04 ch04 特征工程 ═══
  依赖: ch01 + ch03 情感标签 + ch03 主题分类
  产物: outputs/ch04_feature_engineering/ (4个文件)
  耗时: 5-15分钟

═══ Batch-4: Prompt-05 ch05 事件驱动策略分析 ═══
  依赖: ch01 + ch03 + ch04 全部产物
  产物: outputs/ch05_event_driven_strategy/ (4个文件)
  耗时: 10-20分钟

═══ Batch-5: Prompt-06 ch06 可视化看板与总结报告 ═══
  依赖: ch01-ch05 全部产物
  产物: outputs/ch06_dashboard_summary/ (3个文件)
  耗时: 15-30分钟
```

### 模板 B：单批次派活

```
你正在执行 financial_news_sentiment_analysis 项目的 [Batch-N] 任务。

【项目背景】
- 项目: 金融新闻舆情分析与市场预测
- 数据: 139,919条印度金融新闻（2016-2026）
- 环境: conda activate py310

【当前批次】Batch-N: [章节名称]
【章节目标】[目标简述]

【前置依赖】
- [列出依赖的产物文件路径]

【输入数据】
- [列出输入文件路径]

【预期产物】
- [列出输出文件路径]

【规范要求】
- 遵循 docs/project_convention.md 命名规范
- 参考 docs/flow_design.md 对应章节研究设计
- 参考 docs/financial_news_sentiment_analysis_Execution_Prompts.md 中 Prompt-NN 的执行指令

【完成标志】
- [列出检查项]

请开始执行。
```

### 模板 C：进度检查（一句话）

```
检查金融新闻舆情分析进度：
Batch-0(ch01✅) → Batch-1(ch02) → Batch-2(ch03) → Batch-3(ch04) → Batch-4(ch05) → Batch-5(ch06)
当前应在哪个批次？产物是否齐全？
```

---

## 六、注意事项

1. **严禁跳批**: 每个批次必须等前置依赖全部完成后再启动
2. **产物隔离**: 每个章节产物写入独立的 `outputs/ch{NN}_{dir_name}/` 目录，互不干扰
3. **脚本双格式**: 每个章节提供 `.py` + `.ipynb` 双格式脚本
4. **全局配置**: 所有脚本通过 `src/utils/config.py` 统一路径和参数，禁止硬编码
5. **GPU 注意**: ch03 的 FinBERT 和 BERTopic 需要 GPU 加速，CPU 环境需降采样或延长耗时预期
6. **ch05 无股价数据**: 事件驱动分析聚焦舆情层面，不涉及交易策略回测
