# ISSUE-006: 补充 ch04 福利-薪资关联分析

**类型**: AFK
**优先级**: P1
**批次**: Batch-2
**状态**: done
**依赖**: ISSUE-003

## 描述
在 enterprise.py 新增 Step 4.9：计算福利标签数与salary_avg的Pearson相关系数，绘制分箱箱线图，保存为ch04_benefit_salary_correlation.png。

## 验收标准
- [x] ch04_benefit_salary_correlation.png 存在
- [x] Pearson相关系数在[-1,1]范围内
- [x] 统计表包含相关系数记录

## 相关文件
- src/ch04_enterprise_features/enterprise.py
