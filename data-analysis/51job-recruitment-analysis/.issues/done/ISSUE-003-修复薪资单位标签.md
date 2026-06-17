# ISSUE-003: 修复 ch02/ch05 薪资单位标签

**类型**: AFK
**优先级**: P0
**批次**: Batch-2/3
**状态**: done
**依赖**: ISSUE-005

## 描述
将 salary.py（3处）和 summary.py（19处）中所有"千/月"替换为"万/月"，修复报告中薪资数值被低估10倍的问题。

## 验收标准
- [x] grep "千/月" salary.py 返回空
- [x] grep "千/月" summary.py 返回空
- [x] 重跑后图表标签显示"万/月"

## 相关文件
- src/ch02_salary_analysis/salary.py
- src/ch05_summary_report/summary.py
