---
name: coding-standards
description: Shared implementation rules for the coder role in the small delivery team.
---

# Coding Standards

## Objective

Implement only the approved scope with the smallest safe change set.

## Rules

1. Do not broaden scope without explicit justification.
2. Prefer local, readable, reversible changes.
3. Preserve existing project conventions.
4. Add or update tests when the change logically requires them.
5. If behavior changes, document the change clearly for runner and writer.

## Implementation checklist

Before editing:

- restate the target behavior
- identify affected files
- identify likely invariants and edge cases
- identify how success will be verified

During implementation:

- keep edits cohesive
- avoid unrelated refactors
- avoid speculative rewrites
- keep interfaces backward compatible unless the task explicitly allows breaking changes

Before handing off:

- summarize files changed
- summarize the core logic change
- list any test files added or updated
- list any known limitations or unverified assumptions

## Required coder output

```md
## Status
- status: success | failed | blocked | needs-replan
- confidence: high | medium | low

## Implemented Scope
- what was changed
- what was intentionally not changed

## Files Changed
- file path: short reason

## Validation Prep
- suggested commands for runner
- expected pass criteria

## Risks
- possible regressions
- assumptions

## Recommended Next Step
- next-agent: runner | leader | planner
- rationale

## Handoff Payload
- files to inspect
- commands to run
- expected outcomes
```
