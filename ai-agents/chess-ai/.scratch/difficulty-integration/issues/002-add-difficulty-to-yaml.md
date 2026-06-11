# Add game.difficulty to config.yaml

**Status**: ready-for-agent
**Priority**: P0
**Assigned**: agent

## Context
config/config.yaml is missing the "game.difficulty" field. While code has a fallback default, the YAML template should explicitly declare the field for discoverability and consistency.

## Scope
- Add `difficulty: "medium"` under the `game:` section in config.yaml

## Acceptance Criteria
- [ ] config.yaml contains `game.difficulty: medium`
- [ ] Loading config.yaml with existing field works correctly
- [ ] Changing difficulty via GUI persists and YAML saves correctly

## Dependencies
- Issue #001 (config defaults fix)

## Notes
Completed in commit _ (pending).
