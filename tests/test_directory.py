"""
Tests for the cleaning logic on folders
"""
import pyclean.cli

from helpers import ArgvContext


def test_clean_directory():
    """
    Does traversing directories for cleaning work for Python 2?
    """
    with ArgvContext('pyclean', 'foo'):
        pyclean.cli.main()
