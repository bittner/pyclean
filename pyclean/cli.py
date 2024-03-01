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
    Parse and handle CLI arguments.
    """
    debris_default_topics = ['cache', 'coverage', 'package', 'pytest', 'ruff']
    debris_optional_topics = ['jupyter', 'mypy', 'tox']
    debris_choices = ['all', *debris_default_topics, *debris_optional_topics]
    ignore_default_items = [
        '.git',
        '.hg',
        '.svn',
        '.tox',
        '.venv',
        'node_modules',
        'venv',
    ]

    parser = argparse.ArgumentParser(
        description='Remove byte-compiled files for a package or project.',
    )

    if sys.version_info < (3, 8):  # pragma: no-cover-gt-py37
        parser.register('action', 'extend', compat.ExtendAction)

    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        'directory',
        nargs='+',
        help='directory tree to traverse for byte-code',
    )
    parser.add_argument(
        '-i',
        '--ignore',
        metavar='DIRECTORY',
        action='extend',
        nargs='+',
        default=ignore_default_items,
        help='directory that should be ignored (may be specified multiple times;'
        ' default: %s)' % ' '.join(ignore_default_items),
    )
    parser.add_argument(
        '-d',
        '--debris',
        metavar='TOPIC',
        action='extend',
        nargs='*',
        default=argparse.SUPPRESS,
        choices=debris_choices,
        help='remove leftovers from popular Python development tools'
        ' (may be specified multiple times; optional: all %s; default: %s)'
        % (
            ' '.join(debris_optional_topics),
            ' '.join(debris_default_topics),
        ),
    )
    parser.add_argument(
        '-e',
        '--erase',
        metavar='PATTERN',
        action='extend',
        nargs='+',
        default=[],
        help='delete files or folders matching a globbing pattern (may be specified'
        ' multiple times); this will be interactive unless --yes is used.',
    )
    parser.add_argument(
        '-n',
        '--dry-run',
        action='store_true',
        help='show what would be done',
    )

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-q', '--quiet', action='store_true', help='be quiet')
    verbosity.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='be more verbose',
    )

    parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        help='assume yes as answer for interactive questions',
    )

    args = parser.parse_args()
    init_logging(args)

    if args.yes and not args.erase:
        parser.error('Specifying --yes only makes sense with --erase.')

    if 'debris' in args:
        if 'all' in args.debris:
            args.debris = debris_default_topics + debris_optional_topics
        elif not args.debris:
            args.debris = debris_default_topics
        log.debug('Debris topics to scan for: %s', ' '.join(args.debris))
    else:
        args.debris = []

    log.debug('Ignored directories: %s', ' '.join(args.ignore))

    return args


def init_logging(args):
    """
    Set the log level according to the -v/-q command line options.
    """
    log_level = (
        logging.FATAL if args.quiet else logging.DEBUG if args.verbose else logging.INFO
    )
    log_format = '%(message)s'
    logging.basicConfig(level=log_level, format=log_format)


def main():
    """
    Entry point for CLI application.
    """
    args = parse_arguments()

    try:
        modern.pyclean(args)
    except Exception as err:
        raise SystemExit(err)
