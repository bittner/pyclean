"""
Tests for the pyclean CLI
"""
import os
import platform
import sys
from importlib import import_module

try:
    from unittest.mock import patch
except ImportError:  # Python 2.7, PyPy2
    from mock import patch

import pytest
from cli_test_helpers import ArgvContext, shell

import pyclean.cli


def test_main_module():
    """
    Exercise (most of) the code in the ``__main__`` module.
    """
    import_module('pyclean.__main__')


def test_runas_module():
    """
    Can this package be run as a Python module?
    """
    result = shell('python -m pyclean --help')
    assert result.exit_code == 0


def test_entrypoint():
    """
    Is entrypoint script installed? (setup.py)
    """
    result = shell('pyclean --help')
    assert result.exit_code == 0


def test_entrypoint_py2_installed():
    """
    Is entrypoint script installed for Python 2? (setup.py)
    """
    result = shell('py2clean --help')
    assert result.exit_code == 0


@patch('pyclean.compat.import_module')
def test_entrypoint_py2_working(mock_import_module):
    """
    Is entrypoint overriding with Python 2 implementation?
    """
    with ArgvContext('py2clean', 'foo'):
        pyclean.cli.py2clean()

    args, _ = mock_import_module.call_args
    assert args == ('pyclean.py2clean',)


def test_entrypoint_py3_installed():
    """
    Is entrypoint script installed for Python 3? (setup.py)
    """
    result = shell('py3clean --help')
    assert result.exit_code == 0


@patch('pyclean.compat.import_module')
def test_entrypoint_py3_working(mock_import_module):
    """
    Is entrypoint overriding with Python 3 implementation?
    """
    with ArgvContext('py3clean', 'foo'):
        pyclean.cli.py3clean()

    args, _ = mock_import_module.call_args
    assert args == ('pyclean.py3clean',)


def test_entrypoint_pypy_installed():
    """
    Is entrypoint script installed for PyPy 2/3? (setup.py)
    """
    result = shell('pypyclean --help')
    assert result.exit_code == 0


@patch('pyclean.compat.import_module')
def test_entrypoint_pypy_working(mock_import_module):
    """
    Is entrypoint overriding with PyPy implementation?
    """
    with ArgvContext('pypyclean', 'foo'):
        pyclean.cli.pypyclean()

    args, _ = mock_import_module.call_args
    assert args == ('pyclean.pypyclean',)


@patch('pyclean.cli.modern.pyclean')
@patch('pyclean.cli.compat.get_implementation')
def test_mandatory_arg_missing(mock_getimpl, mock_modern):
    """
    Does CLI abort when neither a path nor a package is specified?
    """
    with ArgvContext('pyclean'), pytest.raises(SystemExit):
        pyclean.cli.main()

    assert not mock_getimpl.called
    assert not mock_modern.called


@pytest.mark.parametrize('options', (['.'], ['--package=foo'], ['.', '-p', 'foo']))
@patch('pyclean.cli.modern.pyclean')
@patch('pyclean.cli.compat.get_implementation')
def test_mandatory_args(mock_getimpl, mock_modern, options):
    """
    Does CLI execute fine when a path or a package or both are specified?
    """
    with ArgvContext('pyclean', *options):
        pyclean.cli.main()

    assert mock_getimpl.called or mock_modern.called


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
def test_dryrun_option():
    """
    Does a --dry-run option exist?
    """
    result = shell('pyclean --dry-run tests')

    assert result.exit_code == 0


def test_ignore_option():
    """
    Does an --ignore option exist and append values to a list of defaults?
    """
    default = ['.git', '.hg', '.svn', '.tox', '.venv', 'node_modules']
    expected_ignore_list = default + ['foo', 'bar']

    with ArgvContext('pyclean', '.', '--ignore', 'foo', 'bar'):
        args = pyclean.cli.parse_arguments()

    assert args.ignore == expected_ignore_list


def test_debris_default_args():
    """
    Does calling `pyclean --debris` use defaults for the debris option?
    """
    with ArgvContext('pyclean', 'foo', '--debris'):
        args = pyclean.cli.parse_arguments()

    assert args.debris == ['build', 'cache', 'coverage', 'pytest']


def test_debris_all():
    """
    Does calling `pyclean --debris all` pick all topics?
    """
    with ArgvContext('pyclean', 'foo', '--debris', 'all'):
        args = pyclean.cli.parse_arguments()

    assert args.debris == ['build', 'cache', 'coverage', 'pytest', 'jupyter', 'tox']


def test_debris_explicit_args():
    """
    Does calling `pyclean --debris` with explicit arguments provide those?
    """
    with ArgvContext('pyclean', 'foo', '--debris', 'build', 'pytest'):
        args = pyclean.cli.parse_arguments()

    assert args.debris == ['build', 'pytest']


def test_debris_invalid_args():
    """
    Does calling `pyclean --debris` with invalid arguments abort execution?
    """
    with ArgvContext('pyclean', 'foo', '--debris', 'not-a-tool-name'), \
            pytest.raises(SystemExit):
        pyclean.cli.parse_arguments()


def test_version_option():
    """
    Does --version yield the expected information?
    """
    expected_output = '' if platform.python_version_tuple() < ('3',) \
        else '%s%s' % (pyclean.__version__, os.linesep)

    result = shell('pyclean --version')

    assert result.stdout == expected_output
    assert result.exit_code == 0


@patch('pyclean.compat.get_implementation')
def test_legacy_calls_compat(mock_get_implementation):
    """
    Does calling `pyclean --legacy` invoke the compat layer?
    """
    with ArgvContext('pyclean', 'foo', '--legacy'):
        pyclean.cli.main()

    assert mock_get_implementation.called


@patch('pyclean.modern.pyclean')
def test_default_modern(mock_modern_pyclean):
    """
    Does simply calling `pyclean` invoke the modern implementation?
    """
    with ArgvContext('pyclean', 'foo'):
        pyclean.cli.main()

    assert mock_modern_pyclean.called
