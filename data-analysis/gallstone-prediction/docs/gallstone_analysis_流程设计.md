# gallstone_analysis — 流程设计文档

> **版本**: v1.0 | **更新日期**: 2026-05-04 | **配套执行文档**: `gallstone_analysis_Execution_Prompts.md`

---

## 文档说明

本文档为**胆结石数据集全流程标准化分析研究框架**，严格遵循临床医学数据分析、生物统计检验、机器学习建模的学术规范。每一章节明确：**研究目标 → 数据输入 → 技术方法 → 实施步骤 → 阶段产物 → 质量标准**，可直接作为课程论文、实训报告、数据分析结题文档原稿使用。

**与执行 Prompt 文档的关系**：本文档定义"做什么、为什么、用什么方法"；配套的 Prompt 文档定义"怎么做——精确到函数、参数、代码级别"。两份文档配合使用：先阅读本文档理解全貌，再参照 Prompt 文档逐步执行。

**与 task_dispatch_guide.md 的关系**：
- 本文档（flow_design.md）= **研究设计文档**，面向读者/评审者，描述"做什么、为什么、用什么方法"
- task_dispatch_guide.md = **执行操作手册**，面向执行者，描述"怎么做、按什么顺序、怎么派活"
- 修改本文档的章节目标或方法后，需同步检查 execution_prompts.md 和 dispatch_guide.md 是否需要更新

---

## 第一章 研究概述

### 1.1 研究背景

胆结石（Gallstone / Cholelithiasis）是一种常见的消化系统疾病，全球成年人患病率约为 10%-15%，女性发病率约为男性的 2-3 倍。胆结石的形成与肥胖、代谢综合征、血脂异常、肝功能异常、炎症反应、维生素 D 缺乏等多种因素密切相关。近年来，人体成分分析（Body Composition Analysis, BCA）技术通过生物电阻抗分析（BIA）获取体脂率、内脏脂肪面积、肌肉量等精细指标，为胆结石风险评估提供了新的数据维度。

本次研究采用**胆结石临床数据集**，数据包含 319 例患者的 39 项特征，涵盖人口统计学（年龄、性别、身高、体重）、合并症（冠心病、甲减、高脂血症、糖尿病）、人体成分指标（BMI、体脂率、内脏脂肪、肌肉量等 16 项）和血液生化指标（血糖、血脂、肝功能、肾功能、炎症标志物、维生素 D 等 13 项）。数据具备**多维度、多类型（连续/分类/有序）、无缺失值、类别均衡**特征，可真实反映胆结石患者与非患者的临床特征差异。

**研究核心问题**：
1. 胆结石患者与非患者在人体成分和血液生化指标上存在哪些显著差异？
2. 哪些特征是胆结石的独立风险因素？
3. 能否基于这些特征构建有效的胆结石预测模型？

### 1.2 数据集基础概况

| 维度 | 值 |
|------|-----|
| 数据量（行） | 319 |
| 特征数（列） | 39（含目标变量） |
| 目标变量 | Gallstone_Status（0=无胆结石, 1=有胆结石） |
| 类别分布 | 0: 161 (50.5%), 1: 158 (49.5%) — 均衡 |
| 缺失值 | 无 |
| 重复行 | 无 |
| 数据来源 | UCI Gallstone Dataset |
| 数据格式 | xlsx（单 Sheet） |

**数据特征**：
- **多维度覆盖**：人口统计(4) + 合并症(5) + 人体成分(16) + 血液生化(13) + 目标(1)
- **类别均衡**：正负样本比约 1:1，无需重采样处理
- **无缺失值**：数据质量高，无需插补
- **高共线性**：人体成分指标间存在大量高度相关特征对（|r| > 0.7 共 50 对），建模时需注意多重共线性

### 1.3 整体研究逻辑

以**清洗后胆结石数据集**为核心，依次完成 6 大分析环节：

```
数据预处理(ch01) → 探索性分析(ch02) → 统计检验(ch03) → 特征筛选(ch04) → 建模预测(ch05) → 总结报告(ch06)
       ↓                  ↓                  ↓                  ↓                  ↓                  ↓
   清洗数据集        描述统计+可视化     组间差异检验       特征重要性排序       预测模型+评估       全流程总结
```

**章节间数据依赖关系**：
- 第一章（数据预处理）是全部后续章节的基础，必须最先完成
- 第二章（探索性分析）依赖第一章的清洗数据，为后续统计检验提供描述性依据
- 第三章（统计检验）依赖第一、二章，为特征筛选提供统计显著性依据
- 第四章（特征筛选）依赖第一、二、三章，为建模提供最优特征子集
- 第五章（建模预测）依赖第一、四章，使用筛选后的特征训练预测模型
- 第六章（总结报告）依赖全部前序章节，汇总全流程成果

### 1.4 整体研究产出总览

| 序号 | 产出类别 | 具体内容 | 产出形式 |
|------|----------|----------|----------|
| 1 | 清洗数据 | 清洗后标准化数据集 + 异常值报告 | CSV + XLSX |
| 2 | 描述统计 | 各特征描述统计表 + 分组对比统计 | CSV |
| 3 | 可视化图表 | 分布图、箱线图、相关性热力图、分组对比图 | PNG (DPI≥150) |
| 4 | 统计检验 | 组间差异检验结果表（含效应量） | CSV |
| 5 | 特征分析 | 特征重要性排序 + 共线性诊断 | CSV + PNG |
| 6 | 预测模型 | 训练好的模型文件 + 评估报告 | PKL + CSV + PNG |
| 7 | 总结报告 | 全流程分析总结文档 | Markdown |

**预计总产出**：40+ 个文件（10 数据 + 20 图片 + 2 模型 + 8 报告）

### 1.5 技术环境与依赖

- **Python**: 3.10（conda 环境 `py310`）
- **执行方式**: 每个章节均提供 **.py + .ipynb 双格式**脚本，按章节编号命名，支持批量执行和交互式调试
- **环境管理**: 使用 conda `py310`，激活命令 `conda activate py310`，通过 `pip install -r requirements.txt` 安装全部依赖
- **核心依赖**: pandas, numpy, matplotlib, seaborn, scipy, statsmodels, scikit-learn
- **完整依赖清单**: 见 `requirements.txt`

---

## 第二章 数据预处理（ch01）

> **章节类型**: 原型 A（数据预处理型）
> **状态**: ✅ 已完成

### 2.1 研究目标

厘清原始数据基本属性，解决**列名不规范**（含括号、空格、缩写不一致）、**异常值**（部分特征存在极端值）问题，构建统一格式、高质量的标准化分析数据集，为后续所有分析建模提供数据基础。

### 2.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 原始数据 | `data/dataset-uci.xlsx` | XLSX | 319 行 × 39 列，单 Sheet "dataset" |

### 2.3 技术方法

| 处理环节 | 方法 | 公式/参数 | 选择理由 |
|----------|------|-----------|----------|
| 列名标准化 | 手动映射 + snake_case | 27 个列名映射表 | 原始列名含括号和空格，不利于代码引用 |
| 异常值检测 | IQR 方法 | `Q1 - 1.5×IQR, Q3 + 1.5×IQR` | 对非正态分布数据稳健，临床数据常用 |
| 异常值处理 | Winsorize（截断） | 截断至 IQR 边界值 | 保留样本量，避免信息损失 |
| 数据质量验证 | 全量检查 | 缺失值、重复行、类型检查 | 确保数据完整性 |

**替代方法**：
- 异常值检测：Z-score 方法（对正态分布更敏感）、Isolation Forest（适用于高维异常检测）
- 异常值处理：删除（简单但损失样本）、替换为中位数（保守但改变分布）

### 2.4 实施步骤

1. **数据读取与结构探查** — 读取 Excel 文件，检查行数、列数、数据类型、缺失值
2. **列名标准化** — 将 27 个含括号/空格的列名映射为 snake_case 格式
3. **异常值检测（IQR）** — 对 30 个连续变量计算 IQR 边界，标记异常值
4. **异常值处理（Winsorize）** — 将超出边界的值截断至边界值
5. **数据质量验证** — 确认无缺失值、无重复行、数据类型正确
6. **清洗后统计摘要** — 生成描述统计表
7. **可视化** — 生成清洗前后箱线图对比、清洗后分布直方图、相关性热力图、目标变量分布图
8. **产物保存** — 输出清洗后数据（CSV + XLSX）和全部报告

### 2.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | 清洗后数据集 | `ch01_cleaned_dataset.csv` | CSV | ch02~ch06 |
| 2 | 清洗后数据集 | `ch01_cleaned_dataset.xlsx` | XLSX | 参考 |
| 3 | 异常值检测报告 | `ch01_outlier_report.csv` | CSV | 参考 |
| 4 | 清洗后统计摘要 | `ch01_cleaned_data_statistics.csv` | CSV | ch02 |
| 5 | 清洗前后箱线图 | `ch01_boxplot_before_after.png` | PNG | 报告配图 |
| 6 | 清洗后分布直方图 | `ch01_histogram_cleaned.png` | PNG | 报告配图 |
| 7 | 相关性热力图 | `ch01_correlation_heatmap.png` | PNG | ch02, ch04 |
| 8 | 目标变量分布图 | `ch01_target_distribution.png` | PNG | 报告配图 |
| 9 | 清洗报告 | `ch01_cleaning_report.json` | JSON | 参考 |

### 2.6 质量验证标准

- [x] 清洗后数据无 NaN 值
- [x] 异常值已通过 IQR + Winsorize 处理（25 列 223 个异常值）
- [x] 列名已标准化为 snake_case 格式（27 个列名）
- [x] 数据完整性：319 行 × 39 列，无缺失值，无重复行
- [x] 所有图片 DPI ≥ 150
- [x] 所有产物文件以 `ch01_` 开头

---

## 第三章 探索性数据分析（ch02）

> **章节类型**: 原型 B（分析探索型）
> **状态**: ⬜ 待执行

### 3.1 研究目标

从**人口统计、合并症、人体成分、血液生化**四个维度全面描述数据分布特征，量化胆结石组与非胆结石组的差异化模式，识别潜在的关键风险因素，为后续统计检验和建模提供直观依据。

### 3.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 清洗后数据集 | `outputs/ch01_preprocessing/ch01_cleaned_dataset.csv` | CSV | 319 行 × 39 列，已完成异常值处理 |

### 3.3 技术方法

| 分析维度 | 方法 | 关键函数/公式 |
|----------|------|---------------|
| 描述统计 | 分组描述统计 | `df.groupby('Gallstone_Status').describe()` |
| 分布分析 | 直方图 + KDE | `sns.histplot(kde=True)` |
| 组间对比 | 箱线图 + 小提琴图 | `sns.boxplot()`, `sns.violinplot()` |
| 相关性分析 | Pearson / Spearman | `df.corr(method='pearson')` |
| 分类变量分析 | 频率表 + 堆叠柱状图 | `pd.crosstab()`, `sns.countplot()` |
| 交互分析 | 性别 × 胆结石 分层分析 | `sns.catplot(hue='Gender')` |

**多变量关系探索**：
- 优先：按特征分组（人体成分 vs 血液生化）分别绘制与目标变量的关系
- 备选：使用 pairplot 展示关键特征间的两两关系

**替代方法**：Parallel Coordinates Plot（平行坐标图，适合高维可视化）、t-SNE/PCA 降维可视化

### 3.4 实施步骤

1. **全局描述统计** — 计算全部连续变量的均值、标准差、中位数、四分位数、偏度、峰度
2. **分组描述统计** — 按 Gallstone_Status 分组计算上述统计量，计算组间差异（均值差、效应量 Cohen's d）
3. **连续变量分布图** — 分组绘制直方图 + KDE，覆盖全部 30 个连续变量
4. **分组箱线图** — 按胆结石状态分组绘制箱线图，直观展示组间差异
5. **分类变量分析** — 对 Gender, Comorbidity, CAD, Hypothyroidism, Hyperlipidemia, DM 绘制频率分布和堆叠柱状图
6. **相关性矩阵细化** — 按特征分组（人体成分 / 血液生化）分别绘制相关性热力图
7. **性别分层分析** — 按性别分层，分析各特征在胆结石组与非胆结石组间的差异
8. **关键发现汇总** — 提取 Top 10 差异最大的特征，生成汇总表

### 3.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | 全局描述统计表 | `ch02_descriptive_stats_all.csv` | CSV | ch03 |
| 2 | 分组描述统计表 | `ch02_descriptive_stats_by_group.csv` | CSV | ch03 |
| 3 | 组间效应量表 | `ch02_effect_sizes.csv` | CSV | ch03, ch04 |
| 4 | 连续变量分布图 | `ch02_distribution_plots.png` | PNG | 报告配图 |
| 5 | 分组箱线图 | `ch02_boxplots_by_group.png` | PNG | 报告配图 |
| 6 | 分类变量频率图 | `ch02_categorical_plots.png` | PNG | 报告配图 |
| 7 | 人体成分相关性热力图 | `ch02_corr_body_composition.png` | PNG | 报告配图 |
| 8 | 血液生化相关性热力图 | `ch02_corr_blood_biomarkers.png` | PNG | 报告配图 |
| 9 | 性别分层对比图 | `ch02_gender_stratified.png` | PNG | 报告配图 |
| 10 | Top 10 差异特征汇总 | `ch02_top10_differences.csv` | CSV | ch04 |

### 3.6 质量验证标准

- [ ] 描述统计表覆盖全部 30 个连续变量
- [ ] 分组统计覆盖胆结石组和非胆结石组
- [ ] 效应量（Cohen's d）已计算
- [ ] 分布图覆盖全部连续变量
- [ ] 分类变量分析覆盖全部 6 个分类/二分类变量
- [ ] 所有图片 DPI ≥ 150，文件名以 `ch02_` 开头

---

## 第四章 统计检验（ch03）

> **章节类型**: 原型 B（分析探索型）
> **状态**: ⬜ 待执行

### 4.1 研究目标

通过严格的统计检验方法，量化胆结石组与非胆结石组在各特征上的差异是否具有统计学意义，控制多重比较带来的假阳性风险，为特征筛选提供统计显著性依据。

### 4.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 清洗后数据集 | `outputs/ch01_preprocessing/ch01_cleaned_dataset.csv` | CSV | 319 行 × 39 列 |
| 分组效应量表 | `outputs/ch02_eda/ch02_effect_sizes.csv` | CSV | Cohen's d 效应量 |

### 4.3 技术方法

| 检验类型 | 方法 | 适用条件 | 公式/参数 |
|----------|------|----------|-----------|
| 正态性检验 | Shapiro-Wilk | 连续变量 | `scipy.stats.shapiro()` |
| 方差齐性检验 | Levene's test | 连续变量 | `scipy.stats.levene()` |
| 两独立样本均值比较 | Independent t-test | 正态 + 方差齐 | `scipy.stats.ttest_ind()` |
| 两独立样本均值比较 | Welch's t-test | 正态 + 方差不齐 | `scipy.stats.ttest_ind(equal_var=False)` |
| 两独立样本秩和检验 | Mann-Whitney U | 非正态分布 | `scipy.stats.mannwhitneyu()` |
| 分类变量关联检验 | Chi-squared test | 分类变量 | `scipy.stats.chi2_contingency()` |
| 多重比较校正 | Bonferroni / BH-FDR | 全部检验 | `statsmodels.stats.multitest.multipletests()` |

**检验策略**：
- 先对每个连续变量做 Shapiro-Wilk 正态性检验
- 正态分布 → Levene 方差齐性检验 → t-test 或 Welch's t-test
- 非正态分布 → Mann-Whitney U 检验
- 分类变量 → Chi-squared 检验（期望频数 < 5 时用 Fisher's exact test）
- 全部 p 值通过 Benjamini-Hochberg FDR 校正

**替代方法**：
- 非参数检验：Kolmogorov-Smirnov test（对分布形状差异更敏感）
- 多重比较：Bonferroni（更保守，控制族错误率）

### 4.4 实施步骤

1. **正态性检验** — 对 30 个连续变量分别做 Shapiro-Wilk 检验，记录 p 值和正态性判定（α=0.05）
2. **方差齐性检验** — 对正态分布变量做 Levene 检验
3. **连续变量组间检验** — 根据正态性和方差齐性结果，选择 t-test / Welch's t-test / Mann-Whitney U
4. **分类变量关联检验** — 对 6 个分类/二分类变量做 Chi-squared 检验
5. **多重比较校正** — 对全部 p 值应用 BH-FDR 校正，计算校正后 p 值和 q 值
6. **效应量计算** — 连续变量计算 Cohen's d，分类变量计算 Cramér's V
7. **结果汇总** — 生成完整检验结果表，标记显著/不显著
8. **可视化** — 绘制检验结果森林图（Forest Plot），展示各特征的效应量和置信区间

### 4.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | 正态性检验结果 | `ch03_normality_test.csv` | CSV | 参考 |
| 2 | 完整检验结果表 | `ch03_statistical_tests.csv` | CSV | ch04 |
| 3 | 校正后检验结果 | `ch03_adjusted_p_values.csv` | CSV | ch04 |
| 4 | 效应量汇总表 | `ch03_effect_sizes.csv` | CSV | ch04 |
| 5 | 检验结果森林图 | `ch03_forest_plot.png` | PNG | 报告配图 |
| 6 | 显著特征汇总 | `ch03_significant_features.csv` | CSV | ch04, ch05 |

### 4.6 质量验证标准

- [ ] 全部 30 个连续变量均完成正态性检验
- [ ] 检验方法选择与正态性/方差齐性结果一致
- [ ] 全部 6 个分类变量均完成 Chi-squared 检验
- [ ] 多重比较校正（BH-FDR）已应用
- [ ] 效应量已计算（Cohen's d / Cramér's V）
- [ ] 森林图包含全部检验特征的效应量和 95% 置信区间

---

## 第五章 特征筛选（ch04）

> **章节类型**: 原型 B（分析探索型）
> **状态**: ⬜ 待执行

### 5.1 研究目标

综合统计显著性、效应量、特征重要性和共线性诊断，从 38 个候选特征中筛选出胆结石预测的最优特征子集，解决人体成分指标间高度共线性问题，为建模提供稳健的特征输入。

### 5.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 清洗后数据集 | `outputs/ch01_preprocessing/ch01_cleaned_dataset.csv` | CSV | 319 行 × 39 列 |
| 统计检验结果 | `outputs/ch03_statistical_test/ch03_significant_features.csv` | CSV | 显著特征列表 |
| 效应量表 | `outputs/ch03_statistical_test/ch03_effect_sizes.csv` | CSV | Cohen's d / Cramér's V |

### 5.3 技术方法

| 筛选环节 | 方法 | 参数 | 选择理由 |
|----------|------|------|----------|
| 统计显著性筛选 | p 值阈值 | FDR 校正后 p < 0.05 | 去除统计不显著的特征 |
| 效应量筛选 | Cohen's d 阈值 | \|d\| > 0.2（小效应） | 去除效应量过小的特征 |
| 共线性诊断 | VIF（方差膨胀因子） | VIF > 10 需处理 | 识别多重共线性 |
| 基于模型的筛选 | LASSO 回归 | `sklearn.linear_model.LassoCV` | 自动特征选择，处理共线性 |
| 递归特征消除 | RFE + Cross-validation | `sklearn.feature_selection.RFECV` | 基于模型性能的特征排序 |
| 最终特征确认 | 综合评分 | 统计+模型+领域知识 | 确保筛选结果的临床可解释性 |

**替代方法**：
- 嵌入法：Random Forest Feature Importance（对非线性关系敏感）
- 过滤法：Mutual Information（捕获非线性依赖）
- 降维法：PCA（但损失可解释性，不推荐用于临床研究）

### 5.4 实施步骤

1. **统计筛选** — 筛选 FDR 校正后 p < 0.05 且 \|Cohen's d\| > 0.2 的特征
2. **VIF 共线性诊断** — 对通过统计筛选的特征计算 VIF，识别高共线性特征对
3. **LASSO 回归筛选** — 使用 LassoCV 自动选择正则化强度，获取非零系数特征
4. **RFE 递归特征消除** — 使用 Logistic Regression + 5-fold CV，获取特征排序
5. **Random Forest 特征重要性** — 训练随机森林，获取基于基尼不纯度的特征重要性
6. **综合评分** — 对每个特征计算综合得分（统计得分 + 模型得分 + 领域知识加分）
7. **最终特征子集确定** — 结合 VIF 诊断结果，去除冗余特征，确定最终特征列表
8. **筛选结果可视化** — 绘制特征重要性排序图、VIF 柱状图、筛选流程图

### 5.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | VIF 诊断结果 | `ch04_vif_analysis.csv` | CSV | 参考 |
| 2 | LASSO 筛选结果 | `ch04_lasso_selection.csv` | CSV | 参考 |
| 3 | RFE 特征排序 | `ch04_rfe_ranking.csv` | CSV | 参考 |
| 4 | RF 特征重要性 | `ch04_rf_importance.csv` | CSV | 参考 |
| 5 | 综合评分表 | `ch04_composite_score.csv` | CSV | ch05 |
| 6 | 最终特征列表 | `ch04_final_features.csv` | CSV | ch05 |
| 7 | 特征重要性图 | `ch04_feature_importance.png` | PNG | 报告配图 |
| 8 | VIF 柱状图 | `ch04_vif_barplot.png` | PNG | 报告配图 |
| 9 | 筛选后数据集 | `ch04_selected_features_data.csv` | CSV | ch05 |

### 5.6 质量验证标准

- [ ] 统计筛选标准明确（p < 0.05 FDR, \|d\| > 0.2）
- [ ] VIF 共线性诊断完成，最终特征子集 VIF < 10
- [ ] 至少使用 3 种筛选方法交叉验证
- [ ] 最终特征列表包含临床可解释性说明
- [ ] 筛选后特征数量合理（建议 8-15 个）

---

## 第六章 建模预测（ch05）

> **章节类型**: 原型 B（分析探索型）
> **状态**: ⬜ 待执行

### 6.1 研究目标

基于筛选后的特征子集，训练多种机器学习模型，通过严格的交叉验证评估预测性能，比较不同模型的优劣，确定最优胆结石预测模型，并分析关键预测特征。

### 6.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 筛选后数据集 | `outputs/ch04_feature_selection/ch04_selected_features_data.csv` | CSV | 319 行 × N 列（N 为筛选后特征数） |
| 最终特征列表 | `outputs/ch04_feature_selection/ch04_final_features.csv` | CSV | 特征名称列表 |

### 6.3 技术方法

| 环节 | 方法 | 参数 | 选择理由 |
|------|------|------|----------|
| 数据划分 | Stratified K-Fold | k=5, stratify by Gallstone_Status | 保持类别比例，小样本适用 |
| 基线模型 | Logistic Regression | `sklearn.linear_model.LogisticRegressionCV` | 可解释性强，临床研究标准方法 |
| 集成模型 | Random Forest | `sklearn.ensemble.RandomForestClassifier` | 对非线性关系鲁棒 |
| 集成模型 | Gradient Boosting | `sklearn.ensemble.GradientBoostingClassifier` | 通常性能最优 |
| 树模型 | XGBoost | `xgboost.XGBClassifier` | 高性能梯度提升 |
| 评估指标 | AUC-ROC, F1, Accuracy, Precision, Recall | `sklearn.metrics.*` | 多维度评估分类性能 |
| 阈值优化 | Youden's J | `J = sensitivity + specificity - 1` | 选择最优分类阈值 |
| 特征重要性 | SHAP | `shap.Explainer` | 模型可解释性分析 |

**替代方法**：
- SVM（对小样本有效，但可解释性差）
- KNN（简单但对特征尺度敏感）
- 神经网络（样本量不足，不推荐）

### 6.4 实施步骤

1. **数据准备** — 加载筛选后数据集，划分特征矩阵 X 和目标向量 y
2. **基线模型训练** — 训练 Logistic Regression，5-fold Stratified CV 评估
3. **集成模型训练** — 分别训练 Random Forest、Gradient Boosting、XGBoost
4. **模型评估** — 计算 AUC-ROC、F1-Score、Accuracy、Precision、Recall
5. **模型比较** — 生成模型性能对比表，确定最优模型
6. **ROC 曲线绘制** — 绘制各模型的 ROC 曲线和 AUC 对比图
7. **特征重要性分析** — 使用 SHAP 分析最优模型的特征贡献
8. **最优模型保存** — 保存最优模型为 .pkl 文件

### 6.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | 模型性能对比表 | `ch05_model_comparison.csv` | CSV | ch06 |
| 2 | 交叉验证详细结果 | `ch05_cv_results.csv` | CSV | 参考 |
| 3 | ROC 曲线对比图 | `ch05_roc_curves.png` | PNG | 报告配图 |
| 4 | 混淆矩阵图 | `ch05_confusion_matrices.png` | PNG | 报告配图 |
| 5 | SHAP 特征重要性图 | `ch05_shap_summary.png` | PNG | 报告配图 |
| 6 | SHAP 依赖图 | `ch05_shap_dependence.png` | PNG | 报告配图 |
| 7 | 最优模型文件 | `ch05_best_model.pkl` | PKL | 部署参考 |
| 8 | 建模报告 | `ch05_modeling_report.md` | Markdown | ch06 |

### 6.6 质量验证标准

- [ ] 至少训练 4 种模型（LR, RF, GB, XGBoost）
- [ ] 使用 5-fold Stratified CV 评估（非简单 train/test split）
- [ ] 评估指标覆盖 AUC-ROC, F1, Accuracy, Precision, Recall
- [ ] 最优模型 AUC-ROC > 0.70（基线水平）
- [ ] SHAP 分析完成，特征重要性可解释
- [ ] 最优模型已保存为 .pkl 文件

---

## 第七章 总结报告（ch06）

> **章节类型**: 原型 C（总结报告型）
> **状态**: ⬜ 待执行

### 7.1 研究目标

系统完成胆结石数据集全链条研究，完整揭示胆结石患者与非患者的临床特征差异、独立风险因素和预测模型性能，形成可供临床参考的分析报告。

### 7.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 全部前序章节产物 | `outputs/ch01~ch05/*/` | 混合格式 | 各章节分析结论与数据 |

### 7.3 技术方法

| 环节 | 方法 | 说明 |
|------|------|------|
| 成果汇总 | 结构化整理 | 按章节顺序汇总核心发现与关键指标 |
| 指标总览 | 交叉引用 | 提取各章节核心指标，形成总览表 |
| 不足分析 | 反思归纳 | 系统梳理研究局限性与改进方向 |
| 展望规划 | 前瞻推演 | 提出未来可拓展的研究方向 |

### 7.4 实施步骤

1. **全流程成果梳理** — 按章节顺序，逐章提取核心发现、关键指标、代表性图表
2. **关键指标总览表编制** — 汇总全部量化指标（显著特征数、效应量、模型 AUC 等）
3. **研究局限性分析** — 从数据（样本量、横截面设计）、方法（共线性、模型选择）、范围（外部验证）三个维度梳理不足
4. **未来研究方向展望** — 提出扩大样本量、纵向研究、外部验证、深度学习等改进方向
5. **总结报告撰写** — 整合以上内容，形成完整 Markdown 总结文档

### 7.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | 成果汇总报告 | `ch06_achievements_summary.md` | Markdown | 最终交付 |
| 2 | 关键指标总览表 | `ch06_key_metrics_table.csv` | CSV | 最终交付 |

### 7.6 质量验证标准

- [ ] 全部前序章节的核心发现均已纳入总结
- [ ] 关键指标总览表覆盖所有量化结论
- [ ] 局限性分析覆盖数据、方法、范围三个维度
- [ ] 每个改进方向均有明确的预期效果说明

---

## 附录

### 附录 A: 项目文件目录结构

```
gallstone_analysis/
├── data/                              # 原始数据（只读）
│   └── dataset-uci.xlsx
├── src/                               # 源代码
│   ├── utils/                         #   通用工具模块
│   │   ├── config.py
│   │   ├── data_loader.py
│   │   ├── output_manager.py
│   │   └── task_graph.py
│   ├── ch01_preprocessing/
│   ├── ch02_eda/
│   ├── ch03_statistical_test/
│   ├── ch04_feature_selection/
│   ├── ch05_modeling/
│   └── ch06_summary/
├── outputs/                           # 输出产物
│   ├── ch01_preprocessing/            #   9 个文件 ✅
│   ├── ch02_eda/
│   ├── ch03_statistical_test/
│   ├── ch04_feature_selection/
│   ├── ch05_modeling/
│   └── ch06_summary/
├── docs/                              # 项目文档
│   ├── project_convention.md          #   项目规范
│   ├── gallstone_analysis_流程设计.md  #   本文档
│   ├── task_dispatch_guide.md         #   任务分发指南
│   └── gallstone_analysis_Execution_Prompts.md
├── requirements.txt
└── README.md
```

### 附录 B: 文件命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 数据文件 | `ch{NN}_{描述}.csv` | `ch01_cleaned_dataset.csv` |
| 图片文件 | `ch{NN}_{描述}.png` | `ch02_distribution_plots.png` |
| 模型文件 | `ch{NN}_{模型名}.pkl` | `ch05_best_model.pkl` |
| 报告文件 | `ch{NN}_{描述}.md` | `ch05_modeling_report.md` |

### 附录 C: 全局可复用 Skill 库

| Skill | 名称 | 适用章节 | 核心功能 |
|-------|------|----------|----------|
| Skill-01 | 标准数据加载器 | 全部 6 章 | `load_cleaned_data()`, `load_selected_features()` |
| Skill-02 | 标准可视化出图器 | ch02~ch05 | `plot_grouped_boxplot()`, `plot_roc_curves()`, `plot_forest()` |
| Skill-03 | 标准评估指标计算器 | ch03, ch05 | `calc_cohens_d()`, `calc_vif()`, `compare_models()` |
| Skill-04 | 标准输出产物管理器 | 全部 6 章 | `save_dataframe()`, `save_figure()`, `generate_quality_checklist()` |

### 附录 D: 完整依赖清单

```
pandas>=2.0.0              # 数据处理
numpy>=1.24.0              # 数值计算
openpyxl>=3.1.0            # Excel 读写
matplotlib>=3.7.0          # 基础可视化
seaborn>=0.12.0            # 统计可视化
scipy>=1.10.0              # 统计检验
statsmodels>=0.14.0        # 统计建模与多重比较校正
scikit-learn>=1.3.0        # 机器学习模型
xgboost>=2.0.0             # XGBoost 梯度提升
shap>=0.43.0               # 模型可解释性分析
jupyter>=1.0.0             # Jupyter Notebook
ipykernel>=6.25.0          # IPython Kernel
tqdm>=4.65.0               # 进度条
```

### 附录 E: 已知版本兼容性约束

| 约束 | 说明 | 推荐处理 |
|------|------|----------|
| xgboost + scikit-learn | xgboost 2.x 需要 scikit-learn >= 1.3 | 使用 requirements.txt 锁定版本 |
| shap + xgboost | shap 0.43+ 兼容 xgboost 2.x | 保持版本一致 |
| statsmodels + scipy | statsmodels 0.14+ 需要 scipy >= 1.10 | 使用 requirements.txt 锁定版本 |
| matplotlib 中文字体 | Linux 环境需安装中文字体 | `WenQuanYi Micro Hei` 或 `Noto Sans CJK SC` |
