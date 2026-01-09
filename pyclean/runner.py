# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Cleanup runner with dry-run and file operations functionality."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace
    from pathlib import Path

log = logging.getLogger(__name__)


def noop(_: Path) -> None:
    """No-op function for uninitialized runner."""


class CleanupRunner:
    """Execution engine with object counting, logging and optional dry-run."""

    def __init__(self):
        """Cleanup runner with optional dry-run behavior."""
        self.unlink = noop
        self.rmdir = noop
        self.ignore: list[str] = []
        self.unlink_count = 0
        self.unlink_failed = 0
        self.rmdir_count = 0
        self.rmdir_failed = 0

    def configure(self, args: Namespace) -> None:
        """Set up runner according to command line options."""
        self.unlink = print_filename if args.dry_run else remove_file
        self.rmdir = print_dirname if args.dry_run else remove_directory
        self.ignore = args.ignore
        self.unlink_count = 0
        self.unlink_failed = 0
        self.rmdir_count = 0
        self.rmdir_failed = 0


Runner = CleanupRunner()


def remove_file(fileobj: Path) -> None:
    """Attempt to delete a file object for real."""
    log.debug('Deleting file: %s', fileobj)
    try:
        fileobj.unlink()
        Runner.unlink_count += 1
    except OSError as err:
        log.debug('File not deleted. %s', err)
        Runner.unlink_failed += 1


def remove_directory(dirobj: Path) -> None:
    """Attempt to remove a directory object for real."""
    log.debug('Removing directory: %s', dirobj)
    try:
        dirobj.rmdir()
        Runner.rmdir_count += 1
    except OSError as err:
        log.debug('Directory not removed. %s', err)
        Runner.rmdir_failed += 1


def print_filename(fileobj: Path) -> None:
    """Only display the file name, used with --dry-run."""
    log.debug('Would delete file: %s', fileobj)
    Runner.unlink_count += 1


def print_dirname(dirobj: Path) -> None:
    """Only display the directory name, used with --dry-run."""
    log.debug('Would delete directory: %s', dirobj)
    Runner.rmdir_count += 1
