# Issue Tracker

Local markdown-based issue tracking system for the chess_ai project.

## Overview

Issues are stored as markdown files in the `.scratch/` directory, organized by feature. This approach:

- Requires no external services
- Works offline
- Keeps issues versioned with the codebase
- Integrates with git workflow

## Directory Structure

```
.scratch/
├── README.md                    # This file
├── <feature>/
│   ├── issues/                  # Individual issue files
│   │   ├── 001-issue-title.md
│   │   └── 002-another-issue.md
│   └── prd.md                   # Optional PRD for feature
```

## Issue File Format

Each issue follows this structure:

```markdown
# Issue Title

**Status**: needs-triage | needs-info | ready-for-agent | ready-for-human | wontfix
**Priority**: P0 | P1 | P2
**Assigned**: agent | human

## Context
Background and motivation

## Scope
What's in scope / out of scope

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Dependencies
- Issue #XXX (or N/A)

## Notes
Additional context, decisions, blockers
```

## Workflow

1. **Create**: Write new issue file in appropriate `issues/` directory
2. **Triage**: Review and update status
3. **Work**: Implement when status is `ready-for-agent`
4. **Complete**: Close by moving to `closed/` or updating status

## Naming Convention

Issue files use zero-padded numbers:
- `001-feature-name.md`
- `002-bug-description.md`

Numbers auto-increment within each feature directory.