"""
Tests for filtering by Python version
"""
import platform
import pytest

try:
    from unittest.mock import patch
except ImportError:  # Python 2.7, PyPy2
    from mock import patch

from cli_test_helpers import ArgvContext

import pyclean.cli


@pytest.mark.skipif(platform.python_implementation() != 'CPython',
                    reason="requires CPython")
def test_filterversion_py():
    """
    Does filtering by Python version work when run with Python 3?
    """
    with ArgvContext('pyclean', '--legacy', '-V', '3.5', '-p', 'python-apt'):
        pyclean.cli.main()


@pytest.mark.skipif(platform.python_implementation() != 'PyPy',
                    reason="requires PyPy")
@patch('pyclean.pypyclean.installed_namespaces', return_value={})
def test_filterversion_pypy(mock_namespaces):
    """
    Does filtering by Python version work when run with PyPy?
    """
    with ArgvContext('pyclean', '--legacy', '-V', '2.7', '-p', 'python-apt'):
        pyclean.cli.main()

    assert mock_namespaces.called
