# SPDX-FileCopyrightText: 2019 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tests for the pyclean CLI.
"""

import os
import re
import shutil
from importlib import import_module
from unittest.mock import patch

import pytest
from cli_test_helpers import ArgvContext, shell

import pyclean
import pyclean.cli


def test_main_module():
    """
    Exercise (most of) the code in the ``__main__`` module.
    """
    import_module('pyclean.__main__')


def test_runas_module():
    """
    Can this package be run as a Python module?
    """
    result = shell('python -m pyclean --help')
    assert result.exit_code == 0


def test_entrypoint():
    """
    Is entrypoint script installed? (pyproject.toml)
    """
    assert shutil.which('pyclean')


@patch('pyclean.cli.modern.pyclean', side_effect=Exception('Error test'))
def test_main_handles_exceptions(mock_modern):
    """
    The main CLI entry point handles exceptions gracefully.
    """
    with ArgvContext('pyclean', '.'), pytest.raises(SystemExit, match=r'Error test'):
        pyclean.cli.main()


@patch('pyclean.cli.modern.pyclean')
def test_mandatory_arg_missing(mock_modern):
    """
    Does CLI abort when no path is specified?
    """
    with ArgvContext('pyclean'), pytest.raises(SystemExit):
        pyclean.cli.main()

    assert not mock_modern.called


@patch('pyclean.cli.modern.pyclean')
def test_mandatory_args(mock_modern):
    """
    Does CLI execute fine when a path is specified?
    """
    with ArgvContext('pyclean', '.'):
        pyclean.cli.main()

    assert mock_modern.called


def test_dryrun_option():
    """
    Does a --dry-run option exist?
    """
    result = shell('pyclean --dry-run tests')

    assert result.exit_code == 0


def test_ignore_option():
    """
    Does an --ignore option exist and append values to a list of defaults?
    """
    default = ['.git', '.hg', '.svn', '.tox', '.venv', 'node_modules', 'venv']
    expected_ignore_list = [*default, 'foo', 'bar']

    with ArgvContext('pyclean', '.', '--ignore', 'foo', 'bar'):
        args = pyclean.cli.parse_arguments()

    assert args.ignore == expected_ignore_list


def test_debris_default_args():
    """
    Does calling `pyclean --debris` use defaults for the debris option?
    """
    with ArgvContext('pyclean', 'foo', '--debris'):
        args = pyclean.cli.parse_arguments()

    assert args.debris == ['cache', 'coverage', 'package', 'pytest', 'ruff']


def test_debris_optional_args():
    """
    Does the help screen explain all --debris options?
    """
    expected_debris_options_help = (
        '(may be specified multiple times; '
        'optional: all jupyter mypy tox; '
        'default: cache coverage package pytest ruff)'
    )

    result = shell('pyclean --help')
    normalized_stdout = re.sub(os.linesep + ' *', ' ', result.stdout)

    assert expected_debris_options_help in normalized_stdout


def test_debris_all():
    """
    Does calling `pyclean --debris all` pick all topics?
    """
    with ArgvContext('pyclean', 'foo', '--debris', 'all'):
        args = pyclean.cli.parse_arguments()

    assert args.debris == [
        'cache',
        'coverage',
        'package',
        'pytest',
        'ruff',
        'jupyter',
        'mypy',
        'tox',
    ]


def test_debris_explicit_args():
    """
    Does calling `pyclean --debris` with explicit arguments provide those?
    """
    with ArgvContext('pyclean', 'foo', '--debris', 'package', 'pytest'):
        args = pyclean.cli.parse_arguments()

    assert args.debris == ['package', 'pytest']


def test_debris_invalid_args():
    """
    Does calling `pyclean --debris` with invalid arguments abort execution?
    """
    args = ('pyclean', 'foo', '--debris', 'not-a-tool-name')

    with ArgvContext(*args), pytest.raises(SystemExit):
        pyclean.cli.parse_arguments()


@pytest.mark.parametrize(
    ('cli_args', 'erase_result'),
    [
        (['--erase', 'foo'], ['foo']),
        (['--erase', 'a', 'b', 'c'], ['a', 'b', 'c']),
        (['--erase=tmp/*', '--erase=tmp'], ['tmp/*', 'tmp']),
        (['-e', 'x', '-e', 'y', 'z'], ['x', 'y', 'z']),
    ],
)
def test_erase_multiple_args(cli_args, erase_result):
    """
    Does `--erase` accept multiple arguments, in different styles?
    """
    with ArgvContext('pyclean', '.', *cli_args):
        args = pyclean.cli.parse_arguments()

    assert args.erase == erase_result
    assert not args.yes


def test_erase_alone_aborts():
    """
    Does CLI abort when using `--erase` option without arguments?
    """
    with ArgvContext('pyclean', '.', '--erase'), pytest.raises(SystemExit):
        pyclean.cli.parse_arguments()


@pytest.mark.parametrize('option', ['--yes', '-y'])
def test_yes_option(option):
    """
    Is `--yes` option available, in long and short form?
    """
    with ArgvContext('pyclean', '.', '-e', 'tmp', option):
        args = pyclean.cli.parse_arguments()

    assert args.yes
    assert args.erase == ['tmp']


def test_yes_aborts_without_erase():
    """
    Does CLI abort when `--yes` is specified without `--erase`?
    """
    with ArgvContext('pyclean', '.', '--yes'), pytest.raises(SystemExit):
        pyclean.cli.parse_arguments()


def test_version_option():
    """
    Does --version yield the expected information?
    """
    expected_output = '%s%s' % (pyclean.__version__, os.linesep)

    result = shell('pyclean --version')

    assert result.stdout == expected_output
    assert result.exit_code == 0


@patch('pyclean.modern.pyclean')
def test_default_modern(mock_modern_pyclean):
    """
    Does simply calling `pyclean` invoke the modern implementation?
    """
    with ArgvContext('pyclean', 'foo'):
        pyclean.cli.main()

    assert mock_modern_pyclean.called


@pytest.mark.parametrize('option', ['--folders', '-f'])
def test_folders_option(option):
    """
    Is `--folders` option available, in long and short form?
    """
    with ArgvContext('pyclean', '.', option):
        args = pyclean.cli.parse_arguments()

    assert args.folders


def test_folders_default():
    """
    Does `--folders` default to False when not specified?
    """
    with ArgvContext('pyclean', '.'):
        args = pyclean.cli.parse_arguments()

    assert not args.folders
