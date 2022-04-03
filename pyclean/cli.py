"""
Command line interface implementation for pyclean.
"""
import argparse
import logging

from . import __version__, compat, modern

log = logging.getLogger(__name__)


def parse_arguments():
    """
    Parse and handle CLI arguments
    """
    debris_default_topics = ['build', 'cache', 'coverage', 'pytest']
    debris_optional_topics = ['tox']

    parser = argparse.ArgumentParser(
        description='Remove byte-compiled files for a package or project.',
    )

    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-V', metavar='VERSION', dest='version',
                        help='specify Python version to clean')
    parser.add_argument('-p', '--package', metavar='PACKAGE',
                        action='append', default=[],
                        help='Debian package to byte-compile '
                             '(may be specified multiple times)')
    parser.add_argument('directory', nargs='*',
                        help='directory tree to traverse for byte-code')
    parser.add_argument('-i', '--ignore', metavar='DIRECTORY', action='extend',
                        nargs='+', default=['.git', '.tox', '.venv'],
                        help='directory that should be ignored '
                             '(may be specified multiple times; '
                             'default: %(default)s)')
    parser.add_argument('-d', '--debris', metavar='TOPIC', action='extend',
                        nargs='*', default=argparse.SUPPRESS,
                        choices=debris_default_topics + debris_optional_topics,
                        help='remove typical leftovers from well-known '
                             'programs (may be specified multiple times; '
                             'default: %s)' % debris_default_topics)
    parser.add_argument('--legacy', action='store_true',
                        help='use legacy Debian implementation (autodetect)')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='show what would be done')

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-q', '--quiet', action='store_true',
                           help='be quiet')
    verbosity.add_argument('-v', '--verbose', action='store_true',
                           help='be more verbose')

    args = parser.parse_args()
    init_logging(args)

    if not (args.package or args.directory):
        parser.error('A directory (or files) or a list of packages '
                     'must be specified.')

    if 'debris' in args:
        if args.debris == []:
            args.debris = debris_default_topics
        log.debug("Debris requested to clean up for: %s", ' '.join(args.debris))
    else:
        args.debris = []

    log.debug("Ignored directories: %s", ' '.join(args.ignore))

    return args


def init_logging(args):
    """
    Set the log level according to the -v/-q command line options.
    """
    log_level = logging.FATAL if args.quiet \
        else logging.DEBUG if args.verbose \
        else logging.INFO
    log_format = "%(message)s"
    logging.basicConfig(level=log_level, format=log_format)


def main(override=None):
    """
    Entry point for all scripts
    """
    args = parse_arguments()
    if override or args.legacy:
        impl = compat.get_implementation(override=override)
        impl.main(args)
    else:
        modern.pyclean(args)


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
