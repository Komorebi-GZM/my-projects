# Data Analysis

本目录收录 9 个数据分析项目，覆盖能源电力、金融文本挖掘、医疗建模、工业异常检测、市场分析等多个领域。项目统一采用 `src/` 分章节模块化 + `outputs/` 产物输出 + `docs/` 规范文档的标准化工程结构。

---

## 项目列表

| 目录 | 项目名 | 领域 | 数据规模 | 状态 |
|------|--------|------|----------|------|
| [morocco-load-analysis/](./morocco-load-analysis/) | 摩洛哥电力负荷分析 | 能源/电力 | 4城市时序 | 已完成 |
| [ev-market-analysis/](./ev-market-analysis/) | 全球电动汽车市场分析 | 汽车/市场 | EV参数数据 | 已完成 |
| [ab-test-analysis/](./ab-test-analysis/) | A/B 测试数据分析 | 互联网产品 | 20,000 用户 | 已完成 |
| [financial-news-sentiment/](./financial-news-sentiment/) | 财经新闻情感分析与股市预测 | 金融/NLP | 14 万条新闻 | 已完成 |
| [online-gaming-analysis/](./online-gaming-analysis/) | 在线小游戏平台数据分析 | 游戏 | 平台数据 | 已完成 |
| [gallstone-prediction/](./gallstone-prediction/) | 胆结石临床预测建模 | 医疗/临床 | 319 例患者 | 已完成 |
| [plc-genesis-anomaly/](./plc-genesis-anomaly/) | PLC 零件分拣系统异常检测 | 工业自动化 | 传感器时序 | 已完成 |
| [product-sales-analysis/](./product-sales-analysis/) | 产品销量与价格弹性分析 | 零售/电商 | 1,000 条交易 | 已完成 |
| [51job-recruitment-analysis/](./51job-recruitment-analysis/) | 前程无忧招聘数据分析 | 招聘/HR | 295 条职位 | 已完成 |

---

### 摩洛哥电力负荷分析

基于摩洛哥 4 城市智能电表高分辨率数据的电力负荷特征挖掘、峰值检测、多模型负荷预测（ARIMA/LSTM/XGBoost/Prophet）及配电网优化（PuLP 线性规划）。

- **关键技术**：STL 分解 · 时间序列预测 · 跨国对比（中摩） · 配网优化
- **技术栈**：Python · pandas · XGBoost · LightGBM · Prophet · PyTorch · PuLP

### 全球电动汽车市场分析

对全球 EV 市场数据进行全维度分析，涵盖价格机制建模、技术参数 CAGR 趋势、销量归因分析、竞品雷达对标及聚类建模（KMeans+PCA+t-SNE），产出商业策略建议。

- **关键技术**：聚类分析 · PCA 降维 · 竞品雷达图 · CAGR 趋势
- **技术栈**：Python · scikit-learn · matplotlib · seaborn

### A/B 测试数据分析

对互联网产品新旧版页面的 A/B 测试点击数据进行规范的统计推断，包括 CTR 指标可视化、Z 检验/Fisher 精确检验、置信区间及时间趋势分析。

- **关键技术**：假设检验 · 置信区间 · CTR 对比 · 业务决策建议
- **技术栈**：Python · scipy · statsmodels · pandas

### 财经新闻情感分析与股市预测

对印度金融市场约 14 万条财经新闻（2016–2026）进行 NLP 文本情感分析、BERTopic/LDA 主题建模、特征工程及事件驱动策略回测，生成 Streamlit 交互看板。

- **关键技术**：情感分析 · BERTopic · 事件驱动策略 · Streamlit 看板
- **技术栈**：Python · transformers · PyTorch · sentence-transformers · gensim · Streamlit

### 在线小游戏平台数据分析

在线小游戏平台（Newgrounds/Poki）热度分析、标签共现矩阵挖掘、长尾分布分析及跨平台统计差异检验。

- **关键技术**：头部效应分析 · 共现矩阵 · 长尾分析 · 跨平台对比
- **技术栈**：Python · pandas · matplotlib · seaborn

### 胆结石临床预测建模

基于 UCI 胆结石临床数据集（319 例，39 特征），通过多维度 EDA、统计检验（正态性+差异检验+森林图）、LASSO+RF+RFE 特征选择及 ML 建模（ROC+SHAP 可解释性）。

- **关键技术**：特征选择 · ROC 曲线 · SHAP 可解释性 · 可视化报表
- **技术栈**：Python · scikit-learn · scipy · statsmodels · SHAP

### PLC 零件分拣系统异常检测

对 PLC 控制的 Genesis 小型零件自动分拣系统传感器数据进行分析，包含状态机流程建模、异常工况检测、传感器相关性分析及分拣效率评估。

- **关键技术**：PLC 状态机分析 · 异常检测 · 传感器相关性 · 效率评估
- **技术栈**：Python · pandas · scipy · matplotlib · seaborn

### 产品销量与价格弹性分析

零售/电商产品 1,000 条交易数据的清洗、描述统计、时序销售预测（移动平均+指数平滑）、价格弹性回归分析及分类/区域/定价策略建议。

- **关键技术**：移动平均预测 · 指数平滑 · 价格弹性回归 · 策略建议
- **技术栈**：Python · pandas · scipy · matplotlib · seaborn · statsmodels

### 前程无忧招聘数据分析

前程无忧（51job）招聘平台 295 条数据的薪资分布（按学历/经验/行业）、人才供需热力图、企业福利特征及招聘偏好多维度可视化分析。

- **关键技术**：薪资分析 · 供需热力图 · 企业特征挖掘 · 多维可视化
- **技术栈**：Python · pandas · matplotlib · seaborn · jieba · wordcloud
