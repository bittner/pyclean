"""
Tests for the cleaning logic on Python packages
"""
import platform
import pytest
import sys

try:
    from unittest.mock import patch
except ImportError:  # Python 2.7, PyPy2
    from mock import patch

import pyclean.cli

from helpers import ArgvContext


@pytest.mark.skipif(sys.version_info >= (3,), reason="requires Python 2")
def test_package_py2():
    """
    Does collecting/traversing packages for cleaning work for Python 2?
    """
    with ArgvContext('pyclean', '-p', 'python-apt'):
        pyclean.cli.pyclean()


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
def test_package_py3():
    """
    Does collecting/traversing packages for cleaning work for Python 3?
    """
    with ArgvContext('py3clean', '-p', 'python-apt'):
        pyclean.cli.py3clean()


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info >= (3,),
                    reason="requires PyPy2")
@patch('pyclean.pypyclean.installed_namespaces', return_value={})
def test_package_pypy(mock_namespaces):
    """
    Does collecting/traversing packages for cleaning work for PyPy?
    """
    with ArgvContext('pypyclean', '-p', 'python-apt'):
        pyclean.cli.pypyclean()

    assert mock_namespaces.called


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info < (3,),
                    reason="requires PyPy3")
@patch('pyclean.pypyclean.installed_namespaces', return_value={})
def test_package_pypy3(mock_namespaces):
    """
    Does collecting/traversing packages for cleaning work for PyPy3?
    """
    with ArgvContext('pypyclean', '-p', 'python-apt'):
        pyclean.cli.pypyclean()

    assert mock_namespaces.called
