# Triage Labels

Five canonical triage labels for issue status management.

## Label Definitions

### `needs-triage`
**When to use**: New issues that haven't been reviewed yet.

**Transitions to**:
- `needs-info` if more context required
- `ready-for-agent` if implementation-ready
- `ready-for-human` if requires human intervention
- `wontfix` if rejected

### `needs-info`
**When to use**: Issue blocked by missing context, unclear requirements, or pending decisions.

**Transitions to**:
- `needs-triage` when info received
- `wontfix` if info cannot be provided

### `ready-for-agent`
**When to use**: Issue ready for automated/agent implementation. Clear scope, no blockers.

**Transitions to**:
- `ready-for-human` if agent encounters blockers
- Closed when complete

### `ready-for-human`
**When to use**: Issue requires human intervention, review, or decision-making.

**Transitions to**:
- `ready-for-agent` when human provides input
- Closed when complete

### `wontfix`
**When to use**: Issue rejected, out of scope, or deferred indefinitely.

**Transitions to**: None (terminal state)

## Priority Levels

| Level | Description |
|-------|-------------|
| P0 | Critical - blocks release |
| P1 | High - important but not blocking |
| P2 | Medium - nice to have |

## Assignment

| Value | Meaning |
|-------|---------|
| `agent` | Will be handled by AI agent |
| `human` | Requires human action |

## Workflow Diagram

```
needs-triage
    │
    ├─→ needs-info ──→ needs-triage
    │
    ├─→ ready-for-agent
    │       │
    │       └─→ (complete) ──→ closed
    │           │
    │           └─→ ready-for-human
    │
    ├─→ ready-for-human ──→ ready-for-agent ──→ closed
    │
    └─→ wontfix ──→ (terminal)
```