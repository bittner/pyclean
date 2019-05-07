"""
Tests for our tests helpers  8-}
"""
import sys

from helpers import ArgvContext


def test_argv_context():
    """
    Test if ArgvContext sets the right argvs and resets to the old correctly
    """
    old = sys.argv
    new = ["Alice", "Bob", "Chris", "Daisy"]

    assert sys.argv == old

    with ArgvContext(*new):
        assert sys.argv == new, \
            "sys.argv wasn't correctly changed by the contextmanager"

    assert sys.argv == old, "sys.argv wasn't correctly reset"
