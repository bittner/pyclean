# SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tests for the modern module
"""

import logging
import platform
from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, call, patch

import pytest
from cli_test_helpers import ArgvContext
from conftest import DirectoryMock, FileMock, SymlinkMock

import pyclean.cli
import pyclean.modern
from pyclean.modern import (
    delete_filesystem_objects,
    normalize,
    remove_debris_for,
    remove_directory,
    remove_file,
    remove_freeform_targets,
    should_ignore,
)


@patch('pyclean.modern.descend_and_clean')
def test_walks_tree(mock_descend):
    """
    Does pyclean walk the directory tree?
    """
    with ArgvContext('pyclean', '.'):
        pyclean.cli.main()

    assert mock_descend.mock_calls == [
        call(Path(), ['.pyc', '.pyo'], ['__pycache__']),
    ]


@patch('pyclean.modern.descend_and_clean')
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


@patch.object(pyclean.modern.logging, 'basicConfig')
@patch('pyclean.modern.descend_and_clean')
def test_normal_logging(mock_descend, mock_logconfig):
    """
    Does a normal run use log level INFO?
    """
    with ArgvContext('pyclean', '.'):
        pyclean.cli.main()

    assert mock_logconfig.mock_calls == [
        call(format='%(message)s', level=logging.INFO),
    ]


@patch.object(pyclean.modern.logging, 'basicConfig')
@patch('pyclean.modern.descend_and_clean')
def test_verbose_logging(mock_descend, mock_logconfig):
    """
    Does --verbose use log level DEBUG?
    """
    with ArgvContext('pyclean', '.', '--verbose'):
        pyclean.cli.main()

    assert mock_logconfig.mock_calls == [
        call(format='%(message)s', level=logging.DEBUG),
    ]


@patch.object(pyclean.modern.logging, 'basicConfig')
@patch('pyclean.modern.descend_and_clean')
def test_quiet_logging(mock_descend, mock_logconfig):
    """
    Does --quiet use log level FATAL?
    """
    with ArgvContext('pyclean', '.', '--quiet'):
        pyclean.cli.main()

    assert mock_logconfig.mock_calls == [
        call(format='%(message)s', level=logging.FATAL),
    ]


@patch('pathlib.Path.iterdir', return_value=[SymlinkMock()])
def test_ignore_otherobjects(mock_iterdir):
    """
    Is "ignoring" displayed for any uncommon file system object?
    """
    pyclean.modern.Runner.unlink = Mock()
    pyclean.modern.Runner.rmdir = Mock()
    pyclean.modern.log = Mock()

    pyclean.modern.descend_and_clean(
        Path(),
        pyclean.modern.BYTECODE_FILES,
        pyclean.modern.BYTECODE_DIRS,
    )

    assert not pyclean.modern.Runner.unlink.called
    assert not pyclean.modern.Runner.rmdir.called
    assert pyclean.modern.log.mock_calls == [
        call.debug('Ignoring %s (neither a file nor a folder)', SymlinkMock()),
    ]


@pytest.mark.parametrize(
    ('unlink_failures', 'rmdir_failures'),
    [
        (7, 0),
        (0, 3),
        (1, 1),
    ],
)
def test_report_failures(unlink_failures, rmdir_failures):
    """
    Are failures to delete a file or folder reported with ``log.debug``?
    """
    args = Namespace(
        debris=[],
        directory=[],
        dry_run=True,
        erase=[],
        ignore=[],
        yes=False,
    )
    pyclean.modern.Runner.configure(args)
    pyclean.modern.Runner.unlink_failed = unlink_failures
    pyclean.modern.Runner.rmdir_failed = rmdir_failures
    pyclean.modern.log = Mock()

    with patch('pyclean.modern.CleanupRunner.configure'):
        pyclean.modern.pyclean(args)

    pyclean.modern.log.debug.assert_called_with(
        '%d files, %d directories %s not be removed.',
        unlink_failures,
        rmdir_failures,
        'would',
    )


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


@patch('pyclean.modern.log')
@patch('pathlib.Path.unlink', side_effect=OSError)
def test_unlink_failure(mock_unlink, mock_log):
    """
    Is a deletion error caught and logged?
    """
    args = Namespace(dry_run=False, ignore=[])
    pyclean.modern.Runner.configure(args)

    remove_file(Path('tmp'))

    mock_log.debug.assert_called()
    assert 'File not deleted.' in str(mock_log.debug.call_args)


@patch('pyclean.modern.log')
@patch('pathlib.Path.rmdir', side_effect=OSError)
def test_rmdir_failure(mock_rmdir, mock_log):
    """
    Is a deletion error caught and logged?
    """
    args = Namespace(dry_run=False, ignore=[])
    pyclean.modern.Runner.configure(args)

    remove_directory(Path('tmp'))

    mock_log.debug.assert_called()
    assert 'Directory not removed.' in str(mock_log.debug.call_args)


@patch('pyclean.modern.log')
def test_dryrun_output(mock_log):
    """
    Do we explain what would be done, when --dry-run is used?
    """
    expected_debug_log_count = 2
    args = Namespace(dry_run=True, ignore=[])

    pyclean.modern.Runner.configure(args)
    pyclean.modern.Runner.unlink(Path('tmp'))
    pyclean.modern.Runner.rmdir(Path('tmp'))

    assert mock_log.debug.call_count == expected_debug_log_count
    assert 'Would delete file:' in str(mock_log.debug.call_args_list[0])
    assert 'Would delete directory:' in str(mock_log.debug.call_args_list[1])


@patch('pyclean.modern.print_dirname')
@patch('pyclean.modern.print_filename')
@patch('pyclean.modern.remove_directory')
@patch('pyclean.modern.remove_file')
def test_delete(
    mock_real_unlink,
    mock_real_rmdir,
    mock_dry_unlink,
    mock_dry_rmdir,
):
    """
    Is actual deletion attempted w/o --dry-run?
    """
    with ArgvContext('pyclean', '.'):
        pyclean.cli.main()

    assert mock_real_unlink.called
    assert mock_real_rmdir.called
    assert not mock_dry_unlink.called
    assert not mock_dry_rmdir.called


@patch('pyclean.modern.print_dirname')
@patch('pyclean.modern.print_filename')
@patch('pyclean.modern.remove_directory')
@patch('pyclean.modern.remove_file')
def test_dryrun(
    mock_real_unlink,
    mock_real_rmdir,
    mock_dry_unlink,
    mock_dry_rmdir,
):
    """
    Does --dry-run option avoid real deletion?
    """
    with ArgvContext('pyclean', '.', '--dry-run'):
        pyclean.cli.main()

    assert not mock_real_unlink.called
    assert not mock_real_rmdir.called
    assert mock_dry_unlink.called
    assert mock_dry_rmdir.called


@pytest.mark.parametrize(
    ('options', 'scanned_topics'),
    [
        ([], []),
        (['-d'], ['cache', 'coverage', 'package', 'pytest', 'ruff']),
        (['-d', 'coverage', 'package'], ['coverage', 'package']),
        (['-d', 'jupyter', 'mypy', 'tox'], ['jupyter', 'mypy', 'tox']),
    ],
)
@patch('pyclean.modern.remove_freeform_targets')
@patch('pyclean.modern.remove_debris_for')
@patch('pyclean.modern.descend_and_clean')
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


@patch('pyclean.modern.remove_freeform_targets')
@patch('pyclean.modern.remove_debris_for')
@patch('pyclean.modern.descend_and_clean')
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
@patch('pyclean.modern.recursive_delete_debris')
def test_debris_loop(mock_recursive_delete_debris, debris_topic):
    """
    Does ``remove_debris_for()`` call debris cleanup with all patterns?
    """
    fileobject_globs = pyclean.modern.DEBRIS_TOPICS[debris_topic]
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
    topic_globs = pyclean.modern.DEBRIS_TOPICS[topic]
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


@patch('pyclean.modern.delete_filesystem_objects')
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


@patch('pyclean.modern.remove_directory')
@patch('pyclean.modern.remove_file')
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

    pyclean.modern.Runner.configure(args)
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


@patch('pyclean.modern.remove_directory')
@patch('pyclean.modern.remove_file')
@patch('builtins.input', return_value='n')
@patch(
    'pathlib.Path.glob',
    return_value=[
        DirectoryMock(),
        SymlinkMock(),
        FileMock(),
    ],
)
def test_no_skips_deletion(mock_glob, mock_no, mock_unlink, mock_rmdir):
    """
    Is deletion skipped with --erase when user says "no" at the prompt?
    """
    args = Namespace(dry_run=False, ignore=[])
    directory = Path()

    pyclean.modern.Runner.configure(args)

    assert pyclean.modern.Runner.unlink_failed == 0
    assert pyclean.modern.Runner.rmdir_failed == 0

    delete_filesystem_objects(directory, 'tmp/**/*', prompt=True)

    assert mock_glob.called
    assert mock_no.called
    assert not mock_unlink.called
    assert not mock_rmdir.called
    assert pyclean.modern.Runner.unlink_failed > 0
    assert pyclean.modern.Runner.rmdir_failed > 0


@patch('pyclean.modern.remove_directory')
@patch('pyclean.modern.remove_file')
@patch(
    'pathlib.Path.glob',
    return_value=[
        DirectoryMock(),
        SymlinkMock(),
        FileMock(),
    ],
)
@patch('pyclean.modern.remove_debris_for')
@patch('pyclean.modern.descend_and_clean')
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
        pyclean.modern.confirm('Abort execution')


@patch('pyclean.modern.print_dirname')
@patch('pyclean.modern.print_filename')
@patch('builtins.input')
@patch('pathlib.Path.glob', return_value=[DirectoryMock(), FileMock()])
def test_dryrun_no_prompt(mock_glob, mock_input, mock_print_file, mock_print_dir):
    """
    Does --dry-run skip the confirmation prompt for --erase?
    This test verifies the fix for the issue where prompts were shown
    even with --dry-run.
    """
    args = Namespace(dry_run=True, ignore=[])
    directory = Path()

    pyclean.modern.Runner.configure(args)
    delete_filesystem_objects(directory, 'tmp/**/*', prompt=True, dry_run=True)

    assert mock_glob.called
    # input() should NOT be called with dry_run=True
    assert not mock_input.called
    # But the print functions should be called (since it's a dry run)
    assert mock_print_file.called
    assert mock_print_dir.called


@patch('pyclean.modern.remove_directory')
@patch('pyclean.modern.remove_file')
@patch('builtins.input', return_value='y')
@patch('pathlib.Path.glob', return_value=[DirectoryMock(), FileMock()])
def test_no_dryrun_with_prompt(mock_glob, mock_input, mock_unlink, mock_rmdir):
    """
    Does non-dry-run mode show prompts when expected?
    This test ensures the fix doesn't break normal prompt behavior.
    """
    args = Namespace(dry_run=False, ignore=[])
    directory = Path()

    pyclean.modern.Runner.configure(args)
    delete_filesystem_objects(directory, 'tmp/**/*', prompt=True, dry_run=False)

    assert mock_glob.called
    # input() SHOULD be called with dry_run=False and prompt=True
    assert mock_input.called
    # The real deletion functions should be called (not dry-run)
    assert mock_unlink.called
    assert mock_rmdir.called


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

        detected = pyclean.modern.detect_debris_in_directory(directory)

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

        detected = pyclean.modern.detect_debris_in_directory(directory)

        assert detected == []


@patch('pyclean.modern.log')
@patch('pyclean.modern.descend_and_clean')
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


@patch('pyclean.modern.log')
@patch('pyclean.modern.descend_and_clean')
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


@patch('pyclean.modern.log')
@patch('pyclean.modern.descend_and_clean')
def test_no_suggest_debris_when_used(mock_descend, mock_log):
    """
    Does pyclean NOT suggest --debris when it's already used?
    """
    with TemporaryDirectory() as tmp, ArgvContext('pyclean', tmp, '--debris'):
        pyclean.cli.main()

    # Check that the suggestion was NOT logged
    log_info_calls = [str(call) for call in mock_log.info.call_args_list]
    assert not any('Hint: Use --debris' in msg for msg in log_info_calls)


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
    with TemporaryDirectory() as tmp:
        directory = Path(tmp)

        # Create structure: foo/bar/test.pyc and baz/bar/test.pyc
        (directory / 'foo' / 'bar').mkdir(parents=True)
        (directory / 'baz' / 'bar').mkdir(parents=True)
        (directory / 'foo' / 'bar' / 'test.pyc').write_text('test')
        (directory / 'baz' / 'bar' / 'test.pyc').write_text('test')

        args = Namespace(dry_run=False, ignore=['bar'])
        pyclean.modern.Runner.configure(args)
        pyclean.modern.descend_and_clean(
            directory,
            pyclean.modern.BYTECODE_FILES,
            pyclean.modern.BYTECODE_DIRS,
        )

        # Both bar directories should be ignored
        assert (directory / 'foo' / 'bar' / 'test.pyc').exists()
        assert (directory / 'baz' / 'bar' / 'test.pyc').exists()


def test_ignore_with_path_pattern():
    """
    Does --ignore with a path pattern match specific paths?
    """
    with TemporaryDirectory() as tmp:
        directory = Path(tmp)

        # Create structure: foo/bar/test.pyc and baz/bar/test.pyc
        (directory / 'foo' / 'bar').mkdir(parents=True)
        (directory / 'baz' / 'bar').mkdir(parents=True)
        (directory / 'foo' / 'bar' / 'test.pyc').write_text('test')
        (directory / 'baz' / 'bar' / 'test.pyc').write_text('test')

        args = Namespace(dry_run=False, ignore=['foo/bar'])
        pyclean.modern.Runner.configure(args)
        pyclean.modern.descend_and_clean(
            directory,
            pyclean.modern.BYTECODE_FILES,
            pyclean.modern.BYTECODE_DIRS,
        )

        # Only foo/bar should be ignored, baz/bar should be cleaned
        assert (directory / 'foo' / 'bar' / 'test.pyc').exists()
        assert not (directory / 'baz' / 'bar' / 'test.pyc').exists()


def test_ignore_with_debris_cleanup():
    """
    Does --ignore work correctly during debris cleanup?
    """
    with TemporaryDirectory() as tmp:
        directory = Path(tmp)

        # Create .cache directories in different locations
        (directory / '.cache').mkdir()
        (directory / 'foo' / '.cache').mkdir(parents=True)
        (directory / '.cache' / 'test.txt').write_text('test')
        (directory / 'foo' / '.cache' / 'test.txt').write_text('test')

        args = Namespace(dry_run=False, ignore=['foo'])
        pyclean.modern.Runner.configure(args)
        pyclean.modern.remove_debris_for('cache', directory)

        # Root .cache should be removed, foo/.cache should remain
        assert not (directory / '.cache').exists()
        assert (directory / 'foo' / '.cache').exists()
        assert (directory / 'foo' / '.cache' / 'test.txt').exists()


def test_debris_cleanup_scans_directories_once():
    """
    Does debris cleanup scan each directory only once per topic,
    rather than once per glob pattern?
    """
    with TemporaryDirectory() as tmp:
        directory = Path(tmp)

        # Create a directory structure with ignored directories
        (directory / '.git').mkdir()
        (directory / 'subdir1').mkdir()
        (directory / 'subdir2').mkdir()

        # Mock the should_ignore function to count calls
        original_should_ignore = pyclean.modern.should_ignore
        call_count = {'total': 0, 'git_checks': 0}

        def counting_should_ignore(path, patterns):
            call_count['total'] += 1
            if path.name == '.git':
                call_count['git_checks'] += 1
            return original_should_ignore(path, patterns)

        args = Namespace(dry_run=False, ignore=['.git'])
        pyclean.modern.Runner.configure(args)

        with patch('pyclean.modern.should_ignore', side_effect=counting_should_ignore):
            # Remove debris for a topic with multiple patterns ('cache' has 2 patterns)
            pyclean.modern.remove_debris_for('cache', directory)

        # Each subdirectory should be checked once per directory traversal,
        # not once per glob pattern
        # With 3 subdirs (.git, subdir1, subdir2), we expect:
        # - 1 check for .git at root level
        # - 1 check for .git inside subdir1
        # - 1 check for .git inside subdir2
        # Total: at most 3 checks for .git (not 6 if it were called for each pattern)
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
@patch('pyclean.modern.log')
def test_recursive_delete_debris_error(mock_log, system_error):
    """
    Does recursive_delete_debris log a warning when directory access fails?
    """
    args = Namespace(dry_run=False, ignore=[])
    pyclean.modern.Runner.configure(args)

    directory = Path('/nonexistent/test/directory')
    patterns = ['.cache/**/*', '.cache/']

    with patch('os.scandir', side_effect=system_error) as mock_scandir:
        pyclean.modern.recursive_delete_debris(directory, patterns)

    mock_log.warning.assert_called_once_with(
        'Cannot access directory %s: %s',
        directory,
        mock_scandir.side_effect,
    )


def test_remove_empty_directories():
    """
    Does remove_empty_directories remove nested empty directories?
    """
    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        (directory / 'empty1' / 'empty2' / 'empty3').mkdir(parents=True)
        (directory / 'nonempty').mkdir()
        (directory / 'nonempty' / 'file.txt').write_text('content')

        args = Namespace(dry_run=False, ignore=[])
        pyclean.modern.Runner.configure(args)
        pyclean.modern.remove_empty_directories(directory)

        assert not (directory / 'empty1').exists()
        assert not (directory / 'empty1' / 'empty2').exists()
        assert not (directory / 'empty1' / 'empty2' / 'empty3').exists()
        assert (directory / 'nonempty').exists()
        assert (directory / 'nonempty' / 'file.txt').exists()


def test_remove_empty_directories_with_ignore():
    """
    Does remove_empty_directories respect ignore patterns?
    """
    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        (directory / 'empty1').mkdir()
        (directory / '.venv' / 'empty2').mkdir(parents=True)

        args = Namespace(dry_run=False, ignore=['.venv'])
        pyclean.modern.Runner.configure(args)
        pyclean.modern.remove_empty_directories(directory)

        assert not (directory / 'empty1').exists()
        assert (directory / '.venv').exists()
        assert (directory / '.venv' / 'empty2').exists()


def test_remove_empty_directories_dry_run():
    """
    Does remove_empty_directories honor dry-run mode?
    """
    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        (directory / 'empty').mkdir()

        args = Namespace(dry_run=True, ignore=[])
        pyclean.modern.Runner.configure(args)
        pyclean.modern.remove_empty_directories(directory)

        assert (directory / 'empty').exists()


@patch('pyclean.modern.remove_empty_directories')
@patch('pyclean.modern.descend_and_clean')
def test_folders_option_calls_remove_empty(mock_descend, mock_remove_empty):
    """
    Does the --folders option trigger empty directory removal?
    """
    with ArgvContext('pyclean', '.', '--folders'):
        pyclean.cli.main()

    assert mock_remove_empty.called


@patch('pyclean.modern.remove_empty_directories')
@patch('pyclean.modern.descend_and_clean')
def test_no_folders_option_skips_remove_empty(mock_descend, mock_remove_empty):
    """
    Does pyclean skip empty directory removal without --folders?
    """
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
@patch('pyclean.modern.log')
def test_remove_empty_directories_error(mock_log, system_error):
    """
    Does remove_empty_directories log a warning when directory access fails?
    """
    args = Namespace(dry_run=False, ignore=[])
    pyclean.modern.Runner.configure(args)

    directory = Path('/nonexistent/test/directory')

    with patch('pathlib.Path.iterdir', side_effect=system_error) as mock_iterdir:
        pyclean.modern.remove_empty_directories(directory)

    mock_log.warning.assert_called_once_with(
        'Cannot access directory %s: %s',
        directory,
        mock_iterdir.side_effect,
    )
