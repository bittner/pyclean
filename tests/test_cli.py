"""
Tests for the pyclean CLI
"""
import os
import platform
import pytest
import sys

try:
    from unittest.mock import patch
except ImportError:  # Python 2.7, PyPy2
    from mock import patch

import pyclean.cli

from helpers import ArgvContext


@pytest.mark.skipif(platform.python_implementation() != 'CPython'
                    or sys.version_info >= (3,),
                    reason="requires CPython 2")
def test_entrypoint_py2():
    """
    Is entrypoint script installed for Python 2? (setup.py)
    """
    exit_status = os.system('pyclean --help')
    assert exit_status == 0


@pytest.mark.skipif(platform.python_implementation() != 'CPython'
                    or sys.version_info < (3,),
                    reason="requires CPython 3")
def test_entrypoint_py3():
    """
    Is entrypoint script installed for Python 3? (setup.py)
    """
    exit_status = os.system('py3clean --help')
    assert exit_status == 0


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info >= (3,),
                    reason="requires PyPy2")
def test_entrypoint_pypy():
    """
    Is entrypoint script installed for PyPy? (setup.py)
    """
    exit_status = os.system('pypyclean --help')
    assert exit_status == 0


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info < (3,),
                    reason="requires PyPy3")
def test_entrypoint_pypy3():
    """
    Is entrypoint script installed for PyPy3? (setup.py)
    """
    exit_status = os.system('pypyclean --help')
    assert exit_status == 0


@patch('pyclean.compat.get_implementation')
def test_calls_compat(mock_get_implementation):
    """
    Does a call to `pyclean` invoke the compat layer?
    """
    with ArgvContext('pyclean', 'foo'):
        pyclean.cli.main()

    assert mock_get_implementation.called
