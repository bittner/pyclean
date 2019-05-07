"""
Tests for the cleaning logic on folders
"""
import platform
import pytest
import sys

import pyclean.cli

from helpers import ArgvContext


@pytest.mark.skipif(sys.version_info >= (3,), reason="requires Python 2")
def test_directory_py2():
    """
    Does traversing directories for cleaning work for Python 2?
    """
    with ArgvContext('pyclean', 'foo'):
        pyclean.cli.pyclean()


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
def test_directory_py3():
    """
    Does traversing directories for cleaning work for Python 3?
    """
    with ArgvContext('py3clean', 'foo'):
        pyclean.cli.py3clean()


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info >= (3,),
                    reason="requires PyPy2")
def test_directory_pypy():
    """
    Does traversing directories for cleaning work for PyPy?
    """
    with ArgvContext('pypyclean', 'foo'):
        pyclean.cli.pypyclean()


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info < (3,),
                    reason="requires PyPy3")
def test_directory_pypy3():
    """
    Does traversing directories for cleaning work for PyPy3?
    """
    with ArgvContext('pypyclean', 'foo'):
        pyclean.cli.pypyclean()
