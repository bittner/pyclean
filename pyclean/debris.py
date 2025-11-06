# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tool-specific artifact cleanup and debris detection (to suggest option usage)."""

import logging
import os
from pathlib import Path

from .erase import delete_filesystem_objects
from .runner import Runner
from .traversal import should_ignore

log = logging.getLogger(__name__)

DEBRIS_TOPICS = {
    'cache': [
        '.cache/**/*',
        '.cache/',
    ],
    'coverage': [
        '.coverage',
        'coverage.json',
        'coverage.lcov',
        'coverage.xml',
        'htmlcov/**/*',
        'htmlcov/',
    ],
    'jupyter': [
        '.ipynb_checkpoints/**/*',
        '.ipynb_checkpoints/',
    ],
    'mypy': [
        '.mypy_cache/**/*',
        '.mypy_cache/',
    ],
    'package': [
        'build/bdist.*/**/*',
        'build/bdist.*/',
        'build/lib/**/*',
        'build/lib/',
        'build/',
        'dist/**/*',
        'dist/',
        'sdist/**/*',
        'sdist/',
        '*.egg-info/**/*',
        '*.egg-info/',
    ],
    'pyright': [
        '.pyright-app-cache-*/**/*',
        '.pyright-app-cache-*/',
        '.pyright-stubs-*/**/*',
        '.pyright-stubs-*/',
        '.pyright/',
    ],
    'pytest': [
        '.pytest_cache/**/*',
        '.pytest_cache/',
        'pytestdebug.log',
    ],
    'ruff': [
        '.ruff_cache/**/*',
        '.ruff_cache/',
    ],
    'tox': [
        '.tox/**/*',
        '.tox/',
    ],
}


def remove_debris_for(topic, directory):
    """
    Clean up debris for a specific topic.
    """
    log.debug('Scanning for debris of %s ...', topic.title())

    patterns = DEBRIS_TOPICS[topic]
    recursive_delete_debris(directory, patterns)


def recursive_delete_debris(directory: Path, patterns: list[str]):
    """
    Recursively delete debris matching any of the given patterns.

    This function walks the directory tree once and applies all patterns
    at each level, avoiding redundant directory scans.
    """
    for pattern in patterns:
        delete_filesystem_objects(directory, pattern)

    try:
        subdirs = [entry for entry in os.scandir(directory) if entry.is_dir()]
    except (OSError, PermissionError) as err:
        log.warning('Cannot access directory %s: %s', directory, err)
        return

    for subdir in subdirs:
        if should_ignore(subdir.path, Runner.ignore):
            log.debug('Skipping %s', subdir.name)
        else:
            recursive_delete_debris(Path(subdir.path), patterns)


def detect_debris_in_directory(directory):
    """
    Scan a directory for debris artifacts and return a list of detected topics.
    """
    detected_topics = []

    for topic, patterns in DEBRIS_TOPICS.items():
        for pattern in patterns:
            if '**' in pattern:
                continue
            matches = list(directory.glob(pattern))
            if matches:
                detected_topics.append(topic)
                break

    return detected_topics


def suggest_debris_option(args):
    """
    Suggest using the --debris option when it wasn't used.
    Optionally provide targeted suggestions based on detected artifacts.
    """
    all_detected = set()
    for dir_name in args.directory:
        dir_path = Path(dir_name)
        if dir_path.exists():
            detected = detect_debris_in_directory(dir_path)
            all_detected.update(detected)

    if all_detected:
        topics_str = ' '.join(sorted(all_detected))
        log.info(
            'Hint: Use --debris to also clean up build artifacts. Detected: %s',
            topics_str,
        )
    else:
        log.info(
            'Hint: Use --debris to also clean up build artifacts '
            'from common Python development tools.',
        )
