# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the runner module."""

from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from cli_test_helpers import ArgvContext

import pyclean.cli
import pyclean.main
from pyclean.runner import remove_directory, remove_file


@patch('pathlib.Path.unlink')
def test_unlink_success(mock_unlink):
    """
    Walk the code of a successful deletion.
    """
    remove_file(Path('tmp'))

    assert mock_unlink.called


@patch('pathlib.Path.rmdir')
def test_rmdir_success(mock_rmdir):
    """
    Walk the code of a successful deletion.
    """
    remove_directory(Path('tmp'))

    assert mock_rmdir.called


@patch('pyclean.runner.log')
@patch('pathlib.Path.unlink', side_effect=OSError)
def test_unlink_failure(mock_unlink, mock_log):
    args = Namespace(dry_run=False, ignore=[])
    pyclean.main.Runner.configure(args)

    remove_file(Path('tmp'))

    mock_log.debug.assert_called()
    assert 'File not deleted.' in str(mock_log.debug.call_args)


@patch('pyclean.runner.log')
@patch('pathlib.Path.rmdir', side_effect=OSError)
def test_rmdir_failure(mock_rmdir, mock_log):
    args = Namespace(dry_run=False, ignore=[])
    pyclean.main.Runner.configure(args)

    remove_directory(Path('tmp'))

    mock_log.debug.assert_called()
    assert 'Directory not removed.' in str(mock_log.debug.call_args)


@patch('pyclean.runner.log')
def test_dryrun_output(mock_log):
    expected_debug_log_count = 2
    args = Namespace(dry_run=True, ignore=[])
    pyclean.main.Runner.configure(args)

    pyclean.main.Runner.unlink(Path('tmp'))
    pyclean.main.Runner.rmdir(Path('tmp'))

    assert mock_log.debug.call_count == expected_debug_log_count
    assert 'Would delete file:' in str(mock_log.debug.call_args_list[0])
    assert 'Would delete directory:' in str(mock_log.debug.call_args_list[1])


@patch('pyclean.runner.print_dirname')
@patch('pyclean.runner.print_filename')
@patch('pyclean.runner.remove_directory')
@patch('pyclean.runner.remove_file')
def test_delete(
    mock_real_unlink,
    mock_real_rmdir,
    mock_dry_unlink,
    mock_dry_rmdir,
):
    with ArgvContext('pyclean', '.'):
        pyclean.cli.main()

    assert mock_real_unlink.called
    assert mock_real_rmdir.called
    assert not mock_dry_unlink.called
    assert not mock_dry_rmdir.called


@patch('pyclean.runner.print_dirname')
@patch('pyclean.runner.print_filename')
@patch('pyclean.runner.remove_directory')
@patch('pyclean.runner.remove_file')
def test_dryrun(
    mock_real_unlink,
    mock_real_rmdir,
    mock_dry_unlink,
    mock_dry_rmdir,
):
    with ArgvContext('pyclean', '.', '--dry-run'):
        pyclean.cli.main()

    assert not mock_real_unlink.called
    assert not mock_real_rmdir.called
    assert mock_dry_unlink.called
    assert mock_dry_rmdir.called


def test_is_ignored_for_dir_itself():
    """
    Does Runner.is_ignored return True for an ignored directory itself?
    """
    pyclean.main.Runner.ignore = ['allure-results']
    assert pyclean.main.Runner.is_ignored(Path('allure-results'))


def test_is_ignored_for_file_in_ignored_dir():
    """
    Does Runner.is_ignored return True for a file inside an ignored directory?
    """
    pyclean.main.Runner.ignore = ['allure-results']
    assert pyclean.main.Runner.is_ignored(Path('allure-results/foo.txt'))


def test_is_ignored_for_nested_path_in_ignored_dir():
    """
    Does Runner.is_ignored return True for a deeply nested path inside an ignored
    directory?
    """
    pyclean.main.Runner.ignore = ['allure-results']
    assert pyclean.main.Runner.is_ignored(Path('allure-results/sub/deep/file.txt'))


def test_is_not_ignored_for_unrelated_path():
    """
    Does Runner.is_ignored return False for a path not matching any ignore pattern?
    """
    pyclean.main.Runner.ignore = ['allure-results']
    assert not pyclean.main.Runner.is_ignored(Path('keep.txt'))
    assert not pyclean.main.Runner.is_ignored(Path('other/foo.txt'))
