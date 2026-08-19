---
name: test-it
description: Turn behavior described in the current conversation into a focused executable test. Use when the user asks to capture, prove, reproduce, characterize, or test the behavior being discussed before implementation. For planned or missing behavior, write and verify a test that currently fails for the intended reason so CI stays red until implementation; for behavior that already exists, write and verify a passing regression or characterization test.
---

# Test It

Convert the behavior established in the conversation into the smallest meaningful test. Change test code only; do not implement the behavior.

## Establish the contract

1. Read the current conversation and treat the user's latest statements as authoritative.
2. State the observable contract in one sentence: given a condition or action, identify the result visible at a public boundary.
3. Resolve minor gaps from repository conventions and surrounding code. Ask the user only when different interpretations would produce materially different contracts.
4. Classify the contract:
   - **Planned, missing, or buggy behavior:** create a red test that fails against the current implementation.
   - **Existing behavior:** create a passing characterization or regression test.

Do not invent adjacent requirements. Prefer one representative example; add cases only when each proves a distinct part of the discussed contract.

## Find the right test boundary

1. Read applicable repository instructions and inspect nearby production code, tests, test scripts, and CI configuration.
2. Follow the project's existing framework, naming, fixtures, helpers, and file placement.
3. Test the public behavior closest to what the user described. Avoid assertions on private implementation details, snapshots with unrelated output, and mocks that merely restate the expected algorithm.
4. Reuse existing test infrastructure. Do not add a dependency, test framework, or CI job unless the user explicitly requests it or the repository has no viable test path and the user approves the expansion.
5. Preserve unrelated work in a dirty tree and keep edits limited to the test files necessary for the contract.

## Build the test

Name the test after the behavior it proves. Arrange only the state needed to exercise the contract, perform the action through the intended public boundary, and assert the user-visible outcome.

For planned, missing, or buggy behavior:

- Encode the desired outcome, not the current incorrect output.
- Do not weaken, skip, quarantine, invert, mark pending, or label the test as an expected failure.
- Do not change production code, generated artifacts, or unrelated tests to manufacture the failure.
- Ensure the repository's normal CI test discovery will include the test.

For existing behavior:

- Assert the observed contract directly.
- Avoid freezing incidental details that are not part of the discussion.

## Verify the evidence

Run the narrowest repository-native command that executes the new test.

For a red test, confirm all of the following:

- the new test is discovered and executed;
- it fails because the discussed behavior is absent or wrong;
- the failure points to the intended assertion or missing public capability, not a syntax error, malformed fixture, invalid import, environment problem, or unrelated failure;
- no production-code change was made.

Treat the expected red exit status as evidence, not as a reason to repair the implementation. If the failure is accidental, fix the test and rerun it. If the current implementation unexpectedly passes, report that the behavior already exists and verify it as a passing regression test; never force a failure.

For an existing-behavior test, require the focused command to pass. Do not deliberately break production code merely to validate test sensitivity unless the user asks for mutation testing.

## Report

Return:

- the contract the test captures;
- the test file changed;
- the exact verification command and whether it passed or failed;
- for a red test, the concise expected failure proving what remains to implement;
- any assumption that materially shaped the test.

Call out explicitly that a verified red test is intentionally left failing and will keep CI red until the implementation satisfies it.
