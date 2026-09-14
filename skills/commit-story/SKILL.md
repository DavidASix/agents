---
name: commit-story
description: Analyze uncommitted Git changes, explain the changeset's narrative, and design a coherent series of atomic commits. Use when a user wants to understand a dirty working tree or plan how its changes should be committed; do not use it to create commits unless the user separately asks.
---

# Commit Story

Inspect the repository's instructions and the complete working-tree state, including staged, unstaged, deleted, renamed, and untracked files. Read enough surrounding code, tests, documentation, and recent commit history to understand intent and local commit-message conventions. Treat all existing changes as user-owned and keep the analysis read-only.

Summarize the changeset in a few sentences: the problem or goal, the approach taken, and the resulting behavior. Call out unrelated work, generated files, secrets, accidental artifacts, or changes whose purpose cannot be established rather than forcing them into the story.

Then propose a commit stack that tells that story clearly. Do not optimize for fewer commits or easier staging; use as many commits as the changes require. Split a file across commits when its hunks belong to different concerns.

Before choosing commits, classify every hunk by both its narrow concern and its abstraction layer. Useful layers include reusable UI primitives, domain or data helpers, reusable feature components, screens or routes, integration and navigation, tests, documentation, and incidental polish. This classification is for analysis only; do not print it separately.

Combine hunks only when they form one cohesive code or content concern at the same abstraction layer and would normally be reviewed and reverted together. Do not split coordinated changes to one reusable component family merely because they touch several files. A shared feature motivation, dependency chain, or broad label such as "foundations" is not enough to pull other layers into that commit. For example:

- Related changes across reusable `components/ui/*` primitives form one UI-primitives commit; do not split them per component or mix in domain helpers and documentation.
- Client conversion helpers are a separate domain-helper commit, even when the same form needs both changes.
- Evolution of a reusable form component is separate from the screen or route that consumes it.
- Navigation, success feedback, care-status controls, and documentation are separate concerns when their hunks can stand alone.

Order these narrow commits by dependency, placing reusable enablers before their consumers. If a proposed commit message needs "and" to join independent behaviors, covers more than one abstraction layer, or uses an umbrella noun to hide several concerns, split it again.

Put substantial new test suites or broad behavioral test changes in their own commit immediately after the production commit they verify. Keep only small, inseparable test adjustments with implementation. Do not put all tests for a multi-commit feature into one catch-all test commit; align each test commit with the narrow production concern it verifies.

For each proposed commit:

- Give a one-sentence, imperative commit message consistent with repository conventions.
- Give at most a brief sentence of purpose when the commit message does not make it clear.
- List every included file by its exact repository-relative path, with exactly one line per file. Never replace paths with directory summaries, globs, file counts, or phrases such as "related files."
- Put that file's included hunk ranges on the same line as its path, such as `path/to/file: lines 12-18, 41-46`. Report staging-sized ranges, not every individual changed line within a hunk. Use only line numbers, without symbols, code snippets, or descriptions of the edits. Use working-tree line numbers; for deleted files or deletion-only hunks, label ranges as `old lines`. When a file spans commits, make its ranges precise enough to stage interactively and repeat the path under every commit that uses it.
- Briefly name checks that are specific to that commit. Put checks that apply to the entire stack once after the stack instead of repeating them for every commit. Distinguish checks actually run from checks merely recommended and omit generic reasoning about them.

Prefer commits that are independently understandable and usually pass lint and type checks. The final commit in the proposed stack must leave the full changeset in a state expected to pass applicable lint, type, and test suites. If a known defect remains in the inspected changes, identify it as a blocker and do not describe the final state as ready or passing.

After drafting the stack, audit every proposed commit before responding:

- Do its hunks share one narrow concern and abstraction layer, rather than merely one feature?
- Could a prerequisite, reusable component, integration change, test suite, documentation change, or incidental polish be reviewed and reverted independently?
- Does every mixed-purpose file have its hunks assigned to the appropriate separate commits?
- Is every substantial test change immediately after the implementation it verifies?

If any answer exposes another clean boundary, revise the stack. Do not state a target commit count; let the number of independently understandable concerns determine it.

Present the commit stack directly in order; do not repeat it in a second summary. Keep each entry compact and put staging cautions next to the affected path or hunk. If one commit is the clearest story, recommend one. Do not modify files, stage changes, create commits, or rewrite history unless the user explicitly extends the request.

Use this output shape:

```markdown
Changeset: <brief narrative>

1. <imperative commit message>
   <optional one-sentence purpose>
   - path/to/file: lines 12-18, 41-46
   - path/to/other-file: lines 7-20
   Checks: <only when specific to this commit>

Checks: <stack-wide checks, run versus recommended>
```
