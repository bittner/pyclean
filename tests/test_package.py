"""
Tests for the cleaning logic on Python packages
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
def test_clean_package():
    """
    Does collecting/traversing packages for cleaning work for Python 2+3?
    """
    with ArgvContext('pyclean', '--legacy', '-p', 'python-apt'):
        pyclean.cli.main()


@pytest.mark.skipif(platform.python_implementation() != 'PyPy',
                    reason="requires PyPy")
@patch('pyclean.pypyclean.installed_namespaces', return_value={})
def test_clean_package_pypy(mock_namespaces):
    """
    Does collecting/traversing packages for cleaning work for PyPy?
    """
    with ArgvContext('pyclean', '--legacy', '-p', 'python-apt'):
        pyclean.cli.main()

    assert mock_namespaces.called
