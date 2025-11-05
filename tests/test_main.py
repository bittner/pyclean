# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for pyclean's main module."""

import logging
from argparse import Namespace
from pathlib import Path
from unittest.mock import call, patch

import pytest
from cli_test_helpers import ArgvContext

import pyclean.cli
import pyclean.main


@patch('pyclean.main.descend_and_clean')
def test_walks_tree(mock_descend):
    """
    Does pyclean walk the directory tree?
    """
    with ArgvContext('pyclean', '.'):
        pyclean.cli.main()

    assert mock_descend.mock_calls == [
        call(Path(), ['.pyc', '.pyo'], ['__pycache__']),
    ]


@patch('pyclean.main.descend_and_clean')
def test_walks_all_trees(mock_descend):
    """
    Are all positional args evaluated?
    """
    with ArgvContext('pyclean', 'foo', 'bar', 'baz'):
        pyclean.cli.main()

    assert mock_descend.mock_calls == [
        call(Path('foo'), ['.pyc', '.pyo'], ['__pycache__']),
        call(Path('bar'), ['.pyc', '.pyo'], ['__pycache__']),
        call(Path('baz'), ['.pyc', '.pyo'], ['__pycache__']),
    ]


@patch.object(pyclean.main.logging, 'basicConfig')
@patch('pyclean.main.descend_and_clean')
def test_normal_logging(mock_descend, mock_logconfig):
    """
    Does a normal run use log level INFO?
    """
    with ArgvContext('pyclean', '.'):
        pyclean.cli.main()

    assert mock_logconfig.mock_calls == [
        call(format='%(message)s', level=logging.INFO),
    ]


@patch.object(pyclean.main.logging, 'basicConfig')
@patch('pyclean.main.descend_and_clean')
def test_verbose_logging(mock_descend, mock_logconfig):
    """
    Does --verbose use log level DEBUG?
    """
    with ArgvContext('pyclean', '.', '--verbose'):
        pyclean.cli.main()

    assert mock_logconfig.mock_calls == [
        call(format='%(message)s', level=logging.DEBUG),
    ]


@patch.object(pyclean.main.logging, 'basicConfig')
@patch('pyclean.main.descend_and_clean')
def test_quiet_logging(mock_descend, mock_logconfig):
    """
    Does --quiet use log level FATAL?
    """
    with ArgvContext('pyclean', '.', '--quiet'):
        pyclean.cli.main()

    assert mock_logconfig.mock_calls == [
        call(format='%(message)s', level=logging.FATAL),
    ]


@pytest.mark.parametrize(
    ('unlink_failures', 'rmdir_failures', 'git_clean', 'explanation'),
    [
        (7, 0, False, ''),
        (0, 3, False, ''),
        (1, 1, False, ''),
        (42, 42, True, ' (Not counting git clean)'),
    ],
)
@patch('pyclean.main.suggest_debris_option')
@patch('pyclean.runner.CleanupRunner.configure')
@patch('pyclean.main.log')
def test_report_failures(  # noqa: PLR0913
    mock_log,
    mock_configure,
    mock_suggest,
    unlink_failures,
    rmdir_failures,
    git_clean,
    explanation,
):
    args = Namespace(
        debris=[],
        directory=[],
        dry_run=True,
        erase=[],
        git_clean=git_clean,
        ignore=[],
        yes=False,
    )
    pyclean.main.Runner.configure(args)
    pyclean.main.Runner.unlink_failed = unlink_failures
    pyclean.main.Runner.rmdir_failed = rmdir_failures

    pyclean.main.pyclean(args)

    mock_log.debug.assert_called_with(
        '%d files, %d directories %s not be removed.%s',
        unlink_failures,
        rmdir_failures,
        'would',
        explanation,
    )
    mock_log.info.assert_called_with(
        'Total %d files, %d directories %s.%s',
        0,
        0,
        'would be removed',
        explanation,
    )
