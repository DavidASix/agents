---
name: fa-fetch
description: Fetch and analyze all feedback on the pull request for the current Git branch without changing code. Use to assess whether PR review comments are valid and summarize possible fixes.
---

# Feedback Analysis Fetched

1. Identify the current Git branch and its open GitHub pull request.
2. Fetch review comments, review summaries, and conversation comments for that pull request.
3. Read the relevant code, repository instructions, PR description, and surrounding changes to understand intent.
4. When subagents are available, delegate each independent feedback item for a focused validation pass. Give each subagent only the comment and the minimum code context needed; do not disclose a preferred conclusion.
5. Classify every feedback item as valid, invalid, already resolved, or requiring clarification, and explain the evidence.
6. For valid feedback, summarize the impact and a practical fix. For invalid feedback, explain why it does not apply.

This skill is analysis-only. Do not edit files, post GitHub comments, change PR state, or run tests unless the user separately authorizes those actions.
