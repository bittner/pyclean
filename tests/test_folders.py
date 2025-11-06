# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the folders module."""

from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest
from cli_test_helpers import ArgvContext

import pyclean.cli
import pyclean.main
from pyclean.folders import remove_empty_directories


def test_remove_empty_directories():
    """
    Does remove_empty_directories remove nested empty directories?
    """
    args = Namespace(dry_run=False, ignore=[])
    pyclean.main.Runner.configure(args)

    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        (directory / 'empty1' / 'empty2' / 'empty3').mkdir(parents=True)
        (directory / 'nonempty').mkdir()
        (directory / 'nonempty' / 'file.txt').write_text('content')

        remove_empty_directories(directory)

        assert not (directory / 'empty1').exists()
        assert not (directory / 'empty1' / 'empty2').exists()
        assert not (directory / 'empty1' / 'empty2' / 'empty3').exists()
        assert (directory / 'nonempty').exists()
        assert (directory / 'nonempty' / 'file.txt').exists()


def test_remove_empty_directories_with_ignore():
    """
    Does remove_empty_directories respect ignore patterns?
    """
    args = Namespace(dry_run=False, ignore=['.venv'])
    pyclean.main.Runner.configure(args)

    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        (directory / 'empty1').mkdir()
        (directory / '.venv' / 'empty2').mkdir(parents=True)

        remove_empty_directories(directory)

        assert not (directory / 'empty1').exists()
        assert (directory / '.venv').exists()
        assert (directory / '.venv' / 'empty2').exists()


def test_remove_empty_directories_dry_run():
    """
    Does remove_empty_directories honor dry-run mode?
    """
    args = Namespace(dry_run=True, ignore=[])
    pyclean.main.Runner.configure(args)

    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        (directory / 'empty').mkdir()

        remove_empty_directories(directory)

        assert (directory / 'empty').exists()


@patch('pyclean.folders.remove_empty_directories')
@patch('pyclean.main.descend_and_clean')
def test_folders_option_calls_remove_empty(mock_descend, mock_remove_empty):
    with ArgvContext('pyclean', '.', '--folders'):
        pyclean.cli.main()

    assert mock_remove_empty.called


@patch('pyclean.folders.remove_empty_directories')
@patch('pyclean.main.descend_and_clean')
def test_no_folders_option_skips_remove_empty(mock_descend, mock_remove_empty):
    with ArgvContext('pyclean', '.'):
        pyclean.cli.main()

    assert not mock_remove_empty.called


@pytest.mark.parametrize(
    ('system_error'),
    [
        PermissionError('Permission denied'),
        OSError('I/O error'),
    ],
)
@patch('pyclean.folders.log')
def test_remove_empty_directories_error(mock_log, system_error):
    args = Namespace(dry_run=False, ignore=[])
    pyclean.main.Runner.configure(args)

    directory = Path('/nonexistent/test/directory')

    with patch('os.scandir', side_effect=system_error) as mock_scandir:
        remove_empty_directories(directory)

    mock_log.warning.assert_called_once_with(
        'Cannot access directory %s: %s',
        directory,
        mock_scandir.side_effect,
    )


@pytest.mark.parametrize(
    ('system_error'),
    [
        PermissionError('Permission denied'),
        OSError('I/O error'),
    ],
)
@patch('pyclean.folders.log')
def test_remove_empty_directories_with_nested_error(mock_log, system_error):
    args = Namespace(dry_run=False, ignore=[], verbose=True)
    pyclean.main.Runner.configure(args)

    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        subdir = directory / 'child'
        subdir.mkdir()

        with patch('pyclean.main.Runner.rmdir', side_effect=system_error):
            remove_empty_directories(directory)

        mock_log.debug.assert_called_once_with(
            'Cannot check or remove directory %s: %s',
            str(subdir),
            system_error,
        )
