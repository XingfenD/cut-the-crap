#!/usr/bin/env python3
"""Flag candidate session-residue asides for human review.

This is an advisory tool: it over-reports by design, and a candidate is not a
verdict. Adjudicate every hit with the audience test and the redundancy test
from SKILL.md, and never delete text from this output alone. Exit status 0 means
the scan completed, not that the surfaces are clean.

Each PATH may be a text file or a directory (scanned recursively). Candidates
are reported as a JSON payload with the file path, line number, tag list, and a
clipped snippet.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from pathlib import Path

TEXT_SUFFIXES = frozenset(
    {
        ".md",
        ".markdown",
        ".txt",
        ".rst",
        ".html",
        ".htm",
        ".css",
        ".js",
        ".mjs",
        ".ts",
        ".tsx",
        ".jsx",
        ".rs",
        ".py",
        ".sh",
        ".bash",
        ".zsh",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
        ".log",
    }
)
SKIP_DIRECTORIES = frozenset(
    {".git", ".hg", ".svn", "node_modules", "target", "dist", "build", "__pycache__"}
)
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_SNIPPET_CHARS = 160

DENIAL = "不|无|没|未|否|免"
TRAJECTORY = "不再|仍未|依然|依旧|照旧|照样|此前|本次|本轮|这次|原本|原先"
REASSURANCE = "无害|不受影响|不影响|不必|无需|无须|放心|没问题|并不|并未"

_PARENTHETICAL_PATTERN = re.compile(
    rf"[（(][^）)\n]{{0,120}}(?:{DENIAL}|{TRAJECTORY}|{REASSURANCE})[^）)\n]{{0,120}}[）)]"
)
_TRAJECTORY_PATTERN = re.compile(TRAJECTORY)
_REASSURANCE_PATTERN = re.compile(REASSURANCE)
_ENGLISH_PATTERN = re.compile(
    r"(?i)\b(?:no longer|no more|still (?:flows?|works?|applies|emits)|already|"
    r"can now|harmless|unaffected|unnecessary|not needed|isn't|doesn't|won't|"
    r"this (?:round|time|change))\b"
)


def tags_for_line(line: str) -> list[str]:
    """Return heuristic tags for one line (candidates only, never verdicts)."""
    tags: list[str] = []
    if _PARENTHETICAL_PATTERN.search(line):
        tags.append("parenthetical")
    if _TRAJECTORY_PATTERN.search(line):
        tags.append("change-relative")
    if _REASSURANCE_PATTERN.search(line):
        tags.append("reassurance")
    if _ENGLISH_PATTERN.search(line):
        tags.append("english")
    return tags


def _iter_text_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    files: list[Path] = []
    for current, directory_names, file_names in os.walk(path, topdown=True):
        directory_names[:] = sorted(
            name for name in directory_names if name not in SKIP_DIRECTORIES
        )
        for name in sorted(file_names):
            candidate = Path(current) / name
            if candidate.suffix.lower() in TEXT_SUFFIXES:
                files.append(candidate)
    return files


def _read_lines(path: Path) -> list[str]:
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_FILE_BYTES:
        raise OSError(f"not a readable text surface: {path}")
    text = path.read_bytes().decode("utf-8-sig", errors="replace")
    return text.splitlines()


def _snippet(line: str) -> str:
    clipped = " ".join(line.split())
    if len(clipped) > MAX_SNIPPET_CHARS:
        clipped = clipped[: MAX_SNIPPET_CHARS - 1] + "…"
    return clipped


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag candidate session-residue asides for human review "
            "(advisory only; over-reports by design)."
        )
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=200,
        help="stop collecting candidates after this many hits (default: 200)",
    )
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    files: list[Path] = []
    for supplied in args.paths:
        if supplied.is_dir():
            files.extend(_iter_text_files(supplied))
        elif supplied.is_file():
            files.append(supplied)
        else:
            print(
                json.dumps(
                    {
                        "status": "ERROR",
                        "reason_code": "path_not_found",
                        "path": str(supplied),
                    },
                    ensure_ascii=True,
                    sort_keys=True,
                )
            )
            return 2

    candidates: list[dict[str, object]] = []
    checked = 0
    truncated = False
    for path in files:
        try:
            lines = _read_lines(path)
        except OSError:
            continue
        checked += 1
        for number, line in enumerate(lines, start=1):
            tags = tags_for_line(line)
            if not tags:
                continue
            if len(candidates) >= args.max_candidates:
                truncated = True
                break
            candidates.append(
                {
                    "file": str(path),
                    "line": number,
                    "tags": tags,
                    "snippet": _snippet(line),
                }
            )
        if truncated:
            break

    print(
        json.dumps(
            {
                "status": "CANDIDATES" if candidates else "CLEAN",
                "files_checked": checked,
                "truncated": truncated,
                "candidates": candidates,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
