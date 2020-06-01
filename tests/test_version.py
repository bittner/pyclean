"""
Tests for filtering by Python version
"""
import platform
import sys
import pytest

try:
    from unittest.mock import patch
except ImportError:  # Python 2.7, PyPy2
    from mock import patch

from cli_test_helpers import ArgvContext

import pyclean


@pytest.mark.skipif(platform.python_implementation() != 'CPython' or
                    sys.version_info < (3,), reason="requires CPython 3")
@patch('pyclean.py3clean.Interpreter.magic_tag', return_value='{impl}-{ver}'
       .format(
           impl=platform.python_implementation().lower(),  # e.g. "cpython"
           ver=''.join(platform.python_version().split('.')[:2]),  # e.g. "36"
       ))
def test_filterversion_py3(mock_magictag):
    """
    Does filtering by Python version work when run with Python 3?
    """
    with ArgvContext('pyclean', '--legacy', '-V', '3.5', '-p', 'python'), \
            pytest.raises(SystemExit):
        pyclean.cli.main()


@pytest.mark.skipif(platform.python_implementation() != 'CPython' or
                    sys.version_info >= (3,), reason="requires CPython 2")
def test_filterversion_py2():
    """
    Does filtering by Python version work when run with Python 2?
    """
    with ArgvContext('pyclean', '--legacy', '-V', '2.7', '-p', 'python'):
        pyclean.cli.main()


@pytest.mark.skipif(platform.python_implementation() != 'PyPy',
                    reason="requires PyPy")
@patch('pyclean.pypyclean.installed_namespaces', return_value={})
def test_filterversion_pypy(mock_namespaces):
    """
    Does filtering by Python version work when run with PyPy?
    """
    with ArgvContext('pyclean', '--legacy', '-V', '2.7', '-p', 'python'):
        pyclean.cli.main()

    assert mock_namespaces.called
