# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the debris module."""

from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import call, patch

import pytest
from cli_test_helpers import ArgvContext

import pyclean.cli
import pyclean.main
import pyclean.traversal
from pyclean.debris import (
    DEBRIS_TOPICS,
    detect_debris_in_directory,
    recursive_delete_debris,
    remove_debris_for,
)


@pytest.mark.parametrize(
    ('options', 'scanned_topics'),
    [
        ([], []),
        (['-d'], ['cache', 'coverage', 'package', 'pytest', 'ruff']),
        (['-d', 'coverage', 'package'], ['coverage', 'package']),
        (['-d', 'jupyter', 'mypy', 'tox'], ['jupyter', 'mypy', 'tox']),
    ],
)
@patch('pyclean.main.remove_freeform_targets')
@patch('pyclean.main.remove_debris_for')
@patch('pyclean.main.descend_and_clean')
def test_debris_option(mock_descend, mock_debris, mock_erase, options, scanned_topics):
    """
    Does ``--debris`` execute the appropriate cleanup code?
    """
    with ArgvContext('pyclean', '.', *options):
        pyclean.cli.main()

    debris_calls = [call_args[0][0] for call_args in mock_debris.call_args_list]

    assert mock_descend.called
    assert debris_calls == scanned_topics
    assert mock_erase.called


@pytest.mark.parametrize(
    'debris_topic',
    [
        'cache',
        'coverage',
        'package',
        'pytest',
        'jupyter',
        'mypy',
        'ruff',
        'tox',
    ],
)
@patch('pyclean.debris.recursive_delete_debris')
def test_debris_loop(mock_recursive_delete_debris, debris_topic):
    """
    Does ``remove_debris_for()`` call debris cleanup with all patterns?
    """
    fileobject_globs = DEBRIS_TOPICS[debris_topic]
    directory = Path()

    remove_debris_for(debris_topic, directory)

    # Should call recursive_delete_debris once with all patterns
    assert mock_recursive_delete_debris.call_count == 1
    assert mock_recursive_delete_debris.call_args == call(directory, fileobject_globs)


def test_debris_recursive():
    """
    Does ``delete_filesystem_objects`` walk through the folder hierarchy
    when deleting debris?
    """
    topic = 'cache'
    topic_globs = DEBRIS_TOPICS[topic]
    topic_folder = topic_globs[1]

    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        dir_topic = directory / topic_folder
        dir_topic.mkdir()
        dir_nested_topic = directory / 'nested' / topic_folder
        dir_nested_topic.mkdir(parents=True)

        assert dir_nested_topic.exists()
        assert dir_topic.exists()

        remove_debris_for(topic, directory)

        assert not dir_topic.exists()
        assert not dir_nested_topic.exists()
        assert dir_nested_topic.parent.exists()


def test_detect_debris_in_directory():
    """
    Does ``detect_debris_in_directory()`` identify debris artifacts?
    """
    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        # Create some debris artifacts
        build_dir = directory / 'build'
        build_dir.mkdir()
        cache_dir = directory / '.cache'
        cache_dir.mkdir()
        (directory / '.coverage').touch()

        detected = detect_debris_in_directory(directory)

        # Should detect cache, coverage, and package topics
        assert 'cache' in detected
        assert 'coverage' in detected
        assert 'package' in detected
        # Should not detect pytest (no pytest artifacts created)
        assert 'pytest' not in detected


def test_detect_no_debris_in_directory():
    """
    Does ``detect_debris_in_directory()`` return empty list when no debris?
    """
    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        # Create only non-debris files
        (directory / 'test.py').touch()
        (directory / 'README.md').touch()

        detected = detect_debris_in_directory(directory)

        assert detected == []


@patch('pyclean.debris.log')
@patch('pyclean.main.descend_and_clean')
def test_suggest_debris_without_artifacts(mock_descend, mock_log):
    """
    Does pyclean suggest --debris when executed without it and no artifacts present?
    """
    with TemporaryDirectory() as tmp, ArgvContext('pyclean', tmp):
        pyclean.cli.main()

    # Check that the suggestion was logged
    log_info_calls = [str(call) for call in mock_log.info.call_args_list]
    assert any('Hint: Use --debris' in msg for msg in log_info_calls)
    assert any('common Python development tools' in msg for msg in log_info_calls)


@patch('pyclean.debris.log')
@patch('pyclean.main.descend_and_clean')
def test_suggest_debris_with_artifacts(mock_descend, mock_log):
    """
    Does pyclean suggest specific --debris topics when artifacts are detected?
    """
    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        # Create some debris
        (directory / 'build').mkdir()
        (directory / '.pytest_cache').mkdir()

        with ArgvContext('pyclean', tmp):
            pyclean.cli.main()

    # Check that the suggestion was logged with detected topics
    log_info_calls = [str(call) for call in mock_log.info.call_args_list]
    assert any('Hint: Use --debris' in msg for msg in log_info_calls)
    assert any('Detected:' in msg for msg in log_info_calls)


@patch('pyclean.debris.log')
@patch('pyclean.main.descend_and_clean')
def test_no_suggest_debris_when_used(mock_descend, mock_log):
    """
    Does pyclean NOT suggest --debris when it's already used?
    """
    with TemporaryDirectory() as tmp, ArgvContext('pyclean', tmp, '--debris'):
        pyclean.cli.main()

    # Check that the suggestion was NOT logged
    log_info_calls = [str(call) for call in mock_log.info.call_args_list]
    assert not any('Hint: Use --debris' in msg for msg in log_info_calls)


def test_ignore_with_debris_cleanup():
    """
    Does --ignore work correctly during debris cleanup?
    """
    args = Namespace(dry_run=False, ignore=['foo'])
    pyclean.main.Runner.configure(args)

    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        # Create .cache directories in different locations
        (directory / '.cache').mkdir()
        (directory / 'foo' / '.cache').mkdir(parents=True)
        (directory / '.cache' / 'test.txt').write_text('test')
        (directory / 'foo' / '.cache' / 'test.txt').write_text('test')

        remove_debris_for('cache', directory)

        # Root .cache should be removed, foo/.cache should remain
        assert not (directory / '.cache').exists()
        assert (directory / 'foo' / '.cache').exists()
        assert (directory / 'foo' / '.cache' / 'test.txt').exists()


def test_debris_cleanup_scans_directories_once():
    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        (directory / '.git').mkdir()
        (directory / 'subdir1').mkdir()
        (directory / 'subdir2').mkdir()

        original_should_ignore = pyclean.traversal.should_ignore
        call_count = {'total': 0, 'git_checks': 0}

        def counting_should_ignore(path, patterns):
            call_count['total'] += 1
            if path.name == '.git':
                call_count['git_checks'] += 1
            return original_should_ignore(path, patterns)

        args = Namespace(dry_run=False, ignore=['.git'])
        pyclean.main.Runner.configure(args)

        with patch('pyclean.debris.should_ignore', side_effect=counting_should_ignore):
            remove_debris_for('cache', directory)

        assert call_count['git_checks'] == 1, (
            f'Expected 1 check for .git directory, but got {call_count["git_checks"]}'
        )


@pytest.mark.parametrize(
    ('system_error'),
    [
        PermissionError('Permission denied'),
        OSError('I/O error'),
    ],
)
@patch('pyclean.debris.log')
def test_recursive_delete_debris_error(mock_log, system_error):
    args = Namespace(dry_run=False, ignore=[])
    pyclean.main.Runner.configure(args)

    directory = Path('/nonexistent/test/directory')
    patterns = ['.cache/**/*', '.cache/']

    with patch('os.scandir', side_effect=system_error) as mock_scandir:
        recursive_delete_debris(directory, patterns)

    mock_log.warning.assert_called_once_with(
        'Cannot access directory %s: %s',
        directory,
        mock_scandir.side_effect,
    )
