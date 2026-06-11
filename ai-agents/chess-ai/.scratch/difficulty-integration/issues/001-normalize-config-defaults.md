# Normalize config defaults structure

**Status**: ready-for-agent
**Priority**: P0
**Assigned**: agent

## Context
ConfigManager._defaults uses flat dotted keys ("game.difficulty") but set_difficulty() and YAML config use nested dict structure ("game" → {"difficulty": ...}). This causes _compute_diff() to produce incorrect diffs for save().

## Scope
- Convert _defaults from flat keys to nested dict
- Use copy.deepcopy in _load_config to prevent _defaults pollution
- Update _compute_diff to work consistently with nested dicts

## Acceptance Criteria
- [ ] get("game.difficulty") returns correct value
- [ ] set_difficulty → save → reload preserves value
- [ ] All existing tests pass

## Dependencies
- None

## Notes
Completed in commit _ (pending). Core config infrastructure fix.
