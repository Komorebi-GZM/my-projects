# UCI 胆结石数据集分析 — 最终交付清单

> 生成时间：2026-05-04（终版）
> 项目名称：gallstone_analysis（UCI 胆结石数据集分析）
> Python 版本：3.10.12
> 交付状态：✅ 可交付

---

## 一、项目目录结构

```
gallstone_analysis/
├── data/                              # 原始数据（只读）
│   └── dataset-uci.xlsx               #    UCI 胆结石数据集（319×39）
├── src/                               # 源代码
│   ├── utils/                         #    通用工具模块（7 个文件）
│   ├── ch01_preprocessing/            #    数据预处理
│   ├── ch02_eda/                      #    探索性数据分析
│   ├── ch03_statistical_test/         #    统计检验
│   ├── ch04_feature_selection/        #    特征筛选
│   ├── ch05_modeling/                 #    建模预测
│   └── ch06_summary/                  #    总结报告
├── outputs/                           # 输出产物（49 个文件）
│   ├── ch01_preprocessing/            #    ch01 产物（9 个）
│   ├── ch02_eda/                      #    ch02 产物（13 个）
│   ├── ch03_statistical_test/         #    ch03 产物（6 个）
│   ├── ch04_feature_selection/        #    ch04 产物（12 个）
│   ├── ch05_modeling/                 #    ch05 产物（7 个）
│   ├── ch06_summary/                  #    ch06 产物（2 个）
│   ├── final_quality_report.md        #    质量报告
│   └── final_delivery_list.md         #    本交付清单
├── docs/                              # 项目文档（4 个文件）
└── requirements.txt                   # Python 依赖清单
```

---

## 二、源代码（16 个文件）

| 文件路径 | 说明 |
|----------|------|
| src/utils/__init__.py | 工具包初始化 |
| src/utils/config.py | 全局配置（路径、领域参数、绘图样式、质量阈值） |
| src/utils/data_loader.py | 数据加载器（支持 CSV/Excel/JSON） |
| src/utils/output_manager.py | 产物保存工具（DataFrame/图片/Markdown） |
| src/utils/metrics.py | 评估指标工具（Cohen's d、VIF 等） |
| src/utils/visualizer.py | 可视化工具（热力图、箱线图、分布图等） |
| src/utils/task_graph.py | 任务依赖图与进度检查（CLI 工具） |
| src/ch01_preprocessing/preprocess.py | 数据预处理脚本 |
| src/ch01_preprocessing/preprocess.ipynb | 数据预处理 Notebook |
| src/ch02_eda/eda.py | 探索性数据分析脚本 |
| src/ch02_eda/eda.ipynb | 探索性数据分析 Notebook |
| src/ch03_statistical_test/stat_test.py | 统计检验脚本 |
| src/ch03_statistical_test/stat_test.ipynb | 统计检验 Notebook |
| src/ch04_feature_selection/feature_select.py | 特征筛选脚本 |
| src/ch04_feature_selection/feature_select.ipynb | 特征筛选 Notebook |
| src/ch05_modeling/modeling.py | 建模预测脚本 |
| src/ch05_modeling/modeling.ipynb | 建模预测 Notebook |
| src/ch06_summary/summary.py | 总结报告脚本 |
| src/ch06_summary/summary.ipynb | 总结报告 Notebook |

---

## 三、产物文件（49 个）

### 3.1 ch01 数据预处理（9 个）

| 文件路径 | 说明 |
|----------|------|
| outputs/ch01_preprocessing/ch01_cleaned_dataset.csv | 清洗后数据集（319×39） |
| outputs/ch01_preprocessing/ch01_cleaned_dataset.xlsx | 清洗后数据集（Excel 格式） |
| outputs/ch01_preprocessing/ch01_cleaned_data_statistics.csv | 清洗后数据统计摘要 |
| outputs/ch01_preprocessing/ch01_cleaning_report.json | 清洗操作记录（列名映射、异常值统计） |
| outputs/ch01_preprocessing/ch01_outlier_report.csv | 异常值检测报告（IQR 方法，26 列 226 个异常值） |
| outputs/ch01_preprocessing/ch01_boxplot_before_after.png | 异常值处理前后箱线图 |
| outputs/ch01_preprocessing/ch01_correlation_heatmap.png | 特征相关性热力图 |
| outputs/ch01_preprocessing/ch01_histogram_cleaned.png | 清洗后连续变量分布直方图 |
| outputs/ch01_preprocessing/ch01_target_distribution.png | 目标变量分布图 |

### 3.2 ch02 探索性分析（13 个）

| 文件路径 | 说明 |
|----------|------|
| outputs/ch02_eda/ch02_descriptive_stats.csv | 全量描述性统计表 |
| outputs/ch02_eda/ch02_group_descriptive_stats.csv | 按 Gallstone_Status 分组统计 |
| outputs/ch02_eda/ch02_sex_stratified_stats.csv | 性别分层统计 |
| outputs/ch02_eda/ch02_effect_sizes.csv | Cohen's d 效应量表 |
| outputs/ch02_eda/ch02_top10_differences.csv | Top 10 组间差异特征 |
| outputs/ch02_eda/ch02_categorical_summary.csv | 分类变量汇总 |
| outputs/ch02_eda/ch02_continuous_distributions.png | 连续变量分布图 |
| outputs/ch02_eda/ch02_group_boxplots.png | 分组箱线图 |
| outputs/ch02_eda/ch02_correlation_heatmap.png | 相关性热力图 |
| outputs/ch02_eda/ch02_group_correlation_heatmaps.png | 分组相关性热力图 |
| outputs/ch02_eda/ch02_sex_stratified_distributions.png | 性别分层分布图 |
| outputs/ch02_eda/ch02_categorical_stacked_barplots.png | 分类变量堆叠条形图 |
| outputs/ch02_eda/ch02_top10_differences.png | Top 10 差异可视化 |

### 3.3 ch03 统计检验（6 个）

| 文件路径 | 说明 |
|----------|------|
| outputs/ch03_statistical_test/ch03_normality_test.csv | Shapiro-Wilk 正态性检验结果 |
| outputs/ch03_statistical_test/ch03_continuous_tests.csv | 连续变量组间差异检验（t-test/Mann-Whitney U） |
| outputs/ch03_statistical_test/ch03_categorical_tests.csv | 分类变量卡方检验结果 |
| outputs/ch03_statistical_test/ch03_corrected_results.csv | FDR + Bonferroni 多重比较校正结果 |
| outputs/ch03_statistical_test/ch03_significant_features.csv | 显著特征汇总（15 个，FDR p<0.05） |
| outputs/ch03_statistical_test/ch03_forest_plot.png | 效应量森林图 |

### 3.4 ch04 特征筛选（12 个）

| 文件路径 | 说明 |
|----------|------|
| outputs/ch04_feature_selection/ch04_statistical_selection.csv | 统计显著性筛选结果 |
| outputs/ch04_feature_selection/ch04_vif_analysis.csv | VIF 共线性诊断结果 |
| outputs/ch04_feature_selection/ch04_lasso_selection.csv | LASSO 回归筛选结果 |
| outputs/ch04_feature_selection/ch04_rfe_ranking.csv | 递归特征消除（RFE）排序 |
| outputs/ch04_feature_selection/ch04_rf_importance.csv | 随机森林特征重要性 |
| outputs/ch04_feature_selection/ch04_composite_score.csv | 5 种方法综合评分表 |
| outputs/ch04_feature_selection/ch04_final_features.csv | 最终 11 个特征列表 |
| outputs/ch04_feature_selection/ch04_selected_features_data.csv | 筛选后数据集（319×11） |
| outputs/ch04_feature_selection/ch04_feature_importance.png | 综合评分 + VIF 双面板图 |
| outputs/ch04_feature_selection/ch04_lasso_coefficients.png | LASSO 系数路径图 |
| outputs/ch04_feature_selection/ch04_rf_importance.png | 随机森林重要性图 |
| outputs/ch04_feature_selection/ch04_composite_score_heatmap.png | 综合评分热力图 |

### 3.5 ch05 建模预测（7 个）

| 文件路径 | 说明 |
|----------|------|
| outputs/ch05_modeling/ch05_model_comparison.csv | 3 种模型 5 折交叉验证对比 |
| outputs/ch05_modeling/ch05_best_model.pkl | 最优模型（LogisticRegression + scaler + 特征列表） |
| outputs/ch05_modeling/ch05_best_model_info.csv | 最优模型参数信息 |
| outputs/ch05_modeling/ch05_roc_curves.png | ROC 曲线对比图 |
| outputs/ch05_modeling/ch05_shap_summary.png | SHAP 特征重要性图 |
| outputs/ch05_modeling/ch05_shap_dependence.png | SHAP 依赖图（Top 3 特征） |
| outputs/ch05_modeling/ch05_shap_values.csv | SHAP 值数据 |

### 3.6 ch06 总结报告（2 个）

| 文件路径 | 说明 |
|----------|------|
| outputs/ch06_summary/ch06_achievements_summary.md | 全流程总结报告 |
| outputs/ch06_summary/ch06_key_metrics_table.csv | 关键指标总览表 |
| outputs/ch06_summary/ch06_final_summary_report.md | 最终领域洞察报告 |

---

## 四、项目文档（4 个）

| 文件路径 | 说明 |
|----------|------|
| docs/project_convention.md | 项目规范（唯一规范依据，645 行） |
| docs/gallstone_analysis_流程设计.md | 流程设计文档（6 章详细步骤） |
| docs/gallstone_analysis_Execution_Prompts.md | 各 Prompt 执行细节 |
| docs/task_dispatch_guide.md | 任务分发指南（依赖图 + 派活模板） |

---

## 五、配置与依赖（2 个）

| 文件路径 | 说明 |
|----------|------|
| requirements.txt | Python 依赖清单 |
| data/dataset-uci.xlsx | 原始数据集（只读，319×39） |

---

## 六、最终交付物（3 个）

| 文件路径 | 说明 |
|----------|------|
| outputs/final_quality_report.md | 质量报告（合规性检查 + 修复记录） |
| outputs/final_delivery_list.md | 本交付清单 |
| outputs/ch06_summary/ch06_final_summary_report.md | 最终领域洞察报告 |

---

## 七、交付统计

| 类别 | 数量 |
|------|------|
| 源代码文件（.py） | 13 |
| Jupyter Notebook（.ipynb） | 6 |
| 产物文件 | 49 |
| 项目文档 | 4 |
| 配置/依赖 | 2 |
| 最终交付物 | 3 |
| **总计** | **77** |
