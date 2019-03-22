"""
Tests for the pyclean CLI
"""
import os
import platform
import pytest
import sys


@pytest.mark.skipif(sys.version_info >= (3,), reason="requires Python 2")
def test_entrypoint_py2():
    """
    Is entrypoint script installed for Python 2? (setup.py)
    """
    exit_status = os.system('pyclean --help')
    assert exit_status == 0


@pytest.mark.skipif(sys.version_info < (3,), reason="requires Python 3")
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
