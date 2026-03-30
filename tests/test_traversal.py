# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the traversal module."""

from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import call, patch

from conftest import SymlinkMock

import pyclean.main
from pyclean.bytecode import BYTECODE_DIRS, BYTECODE_FILES
from pyclean.traversal import descend_and_clean


@patch('pyclean.main.Runner.unlink')
@patch('pyclean.main.Runner.rmdir')
@patch('pyclean.traversal.log')
@patch('os.scandir', return_value=[SymlinkMock()])
def test_ignore_otherobjects(mock_scandir, mock_log, mock_rmdir, mock_unlink):
    """
    Does descend_and_clean log unidentified file objects in verbose mode?
    """
    expected_filename = SymlinkMock().path

    descend_and_clean(Path(), BYTECODE_FILES, BYTECODE_DIRS)

    assert not mock_unlink.called
    assert not mock_rmdir.called
    assert mock_log.mock_calls == [
        call.debug('Ignoring %s (neither a file nor a folder)', expected_filename),
    ]


@patch('pyclean.traversal.log')
def test_skip_ignored_directories(mock_log):
    """
    Does descend_and_clean log skipped directories correctly?
    This ensures verbose output shows path strings, not DirEntry objects.
    """
    args = Namespace(dry_run=True, ignore=['.git'])
    pyclean.main.Runner.configure(args)

    # Our project directory contains the .git folder
    directory = Path(__file__).parent.parent

    descend_and_clean(directory, BYTECODE_FILES, BYTECODE_DIRS)

    mock_log.debug.assert_called_with('Skipping %s', '.git')


def test_ignore_with_simple_name():
    """
    Does --ignore with a simple name match directories anywhere?
    """
    args = Namespace(dry_run=False, ignore=['bar'])
    pyclean.main.Runner.configure(args)

    with TemporaryDirectory() as tmp:
        directory = Path(tmp)

        # Create structure: foo/bar/test.pyc and baz/bar/test.pyc
        (directory / 'foo' / 'bar').mkdir(parents=True)
        (directory / 'baz' / 'bar').mkdir(parents=True)
        (directory / 'foo' / 'bar' / 'test.pyc').write_text('test')
        (directory / 'baz' / 'bar' / 'test.pyc').write_text('test')

        descend_and_clean(directory, BYTECODE_FILES, BYTECODE_DIRS)

        # Both bar directories should be ignored
        assert (directory / 'foo' / 'bar' / 'test.pyc').exists()
        assert (directory / 'baz' / 'bar' / 'test.pyc').exists()


def test_ignore_with_path_pattern():
    """
    Does --ignore with a path pattern match specific paths?
    """
    args = Namespace(dry_run=False, ignore=['foo/bar'])
    pyclean.main.Runner.configure(args)

    with TemporaryDirectory() as tmp:
        directory = Path(tmp)

        # Create structure: foo/bar/test.pyc and baz/bar/test.pyc
        (directory / 'foo' / 'bar').mkdir(parents=True)
        (directory / 'baz' / 'bar').mkdir(parents=True)
        (directory / 'foo' / 'bar' / 'test.pyc').write_text('test')
        (directory / 'baz' / 'bar' / 'test.pyc').write_text('test')

        descend_and_clean(directory, BYTECODE_FILES, BYTECODE_DIRS)

        # Only foo/bar should be ignored, baz/bar should be cleaned
        assert (directory / 'foo' / 'bar' / 'test.pyc').exists()
        assert not (directory / 'baz' / 'bar' / 'test.pyc').exists()
