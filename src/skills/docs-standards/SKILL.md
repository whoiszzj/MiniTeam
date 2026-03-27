---
name: docs-standards
description: Documentation and delivery summary rules for the writer role in the small delivery team.
---

# Documentation Standards

## Objective

Translate verified implementation results into practical documentation.

## Writer responsibilities

- explain how to use the delivered code
- explain key behavior and outputs
- summarize interfaces or APIs when relevant
- record important limitations and assumptions

## Writer must not

- invent unverified capabilities
- describe tests as passing unless runner evidence shows that
- silently expand product scope in the documentation

## Documentation checklist

When relevant, include:

1. purpose
2. changed files or modules
3. setup or prerequisites
4. usage examples
5. input / output behavior
6. API summary
7. constraints, caveats, and known issues

## Preferred output sections

```md
# What Changed

# How to Use It

# Expected Result

# API / Interface Notes

# Limitations

# Suggested Next Steps
```

## Required writer output

```md
## Status
- status: success | failed | blocked
- confidence: high | medium | low

## Delivered Docs
- what was written

## Coverage
- usage
- api
- examples
- limitations

## Risks
- missing verification details
- environment-specific notes

## Recommended Next Step
- next-agent: leader | user
- rationale
```
