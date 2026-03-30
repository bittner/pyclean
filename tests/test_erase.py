# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the erase module."""

from argparse import Namespace
from pathlib import Path
from unittest.mock import call, patch

import pytest
from cli_test_helpers import ArgvContext
from conftest import DirectoryMock, FileMock, SymlinkMock

import pyclean.cli
import pyclean.main
from pyclean.erase import (
    confirm,
    delete_filesystem_objects,
    remove_freeform_targets,
)


@patch('pyclean.main.remove_freeform_targets')
@patch('pyclean.main.remove_debris_for')
@patch('pyclean.main.descend_and_clean')
def test_erase_option(mock_descend, mock_debris, mock_erase):
    """
    Does ``--erase`` execute the appropriate cleanup code?
    """
    with ArgvContext('pyclean', '.', '--erase', 'tmp/**/*', 'tmp/'):
        pyclean.cli.main()

    erase_calls = [call_args[0][1] for call_args in mock_erase.call_args_list]

    assert mock_descend.called
    assert not mock_debris.called
    assert erase_calls == [['tmp/**/*', 'tmp/']]


@patch('pyclean.erase.delete_filesystem_objects')
def test_erase_loop(mock_delete_fs_obj):
    """
    Does ``remove_freeform_targets()`` call filesystem object removal?
    """
    patterns = ['foo.txt']
    directory = Path()

    remove_freeform_targets(directory, patterns, yes=False, dry_run=False)

    assert mock_delete_fs_obj.mock_calls == [
        call(directory, 'foo.txt', prompt=True, dry_run=False),
    ]


@patch('pyclean.runner.remove_directory')
@patch('pyclean.runner.remove_file')
@patch('builtins.input', return_value='y')
@patch(
    'pathlib.Path.glob',
    return_value=[
        DirectoryMock(),
        SymlinkMock(),
        FileMock(),
    ],
)
def test_delete_filesdir_loop(mock_glob, mock_yes, mock_unlink, mock_rmdir):
    """
    Exercise the file and directory loop code.
    """
    args = Namespace(dry_run=False, ignore=[])
    directory = Path()

    pyclean.main.Runner.configure(args)
    delete_filesystem_objects(directory, 'tmp/**/*', prompt=True)

    assert mock_glob.called
    assert mock_yes.called
    assert mock_unlink.called
    assert mock_rmdir.called

    assert mock_unlink.call_args_list == [
        call(SymlinkMock()),
        call(FileMock()),
    ]
    assert mock_rmdir.call_args_list == [
        call(DirectoryMock()),
    ]


@patch('pyclean.runner.remove_directory')
@patch('pyclean.runner.remove_file')
@patch('builtins.input', return_value='n')
@patch(
    'pathlib.Path.glob',
    return_value=[DirectoryMock(), SymlinkMock(), FileMock()],
)
def test_no_skips_deletion(mock_glob, mock_no, mock_unlink, mock_rmdir):
    """
    Is deletion skipped with --erase when user says "no" at the prompt?
    """
    args = Namespace(dry_run=False, ignore=[])
    pyclean.main.Runner.configure(args)
    directory = Path()

    assert pyclean.main.Runner.unlink_failed == 0
    assert pyclean.main.Runner.rmdir_failed == 0

    delete_filesystem_objects(directory, 'tmp/**/*', prompt=True)

    assert mock_glob.called
    assert mock_no.called
    assert not mock_unlink.called
    assert not mock_rmdir.called
    assert pyclean.main.Runner.unlink_failed > 0
    assert pyclean.main.Runner.rmdir_failed > 0


@patch('pyclean.runner.remove_directory')
@patch('pyclean.runner.remove_file')
@patch(
    'pathlib.Path.glob',
    return_value=[DirectoryMock(), SymlinkMock(), FileMock()],
)
@patch('pyclean.main.remove_debris_for')
@patch('pyclean.main.descend_and_clean')
def test_yes_skips_prompt(
    mock_descend,
    mock_debris,
    mock_glob,
    mock_unlink,
    mock_rmdir,
):
    """
    Does --yes skip the confirmation prompt for --erase?
    """
    with ArgvContext('pyclean', '.', '--erase', 'tmp/*', '--yes'):
        pyclean.cli.main()

    assert mock_glob.called
    assert mock_unlink.mock_calls == [
        call(SymlinkMock()),
        call(FileMock()),
    ]
    assert mock_rmdir.mock_calls == [
        call(DirectoryMock()),
    ]


@patch('builtins.input', side_effect=KeyboardInterrupt)
def test_abort_confirm(mock_input):
    """
    Does the CLI abort cleanly when user presses Ctrl+C on the keyboard?
    """
    with pytest.raises(SystemExit, match=r'^Aborted by user.$'):
        confirm('Abort execution')


@patch('pyclean.runner.print_dirname')
@patch('pyclean.runner.print_filename')
@patch('builtins.input')
@patch('pathlib.Path.glob', return_value=[DirectoryMock(), FileMock()])
def test_dryrun_no_prompt(mock_glob, mock_input, mock_print_file, mock_print_dir):
    """
    Does --dry-run skip the confirmation prompt for --erase?
    This test verifies the fix for the issue where prompts were shown
    even with --dry-run.
    """
    args = Namespace(dry_run=True, ignore=[])
    pyclean.main.Runner.configure(args)
    directory = Path()

    delete_filesystem_objects(directory, 'tmp/**/*', prompt=True, dry_run=True)

    assert mock_glob.called
    # input() should NOT be called with dry_run=True
    assert not mock_input.called
    # But the print functions should be called (since it's a dry run)
    assert mock_print_file.called
    assert mock_print_dir.called


@patch('pyclean.runner.remove_directory')
@patch('pyclean.runner.remove_file')
@patch('builtins.input', return_value='y')
@patch('pathlib.Path.glob', return_value=[DirectoryMock(), FileMock()])
def test_no_dryrun_with_prompt(mock_glob, mock_input, mock_unlink, mock_rmdir):
    """
    Does non-dry-run mode show prompts when expected?
    This test ensures the fix doesn't break normal prompt behavior.
    """
    args = Namespace(dry_run=False, ignore=[])
    pyclean.main.Runner.configure(args)
    directory = Path()

    delete_filesystem_objects(directory, 'tmp/**/*', prompt=True, dry_run=False)

    assert mock_glob.called
    # input() SHOULD be called with dry_run=False and prompt=True
    assert mock_input.called
    # The real deletion functions should be called (not dry-run)
    assert mock_unlink.called
    assert mock_rmdir.called


@patch('builtins.input', return_value='yes')
def test_confirm_yes(mock_input):
    """
    Does confirm return True for 'yes' answer?
    """
    assert confirm('Test message') is True


@patch('builtins.input', return_value='no')
def test_confirm_no(mock_input):
    """
    Does confirm return False for 'no' answer?
    """
    assert confirm('Test message') is False


def test_path_is_ignored_for_dir_itself():
    """
    Does Runner.is_ignored return True for an ignored directory itself?
    """
    pyclean.main.Runner.ignore = ['allure-results']
    assert pyclean.main.Runner.is_ignored(Path('allure-results'))


def test_path_is_ignored_for_file_in_ignored_dir():
    """
    Does Runner.is_ignored return True for a file inside an ignored directory?
    """
    pyclean.main.Runner.ignore = ['allure-results']
    assert pyclean.main.Runner.is_ignored(Path('allure-results/foo.txt'))


def test_path_is_ignored_for_nested_path_in_ignored_dir():
    """
    Does Runner.is_ignored return True for a deeply nested path inside an ignored
    directory?
    """
    pyclean.main.Runner.ignore = ['allure-results']
    assert pyclean.main.Runner.is_ignored(Path('allure-results/sub/deep/file.txt'))


def test_path_is_not_ignored_for_unrelated_path():
    """
    Does Runner.is_ignored return False for a path not matching any ignore pattern?
    """
    pyclean.main.Runner.ignore = ['allure-results']
    assert not pyclean.main.Runner.is_ignored(Path('keep.txt'))
    assert not pyclean.main.Runner.is_ignored(Path('other/foo.txt'))


def test_delete_filesystem_objects_skips_ignored_dirs(tmp_path):
    """
    Does delete_filesystem_objects skip files and directories in ignored paths?
    """
    ignored_dir = tmp_path / 'allure-results'
    ignored_dir.mkdir()
    ignored_file = ignored_dir / 'foo.txt'
    ignored_file.write_text('test')

    args = Namespace(dry_run=False, ignore=['allure-results'])
    pyclean.main.Runner.configure(args)

    delete_filesystem_objects(tmp_path, 'allure-results/**/*', prompt=False)

    assert ignored_file.exists(), 'File in ignored directory should not be deleted'


def test_delete_filesystem_objects_erases_non_ignored(tmp_path):
    """
    Does delete_filesystem_objects still erase non-ignored paths when ignore is set?
    """
    ignored_dir = tmp_path / 'allure-results'
    ignored_dir.mkdir()
    ignored_file = ignored_dir / 'foo.txt'
    ignored_file.write_text('test')
    non_ignored_file1 = tmp_path / 'keep.txt'
    non_ignored_file1.write_text('keep')
    non_ignored_file2 = tmp_path / 'erase.txt'
    non_ignored_file2.write_text('erase')

    args = Namespace(dry_run=False, ignore=['allure-results'])
    pyclean.main.Runner.configure(args)

    delete_filesystem_objects(tmp_path, '*.txt', prompt=False)

    assert ignored_file.exists(), 'File in ignored directory should not be deleted'
    assert not non_ignored_file1.exists(), 'Non-ignored file should be deleted'
    assert not non_ignored_file2.exists(), 'Non-ignored file should be deleted'
