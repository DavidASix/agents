---
name: pr-time
description: Publish an already-committed local Git branch as a GitHub draft pull request. Use when the user wants to push the current branch and open a draft PR with a concise informal description based on branch-only changes and the current branch name used verbatim as the PR title, without creating commits, running checks, invoking code-review workflows, or adding AI-authorship disclosures.
---

# PR Time

Publish an already-committed branch as a draft pull request. Write the PR body in the user's concise, informal voice before opening the PR.

Keep this workflow self-contained. Never invoke, load, or follow `post-code-review`, and never run its scripts. Do not publish a GitHub review or inline review comments as part of this skill.

## Workflow

1. Read repository instructions. Require `gh` and an authenticated GitHub CLI session. Run `gh --version`, then run `gh auth status` with network access outside any network-restricted sandbox before changing GitHub state. If an initial sandboxed check reports an invalid token or cannot reach GitHub, retry it once with network access and treat the retry as authoritative; do not ask the user to re-authenticate based only on the sandboxed result.
2. Inspect `git status -sb` and the relevant diff. Assume the commits to publish already exist. Do not stage, commit, amend, or otherwise modify the worktree, and do not run linting, type checks, or tests.
3. Require a non-default current branch. Use its name verbatim as the PR title—for example, `davidasix/my-feature`.
4. Find the branch's parent from reflog evidence; do not use `git merge-base`. Inspect only commits and the diff in `<parent-branch>...HEAD` to write the PR description.
5. Write the PR description in an informal, human-sounding voice with no buzzwords or flowery language. It must begin with exactly two sentences that describe the change, then a concise bullet list of the important changes. Do not mention AI authorship, a model or model identifier.
6. Push with tracking: `git push -u origin $(git branch --show-current)`.
7. Open a draft PR using the description from step 5 as the body and the full current branch name as the title. Prefer the GitHub app's PR creation flow after deriving the repository from `origin`, the head from `git branch --show-current`, and the base from the user's request or the remote default branch. If needed, fall back to `gh pr create` with the same title and body.
8. Return the PR URL, branch name, commit, base branch, and description.

## Safety

- Default to a draft PR; do not mark it ready for review unless the user explicitly asks.
- Stop before pushing if the repository is not connected to an accessible GitHub remote.
- Never conclude that GitHub credentials are invalid from a network-restricted authentication check.
- Do not stage, commit, amend, or run checks as part of this skill.
- Never invoke `post-code-review`, its scripts, or any other code-review publishing workflow.
- If the current branch is `main` then the command has been called mistakenly, and you MUST refuse to continue.
- If pushing the branch to github would require a --force push then you MUST refuse to continue and wait for user resolution.
