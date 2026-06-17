# 在线小游戏标签分析报告

> 生成时间：2026-05-01 22:41:28

## 1. 标签数据概况

| 指标 | 值 |
|------|------|
| 分析游戏总数 | 11406 |
| 有标签游戏数 | 11372 |
| 无标签游戏数 | 34 |
| 标签总出现次数 | 31783 |
| 唯一标签数（清洗后） | 214 |
| 唯一标签数（清洗前） | 216 |
| 清洗减少数 | 2 |

## 2. 标签频率统计

### Top 20 标签

| 排名 | 标签 | 出现次数 | 占比 |
|------|------|---------|------|
| 1 | action | 4278 | 37.5% |
| 2 | other | 4108 | 36.0% |
| 3 | platformer | 1635 | 14.3% |
| 4 | adventure | 1621 | 14.2% |
| 5 | puzzle | 1459 | 12.8% |
| 6 | skill | 1226 | 10.7% |
| 7 | shooter | 1101 | 9.7% |
| 8 | simulation | 814 | 7.1% |
| 9 | point and click | 547 | 4.8% |
| 10 | strategy | 527 | 4.6% |
| 11 | mobile | 445 | 3.9% |
| 12 | gadgets | 430 | 3.8% |
| 13 | rpg | 402 | 3.5% |
| 14 | hop and bop | 391 | 3.4% |
| 15 | visual novel | 370 | 3.2% |
| 16 | fighting | 366 | 3.2% |
| 17 | spam | 364 | 3.2% |
| 18 | brain | 363 | 3.2% |
| 19 | mouse | 340 | 3.0% |
| 20 | sports | 335 | 2.9% |

## 3. 每游戏标签数统计

| 统计量 | 值 |
|--------|------|
| 均值 | 2.79 |
| 中位数 | 2.0 |
| 标准差 | 1.86 |
| 最小值 | 0 |
| 最大值 | 26 |
| 25% 分位 | 2 |
| 75% 分位 | 3 |

## 4. 标签共现分析（Top 10 共现对）

| 排名 | 标签对 | 共现次数 |
|------|--------|---------|
| 1 | action + other | 1807 |
| 2 | action + platformer | 1635 |
| 3 | action + shooter | 1101 |
| 4 | other + platformer | 940 |
| 5 | other + puzzle | 531 |
| 6 | other + adventure | 511 |
| 7 | adventure + point and click | 506 |
| 8 | other + simulation | 439 |
| 9 | adventure + rpg | 394 |
| 10 | action + hop and bop | 391 |

## 5. 平台标签偏好对比

### Poki Top 10
| 排名 | 标签 | 出现次数 |
|------|------|---------|
| 1 | mobile | 445 |
| 2 | skill | 400 |
| 3 | puzzle | 372 |
| 4 | brain | 363 |
| 5 | action | 363 |
| 6 | mouse | 340 |
| 7 | games for boys | 300 |
| 8 | 3d | 253 |
| 9 | adventure | 252 |
| 10 | arcade | 249 |

### Newgrounds Top 10
| 排名 | 标签 | 出现次数 |
|------|------|---------|
| 1 | other | 4108 |
| 2 | action | 3915 |
| 3 | platformer | 1635 |
| 4 | adventure | 1369 |
| 5 | shooter | 1101 |
| 6 | puzzle | 1087 |
| 7 | skill | 826 |
| 8 | simulation | 631 |
| 9 | point and click | 489 |
| 10 | strategy | 458 |

## 6. 输出产物清单

| 文件 | 说明 |
|------|------|
| `ch03_tag_frequency.csv` | 标签频率统计表 |
| `ch03_tag_stats.csv` | 标签分布统计表 |
| `ch03_top20_tags.png` | Top 20 标签柱状图 |
| `ch03_tag_long_tail.png` | 标签长尾分布图 |
| `ch03_tag_count_distribution.png` | 标签数量分布图 |
| `ch03_cooccurrence_top20.png` | 标签共现热力图 |
| `ch03_top20_cooccurrence_pairs.png` | Top 20 共现对柱状图 |
| `ch03_platform_tag_comparison.png` | 平台标签偏好对比 |
| `ch03_tag_analysis_report.md` | 本文档 |
