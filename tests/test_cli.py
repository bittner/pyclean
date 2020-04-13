"""
Tests for the pyclean CLI
"""
import os

try:
    from unittest.mock import patch
except ImportError:  # Python 2.7, PyPy2
    from mock import patch

from cli_test_helpers import ArgvContext

import pyclean.cli


def test_entrypoint():
    """
    Is entrypoint script installed? (setup.py)
    """
    exit_status = os.system('pyclean --help')
    assert exit_status == 0


def test_entrypoint_py2_installed():
    """
    Is entrypoint script installed for Python 2? (setup.py)
    """
    exit_status = os.system('py2clean --help')
    assert exit_status == 0


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
    exit_status = os.system('py3clean --help')
    assert exit_status == 0


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
    exit_status = os.system('pypyclean --help')
    assert exit_status == 0


@patch('pyclean.compat.import_module')
def test_entrypoint_pypy_working(mock_import_module):
    """
    Is entrypoint overriding with PyPy implementation?
    """
    with ArgvContext('pypyclean', 'foo'):
        pyclean.cli.pypyclean()

    args, _ = mock_import_module.call_args
    assert args == ('pyclean.pypyclean',)


@patch('pyclean.compat.get_implementation')
def test_legacy_calls_compat(mock_get_implementation):
    """
    Does calling `pyclean --legacy` invoke the compat layer?
    """
    with ArgvContext('pyclean', '--legacy', 'foo'):
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
