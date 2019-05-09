"""
Tests for the cross-Python version compatibility module
"""
import platform
import pytest
import sys

try:
    from unittest.mock import patch
except ImportError:  # Python 2.7, PyPy2
    from mock import patch

from pyclean import compat


@pytest.mark.skipif(platform.python_implementation() != 'CPython'
                    or sys.version_info >= (3,),
                    reason="requires CPython 2")
def test_get_implementation_py2():
    """
    Is pyclean implementation returned for Python 2?
    """
    from pyclean import pyclean
    assert compat.get_implementation() is pyclean


@pytest.mark.skipif(platform.python_implementation() != 'CPython'
                    or sys.version_info < (3,),
                    reason="requires CPython 3")
def test_get_implementation_py3():
    """
    Is py3clean implementation for Python 3?
    """
    from pyclean import py3clean
    assert compat.get_implementation() is py3clean


@pytest.mark.skipif(platform.python_implementation() != 'PyPy',
                    reason="requires PyPy")
def test_get_implementation_pypy():
    """
    Is pypyclean implementation for PyPy?
    """
    from pyclean import pypyclean
    assert compat.get_implementation() is pypyclean
