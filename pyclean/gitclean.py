# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Git integration for cleaning untracked files."""

import logging
import subprocess

GIT_FATAL_ERROR = 128

log = logging.getLogger(__name__)


def build_git_clean_command(
    ignore_patterns: list[str],
    dry_run=False,
    force=False,
) -> list[str]:
    """
    Build the git clean command with appropriate flags.
    """
    exclude = (item for pattern in ignore_patterns for item in ['-e', pattern])
    mode = '-n' if dry_run else '-f' if force else '-i'
    return ['git', 'clean', '-dx', *exclude, mode]


def execute_git_clean(directory, args):
    """
    Execute git clean in the specified directory.
    """
    log.info('Executing git clean...')
    cmd = build_git_clean_command(args.ignore, dry_run=args.dry_run, force=args.yes)

    log.debug('Run: %s', ' '.join(cmd))
    result = subprocess.run(cmd, cwd=directory, check=False)  # noqa: S603

    if result.returncode == GIT_FATAL_ERROR:
        log.warning(
            'Directory %s is not under version control. Skipping git clean.',
            directory,
        )
    elif result.returncode:
        raise SystemExit(result.returncode)
