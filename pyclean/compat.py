"""
Cross-Python version compatibility.
"""
import platform
import sys
from argparse import _AppendAction as AppendAction
from importlib import import_module


def get_implementation(override=None):
    """
    Detect the active Python version and return a reference to the
    module serving the version-specific pyclean implementation.
    """
    implementation = dict(
        CPython2='pyclean.py2clean',
        CPython3='pyclean.py3clean',
        PyPy2='pyclean.pypyclean',
        PyPy3='pyclean.pypyclean',
    )

    detected_version = '%s%s' % (
        platform.python_implementation(),
        sys.version[0],
    )

    module_name = implementation[override if override else detected_version]
    return import_module(module_name)


class ExtendAction(AppendAction):
    """
    Argparse "extend" action for Python < 3.8.
    A simplified backport from the Python standard library.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = [] if items is None else items[:]
        items.extend(values)
        setattr(namespace, self.dest, items)
