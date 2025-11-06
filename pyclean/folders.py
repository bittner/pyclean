# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Empty directory removal."""

import logging
import os
from pathlib import Path

from .runner import Runner
from .traversal import should_ignore

log = logging.getLogger(__name__)


def remove_empty_directories(directory):
    """
    Recursively remove empty directories in the given directory tree.

    This walks the directory tree in post-order (bottom-up), attempting to
    remove directories that are empty.
    """
    try:
        subdirs = [entry for entry in os.scandir(directory) if entry.is_dir()]
    except (OSError, PermissionError) as err:
        log.warning('Cannot access directory %s: %s', directory, err)
        return

    for subdir in subdirs:
        if should_ignore(subdir.path, Runner.ignore):
            log.debug('Skipping %s', subdir)
        else:
            remove_empty_directories(subdir.path)
            try:
                if subdir.is_dir() and not any(os.scandir(subdir.path)):
                    Runner.rmdir(Path(subdir.path))
            except (OSError, PermissionError) as err:
                log.debug('Cannot check or remove directory %s: %s', subdir.path, err)
