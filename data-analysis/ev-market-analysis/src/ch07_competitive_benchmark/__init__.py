# -*- coding: utf-8 -*-
"""ch07_competitive_benchmark - 竞品对标分析模块

本模块实现电动汽车市场的竞品对标分析，包括：
- 同级分组定义与价格对比
- 性价比评分构建与排名
- 竞争力雷达图可视化
- 品牌产品矩阵分析
- 同级综合排名

产物:
- segment_comparison.csv: 同级对比表
- value_ranking.csv: 性价比排名表
- competitiveness_radar.png: 竞争力雷达图
- brand_product_matrix.csv: 品牌产品矩阵
- segment_comprehensive_ranking.csv: 同级综合排名
- ch07_report.md: 章节报告
"""

from .analysis import main

__all__ = ["main"]
