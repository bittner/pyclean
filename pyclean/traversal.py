# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Directory traversal and ignore pattern matching."""

import logging
import os
from pathlib import Path

from .runner import Runner

log = logging.getLogger(__name__)


def normalize(path_pattern: str) -> str:
    """
    Normalize path separators in a pattern for cross-platform support.

    On Windows, both forward slash and backslash are valid path separators.
    On Unix/Posix, only forward slash is valid (backslash can be part of filename).
    """
    return path_pattern.replace(os.sep, os.altsep or os.sep)


def should_ignore(path, ignore_patterns: list[str]) -> bool:
    """
    Check if a path should be ignored based on ignore patterns.

    Patterns can be:
    - Simple names like 'bar': matches any directory with that name
    - Paths like 'foo/bar': matches 'bar' directory inside 'foo' directory
      and also ignores everything inside that directory
    """
    if not ignore_patterns:
        return False

    path = Path(path)

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


def descend_and_clean(directory, file_types, dir_names):
    """
    Walk and descend a directory tree, cleaning up files of a certain type
    along the way. Only delete directories if they are empty, in the end.
    """
    for child in sorted(os.scandir(directory), key=lambda e: e.name):
        if child.is_file():
            if Path(child.path).suffix in file_types:
                Runner.unlink(Path(child.path))
        elif child.is_dir():
            if should_ignore(child.path, Runner.ignore):
                log.debug('Skipping %s', child.path)
            else:
                descend_and_clean(child.path, file_types, dir_names)

            if child.name in dir_names:
                Runner.rmdir(Path(child.path))
        else:
            log.debug('Ignoring %s (neither a file nor a folder)', child.path)
