"""
Tests for the cleaning logic on folders
"""
import os
import platform
import pytest
import sys


@pytest.mark.skipif(sys.version_info >= (3,), reason="requires Python 2")
def test_directory_py2():
    """
    Does traversing directories for cleaning work for Python 2?
    """
    exit_status = os.system('pyclean foo')
    assert exit_status == 0


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
def test_directory_py3():
    """
    Does traversing directories for cleaning work for Python 3?
    """
    exit_status = os.system('py3clean foo')
    assert exit_status == 0


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info >= (3,),
                    reason="requires PyPy2")
def test_directory_pypy():
    """
    Does traversing directories for cleaning work for PyPy?
    """
    exit_status = os.system('pypyclean foo')
    assert exit_status == 0


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info < (3,),
                    reason="requires PyPy3")
def test_directory_pypy3():
    """
    Does traversing directories for cleaning work for PyPy3?
    """
    exit_status = os.system('pypyclean foo')
    assert exit_status == 0
