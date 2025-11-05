# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Cleanup runner with dry-run and file operations functionality."""

import logging

log = logging.getLogger(__name__)


class CleanupRunner:
    """Execution engine with object counting, logging and optional dry-run."""

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


Runner = CleanupRunner()


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
