"""
Tests for the cross-Python version compatibility module
"""
import platform
import sys

import pytest

import pyclean


@pytest.mark.skipif(platform.python_implementation() != 'CPython'
                    or sys.version_info >= (3,)
                    or platform.system() != 'Linux',
                    reason="requires CPython 2 on Debian Linux")
def test_detect_py2():
    """
    Is pyclean implementation returned for Python 2?
    """
    assert pyclean.compat.get_implementation() is pyclean.py2clean


@pytest.mark.skipif(platform.python_implementation() != 'CPython'
                    or sys.version_info < (3,)
                    or platform.system() != 'Linux',
                    reason="requires CPython 3 on Debian Linux")
def test_detect_py3():
    """
    Is py3clean implementation for Python 3?
    """
    assert pyclean.compat.get_implementation() is pyclean.py3clean


@pytest.mark.skipif(platform.python_implementation() != 'PyPy',
                    reason="requires PyPy")
def test_detect_pypy():
    """
    Is pypyclean implementation for PyPy?
    """
    assert pyclean.compat.get_implementation() is pyclean.pypyclean
