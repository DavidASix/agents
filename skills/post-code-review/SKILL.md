---
name: post-code-review
description: Convert actionable findings from a code-review output into separate, code-anchored comments and publish them together as one GitHub pull-request review. Use when Codex has review findings from code-reviewer or another review artifact and the user wants those findings posted as inline PR review comments, submitted as a GitHub code review, or attached to the relevant changed lines.
---

# Post Code Review

Publish an existing review artifact as one GitHub pull-request review containing a separate inline comment for every finding. Preserve the review's substance; do not perform a new code review or modify code.

## Inputs

Require:

- The complete code-review output, available in the conversation or a user-supplied file.
- The exact, fully qualified model identifier that generated the review findings, such as `gpt-5.6-sol`; never use a model family or generic label.
- The Codex or Claude session ID in which the review findings were generated.
- An unambiguous GitHub pull request.

Accept a PR URL, `owner/repository#number`, or PR number when the repository is known. If no selector is supplied, use the PR associated with the current branch only when `gh pr view` resolves it unambiguously. If the PR still is not known, ask the user which PR to use before making any GitHub write.

## Workflow

1. Read repository instructions and the complete review artifact.
2. Determine the exact, fully qualified model identifier that generated the findings, such as `gpt-5.6-sol`. Prefer model metadata attached to the review artifact; otherwise use the current runtime's model identity only when the same model produced the review. Attribute the reviewing model, not merely the model publishing the comments. Never shorten it to a family such as `gpt-5`, and never guess or infer a model from writing style. If the reviewing model cannot be determined, ask the user before making any GitHub write.
3. Determine whether the findings came from a Codex or Claude session and obtain that session's ID. In Codex, use `CODEX_THREAD_ID`; in Claude, use the session ID from Claude's runtime metadata. Prefer metadata attached to the review artifact when a different session generated it. Never invent an ID. If the provider or session ID cannot be determined, ask the user before making any GitHub write.
4. Require `gh` and an authenticated GitHub CLI session. Run `gh --version`, then run `gh auth status` with network access outside a network-restricted sandbox. If a sandboxed authentication check fails or reports an invalid token, retry once with network access and treat that result as authoritative.
5. Resolve the repository and PR. Confirm the PR URL, number, head SHA, head branch, and base branch with `gh pr view`.
6. Fetch the complete PR diff and file list. Use the PR diff—not an uncommitted local diff—as the source of truth for comment anchors. Account for renamed files by using the path shown in the PR.
7. Break the review artifact into discrete findings. Exclude headings, summaries, praise, and a "no findings" result. Keep questions and optional improvements only when the source review presents them as review feedback.
8. Turn each finding into one self-contained inline comment:
   - Preserve its severity and confidence.
   - State the concrete issue and impact.
   - Include the actionable remediation from the source.
   - Keep a compact code example only when it materially clarifies the fix.
   - Do not combine distinct findings merely because they share a file or line.
   - Do not invent new findings.
9. Map every comment to the smallest relevant changed section:
   - Use `RIGHT` for a line in the PR's new file and `LEFT` for a removed line in the old file.
   - Use a multi-line range only when the entire range is necessary to understand the finding.
   - Verify that every chosen line is commentable in the PR diff.
   - Never replace an inline anchor with a file-level or top-level comment. If any finding cannot be anchored unambiguously, stop before submission, identify it, and ask the user how to proceed.
10. Check existing inline comments for exact duplicates by path, side, line, and materially identical body. Ignore the script-added `Authored by AI:` prefix when comparing bodies. If publishing would duplicate all findings, report that the review is already present. If only some are duplicates, stop and ask whether to omit or repost them.
11. Write a temporary JSON manifest:

```json
{
  "model": "gpt-5.6-sol",
  "session_provider": "codex",
  "session_id": "019c1234-example-session-id",
  "body": "Inline findings from the requested code review.",
  "comments": [
    {
      "path": "src/example.ts",
      "line": 42,
      "side": "RIGHT",
      "body": "**P1 — Enforce the organization boundary**\n\nThis query can return another tenant's records because it does not constrain `organization_id`. Add the permission-scoped predicate before returning rows."
    },
    {
      "path": "src/example.ts",
      "start_line": 58,
      "start_side": "RIGHT",
      "line": 62,
      "side": "RIGHT",
      "body": "**P2 — Preserve the failed state**\n\nThis branch overwrites the error before callers can inspect it. Return the failure unchanged or wrap it with its original cause."
    }
  ]
}
```

The script prefixes every inline comment with `Authored by AI:`. It constructs the main review body so that it begins with `Review authored by AI.`, includes `Model used: <exact-model>`, and ends with `Codex session ID: <id>` or `Claude session ID: <id>`. Do not include those wrappers in the manifest bodies.

12. Dry-run `scripts/post_review.py` using the verified repository, PR number, and head SHA. Confirm every inline comment begins with the AI attribution, the main review body has the required opening, exact model, and session-ID footer, then summarize the number and locations of comments before publishing.
13. Submit one review with `scripts/post_review.py`. Default to `COMMENT`. Use `APPROVE` or `REQUEST_CHANGES` only when the user explicitly asks for that review decision. The script aborts if the PR head has changed since the comments were mapped.
14. Verify the returned review and its inline comments through GitHub. Confirm all AI/model/session disclosures, then report the PR URL, review URL or ID, review event, model, session ID, and posted comment count.

## Script

Resolve `scripts/post_review.py` relative to this `SKILL.md`.

```bash
python3 scripts/post_review.py \
  --repo OWNER/REPOSITORY \
  --pr NUMBER \
  --head-sha VERIFIED_HEAD_SHA \
  --input /tmp/review-comments.json \
  --event COMMENT \
  --dry-run

python3 scripts/post_review.py \
  --repo OWNER/REPOSITORY \
  --pr NUMBER \
  --head-sha VERIFIED_HEAD_SHA \
  --input /tmp/review-comments.json \
  --event COMMENT
```

Run the non-dry-run command with network access outside any network-restricted sandbox.

## Safety

- Treat a request to post or publish the review as authorization for the GitHub review write. Do not publish when the user asks only to prepare, preview, or format comments.
- Never guess the PR.
- Never publish without the exact model that generated the review findings.
- Never publish without the Codex or Claude session ID that generated the review findings.
- Never partially publish a review when one or more findings lack valid anchors.
- Never submit one API request per comment; submit all comments together as one review.
- Never infer invalid GitHub credentials from a network-restricted check.
- Do not alter branches, commits, files, labels, reviewers, or PR state.
