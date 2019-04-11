"""
Tests for filtering by Python version 
"""
import os
import platform
import pytest
import sys


@pytest.mark.skipif(sys.version_info >= (3,), reason="requires Python 2")
def test_filterversion_py2():
    """
    Does filtering by Python version work when run with Python 2?
    """
    exit_status = os.system('pyclean -V 2.7 -p python-apt')
    assert exit_status == 0


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
def test_filterversion_py3():
    """
    Does filtering by Python version work when run with Python 3?
    """
    exit_status = os.system('py3clean -V 3.5 -p python-apt')
    assert exit_status == 0


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info >= (3,),
                    reason="requires PyPy2")
def test_filterversion_pypy():
    """
    Does filtering by Python version work when run with PyPy?
    """
    exit_status = os.system('pypyclean -V 2.7 -p python-apt')
    assert exit_status == 0


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info < (3,),
                    reason="requires PyPy3")
def test_filterversion_pypy3():
    """
    Does filtering by Python version work when run with PyPy3?
    """
    exit_status = os.system('pypyclean -V 3.5 -p python-apt')
    assert exit_status == 0
