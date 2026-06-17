# -*- coding: utf-8 -*-
"""ch09_business_recommendations - 商业决策建议模块

本模块整合 ch02-ch08 的分析成果，生成商业决策建议，包括：
- 全流程成果梳理
- 关键指标总览表
- 消费者购车建议
- 企业策略建议
- 行业趋势展望
- 研究局限性分析

产物:
- consumer_advice.md: 消费者购车建议
- enterprise_strategy.md: 企业策略建议
- industry_outlook.md: 行业趋势展望
- key_metrics_overview.csv: 关键指标总览
- ch09_report.md: 总结报告

依赖: ch02-ch08 的全部产物
"""

from .analysis import main

__all__ = ["main"]
