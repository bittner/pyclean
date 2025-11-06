# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Freeform target deletion with interactive prompt."""

import logging
from pathlib import Path

from .runner import Runner

log = logging.getLogger(__name__)


def confirm(message):
    """An interactive confirmation prompt."""
    try:
        answer = input('%s? ' % message)
        return answer.strip().lower() in ['y', 'yes']
    except KeyboardInterrupt:
        msg = 'Aborted by user.'
        raise SystemExit(msg)


def delete_filesystem_objects(
    directory: Path,
    path_glob: str,
    prompt=False,
    dry_run=False,
):
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


def remove_freeform_targets(
    directory: Path,
    glob_patterns: list[str],
    yes,
    dry_run=False,
):
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
