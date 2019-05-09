"""
Cross-Python version compatibility.
"""
import importlib
import platform
import sys


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

    module = implementation[python_version]
    return importlib.import_module(module)
