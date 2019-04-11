"""
Tests for the cleaning logic on Python packages
"""
import os
import platform
import pytest
import sys


@pytest.mark.skipif(sys.version_info >= (3,), reason="requires Python 2")
def test_package_py2():
    """
    Does collecting/traversing packages for cleaning work for Python 2?
    """
    exit_status = os.system('pyclean -p python-apt')
    assert exit_status == 0


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
def test_package_py3():
    """
    Does collecting/traversing packages for cleaning work for Python 3?
    """
    exit_status = os.system('py3clean -p python-apt')
    assert exit_status == 0


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info >= (3,),
                    reason="requires PyPy2")
def test_package_pypy():
    """
    Does collecting/traversing packages for cleaning work for PyPy?
    """
    exit_status = os.system('pypyclean -p python-apt')
    assert exit_status == 0


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info < (3,),
                    reason="requires PyPy2")
def test_package_pypy3():
    """
    Does collecting/traversing packages for cleaning work for PyPy3?
    """
    exit_status = os.system('pypyclean -p python-apt')
    assert exit_status == 0
