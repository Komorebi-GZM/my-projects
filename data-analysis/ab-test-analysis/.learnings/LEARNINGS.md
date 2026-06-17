# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## [LRN-20260507-001] correction

**Logged**: 2026-05-07T10:00:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
`__init__.py` 不应复制 config.py 的内容，应作为包导出文件

### Details
在 code_scaffold 阶段，`src/utils/__init__.py` 被错误地写成了 config.py 的不完整副本，CHAPTERS 字典仅含 ch01，缺少 ch02-ch05。各章节脚本通过 `from src.utils.config import Config` 直接导入 config.py，所以当前不影响运行，但违反了 `__init__.py` 作为包初始化文件应导出公共接口的惯例。

### Suggested Action
将 `__init__.py` 改为正确的包导出文件，从 config.py 导入公共接口

### Metadata
- Source: zoom-out 审查
- Related Files: src/utils/__init__.py, src/utils/config.py
- Tags: init, config, package-structure

---

## [LRN-20260507-002] best_practice

**Logged**: 2026-05-07T10:00:00Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
原始数据文件应仅存在于 data/raw/，项目根目录不应散落数据文件

### Details
项目根目录存在 `ab_test_click_data.csv`，与 `data/raw/` 中的文件重复，违反 project_convention.md 第3条禁止事项。

### Suggested Action
删除根目录冗余文件，确保数据文件仅在 data/ 目录下

### Metadata
- Source: zoom-out 审查
- Related Files: ab_test_click_data.csv, data/raw/ab_test_click_data.csv
- Tags: file-structure, convention

---

## [LRN-20260507-003] best_practice

**Logged**: 2026-05-07T10:00:00Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
报告模板中使用 `.4f` 等格式化时，必须处理 N/A 或缺失值情况

### Details
ch05_conclusion_recommendation/run.py 中，当 ch03 结果缺失时，`summary.get('z_stat', 'N/A')` 返回字符串 'N/A'，但后续 `f"{value:.4f}"` 格式化会抛出 TypeError。

### Suggested Action
使用条件判断或 try/except 处理缺失值，确保格式化安全

### Metadata
- Source: zoom-out 审查
- Related Files: src/ch05_conclusion_recommendation/run.py
- Tags: error-handling, formatting, type-safety
- Pattern-Key: harden.format_missing_values

---

## [LRN-20260507-004] best_practice

**Logged**: 2026-05-07T10:00:00Z
**Priority**: low
**Status**: pending
**Area**: backend

### Summary
避免使用裸 except 子句，应捕获具体异常类型

### Details
ch03 和 ch05 中使用了 `except:` 而非 `except Exception:`，不符合 PEP 8 规范，且可能掩盖真实错误。

### Suggested Action
将裸 except 替换为 `except Exception as e:` 并记录日志

### Metadata
- Source: zoom-out 审查
- Related Files: src/ch03_hypothesis_testing/run.py, src/ch05_conclusion_recommendation/run.py
- Tags: pep8, error-handling
- Pattern-Key: harden.bare_except
