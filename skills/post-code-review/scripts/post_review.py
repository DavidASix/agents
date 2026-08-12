#!/usr/bin/env python3
"""Validate and submit one GitHub pull-request review with inline comments."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import NoReturn


REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA_PATTERN = re.compile(r"^[0-9a-fA-F]{40}$")
ALLOWED_EVENTS = ("COMMENT", "APPROVE", "REQUEST_CHANGES")
ALLOWED_SESSION_PROVIDERS = ("codex", "claude")
ALLOWED_COMMENT_KEYS = {
    "body",
    "line",
    "path",
    "side",
    "start_line",
    "start_side",
}


def fail(message: str) -> NoReturn:
    raise SystemExit(f"error: {message}")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Submit one GitHub PR review containing inline comments."
    )
    parser.add_argument("--repo", required=True, help="GitHub repository as OWNER/REPOSITORY")
    parser.add_argument("--pr", required=True, type=int, help="Pull-request number")
    parser.add_argument(
        "--head-sha",
        required=True,
        help="Expected 40-character PR head SHA used to map comment anchors",
    )
    parser.add_argument("--input", required=True, type=Path, help="Review manifest JSON")
    parser.add_argument(
        "--event",
        choices=ALLOWED_EVENTS,
        default="COMMENT",
        help="GitHub review event (default: COMMENT)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print the API payload without contacting GitHub",
    )
    return parser.parse_args()


def require_object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        fail(f"{label} must be a JSON object")
    if not all(isinstance(key, str) for key in value):
        fail(f"{label} contains a non-string key")
    return value


def require_nonempty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")
    return value


def require_positive_integer(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        fail(f"{label} must be a positive integer")
    return value


def validate_path(value: object, label: str) -> str:
    path = require_nonempty_string(value, label)
    parsed_path = PurePosixPath(path)
    if parsed_path.is_absolute() or ".." in parsed_path.parts:
        fail(f"{label} must be a repository-relative path")
    return path


def validate_comment(value: object, index: int) -> dict[str, object]:
    label = f"comments[{index}]"
    comment = require_object(value, label)
    unknown_keys = sorted(set(comment) - ALLOWED_COMMENT_KEYS)
    if unknown_keys:
        fail(f"{label} contains unsupported keys: {', '.join(unknown_keys)}")

    normalized: dict[str, object] = {
        "path": validate_path(comment.get("path"), f"{label}.path"),
        "line": require_positive_integer(comment.get("line"), f"{label}.line"),
        "side": require_nonempty_string(comment.get("side"), f"{label}.side").upper(),
        "body": require_nonempty_string(comment.get("body"), f"{label}.body"),
    }

    if normalized["side"] not in ("LEFT", "RIGHT"):
        fail(f"{label}.side must be LEFT or RIGHT")

    has_start_line = "start_line" in comment
    has_start_side = "start_side" in comment
    if has_start_line != has_start_side:
        fail(f"{label} must provide start_line and start_side together")

    if has_start_line:
        start_line = require_positive_integer(
            comment.get("start_line"), f"{label}.start_line"
        )
        start_side = require_nonempty_string(
            comment.get("start_side"), f"{label}.start_side"
        ).upper()
        if start_side not in ("LEFT", "RIGHT"):
            fail(f"{label}.start_side must be LEFT or RIGHT")
        if start_side != normalized["side"]:
            fail(f"{label} ranges must remain on one side of the diff")
        end_line = normalized["line"]
        if not isinstance(end_line, int) or start_line >= end_line:
            fail(f"{label}.start_line must be less than line")
        normalized["start_line"] = start_line
        normalized["start_side"] = start_side

    return normalized


def validate_model(value: object) -> str:
    model = require_nonempty_string(value, "manifest.model").strip()
    if len(model) > 200 or not model.isprintable():
        fail("manifest.model must be a single printable line of at most 200 characters")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", model):
        fail("manifest.model must be a specific model identifier, such as gpt-5.6-sol")
    return model


def validate_session_provider(value: object) -> str:
    provider = require_nonempty_string(
        value, "manifest.session_provider"
    ).strip().lower()
    if provider not in ALLOWED_SESSION_PROVIDERS:
        fail("manifest.session_provider must be codex or claude")
    return provider


def validate_session_id(value: object) -> str:
    session_id = require_nonempty_string(value, "manifest.session_id").strip()
    if len(session_id) > 200 or not session_id.isprintable():
        fail("manifest.session_id must be a single printable line of at most 200 characters")
    return session_id


def load_manifest(
    path: Path,
) -> tuple[str, str, str, str, list[dict[str, object]]]:
    try:
        raw_manifest: object = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"input file does not exist: {path}")
    except OSError as error:
        fail(f"could not read input file {path}: {error}")
    except json.JSONDecodeError as error:
        fail(f"input file is not valid JSON: {error}")

    manifest = require_object(raw_manifest, "manifest")
    unknown_keys = sorted(
        set(manifest)
        - {"body", "comments", "model", "session_id", "session_provider"}
    )
    if unknown_keys:
        fail(f"manifest contains unsupported keys: {', '.join(unknown_keys)}")

    model = validate_model(manifest.get("model"))
    session_provider = validate_session_provider(manifest.get("session_provider"))
    session_id = validate_session_id(manifest.get("session_id"))
    body = require_nonempty_string(manifest.get("body"), "manifest.body")
    raw_comments = manifest.get("comments")
    if not isinstance(raw_comments, list) or not raw_comments:
        fail("manifest.comments must be a non-empty JSON array")

    comments = [
        validate_comment(raw_comment, index)
        for index, raw_comment in enumerate(raw_comments)
    ]
    return model, session_provider, session_id, body, comments


def run_gh(arguments: list[str], input_text: str | None = None) -> str:
    try:
        result = subprocess.run(
            ["gh", *arguments],
            check=False,
            capture_output=True,
            input=input_text,
            text=True,
        )
    except FileNotFoundError:
        fail("gh is not installed or is not on PATH")

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown gh error"
        fail(f"gh command failed: {detail}")
    return result.stdout


def current_head_sha(repository: str, pull_request: int) -> str:
    endpoint = f"repos/{repository}/pulls/{pull_request}"
    response = run_gh(["api", endpoint])
    try:
        payload: object = json.loads(response)
    except json.JSONDecodeError as error:
        fail(f"GitHub returned invalid PR metadata: {error}")
    metadata = require_object(payload, "GitHub PR response")
    head = require_object(metadata.get("head"), "GitHub PR response.head")
    return require_nonempty_string(head.get("sha"), "GitHub PR response.head.sha")


def submit_review(
    repository: str, pull_request: int, payload: dict[str, object]
) -> dict[str, object]:
    endpoint = f"repos/{repository}/pulls/{pull_request}/reviews"
    response = run_gh(
        ["api", "--method", "POST", endpoint, "--input", "-"],
        input_text=json.dumps(payload),
    )
    try:
        raw_result: object = json.loads(response)
    except json.JSONDecodeError as error:
        fail(f"GitHub returned an invalid review response: {error}")
    return require_object(raw_result, "GitHub review response")


def main() -> None:
    arguments = parse_arguments()

    if not REPOSITORY_PATTERN.fullmatch(arguments.repo):
        fail("--repo must use the OWNER/REPOSITORY format")
    if arguments.pr < 1:
        fail("--pr must be a positive integer")
    if not SHA_PATTERN.fullmatch(arguments.head_sha):
        fail("--head-sha must be a full 40-character hexadecimal SHA")

    model, session_provider, session_id, body, comments = load_manifest(arguments.input)
    attributed_comments = [
        {**comment, "body": f"Authored by AI:\n\n{comment['body']}"}
        for comment in comments
    ]
    review_body = (
        f"Review authored by AI.\n\n"
        f"Model used: {model}\n\n"
        f"{body}\n\n"
        f"{session_provider.title()} session ID: {session_id}"
    )
    payload: dict[str, object] = {
        "body": review_body,
        "commit_id": arguments.head_sha.lower(),
        "event": arguments.event,
        "comments": attributed_comments,
    }

    if arguments.dry_run:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    actual_head_sha = current_head_sha(arguments.repo, arguments.pr)
    if actual_head_sha.lower() != arguments.head_sha.lower():
        fail(
            "the PR head changed after anchors were mapped "
            f"(expected {arguments.head_sha}, found {actual_head_sha}); "
            "refresh the diff and remap every comment"
        )

    result = submit_review(arguments.repo, arguments.pr, payload)
    summary = {
        "id": result.get("id"),
        "html_url": result.get("html_url"),
        "state": result.get("state"),
        "submitted_at": result.get("submitted_at"),
        "model": model,
        "session_provider": session_provider,
        "session_id": session_id,
        "comment_count": len(comments),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
