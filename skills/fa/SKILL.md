---
name: fa
description: Analyze a supplied pull-request feedback snippet without changing code. Use to determine whether review feedback is valid and, when valid, outline a practical fix.
---

# Feedback Analysis Provided

Analyze the PR feedback supplied by the user against the relevant code and intended behavior.

1. Read repository instructions and inspect enough surrounding code and change context to understand intent.
2. Determine whether the feedback is valid, invalid, already resolved, or requires clarification.
3. Explain the conclusion with concrete evidence.
4. If valid, summarize the impact and a practical way to fix it.

This skill is analysis-only. Do not edit files or run tests unless the user separately authorizes those actions.
