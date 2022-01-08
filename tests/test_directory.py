"""
Tests for the cleaning logic on folders
"""
import platform

import pytest
from cli_test_helpers import ArgvContext

import pyclean.cli


@pytest.mark.skipif(platform.system() != 'Linux',
                    reason="requires Debian Linux")
def test_clean_directory():
    """
    Does traversing directories for cleaning work on Debian Linux?
    """
    with ArgvContext('pyclean', '--legacy', 'foo'):
        pyclean.cli.main()
