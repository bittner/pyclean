# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Main orchestration of the pyclean cleanup process."""

import logging
from pathlib import Path

from .bytecode import BYTECODE_DIRS, BYTECODE_FILES
from .debris import remove_debris_for, suggest_debris_option
from .erase import remove_freeform_targets
from .folders import remove_empty_directories
from .gitclean import execute_git_clean
from .runner import Runner
from .traversal import descend_and_clean

log = logging.getLogger(__name__)


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

        if args.folders:
            log.debug('Removing empty directories...')
            remove_empty_directories(dir_path)

        if args.git_clean:
            execute_git_clean(dir_path, args)

    git_clean_note = ' (Not counting git clean)' if args.git_clean else ''

    log.info(
        'Total %d files, %d directories %s.%s',
        Runner.unlink_count,
        Runner.rmdir_count,
        'would be removed' if args.dry_run else 'removed',
        git_clean_note,
    )

    if Runner.unlink_failed or Runner.rmdir_failed:
        log.debug(
            '%d files, %d directories %s not be removed.%s',
            Runner.unlink_failed,
            Runner.rmdir_failed,
            'would' if args.dry_run else 'could',
            git_clean_note,
        )

    if not args.debris:
        suggest_debris_option(args)
