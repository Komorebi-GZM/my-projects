# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## [LRN-20260504-001] insight

**Logged**: 2026-05-04T13:30:00Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
config.py 中的列名可能与实际数据列名不一致

### Details
config.py 中 categorical_cols 列出了 "Sex" 但实际数据列名为 "Gender"。这是 ch01 清洗时列名标准化导致的差异。在编写脚本时不能完全依赖 config.py 的列名，需要对照实际数据验证。

### Suggested Action
在 ch01 完成后同步更新 config.py 中的列名，或在各章节脚本中显式定义与数据一致的列名。

### Metadata
- Source: conversation
- Related Files: src/utils/config.py, src/ch03_statistical_test/stat_test.py
- Tags: config, column_names, data_consistency

---

## [LRN-20260504-002] best_practice

**Logged**: 2026-05-04T13:30:00Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
Python 脚本中 sys.path 设置需要同时包含 PROJECT_ROOT 和 SRC_DIR

### Details
项目 utils 模块的 __init__.py 使用 `from src.utils.config import ...` 绝对导入，因此需要将 PROJECT_ROOT 加入 sys.path。同时 SRC_DIR 也需要加入以支持 `from utils.config import ...` 相对导入。

### Suggested Action
在所有章节脚本中统一使用双路径设置模式。

### Metadata
- Source: conversation
- Related Files: src/ch03_statistical_test/stat_test.py
- Tags: sys.path, imports, project_structure
