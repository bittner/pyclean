# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the ignore module."""

import platform

import pytest

from pyclean.ignore import normalize, should_ignore


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
    result = should_ignore(path_str, patterns)
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
    result = should_ignore(path_str, patterns)
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
