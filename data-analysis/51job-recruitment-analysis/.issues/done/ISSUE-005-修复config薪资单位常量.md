# ISSUE-005: 修复 config.py SALARY_UNIT 常量

**类型**: AFK
**优先级**: P0
**批次**: 前置
**状态**: done
**依赖**: 无

## 描述
将 config.py 第56行 salary_unit 从"千/月"改为"万/月"。

## 验收标准
- [x] grep "salary_unit" config.py 显示"万/月"

## 相关文件
- src/utils/config.py
