---
name: prototype
description: Implement narrowly scoped proof-of-concept code with the fewest practical line changes, explanatory inline comments, and no tests. Use when the user invokes $prototype or says they are experimenting, validating an idea, trying a direction, or building disposable prototype code rather than production-ready functionality.
---

# Prototype

Treat the requested change as a disposable proof of concept intended to validate a direction, not as production-ready code.

## Implement the prototype

1. Implement only the behavior the user explicitly requests.
2. Change the fewest files and lines that can demonstrate the concept while preserving existing project requirements, safety constraints, and security boundaries.
3. Reuse existing code and primitives. Avoid speculative features, abstractions, refactors, cleanup, documentation, and production hardening outside the requested behavior.
4. Add concise inline comments beside the changed prototype logic to explain what those lines or blocks do. Keep comments useful and avoid lengthy commentary or restating obvious syntax.
5. Do not add, update, or delete tests.
6. Do not run tests. Avoid aggregate validation commands that include tests. Run targeted type checks and lint checks only when useful and permitted by the project.
7. Report that the result is a prototype, summarize the narrow change, and state that tests were intentionally not run.
