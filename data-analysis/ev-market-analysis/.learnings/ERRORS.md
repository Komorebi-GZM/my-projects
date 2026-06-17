# Errors

Command failures and integration errors.

---

## [ERR-20260505-001] column_count_mismatch

**Logged**: 2026-05-05T12:00:00Z
**Priority**: low
**Status**: resolved
**Area**: config

### Summary
CSV header appeared to have 25 columns but pandas loaded 24 columns.

### Error
No runtime error, but documentation inconsistency: README and skill templates referenced 25 columns while actual data had 24.

### Context
- File: ev_market_2026.csv
- Diagnosis script reported 24 columns via df.shape
- All downstream code adapted to 24-column schema

### Suggested Fix
Always use `df.shape[1]` for column count verification. Updated all references to 24 columns.

### Resolution
- **Resolved**: 2026-05-05T12:00:00Z
- **Notes**: Confirmed 24 columns via pandas. All code and documentation updated accordingly.

### Metadata
- Reproducible: no
- Related Files: data/ev_market_2026.csv, src/utils/config.py
