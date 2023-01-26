"""
Tests for the modern module
"""
import logging
import sys
from argparse import Namespace

import pytest

try:
    from pathlib import Path
    from unittest.mock import Mock, call, patch
except ImportError:  # Python 2.7, PyPy2
    from mock import patch

from cli_test_helpers import ArgvContext

import pyclean.cli
import pyclean.modern
from pyclean.modern import (
    delete_filesystem_objects,
    initialize_runner,
    remove_debris_for,
    remove_freeform_targets,
)


class FilesystemObjectMock(Mock):

    def __init__(self, *args, **kwargs):
        name = kwargs['name'] if 'name' in kwargs else args[0]
        super().__init__(autospec=Path(name), **kwargs)
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def is_file(self):
        return False

    def is_dir(self):
        return False

    def is_symlink(self):
        return False


class DirectoryMock(FilesystemObjectMock):

    def __init__(self, **kwargs):
        super().__init__('a-dir', **kwargs)

    def is_dir(self):
        return True


class FileMock(FilesystemObjectMock):

    def __init__(self, **kwargs):
        super().__init__('a-file', **kwargs)

    def is_file(self):
        return True


class SymlinkMock(FilesystemObjectMock):

    def __init__(self, **kwargs):
        super().__init__('a-symlink', **kwargs)

    def is_symlink(self):
        return True


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
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


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
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


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
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


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
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


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
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


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
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


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
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


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
@patch('pyclean.modern.print_dirname')
@patch('pyclean.modern.print_filename')
@patch('pyclean.modern.remove_directory')
@patch('pyclean.modern.remove_file')
def test_delete(mock_real_unlink, mock_real_rmdir,
                mock_dry_unlink, mock_dry_rmdir):
    """
    Is actual deletion attempted w/o --dry-run?
    """
    with ArgvContext('pyclean', '.'):
        pyclean.cli.main()

    assert mock_real_unlink.called
    assert mock_real_rmdir.called
    assert not mock_dry_unlink.called
    assert not mock_dry_rmdir.called


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
@patch('pyclean.modern.print_dirname')
@patch('pyclean.modern.print_filename')
@patch('pyclean.modern.remove_directory')
@patch('pyclean.modern.remove_file')
def test_dryrun(mock_real_unlink, mock_real_rmdir,
                mock_dry_unlink, mock_dry_rmdir):
    """
    Does --dry-run option avoid real deletion?
    """
    with ArgvContext('pyclean', '.', '--dry-run'):
        pyclean.cli.main()

    assert not mock_real_unlink.called
    assert not mock_real_rmdir.called
    assert mock_dry_unlink.called
    assert mock_dry_rmdir.called


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
@pytest.mark.parametrize(
    'options,scanned_topics',
    [
        ([], []),
        (['-d'], ['build', 'cache', 'coverage', 'pytest']),
        (['-d', 'build', 'coverage'], ['build', 'coverage']),
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


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
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


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
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


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
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


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
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
