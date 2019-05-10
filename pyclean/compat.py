"""
Cross-Python version compatibility.
"""
import platform
import sys

from importlib import import_module


def get_implementation():
    """
    Return a reference to the function that implements
    pyclean for the active Python version.
    """
    implementation = dict(
        CPython2='pyclean.pyclean',
        CPython3='pyclean.py3clean',
        PyPy2='pyclean.pypyclean',
        PyPy3='pyclean.pypyclean',
    )

    python_version = '%s%s' % (
        platform.python_implementation(),
        sys.version[0],
    )

    module_name = implementation[python_version]
    return import_module(module_name)
