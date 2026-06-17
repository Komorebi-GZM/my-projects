# 在线小游戏跨平台对比分析报告

> 生成时间：2026-05-01 22:42:52
> 对比平台：Poki vs Newgrounds

## 1. 数据概况

| 指标 | Poki | Newgrounds |
|------|------|------------|
| 游戏数量 | 1664 | 9742 |
| 占比 | 14.6% | 85.4% |
| 点赞总数 | 314,078,332 | 581,499 |
| 踩总数 | 60,086,205 | 299,183 |

## 2. 热度指标对比

| 指标 | Poki 均值 | Newgrounds 均值 | Poki 中位数 | Newgrounds 中位数 |
|------|-----------|-----------------|-------------|-------------------|
| likes | 188749.0 | 59.7 | 41900.0 | 37.0 |
| dislikes | 36109.5 | 30.7 | 9050.0 | 28.0 |
| like_ratio | 0.8108 | 0.5957 | 0.8256 | 0.5932 |
| tag_count | 6.25 | 2.20 | 6.0 | 2.0 |

## 3. 统计检验结果（Mann-Whitney U）

| 指标 | Poki 均值 | NG 均值 | U 统计量 | p 值 | 显著差异 |
|------|----------|---------|----------|------|---------|
| likes | 188748.9976 | 59.6899 | 15925487.5 | 0.000000 | 是 |
| dislikes | 36109.4982 | 30.7106 | 15912186.5 | 0.000000 | 是 |
| like_ratio | 0.8108 | 0.5957 | 15160414.0 | 0.000000 | 是 |
| tag_count | 6.2464 | 2.1955 | 15686442.0 | 0.000000 | 是 |

## 4. 平台标签偏好对比

### Poki Top 10 标签
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

### Newgrounds Top 10 标签
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

## 5. 关键差异总结

### 规模差异
- Poki 平台仅 **1664** 款游戏，但其平均点赞数（**188749**）远高于 Newgrounds（**60**）
- Newgrounds 平台游戏数量（**9742**）是 Poki 的 **5.9 倍**

### 热度差异
- Poki 游戏热度方差更大（标准差 603681 vs 84）
- 在 likes、dislikes、like_ratio、tag_count 指标上存在显著统计差异（p < 0.05）

### 标签差异
- Poki 平台标签更丰富：最多 **26** 个标签/游戏
- Newgrounds 平台标签分布更集中：中位数 **2.0** 个标签/游戏

## 6. 输出产物清单

| 文件 | 说明 |
|------|------|
| `ch04_platform_comparison.csv` | 平台对比统计表 |
| `ch04_statistical_tests.csv` | 统计检验结果表 |
| `ch04_metric_comparison.png` | 指标对比箱线图 |
| `ch04_like_ratio_comparison.png` | 点赞率分布对比 |
| `ch04_likes_dist_comparison.png` | 点赞数分布对比 |
| `ch04_tag_count_comparison.png` | 标签数量分布对比 |
| `ch04_platform_correlation.png` | 平台相关性散点图 |
| `ch04_platform_analysis_report.md` | 本文档 |
