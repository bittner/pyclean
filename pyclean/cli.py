"""
Command line interface implementation for pyclean.
"""
import argparse
import logging
import sys

from . import __version__, compat, modern

log = logging.getLogger(__name__)


def parse_arguments():
    """
    Parse and handle CLI arguments
    """
    debris_default_topics = ['build', 'cache', 'coverage', 'pytest']
    debris_optional_topics = ['jupyter', 'tox']
    debris_choices = ['all'] + debris_default_topics + debris_optional_topics
    ignore_default_items = ['.git', '.hg', '.svn', '.tox', '.venv', 'node_modules']

    parser = argparse.ArgumentParser(
        description='Remove byte-compiled files for a package or project.',
    )

    if sys.version_info < (3, 8):
        parser.register('action', 'extend', compat.ExtendAction)

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
                        nargs='+', default=ignore_default_items,
                        help='directory that should be ignored '
                             '(may be specified multiple times; '
                             'default: %s)' % ' '.join(ignore_default_items))
    parser.add_argument('-d', '--debris', metavar='TOPIC', action='extend',
                        nargs='*', default=argparse.SUPPRESS, choices=debris_choices,
                        help='remove leftovers from popular Python development '
                             'tools (may be specified multiple times; '
                             'default: %s)' % ' '.join(debris_default_topics))
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
        if 'all' in args.debris:
            args.debris = debris_default_topics + debris_optional_topics
        elif not args.debris:
            args.debris = debris_default_topics
        log.debug("Debris topics to scan for: %s", ' '.join(args.debris))
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
