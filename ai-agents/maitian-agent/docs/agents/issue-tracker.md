# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues on [Komorebi-GZM/wheatfield_braintrust](https://github.com/Komorebi-GZM/wheatfield_braintrust). Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..." --label "..."`
- **Read an issue**: `gh issue view <number> --comments`
- **List issues**: `gh issue list --state open --json number,title,body,labels`
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v` — `gh` does this automatically when run inside a clone.

## Label system

This repo uses a structured label system defined in `docs/label-design.md`:

- **Priority**: `priority:critical`, `priority:high`, `priority:normal`, `priority:low`
- **Module**: `module:agent`, `module:rag`, `module:memory`, `module:tools`, `module:api`, `module:frontend`, `module:config`, `module:docker`, `module:docs`, `module:demo`
- **Type**: `type:feat`, `type:fix`, `type:refactor`, `type:test`, `type:docs`, `type:chore`, `type:perf`, `type:security`
- **Status**: `status:available`, `status:in-progress`, `status:blocked`, `status:review`, `status:done`
- **Phase**: `phase:1-demo`, `phase:2-core`, `phase:3-optimize`

## Existing issues

22 issues have been defined in `docs/issues.md`, covering 3 phases:

- **Phase 1 (Demo)**: Issue-001 to Issue-006
- **Phase 2 (Core Integration)**: Issue-007 to Issue-015
- **Phase 3 (Optimization)**: Issue-016 to Issue-022

See `docs/triage-report.md` for triage results and recommended execution order.

## When a skill says "publish to the issue tracker"

Create a GitHub issue using the label conventions above.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.
