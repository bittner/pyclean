# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Modern, cross-platform, pure-Python pyclean implementation.
"""

import logging
import os
from pathlib import Path

BYTECODE_FILES = ['.pyc', '.pyo']
BYTECODE_DIRS = ['__pycache__']
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


class CleanupRunner:
    """Module-level configuration and value store."""

    def __init__(self):
        """Cleanup runner with optional dry-run behavior."""
        self.unlink = None
        self.rmdir = None
        self.ignore = None
        self.unlink_count = None
        self.unlink_failed = None
        self.rmdir_count = None
        self.rmdir_failed = None

    def configure(self, args):
        """Set up runner according to command line options."""
        self.unlink = print_filename if args.dry_run else remove_file
        self.rmdir = print_dirname if args.dry_run else remove_directory
        self.ignore = args.ignore
        self.unlink_count = 0
        self.unlink_failed = 0
        self.rmdir_count = 0
        self.rmdir_failed = 0


log = logging.getLogger(__name__)
Runner = CleanupRunner()


def normalize(path_pattern: str) -> str:
    """
    Normalize path separators in a pattern for cross-platform support.

    On Windows, both forward slash and backslash are valid path separators.
    On Unix/Posix, only forward slash is valid (backslash can be part of filename).
    """
    return path_pattern.replace(os.sep, os.altsep or os.sep)


def should_ignore(path: Path, ignore_patterns: list[str]) -> bool:
    """
    Check if a path should be ignored based on ignore patterns.

    Patterns can be:
    - Simple names like 'bar': matches any directory with that name
    - Paths like 'foo/bar': matches 'bar' directory inside 'foo' directory
      and also ignores everything inside that directory
    """
    if not ignore_patterns:
        return False

    for pattern in ignore_patterns:
        # Check if pattern has multiple components (is a path with separators)
        pattern_parts = Path(normalize(pattern)).parts
        if len(pattern_parts) > 1:
            # Pattern contains path separator - match relative path
            # Path must have at least as many parts as the pattern
            if len(path.parts) < len(pattern_parts):
                continue
            # Check if pattern matches anywhere in the path hierarchy
            for i in range(len(path.parts) - len(pattern_parts) + 1):
                path_slice = path.parts[i : i + len(pattern_parts)]
                if path_slice == pattern_parts:
                    return True
        # Simple name - match the directory name anywhere
        elif path.name == pattern:
            return True
    return False


def remove_file(fileobj):
    """Attempt to delete a file object for real."""
    log.debug('Deleting file: %s', fileobj)
    try:
        fileobj.unlink()
        Runner.unlink_count += 1
    except OSError as err:
        log.debug('File not deleted. %s', err)
        Runner.unlink_failed += 1


def remove_directory(dirobj):
    """Attempt to remove a directory object for real."""
    log.debug('Removing directory: %s', dirobj)
    try:
        dirobj.rmdir()
        Runner.rmdir_count += 1
    except OSError as err:
        log.debug('Directory not removed. %s', err)
        Runner.rmdir_failed += 1


def print_filename(fileobj):
    """Only display the file name, used with --dry-run."""
    log.debug('Would delete file: %s', fileobj)
    Runner.unlink_count += 1


def print_dirname(dirobj):
    """Only display the directory name, used with --dry-run."""
    log.debug('Would delete directory: %s', dirobj)
    Runner.rmdir_count += 1


def pyclean(args):
    """Cross-platform cleaning of Python bytecode."""
    Runner.configure(args)

    for dir_name in args.directory:
        dir_path = Path(dir_name)

        log.info('Cleaning directory %s', dir_path)
        descend_and_clean(dir_path, BYTECODE_FILES, BYTECODE_DIRS)

        for topic in args.debris:
            remove_debris_for(topic, dir_path)

        remove_freeform_targets(dir_path, args.erase, args.yes, args.dry_run)

    log.info(
        'Total %d files, %d directories %s.',
        Runner.unlink_count,
        Runner.rmdir_count,
        'would be removed' if args.dry_run else 'removed',
    )

    if Runner.unlink_failed or Runner.rmdir_failed:
        log.debug(
            '%d files, %d directories %s not be removed.',
            Runner.unlink_failed,
            Runner.rmdir_failed,
            'would' if args.dry_run else 'could',
        )

    # Suggest --debris option if it wasn't used
    if not args.debris:
        suggest_debris_option(args)


def descend_and_clean(directory, file_types, dir_names):
    """
    Walk and descend a directory tree, cleaning up files of a certain type
    along the way. Only delete directories if they are empty, in the end.
    """
    for child in sorted(directory.iterdir()):
        if child.is_file():
            if child.suffix in file_types:
                Runner.unlink(child)
        elif child.is_dir():
            if should_ignore(child, Runner.ignore):
                log.debug('Skipping %s', child)
            else:
                descend_and_clean(child, file_types, dir_names)

            if child.name in dir_names:
                Runner.rmdir(child)
        else:
            log.debug('Ignoring %s (neither a file nor a folder)', child)


def remove_debris_for(topic, directory):
    """
    Clean up debris for a specific topic.
    """
    log.debug('Scanning for debris of %s ...', topic.title())

    patterns = DEBRIS_TOPICS[topic]
    recursive_delete_debris(directory, patterns)


def remove_freeform_targets(directory, glob_patterns, yes, dry_run=False):
    """
    Remove free-form targets using globbing.

    This is **potentially dangerous** since users can delete everything
    anywhere in their file system, including the entire project they're
    working on. For this reason, the implementation imposes the following
    (user experience-related) restrictions:

    - Deleting (directories) is not recursive, directory contents must be
      explicitly specified using globbing (e.g. ``dirname/**/*``).
    - The user is responsible for the deletion order, so that a directory
      is empty when it is attempted to be deleted.
    - A confirmation prompt for the deletion of every single file system
      object is shown (unless the ``--yes`` option is used, in addition).
    """
    for path_glob in glob_patterns:
        log.debug('Erase file system objects matching: %s', path_glob)
        delete_filesystem_objects(directory, path_glob, prompt=not yes, dry_run=dry_run)


def recursive_delete_debris(directory, patterns):
    """
    Recursively delete debris matching any of the given patterns.

    This function walks the directory tree once and applies all patterns
    at each level, avoiding redundant directory scans.
    """
    for pattern in patterns:
        delete_filesystem_objects(directory, pattern)

    try:
        subdirs = (
            Path(entry.path) for entry in os.scandir(directory) if entry.is_dir()
        )
    except (OSError, PermissionError) as err:
        log.warning('Cannot access directory %s: %s', directory, err)
        return

    for subdir in subdirs:
        if should_ignore(subdir, Runner.ignore):
            log.debug('Skipping %s', subdir)
        else:
            recursive_delete_debris(subdir, patterns)


def delete_filesystem_objects(directory, path_glob, prompt=False, dry_run=False):
    """
    Identifies all pathnames matching a specific glob pattern, and attempts
    to delete them in the proper order, optionally asking for confirmation.

    Implementation Note: We sort the file system objects in *reverse order*
    and first delete *all files* before removing directories. This way we
    make sure that the directories that are deepest down in the hierarchy
    are empty (for both files & directories) when we attempt to remove them.
    """
    all_names = sorted(directory.glob(path_glob), reverse=True)
    dirs = (name for name in all_names if name.is_dir() and not name.is_symlink())
    files = (name for name in all_names if not name.is_dir() or name.is_symlink())

    for file_object in files:
        file_type = 'symlink' if file_object.is_symlink() else 'file'
        if (
            not dry_run
            and prompt
            and not confirm('Delete %s %s' % (file_type, file_object))
        ):
            Runner.unlink_failed += 1
            continue
        Runner.unlink(file_object)

    for dir_object in dirs:
        if (
            not dry_run
            and prompt
            and not confirm('Remove empty directory %s' % dir_object)
        ):
            Runner.rmdir_failed += 1
            continue
        Runner.rmdir(dir_object)


def confirm(message):
    """An interactive confirmation prompt."""
    try:
        answer = input('%s? ' % message)
        return answer.strip().lower() in ['y', 'yes']
    except KeyboardInterrupt:
        msg = 'Aborted by user.'
        raise SystemExit(msg)


def detect_debris_in_directory(directory):
    """
    Scan a directory for debris artifacts and return a list of detected topics.
    """
    detected_topics = []

    for topic, patterns in DEBRIS_TOPICS.items():
        for pattern in patterns:
            # Skip patterns that are for recursive cleanup (contain **)
            if '**' in pattern:
                continue
            # Check if the pattern matches anything in the directory
            matches = list(directory.glob(pattern))
            if matches:
                detected_topics.append(topic)
                break  # Found at least one match for this topic, move to next

    return detected_topics


def suggest_debris_option(args):
    """
    Suggest using the --debris option when it wasn't used.
    Optionally provide targeted suggestions based on detected artifacts.
    """
    # Collect all detected debris topics across all directories
    all_detected = set()
    for dir_name in args.directory:
        dir_path = Path(dir_name)
        if dir_path.exists():
            detected = detect_debris_in_directory(dir_path)
            all_detected.update(detected)

    if all_detected:
        # Provide targeted suggestion
        topics_str = ' '.join(sorted(all_detected))
        log.info(
            'Hint: Use --debris to also clean up build artifacts. Detected: %s',
            topics_str,
        )
    else:
        # Provide general suggestion
        log.info(
            'Hint: Use --debris to also clean up build artifacts '
            'from common Python development tools.',
        )
