# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

## Additional status labels used in this repo

This repo also uses a richer status label vocabulary defined in `docs/label-design.md`:

- `status:available` — maps to `ready-for-agent` (can be claimed)
- `status:in-progress` — currently being worked on
- `status:blocked` — blocked by another issue
- `status:review` — pending review
- `status:done` — completed

Edit the right-hand column to match whatever vocabulary you actually use.
