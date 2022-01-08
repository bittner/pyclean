"""
Tests for the modern module
"""
import logging
import sys

import pytest

try:
    from pathlib import Path
    from unittest.mock import call, patch
except ImportError:  # Python 2.7, PyPy2
    from mock import patch

from cli_test_helpers import ArgvContext

import pyclean.cli
import pyclean.modern


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
@patch('pyclean.modern.descend_and_clean_bytecode')
def test_walks_tree(mock_descend):
    """
    Does pyclean walk the directory tree?
    """
    with ArgvContext('pyclean', '.'):
        pyclean.cli.main()

    assert mock_descend.mock_calls == [
        call(Path('.')),
    ]


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
@patch('pyclean.modern.descend_and_clean_bytecode')
def test_walks_all_trees(mock_descend):
    """
    Are all positional args evaluated?
    """
    with ArgvContext('pyclean', 'foo', 'bar', 'baz'):
        pyclean.cli.main()

    assert mock_descend.mock_calls == [
        call(Path('foo')),
        call(Path('bar')),
        call(Path('baz')),
    ]


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
@patch.object(pyclean.modern.logging, 'basicConfig')
@patch('pyclean.modern.descend_and_clean_bytecode')
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
@patch('pyclean.modern.descend_and_clean_bytecode')
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
@patch('pyclean.modern.descend_and_clean_bytecode')
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
