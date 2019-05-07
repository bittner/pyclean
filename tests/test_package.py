"""
Tests for the cleaning logic on Python packages
"""
import platform
import pytest
import sys

import pyclean.cli

from helpers import ArgvContext


@pytest.mark.skipif(sys.version_info >= (3,), reason="requires Python 2")
def test_package_py2():
    """
    Does collecting/traversing packages for cleaning work for Python 2?
    """
    with ArgvContext('-p', 'python-apt'):
        pyclean.cli.pyclean()


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
def test_package_py3():
    """
    Does collecting/traversing packages for cleaning work for Python 3?
    """
    with ArgvContext('-p', 'python-apt'):
        pyclean.cli.py3clean()


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info >= (3,),
                    reason="requires PyPy2")
def test_package_pypy():
    """
    Does collecting/traversing packages for cleaning work for PyPy?
    """
    with ArgvContext('-p', 'python-apt'):
        pyclean.cli.pypyclean()


@pytest.mark.skipif(platform.python_implementation() != 'PyPy'
                    or sys.version_info < (3,),
                    reason="requires PyPy3")
def test_package_pypy3():
    """
    Does collecting/traversing packages for cleaning work for PyPy3?
    """
    with ArgvContext('-p', 'python-apt'):
        pyclean.cli.pypyclean()
