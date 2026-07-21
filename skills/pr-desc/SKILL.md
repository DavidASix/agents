---
name: pr-desc
description: Write a concise, informal pull-request description for the current Git branch from its branch-only commits, then copy the result to the clipboard with xclip.
---

# Pull Request Description

1. Read the repository instructions.
2. Determine which branch the current branch was created from using Git reflog evidence. Do not use `git merge-base`.
3. Inspect only the commits and diff in `<parent-branch>...HEAD`.
4. Write an informal, human-sounding PR description without flowery language or buzzwords.
5. Start with exactly two sentences describing the PR, followed by a concise bullet list of the important changes.
6. Copy the final description to the clipboard using `xclip -selection clipboard -in -r`. Supply the description through standard input without a shell heredoc, and bound the command to approximately 400 ms because `xclip` remains active to serve clipboard data after receiving it.

Return the description in chat as well as copying it so the result remains available if clipboard access fails.
