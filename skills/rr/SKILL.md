---
name: rr
description: Request automated reviews on a GitHub pull request by adding GitHub Copilot as a reviewer and posting an authenticated user comment that says "@codex review this". Use when invoked alongside pr-time after it creates a pull request, after another pull-request creation workflow, or by itself to request reviews on the open pull request for the current Git branch.
---

# Request Review

Request GitHub Copilot and Codex reviews on a newly created or existing open pull request.

## Workflow

1. Require `gh` and an authenticated GitHub CLI session. Reuse a successful authentication check from `$pr-time`; otherwise run `gh auth status` with network access outside a network-restricted sandbox. Retry a sandboxed network or token failure once with network access before treating it as authoritative.
2. Select the pull request:
   - When invoked with `$pr-time` or another creation workflow, let that workflow finish before changing review state. If creation fails, stop and do not post anything. Take the pull-request URL or number from its result.
   - When invoked by itself, get the current branch with `git branch --show-current`, then resolve its pull request with `gh pr view --json number,url,state`. Require a nonempty branch and an `OPEN` pull request. If none exists or the resolved pull request is not open, stop without changing GitHub state.
3. Request GitHub Copilot review with `gh pr edit <pull-request> --add-reviewer @copilot`.
4. Post exactly `@codex review this` from the authenticated user with `gh pr comment <pull-request> --body '@codex review this'`.
5. Return the pull-request URL and the outcome of both actions. If Copilot review is unavailable or disabled, still attempt the Codex comment and report the partial failure clearly.

## Safety

- Do not create, edit, ready, merge, or close the pull request.
- Do not push, commit, amend, stage files, or run checks.
- Target only the pull request created by the accompanying workflow or, in standalone mode, the open pull request for the current branch unless the user explicitly identifies another one.
- Preserve the exact comment text and casing.
- Before retrying after a partial failure, inspect existing comments and do not post a duplicate exact comment from the authenticated user.
