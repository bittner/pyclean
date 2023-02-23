"""
Tests for the modern module
"""
import logging
from argparse import Namespace

import pytest

try:
    from pathlib import Path
    from unittest.mock import Mock, call, patch
except ImportError:  # Python 2.7, PyPy2
    pytest.importorskip("pathlib")

from cli_test_helpers import ArgvContext
from py3_mocks import DirectoryMock, FileMock, SymlinkMock

import pyclean.cli
import pyclean.modern
from pyclean.modern import (
    delete_filesystem_objects,
    initialize_runner,
    remove_debris_for,
    remove_directory,
    remove_file,
    remove_freeform_targets,
)


@patch('pyclean.modern.descend_and_clean')
def test_walks_tree(mock_descend):
    """
    Does pyclean walk the directory tree?
    """
    with ArgvContext('pyclean', '.'):
        pyclean.cli.main()

    assert mock_descend.mock_calls == [
        call(Path('.'), ['.pyc', '.pyo'], ['__pycache__']),
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
        Path('.'), pyclean.modern.BYTECODE_FILES, pyclean.modern.BYTECODE_DIRS
    )

    assert not pyclean.modern.Runner.unlink.called
    assert not pyclean.modern.Runner.rmdir.called
    assert pyclean.modern.log.mock_calls == [
        call.debug('Ignoring %s', SymlinkMock()),
    ]


@pytest.mark.parametrize('unlink_failures,rmdir_failures', [(7, 0), (0, 3), (1, 1)])
def test_report_failures(unlink_failures, rmdir_failures):
    """
    Are failures to delete a file or folder reported with ``log.debug``?
    """
    pyclean.modern.Runner.unlink_failed = unlink_failures
    pyclean.modern.Runner.rmdir_failed = rmdir_failures
    pyclean.modern.log = Mock()
    args = Namespace(
        debris=[],
        directory=[],
        dry_run=True,
        erase=[],
        ignore=[],
        yes=False,
    )

    pyclean.modern.pyclean(args)

    assert pyclean.modern.log.mock_calls[1] == call.debug(
        '%d files, %d directories could not be removed.',
        unlink_failures,
        rmdir_failures,
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
    remove_file(Path('tmp'))

    assert "debug('File not deleted." in str(mock_log.mock_calls[1])


@patch('pyclean.modern.log')
@patch('pathlib.Path.rmdir', side_effect=OSError)
def test_rmdir_failure(mock_rmdir, mock_log):
    """
    Is a deletion error caught and logged?
    """
    remove_directory(Path('tmp'))

    assert "debug('Directory not removed." in str(mock_log.mock_calls[1])


@patch('pyclean.modern.log')
def test_dryrun_output(mock_log):
    """
    Do we explain what would be done, when --dry-run is used?
    """
    args = Namespace(dry_run=True, ignore=[])

    initialize_runner(args)
    pyclean.modern.Runner.unlink(Path('tmp'))
    pyclean.modern.Runner.rmdir(Path('tmp'))

    assert "debug('Would delete file:" in str(mock_log.mock_calls[0])
    assert "debug('Would delete directory:" in str(mock_log.mock_calls[1])


@patch('pyclean.modern.print_dirname')
@patch('pyclean.modern.print_filename')
@patch('pyclean.modern.remove_directory')
@patch('pyclean.modern.remove_file')
def test_delete(
    mock_real_unlink, mock_real_rmdir, mock_dry_unlink, mock_dry_rmdir
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
    mock_real_unlink, mock_real_rmdir, mock_dry_unlink, mock_dry_rmdir
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
    'options,scanned_topics',
    [
        ([], []),
        (['-d'], ['cache', 'coverage', 'package', 'pytest']),
        (['-d', 'coverage', 'package'], ['coverage', 'package']),
    ]
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

    erase_calls = [call_args[0][0] for call_args in mock_erase.call_args_list]

    assert mock_descend.called
    assert not mock_debris.called
    assert erase_calls == [['tmp/**/*', 'tmp/']]


@patch('pyclean.modern.delete_filesystem_objects')
def test_debris_loop(mock_delete_fs_obj):
    """
    Does ``remove_debris_for()`` call filesystem object removal?
    """
    pyclean.modern.DEBRIS_TOPICS = {'foo': ['somedir/']}
    directory = Path('.')

    remove_debris_for('foo', directory)

    assert mock_delete_fs_obj.call_args_list == [
        call(directory, 'somedir/'),
    ]


@patch('pyclean.modern.delete_filesystem_objects')
def test_erase_loop(mock_delete_fs_obj):
    """
    Does ``remove_freeform_targets()`` call filesystem object removal?
    """
    patterns = ['foo.txt']
    directory = Path('.')

    remove_freeform_targets(patterns, yes=False, directory=directory)

    assert mock_delete_fs_obj.call_args_list == [
        call(directory, 'foo.txt', prompt=True),
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
    ]
)
def test_delete_filesdir_loop(mock_glob, mock_yes, mock_unlink, mock_rmdir):
    """
    Exercise the file and directory loop code.
    """
    args = Namespace(dry_run=False, ignore=[])
    directory = Path('.')

    initialize_runner(args)
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
    ]
)
def test_no_skips_deletion(mock_glob, mock_no, mock_unlink, mock_rmdir):
    """
    Is deletion skipped with --erase when user says "no" at the prompt?
    """
    args = Namespace(dry_run=False, ignore=[])
    directory = Path('.')

    initialize_runner(args)
    delete_filesystem_objects(directory, 'tmp/**/*', prompt=True)

    assert mock_glob.called
    assert mock_no.called
    assert not mock_unlink.called
    assert not mock_rmdir.called


@patch('pyclean.modern.remove_directory')
@patch('pyclean.modern.remove_file')
@patch(
    'pathlib.Path.glob',
    return_value=[
        DirectoryMock(),
        SymlinkMock(),
        FileMock(),
    ]
)
@patch('pyclean.modern.remove_debris_for')
@patch('pyclean.modern.descend_and_clean')
def test_yes_skips_prompt(
    mock_descend, mock_debris, mock_glob, mock_unlink, mock_rmdir
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
