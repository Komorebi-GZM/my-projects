# -*- coding: utf-8 -*-
"""ch08_quantitative_modeling - 量化建模模块

本模块实现电动汽车市场的量化建模分析，包括：
- 价格预测模型 (Random Forest, XGBoost)
- 模型对比与特征重要性分析
- K-Means 聚类分析
- 簇特征画像

产物:
- price_model_rf.pkl: Random Forest 价格预测模型
- price_model_xgb.pkl: XGBoost 价格预测模型
- model_metrics.csv: 模型评估指标
- feature_importance.png: 特征重要性图
- prediction_vs_actual.png: 预测vs实际图
- clustering_result.csv: 聚类结果
- silhouette_curve.png: 轮廓系数曲线
- pca_clustering_scatter.png: PCA聚类散点图
- cluster_profiles.csv: 簇特征画像
- ch08_report.md: 章节报告

质量标准:
- RF R² >= 0.75, MAE < $10000
- XGB R² >= 0.75
- 轮廓系数 > 0.3
"""

from .analysis import main

__all__ = ["main"]
