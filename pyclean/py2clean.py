# coding=utf-8
"""
Python 2 pyclean implementation.

Examples:
    # all .py[co] files from the package
    pyclean -p python-mako
    # python2.6
    pyclean /usr/lib/python2.6/dist-packages

Original source at:
https://salsa.debian.org/cpython-team/python-defaults/blob/master/pyclean

Copyright © 2010-2012 Piotr Ożarowski <piotr@debian.org>
"""
import logging
import sys
from os import environ, remove
from os.path import exists

sys.path.insert(1, '/usr/share/python/')

from debpython import files as dpf
from debpython.namespace import add_namespace_files

# initialize script
logging.basicConfig(format='%(levelname).1s: %(module)s:%(lineno)d: '
                           '%(message)s')
log = logging.getLogger(__name__)


def destroyer():  # ;-)
    """Removes every .py[co] file associated to received .py file."""

    def find_files_to_remove(pyfile):
        for filename in ("%sc" % pyfile, "%so" % pyfile):
            if exists(filename):
                yield filename

    counter = 0
    try:
        while True:
            pyfile = (yield)
            for filename in find_files_to_remove(pyfile):
                try:
                    log.debug('removing %s', filename)
                    remove(filename)
                    counter += 1
                except (IOError, OSError) as e:
                    log.error('cannot remove %s', filename)
                    log.debug(e)
    except GeneratorExit:
        log.info("removed files: %s", counter)


def main(args):
    """Entry point for Python 2"""
    if args.verbose or environ.get('PYCLEAN_DEBUG') == '1':
        log.setLevel(logging.DEBUG)
        log.debug('argv: %s', sys.argv)
        log.debug('args: %s', args)
    else:
        log.setLevel(logging.WARNING)

    d = destroyer()
    d.next()  # initialize coroutine

    if args.package:
        for pkg in args.package:
            log.info('cleaning package %s', pkg)
            pfiles = dpf.from_package(pkg, extensions=('.py', '.so'))
            pfiles = add_namespace_files(pfiles, pkg, action=False)
            pfiles = set(dpf.filter_out_ext(pfiles, ('.so',)))

    if args.directory:
        log.info('cleaning directories: %s', args.directory)
        files = dpf.from_directory(args.directory, extensions=('.py', '.so'))
        files = add_namespace_files(files, action=False)
        files = set(dpf.filter_out_ext(files, ('.so',)))
        if args.package:
            files = files & pfiles
    else:
        files = pfiles

    for filename in files:
        d.send(filename)
