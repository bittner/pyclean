# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the gitclean module."""

from argparse import Namespace
from unittest.mock import Mock, patch

import pytest
from cli_test_helpers import ArgvContext
from conftest import skip_if_no_git

import pyclean.cli
import pyclean.main


def test_run_git_clean_dry_run():
    cmd = pyclean.main.build_git_clean_command(
        ignore_patterns=['.idea', '.vscode'],
        dry_run=True,
        force=False,
    )

    cmd_str = ' '.join(cmd)
    assert cmd_str.startswith('git clean -dx')
    assert ' -e .idea' in cmd_str
    assert ' -e .vscode' in cmd_str
    assert '-n' in cmd


def test_run_git_clean_force():
    cmd = pyclean.main.build_git_clean_command(
        ignore_patterns=['.tox'],
        dry_run=False,
        force=True,
    )

    cmd_str = ' '.join(cmd)
    assert cmd_str.startswith('git clean -dx')
    assert ' -e .tox' in cmd_str
    assert '-f' in cmd


def test_run_git_clean_interactive():
    cmd = pyclean.main.build_git_clean_command(
        ignore_patterns=[],
        dry_run=False,
        force=False,
    )

    cmd_str = ' '.join(cmd)
    assert cmd_str.startswith('git clean -dx')
    assert '-i' in cmd


@skip_if_no_git
@patch('pyclean.gitclean.log')
@patch(
    'pyclean.gitclean.subprocess.run',
    return_value=Mock(returncode=pyclean.main.GIT_FATAL_ERROR),
)
def test_execute_git_clean_not_a_git_repo(mock_run, mock_log):
    args = Namespace(ignore=[], git_clean=True, dry_run=False, yes=False)

    pyclean.main.execute_git_clean('/not/a/repo', args)

    assert mock_run.called
    mock_log.warning.assert_called_once_with(
        'Directory %s is not under version control. Skipping git clean.',
        '/not/a/repo',
    )


@skip_if_no_git
@patch('pyclean.main.execute_git_clean')
@patch('pyclean.main.descend_and_clean')
def test_pyclean_with_git_clean(mock_descend, mock_git_clean):
    """
    Does pyclean call execute_git_clean when --git-clean flag is used?
    """
    with ArgvContext('pyclean', '.', '--git-clean'):
        pyclean.cli.main()

    assert mock_git_clean.called


@skip_if_no_git
@patch('pyclean.gitclean.subprocess.run', return_value=Mock(returncode=42))
@patch('pyclean.gitclean.log')
@patch('pyclean.main.descend_and_clean')
def test_git_clean_exit_nonzero_raises(mock_descend, mock_log, mock_git_clean):
    """
    Does pyclean exit with git-clean's status code when git clean fails?
    """
    with (
        ArgvContext('pyclean', '.', '--git-clean'),
        pytest.raises(SystemExit) as exc_info,
    ):
        pyclean.cli.main()

    mock_log.info.assert_called_once_with('Executing git clean...')
    assert exc_info.value.code == 42  # noqa: PLR2004
