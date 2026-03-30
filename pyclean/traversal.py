# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Directory traversal and ignore pattern matching."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from .runner import Runner

log = logging.getLogger(__name__)


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
            if Runner.is_ignored(Path(child.path)):
                log.debug('Skipping %s', child.name)
            else:
                descend_and_clean(child.path, file_types, dir_names)

            if child.name in dir_names:
                Runner.rmdir(Path(child.path))
        else:
            log.debug('Ignoring %s (neither a file nor a folder)', child.name)
