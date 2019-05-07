"""
Useful helpers for our tests
"""
import sys


class ArgvContext:
    """
    A simple context manager allowing to temporarily override ``sys.argv``
    """

    def __init__(self, *new_args):
        self._old = sys.argv
        self.args = type(self._old)(new_args)

    def __enter__(self):
        sys.argv = self.args

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.argv = self._old
