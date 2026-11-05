---
name: branch-walkthrough
description: Create a concise Markdown walkthrough of the currently checked-out Git branch, illustrated with real screenshots of its relevant UI. Use when the user wants a visual PR tour, branch demo, or screenshot walkthrough saved locally.
---

# Branch Walkthrough

Produce a short, practical guide that walks the user through what changed on the current branch, with screenshots from the running application. Explain the workflow from the user's perspective, grounded in both the branch diff and observed behavior.

## Establish the scope

- Read the repository instructions and inspect the current branch, working-tree status, and package scripts. Preserve existing edits and artifacts; do not switch branches, change application code, stage, commit, push, or publish anything as part of this workflow.
- Determine the comparison base from the user's request or existing PR metadata, then local branch/reflog evidence or the repository's default branch. Use the branch-only diff and commits to identify the final changes, excluding unrelated changes brought in by merges. State a material base assumption rather than silently choosing an ambiguous base.
- Trace changed components and their entry points far enough to identify the actual navigation, labels, relevant states, and boundaries. Separate newly added behavior from existing controls that happen to appear in the screenshots. Include backend changes only where they explain user-visible behavior or a practical limitation.
- Choose a small set of screens that tells the story: where the feature lives, how to use it, the saved result, and meaningful history, filters, or alternate states. Scale the coverage to the branch; do not require a fixed screenshot count.

## Capture the running UI

- Use the available `agent-browser` skill and load its installed CLI workflow before driving the browser. For rigc-base, also use the repository's `agent-browser-login` skill for local seed identities, session reuse/reset, and bounded waits. In other repositories, follow their actual startup and authentication instructions; do not reuse rigc-base credentials or assume its port.
- Prefer the running local app. Check reachability first. If a sandbox blocks localhost or browser startup, use the permitted escalation mechanism before concluding the app is unavailable. If the server needs starting, follow repository instructions without restarting or reseeding an already-running app unnecessarily.
- Use an isolated browser session and a desktop viewport large enough to show the relevant UI clearly. Snapshot after page changes, interact through observed controls, and wait for specific content or state rather than fixed delays. Keep authentication state in ignored local storage, outside screenshot artifacts.
- Prefer seeded examples. In a confirmed local/test environment, create the minimum clearly labeled demo records needed to show the workflow and persisted results. Do not send real messages, trigger external deliveries, delete data, or use production records just to populate screenshots. Report demo data added. Do not bypass permissions or mock successful behavior.
- Capture real screenshots of the relevant states, with short sequential kebab-case filenames. Save them in a feature-specific folder such as `documentation/screenshots/<topic>/`, adapting to repository conventions. Keep screenshot files alongside the walkthrough as durable local deliverables; do not stage them.
- View every captured image. Recapture loading states, obstructed controls, unreadable text, or the wrong screen. Never present mockups, edited DOM text, or fabricated data as observed application behavior.
- If the branch has no relevant UI, explain that and write a concise behavior walkthrough without filler screenshots. If browser access remains blocked after a bounded diagnosis, save the useful walkthrough with the exact capture limitation and report that screenshots are incomplete.

## Write the walkthrough

Unless the user specifies a destination, create `<topic>-walkthrough.md` at the repository root with relative image links. Choose a short topic from the branch's actual purpose. Do not overwrite an existing unrelated walkthrough.

Aim for a few hundred words; expand only when the workflow needs it. Use this shape flexibly:

1. One short paragraph explaining what the PR adds and any distinction essential to understanding it.
2. A brief note identifying the local example and demo records added, if applicable.
3. Numbered steps with action-oriented headings, exact UI labels, one or two sentences explaining what to do and what changes, and the corresponding screenshot inline.

Include a local entry URL when useful. Describe observable results, not implementation chronology. Call out manual versus automated behavior, permissions, or limits only when they materially affect how the feature is used. Do not imply a date field schedules an action, a status changes another workflow, or an existing control is new unless the code and UI support it. Keep technical file tours and exhaustive checklists out of this user walkthrough.

## Finish

- Verify every relative image link resolves to a nonempty image file and that the guide matches the screenshots and branch changes. Verify meaningful saved behavior by reopening or inspecting the resulting UI when appropriate.
- Clear temporary view filters and close the isolated browser session when done. Keep saved demo records needed to reproduce the screenshots and disclose them.
- Check the final working-tree status so the deliverables are distinguishable from pre-existing changes. No application tests, lint, or type checks are needed for a walkthrough-only task.
- Return a clickable link to the Markdown file, the screenshot count, and a brief note about demo data or any incomplete capture. Keep the final response concise.
