"""
Tests for the pyclean CLI
"""
import os

try:
    from unittest.mock import patch
except ImportError:  # Python 2.7, PyPy2
    from mock import patch

import pyclean.cli

from helpers import ArgvContext


def test_entrypoint():
    """
    Is entrypoint script installed for Python 2? (setup.py)
    """
    exit_status = os.system('pyclean --help')
    assert exit_status == 0


@patch('pyclean.compat.get_implementation')
def test_calls_compat(mock_get_implementation):
    """
    Does a call to `pyclean` invoke the compat layer?
    """
    with ArgvContext('pyclean', 'foo'):
        pyclean.cli.main()

    assert mock_get_implementation.called
