---
name: narrow
description: Keep implementation work strictly limited to the change explicitly requested. Use when the user invokes $narrow or asks for an exact, minimal, narrowly scoped change without tests, documentation, validation commands, screenshots, refactors, cleanup, or adjacent improvements.
---

# Narrow Changes

Make the smallest change that directly satisfies the request.

## Scope

- Interpret the request narrowly and modify only the files directly required.
- Do not add or update tests, documentation, snapshots, screenshots, examples, dependencies, or generated files unless
  the user explicitly requests them.
- Do not run tests, linters, type checks, formatters, coverage, mutation testing, builds, or other validation commands
  unless the user explicitly requests them.
- Do not perform adjacent cleanup, refactoring, formatting, hardening, or speculative improvements.
- Do not invoke ancillary workflows or delegate work unless the user explicitly requests them or a higher-priority
  instruction requires them.
- Preserve all unrelated existing changes.

If the requested edit cannot be completed safely without broader work, or if a higher-priority instruction requires
additional actions, explain the conflict and ask before expanding the scope.

After making the requested change, report only what changed and note that checks were not run.
