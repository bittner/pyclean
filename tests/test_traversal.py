# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the traversal module."""

import platform
from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, call, patch

import pytest
from conftest import SymlinkMock

import pyclean.main
from pyclean.bytecode import BYTECODE_DIRS, BYTECODE_FILES
from pyclean.traversal import descend_and_clean, normalize, should_ignore


@patch('pyclean.traversal.log')
@patch('os.scandir', return_value=[SymlinkMock()])
def test_ignore_otherobjects(mock_scandir, mock_log):
    pyclean.main.Runner.unlink = Mock()
    pyclean.main.Runner.rmdir = Mock()

    descend_and_clean(Path(), BYTECODE_FILES, BYTECODE_DIRS)

    assert not pyclean.main.Runner.unlink.called
    assert not pyclean.main.Runner.rmdir.called
    assert mock_log.mock_calls == [
        call.debug('Ignoring %s (neither a file nor a folder)', 'a-symlink'),
    ]


@pytest.mark.parametrize(
    ('path_str', 'patterns', 'expected'),
    [
        # Simple name matches
        ('foo/bar', ['bar'], True),
        ('foo/baz/bar', ['bar'], True),
        ('bar', ['bar'], True),
        ('foo/bar', ['baz'], False),
        # Path matches
        ('foo/bar', ['foo/bar'], True),
        ('baz/foo/bar', ['foo/bar'], True),
        ('test/foo/bar', ['foo/bar'], True),
        ('foo/bar/baz', ['foo/bar'], True),  # Subdirectories are also ignored
        ('bar/foo', ['foo/bar'], False),
        ('foo/baz', ['foo/bar'], False),
        # Multiple patterns
        ('foo/bar', ['baz', 'bar'], True),
        ('foo/bar', ['baz', 'foo/bar'], True),
        ('foo/bar', ['test', 'data'], False),
        # Edge cases
        ('bar', ['foo/bar'], False),
        ('foo', ['foo/bar'], False),
        # Pattern longer than path
        ('baz', ['foo/bar/baz'], False),
        ('bar/baz', ['foo/bar/baz'], False),
        # None/empty patterns
        ('foo/bar', None, False),
        ('foo/bar', [], False),
        # Subdirectories of ignored paths
        ('foo/bar/baz/deep', ['foo/bar'], True),
        ('src/foo/bar/models', ['foo/bar'], True),
        ('foo/bar/baz', ['foo/bar/baz'], True),
    ],
)
def test_should_ignore(path_str, patterns, expected):
    """
    Does should_ignore correctly match path patterns?
    """
    path = Path(path_str)
    result = should_ignore(path, patterns)
    assert result == expected


@pytest.mark.skipif(platform.system() != 'Windows', reason='Windows-specific test')
@pytest.mark.parametrize(
    ('path_str', 'patterns', 'expected'),
    [
        # Windows-style pattern (backslash) matching filesystem paths
        ('foo/bar', [r'foo\bar'], True),
        ('foo/bar/baz', [r'foo\bar'], True),
        ('src/foo/bar', [r'foo\bar'], True),
    ],
)
def test_should_ignore_windows_paths(path_str, patterns, expected):
    """
    Does should_ignore correctly handle Windows-style backslash patterns?
    This test only runs on Windows where backslash is a path separator.
    """
    path = Path(path_str)
    result = should_ignore(path, patterns)
    assert result == expected


@pytest.mark.skipif(
    platform.system() not in ['Linux', 'Darwin'],
    reason='Unix-specific test',
)
def test_normalize_pattern_posix():
    """
    Does normalize preserve patterns on Unix?
    On Unix, backslash can be part of a filename.
    """
    assert normalize('foo/bar') == 'foo/bar'
    assert normalize(r'foo\bar') == r'foo\bar'  # Preserved on Linux and macOS
    assert normalize('bar') == 'bar'


@pytest.mark.skipif(platform.system() != 'Windows', reason='Windows-specific test')
def test_normalize_pattern_windows():
    """
    Does normalize convert backslashes to forward slashes on Windows?
    """
    assert normalize('foo/bar') == 'foo/bar'
    assert normalize(r'foo\bar') == 'foo/bar'  # Normalized
    assert normalize('bar') == 'bar'


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
