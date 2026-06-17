# Prompt-04 短期电力负荷预测 — 产物说明文档

## 概述

本章节基于摩洛哥 Laayoune 城市 zone1 馈线的 10 分钟粒度负荷数据（2022-09 ~ 2024-05，共 88,746 个有效样本），构建了 **ARIMA、XGBoost、LightGBM、Prophet、LSTM** 五种短期负荷预测模型进行对比选型，最终选定最优模型完成未来 24 小时滚动预测。

---

## 产物清单与说明

### 1. 文档类产物

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `ch04_target_selection.md` | Markdown | 预测目标选择说明文档，阐述为何选择 Laayoune zone1 作为预测目标（数据跨度最长、采样频率最高、完整性最好） |
| `ch04_data_split_info.json` | JSON | 数据集划分信息，记录训练/验证/测试集的样本数、时间范围、特征列名、划分方式（时序顺序，严禁 shuffle） |

### 2. 数据类产物

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `ch04_feature_dataset.csv` | CSV | 特征工程后的完整数据集（88,746 行 × 19 列），包含原始时间特征 + 6 个滞后特征 + 6 个滚动统计特征，供后续章节复用 |

**`ch04_feature_dataset.csv` 列说明**：

| 列名 | 含义 | 类型 |
|------|------|------|
| `load_kw` | 目标变量：zone1 有功负荷（kW） | float |
| `hour` | 小时（0~23） | int |
| `day_of_week` | 星期几（0=周一, 6=周日） | int |
| `is_weekend` | 是否周末（0=工作日, 1=周末） | int |
| `month` | 月份（1~12） | int |
| `season` | 季节编码（0=冬, 1=春, 2=夏, 3=秋） | int |
| `year` | 年份 | int |
| `lag_1` | 前 1 个时间步（10 分钟）的负荷值 | float |
| `lag_6` | 前 1 小时的负荷值 | float |
| `lag_12` | 前 2 小时的负荷值 | float |
| `lag_24` | 前 4 小时的负荷值 | float |
| `lag_48` | 前 8 小时的负荷值 | float |
| `lag_144` | 前 24 小时（1 天）的负荷值 | float |
| `rolling_mean_6` | 前 1 小时滑动均值 | float |
| `rolling_std_6` | 前 1 小时滑动标准差 | float |
| `rolling_mean_12` | 前 2 小时滑动均值 | float |
| `rolling_std_12` | 前 2 小时滑动标准差 | float |
| `rolling_mean_24` | 前 4 小时滑动均值 | float |
| `rolling_std_24` | 前 4 小时滑动标准差 | float |

### 3. 模型文件

| 文件名 | 格式 | 模型 | 说明 |
|--------|------|------|------|
| `ch04_arima_model.pkl` | pickle | ARIMA(1,1,2) | 纯 ARIMA 非季节模型，在小时级降采样数据上训练，作为统计基线 |
| `ch04_xgb_model.json` | JSON | XGBoost | 梯度提升树模型，最佳迭代 154 轮，支持特征重要性分析 |
| `ch04_lgbm_model.txt` | 文本 | LightGBM | 轻量梯度提升模型，最佳迭代 64 轮，训练速度最快 |
| `ch04_lstm_model.pt` | PyTorch | LSTM | 1 层 LSTM + 全连接层，hidden_size=32，序列窗口 24 步（4 小时） |

### 4. 模型评估对比

| 文件名 | 说明 |
|--------|------|
| `ch04_model_comparison.csv` | 五模型评估指标对比表，按 MAPE 升序排列 |

**`ch04_model_comparison.csv` 列说明**：

| 列名 | 含义 |
|------|------|
| `rank` | 排名（按 MAPE 升序） |
| `model` | 模型名称 |
| `MAE` | 平均绝对误差（kW），越小越好 |
| `RMSE` | 均方根误差（kW），越小越好，对大误差更敏感 |
| `MAPE` | 平均绝对百分比误差（%），跳过低于 0.5 kW 的低负荷点 |
| `quality` | 质量评级：<5% Outstanding / <10% Excellent / <15% Pass / ≥15% Needs Improvement |

**本次评估结果**：

| 排名 | 模型 | MAE | RMSE | MAPE | 质量 |
|------|------|-----|------|------|------|
| 1 | Prophet | 0.44 | 0.44 | 4.09% | Outstanding |
| 2 | LightGBM | 0.66 | 4.74 | 4.88% | Outstanding |
| 3 | XGBoost | 0.84 | 13.71 | 5.50% | Excellent |
| 4 | LSTM | 1.56 | 1.92 | 14.41% | Pass |
| 5 | ARIMA | 2.33 | 2.87 | 20.48% | Needs Improvement |

> **注意**：ARIMA 和 Prophet 在小时级降采样数据上评估（10min → 1h），XGBoost/LightGBM/LSTM 在原始 10min 粒度上评估，因此 MAE/RMSE 量纲不同，**MAPE 为归一化指标，可直接跨模型对比**。

---

## 图表产物详细说明

### 5. 单模型预测对比图（5 张）

| 文件名 | 模型 | 评估粒度 |
|--------|------|----------|
| `ch04_arima_forecast.png` | ARIMA | 小时级 |
| `ch04_xgb_forecast.png` | XGBoost | 10 分钟级 |
| `ch04_lgbm_forecast.png` | LightGBM | 10 分钟级 |
| `ch04_prophet_forecast.png` | Prophet | 小时级 |
| `ch04_lstm_forecast.png` | LSTM | 10 分钟级 |

**图表格式统一**（由 `visualizer.py` 的 `plot_model_forecast()` 生成）：

| 元素 | 说明 |
|------|------|
| **横轴 (X)** | 时间步（Time Step），即测试集中的时间顺序编号 |
| **纵轴 (Y)** | 负荷（Load），单位 kW |
| **蓝色实线** | 实际负荷值（Actual） |
| **红色虚线** | 模型预测值（Predicted） |
| **左上角文本框** | 叠加显示 MAE、RMSE、MAPE 三项评估指标 |
| **图例** | 位于右上角，标注 Actual / Predicted |

### 6. 24 小时滚动预测图（1 张）

| 文件名 | 说明 |
|--------|------|
| `ch04_24h_rolling_forecast.png` | 最优模型（Prophet）对未来 24 小时（144 个 10min 点）的滚动预测结果 |

**图表元素说明**：

| 元素 | 说明 |
|------|------|
| **横轴 (X)** | 时间（DateTime），从数据末尾 2024-05-24 00:10 起，跨度 24 小时至 2024-05-25 00:00 |
| **纵轴 (Y)** | 预测负荷（kW） |
| **红色实线** | 24 小时预测负荷曲线（Prophet 模型） |
| **绿色竖虚线** | 4 小时分界线，标注 "4h" |
| **黄色竖虚线** | 8 小时分界线，标注 "8h" |
| **橙色渐变阴影** | 预测置信度递减区域（越靠右越透明，表示越不可靠） |
| **左下角文本框** | 说明文字："阴影区域表示预测置信度递减，前 4~8 小时预测最为可靠" |

---

## 技术备注

1. **数据划分**：严格按时间顺序 80/10/10 划分，训练集 2022-09 ~ 2024-01，验证集 2024-01 ~ 2024-03，测试集 2024-03 ~ 2024-05，**严禁随机 shuffle**
2. **MAPE 低负荷过滤**：跳过实际负荷低于 0.5 kW 的数据点，避免夜间低谷负荷导致 MAPE 爆炸
3. **ARIMA/Prophet 降采样**：为避免 88K 样本上内存溢出（OOM），ARIMA 和 Prophet 在小时级降采样数据上训练和评估
4. **LSTM 参数**：CPU 友好配置（hidden=32, layers=1, epochs=20, patience=3, batch=128）
5. **24h 滚动预测**：逐步预测存在误差累积，前 4~8 小时预测最为可靠，后续逐步退化属正常现象
