"""
Tests for the cleaning logic on folders
"""
from cli_test_helpers import ArgvContext

import pyclean.cli


def test_clean_directory():
    """
    Does traversing directories for cleaning work for Python 2?
    """
    with ArgvContext('pyclean', '--legacy', 'foo'):
        pyclean.cli.main()
