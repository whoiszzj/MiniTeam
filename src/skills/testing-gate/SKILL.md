---
name: testing-gate
description: Verification and acceptance rules for the runner role in the small delivery team.
---

# Testing Gate

## Objective

Verify the implementation with executable evidence and determine whether it passes, fails, or requires replanning.

## Verification principles

1. Prefer deterministic checks.
2. Report commands exactly.
3. Separate observed facts from interpretation.
4. Do not modify product code to make tests pass.
5. If a check cannot run, explain why and what is missing.

## Verification order

Use the lightest valid sequence first, then go deeper only if needed:

1. syntax / static checks
2. targeted tests for touched scope
3. broader regression tests if risk is non-local
4. runtime smoke checks if the task changes behavior exposed to users or APIs

## Pass / fail policy

Return `success` only when:

- the relevant checks were actually executed, and
- the observed results satisfy the acceptance criteria

Return `failed` when:

- commands execute and demonstrate incorrect behavior
- tests fail
- outputs contradict the expected behavior

Return `blocked` when:

- the checks cannot be executed in the current environment

Return `needs-replan` when:

- evidence shows the approved design or scope is insufficient or wrong

## Required runner output

```md
## Status
- status: success | failed | blocked | needs-replan
- confidence: high | medium | low

## Commands Run
- exact commands

## Results
- concise result summary

## Evidence
- failing tests, stack traces, logs, or observed outputs

## Failure Analysis
- root cause hypothesis
- implementation bug vs plan issue vs environment issue

## Recommended Next Step
- next-agent: writer | coder | planner | leader
- rationale

## Handoff Payload
- minimal actionable payload for the selected next role
```
