# 数据质量报告 — ch01 数据预处理

> 本报告由 `preprocess.py` 自动生成

## 1. 概述

| 指标 | 值 |
|------|-----|
| **总记录数** | 139,919 |
| **总列数** | 24 |
| **内存占用** | 141.98 MB |
| **日期范围** | 2016-01-01 ~ 2026-04-15 |
| **唯一分类数** | 366 |
| **唯一关键词数** | 414 |

## 2. 列信息

| 列名 | 数据类型 | 非空数 | 缺失率 | 唯一值数 | 示例值 |
|------|----------|--------|--------|----------|--------|
| date | datetime64[ns] | 139,919 | 0.0% | 3,182 | 2016-01-01, 2016-01-02 |
| title | object | 139,919 | 0.0% | 139,906 | Lending to foreign step-down arms of ... |
| description | object | 139,919 | 0.0% | 139,867 | RBI slaps 2% additional provision for... |
| url | category | 139,919 | 0.0% | 134,565 | URL_NOT_AVAILABLE, URL_NOT_AVAILABLE |
| source_file | category | 139,919 | 0.0% | 7 | IndianFinancialNews.csv, IndianFinanc... |
| categories | category | 139,919 | 0.0% | 366 | sector_banking_finance, sector_bankin... |
| matched_keywords | object | 139,919 | 0.0% | 10,061 | rbi, basel |
| relevance_score | int8 | 139,919 | 0.0% | 11 | 2, 2 |
| has_negation | bool | 139,919 | 0.0% | 2 | False, False |
| impact_tier | category | 139,919 | 0.0% | 3 | LOW, LOW |
| year | category | 139,919 | 0.0% | 11 | 2016, 2016 |
| month | category | 139,919 | 0.0% | 12 | 1, 1 |
| day | category | 139,919 | 0.0% | 31 | 1, 2 |
| day_of_week | category | 139,919 | 0.0% | 7 | 4, 5 |
| is_weekend | int64 | 139,919 | 0.0% | 2 | 0, 1 |
| categories_list | object | 139,919 | 0.0% | 139,919 | ['sector_banking_finance'], ['sector_... |
| category_count | int64 | 139,919 | 0.0% | 5 | 1, 1 |
| keywords_list | object | 139,919 | 0.0% | 139,919 | ['rbi'], ['basel'] |
| keyword_count | int64 | 139,919 | 0.0% | 13 | 1, 1 |
| full_text | object | 139,919 | 0.0% | 139,906 | Lending to foreign step-down arms of ... |
| text_length | int64 | 139,919 | 0.0% | 371 | 114, 182 |
| title_length | int64 | 139,919 | 0.0% | 193 | 63, 62 |
| desc_length | int64 | 139,919 | 0.0% | 259 | 48, 117 |
| url_available | int64 | 139,919 | 0.0% | 2 | 0, 0 |

## 3. 数据类型分布

- **category**: 8 列
- **int64**: 7 列
- **object**: 6 列
- **datetime64[ns]**: 1 列
- **int8**: 1 列
- **bool**: 1 列

## 4. 影响等级分布

| 等级 | 数量 | 占比 |
|------|------|------|
| LOW | 57,368 | 41.0% |
| MEDIUM | 79,503 | 56.8% |
| HIGH | 3,048 | 2.2% |

## 5. 否定标记统计

- 含否定表述的新闻: **76** 条 (0.05%)

## 6. 文本长度统计

| 指标 | 值 |
|------|-----|
| 平均长度 | 156.8 字符 |
| 中位长度 | 153.0 字符 |
| 最短 | 21 字符 |
| 最长 | 623 字符 |
| 空文本 | 0 条 |

## 7. 相关性评分统计

| 指标 | 值 |
|------|-----|
| 均值 | 2.79 |
| 标准差 | 1.12 |
| 最小值 | 1 |
| 中位数 | 3 |
| 最大值 | 11 |

## 9. 数据来源统计

| 来源文件 | 记录数 | 占比 |
|----------|--------|------|
| News_sentiment_Jan2017_to_Apr2021.csv | 65,927 | 47.1% |
| economic_times_headlines_2022.csv | 23,126 | 16.5% |
| economic_times_headlines_2023.csv | 21,944 | 15.7% |
| economic_times_headlines_2024.csv | 16,783 | 12.0% |
| economic_times_headlines_2025.csv | 5,452 | 3.9% |
| IndianFinancialNews.csv | 5,355 | 3.8% |
| news_gap_2025_06_12_to_2026_04_15.csv | 1,332 | 1.0% |

## 10. 年度分布

| 年份 | 记录数 | 占比 |
|------|--------|------|
| 2016 | 1,293 | 0.9% |
| 2017 | 15,587 | 11.1% |
| 2018 | 18,066 | 12.9% |
| 2019 | 13,731 | 9.8% |
| 2020 | 19,057 | 13.6% |
| 2021 | 3,548 | 2.5% |
| 2022 | 23,126 | 16.5% |
| 2023 | 21,944 | 15.7% |
| 2024 | 16,783 | 12.0% |
| 2025 | 5,974 | 4.3% |
| 2026 | 810 | 0.6% |

---

*报告生成时间: 2026-05-04 23:17:45*
