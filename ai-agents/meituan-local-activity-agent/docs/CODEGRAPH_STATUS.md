# Codegraph Status

As of 2026-05-27, `.codegraph/codegraph.db` exists but contains zero indexed nodes:

```sql
select count(*) from nodes;
-- 0
```

Do not rely on this database for caller/callee analysis until it is regenerated.

When the local codegraph generator is available, regenerate the index from the repository root and re-check:

```bash
sqlite3 .codegraph/codegraph.db "select count(*) from nodes;"
```

Expected after regeneration: count is greater than 0, and `nodes.file_path` contains backend and frontend source files.
