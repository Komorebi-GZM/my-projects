# Issue Tracker

Local markdown-based issue tracker for chess_ai project.

## Structure

```
.scratch/
├── <feature>/
│   ├── issues/
│   │   ├── 001-issue-title.md
│   │   └── 002-another-issue.md
│   └── prd.md (optional)
└── README.md
```

## Issue Format

Each issue file follows this template:

```markdown
# Issue Title

**Status**: needs-triage | needs-info | ready-for-agent | ready-for-human | wontfix
**Priority**: P0 | P1 | P2
**Assigned**: agent | human

## Context
[Background and motivation]

## Scope
[What's in scope / out of scope]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Dependencies
- Issue #XXX

## Notes
[Additional context, decisions, blockers]
```

## Triage Labels

- `needs-triage`: New, unreviewed
- `needs-info`: Requires more context
- `ready-for-agent`: Ready for automated implementation
- `ready-for-human`: Requires human intervention
- `wontfix`: Rejected / not doing

## Workflow

1. Create issue file in appropriate feature directory
2. Set initial status to `needs-triage`
3. Triage → update status based on readiness
4. Work → update status to `ready-for-agent` or `ready-for-human`
5. Complete → close issue (move to `closed/` subdirectory or update status to `done`)
