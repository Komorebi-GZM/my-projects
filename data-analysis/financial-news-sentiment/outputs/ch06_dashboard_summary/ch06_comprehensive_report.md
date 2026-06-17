# Comprehensive Analysis Report: Financial News Sentiment Analysis

**Generated**: 2026-05-05 16:51


## Executive Summary


This report summarizes the analysis of **139,919** financial news articles spanning from **2016-01-01** to **2026-04-15** (3757 days). The dataset covers **5** industry categories from **7** news sources.


---


## ch01: Data Preprocessing


- **Original records**: 139,919

- **Final columns**: 26

- **Date range**: 2016-01-01 ~ 2026-04-15

- **Missing values**: 0

- **Duplicates**: 0

- **Impact tier distribution**: HIGH 2.2%, MEDIUM 56.8%, LOW 41.0%


## ch02: Descriptive Statistics


- **Top categories**: {'macro_government': 43680, 'stock_specific': 34272, 'geopolitical': 18187, 'sector_banking_finance': 12881, 'sector_cement_infra': 5948}

- **Average text length**: 156.8 characters

- **News volume trend**: Peak years observed in 2020-2022 (COVID + geopolitical events)


## ch03: Sentiment Analysis & Topic Modeling


- **Sentiment distribution**: Positive 23.5%, Neutral 55.9%, Negative 20.6%

- **Mean confidence**: 0.8293

- **Model**: FinBERT (ProsusAI/finbert)

- **Topic diversity (avg entropy)**: 2.445


## ch04: Feature Engineering


- **Total features**: 51

- **Daily frequency**: 3758 days

- **Key features**: sentiment_mean, positive_ratio, news_count, topic_shannon_entropy, impact_weighted

- **Feature importance (Top 3)**: negative_ratio, polarization_idx, positive_ratio


## ch05: Event-Driven Strategy Analysis


- **High-impact events identified**: 959

- **Event type distribution**: {'Policy': 665, 'Earnings': 109, 'Industry': 96, 'Geopolitical': 46, 'Other': 43}

- **Mean influence score**: 0.222

- **Positive impact events**: 516 (53.8%)

- **Negative impact events**: 443 (46.2%)


## Key Findings


1. The Indian financial news landscape is dominated by **neutral** sentiment (55.9%), reflecting the objective nature of financial reporting.

2. **Policy events** are the most frequent high-impact category, accounting for 69.3% of all high-impact events.

3. Feature engineering produced **51** daily features, with sentiment-related features showing the highest importance scores.

4. Event window analysis reveals that high-impact events create measurable sentiment shifts (mean change: 0.0081).


## Limitations & Future Work


1. **No stock price data**: Cannot validate correlation between sentiment and market movements.

2. **Rule-based event classification**: Could be improved with NLP-based semantic clustering.

3. **Static analysis**: Real-time monitoring capability not yet implemented.

4. **Topic model tuning**: BERTopic produced a large number of topics; parameter optimization recommended.


---

*Report generated automatically by ch06_dashboard_summary pipeline.*
