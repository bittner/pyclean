"""
Command line interface implementation for pyclean.
"""
import argparse

from . import __version__, compat


def parse_arguments():
    """
    Parse and handle CLI arguments
    """
    parser = argparse.ArgumentParser(
        description='Remove byte-compiled files for a package')

    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-V', metavar='VERSION', dest='version',
                        help='specify Python version to clean')
    parser.add_argument('-p', '--package', metavar='PACKAGE',
                        action='append', default=[],
                        help='Debian package to byte-compile '
                             '(may be specified multiple times)')
    parser.add_argument('directory', nargs='*',
                        help='Directory tree (or file) to byte-compile')

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-v', '--verbose', action='store_true',
                           help='Be more verbose')
    verbosity.add_argument('-q', '--quiet', action='store_true',
                           help='Be quiet')

    args = parser.parse_args()

    if not (args.package or args.directory):
        parser.error('A directory (or files) or a list of packages '
                     'must be specified.')
    return args


def main(override=None):
    """
    Entry point for all scripts
    """
    args = parse_arguments()
    impl = compat.get_implementation(override=override)
    impl.main(args)


def py2clean():
    """
    Forces the use of the implementation for Python 2
    """
    main('CPython2')


def py3clean():
    """
    Forces the use of the implementation for Python 3
    """
    main('CPython3')


def pypyclean():
    """
    Forces the use of the implementation for PyPy (2+3)
    """
    main('PyPy2')
