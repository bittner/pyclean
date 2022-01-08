"""
Cross-Python version compatibility.
"""
import platform
import sys
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

    # pylint: disable=consider-using-f-string
    detected_version = '%s%s' % (
        platform.python_implementation(),
        sys.version[0],
    )

    module_name = implementation[override if override else detected_version]
    return import_module(module_name)
