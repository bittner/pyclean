# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ignore pattern matching utilities."""

from __future__ import annotations

import os
from pathlib import Path


def normalize(path_pattern: str) -> str:
    """
    Normalize path separators in a pattern for cross-platform support.

    On Windows, both forward slash and backslash are valid path separators.
    On Unix/Posix, only forward slash is valid (backslash can be part of filename).
    """
    return path_pattern.replace(os.sep, os.altsep or os.sep)


def should_ignore(pathname: str, ignore_patterns: list[str] | None) -> bool:
    """
    Check if a path should be ignored based on ignore patterns.

    Patterns can be:
    - Simple names like 'bar': matches any directory with that name
    - Paths like 'foo/bar': matches 'bar' directory inside 'foo' directory
      and also ignores everything inside that directory
    """
    if not ignore_patterns:
        return False

    path = Path(pathname)

    for pattern in ignore_patterns:
        pattern_parts = Path(normalize(pattern)).parts
        if len(pattern_parts) > 1:
            if len(path.parts) < len(pattern_parts):
                continue
            for i in range(len(path.parts) - len(pattern_parts) + 1):
                path_slice = path.parts[i : i + len(pattern_parts)]
                if path_slice == pattern_parts:
                    return True
        elif path.name == pattern:
            return True
    return False


def path_is_ignored(path: Path, ignore_patterns: list[str]) -> bool:
    """Check if a path or any of its ancestors matches an ignore pattern."""
    if not isinstance(path, Path):
        path = Path(str(path))
    return any(should_ignore(str(p), ignore_patterns) for p in [path, *path.parents])
