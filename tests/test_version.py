"""
Tests for filtering by Python version
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
def test_filterversion_py2():
    """
    Does filtering by Python version work when run with Python 2?
    """
    with ArgvContext('-V', '2.7', '-p', 'python-apt'):
        pyclean.cli.pyclean()


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
def test_filterversion_py3():
    """
    Does filtering by Python version work when run with Python 3?
    """
    with ArgvContext('-V', '3.5', '-p', 'python-apt'):
        pyclean.cli.py3clean()


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info >= (3,),
                    reason="requires PyPy2")
@patch('pyclean.pypyclean.installed_namespaces', return_value={})
def test_filterversion_pypy(mock_namespaces):
    """
    Does filtering by Python version work when run with PyPy?
    """
    with ArgvContext('-V', '2.7', '-p', 'python-apt'):
        pyclean.cli.pypyclean()

    assert mock_namespaces.called


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info < (3,),
                    reason="requires PyPy3")
@patch('pyclean.pypyclean.installed_namespaces', return_value={})
def test_filterversion_pypy3(mock_namespaces):
    """
    Does filtering by Python version work when run with PyPy3?
    """
    with ArgvContext('-V', '3.5', '-p', 'python-apt'):
        pyclean.cli.pypyclean()

    assert mock_namespaces.called
