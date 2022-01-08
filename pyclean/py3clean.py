# coding=utf-8
"""
Python 3 pyclean implementation.

Examples:
    # all .py[co] files and __pycache__ directories from the package
    py3clean -p python3-mako
    # python3.1
    py3clean /usr/lib/python3.1/dist-packages
    # python 3.3 only
    py3clean -V 3.3 /usr/lib/python3/
    # bar/__pycache__/bar.cpython-33.py[co]
    py3clean -V 3.3 /usr/lib/foo/bar.py
    # all Python 3.X
    py3clean /usr/lib/python3/

Original source at:
https://salsa.debian.org/cpython-team/python3-defaults/blob/master/py3clean

Copyright © 2010-2012 Piotr Ożarowski <piotr@debian.org>
"""
import logging
import sys

# glob1() is not in the public documentation, UTSL.
from glob import glob1
from os import environ, remove, rmdir
from os.path import basename, dirname, exists, join, splitext

sys.path.insert(1, '/usr/share/python3/')

from debpython import files as dpf
from debpython.interpreter import Interpreter
from debpython.version import SUPPORTED, getver, vrepr

# initialize script
logging.basicConfig(format='%(levelname).1s: %(module)s:%(lineno)d: '
                           '%(message)s')
log = logging.getLogger(__name__)


def get_magic_tag_to_remove(version):
    """Returns magic tag or True if all of them should be removed."""
    i = Interpreter('python')
    map_ = {}
    for v in SUPPORTED:
        try:
            map_[v] = i.magic_tag(v)
        except Exception:
            log.debug('magic tag for %s not recognized', vrepr(v),
                      exc_info=True)
    if version not in map_:
        try:
            map_[version] = i.magic_tag(version)
        except Exception as e:
            log.error('cannot find magic tag for Python %s: %s',
                      vrepr(version), e)
            exit(4)

    tag = map_[version]
    # skip shared tags
    for v, t in map_.items():
        if v == version:
            continue
        if t == tag:
            log.info('magic tag(s) used by python%s. Nothing to remove.',
                     vrepr(v))
            exit(0)

    log.debug('magic tags to remove: %s', tag)
    return tag


def destroyer(magic_tag=None):  # ;-)
    """Remove every .py[co] file associated to received .py file.

    :param magic_tag:
        * If None, removes all associated .py[co] files from __pycache__
          directory.  If the resulting directory is empty, and is not a system
          site package, then the directory is also removed.
        * If False, removes python3.1's .pyc files only
        * Otherwise removes given magic tag from __pycache__ directory.  If
          the resulting directory is empty, and is not a system site package,
          then the directory is also removed.
    :type magic_tag: None or False or str
    """
    if magic_tag is None:

        # remove compiled files in __pycache__ directory
        def find_files_to_remove(pyfile):
            directory = join(dirname(pyfile), '__pycache__')
            fname = splitext(basename(pyfile))[0]
            for fn in glob1(directory, "%s.*" % fname):
                yield join(directory, fn)
            # remove "classic" .pyc files as well
            for filename in ("%sc" % pyfile, "%so" % pyfile):
                if exists(filename):
                    yield filename
            # workaround for http://bugs.python.org/issue22966
            if '.' in fname:
                sane_fname = join(dirname(pyfile), fname.split('.', 1)[0])
                for fn in find_files_to_remove(sane_fname):
                    yield join(directory, fn)
    elif magic_tag is False:

        # remove 3.1's .pyc files only
        def find_files_to_remove(pyfile):  # NOQA
            for filename in ("%sc" % pyfile, "%so" % pyfile):
                if exists(filename):
                    yield filename
    else:

        # remove .pyc files for no longer needed magic tags
        def find_files_to_remove(pyfile):  # NOQA
            directory = join(dirname(pyfile), '__pycache__')
            fname = splitext(basename(pyfile))[0]
            for fn in glob1(directory, "%s.%s.py[co]" % (fname, magic_tag)):
                yield join(directory, fn)
            # workaround for http://bugs.python.org/issue22966
            if '.' in fname:
                sane_fname = join(dirname(pyfile), fname.split('.', 1)[0])
                for fn in find_files_to_remove(sane_fname):
                    yield join(directory, fn)

    def myremove(fname):
        remove(fname)
        directory = dirname(fname)
        # remove __pycache__ directory if it's empty
        if directory.endswith('__pycache__'):
            try:
                rmdir(directory)
            except Exception:
                pass

    counter = 0
    try:
        while True:
            pyfile = (yield)
            for filename in find_files_to_remove(pyfile):
                try:
                    myremove(filename)
                    counter += 1
                except (IOError, OSError) as e:
                    log.error('cannot remove %s', filename)
                    log.debug(e)
    except GeneratorExit:
        log.info("removed files: %s", counter)


def main(args):
    """Entry point for Python 3"""
    if args.verbose or environ.get('PYCLEAN_DEBUG') == '1':
        log.setLevel(logging.DEBUG)
        log.debug('argv: %s', sys.argv)
        log.debug('args: %s', args)
    else:
        log.setLevel(logging.WARNING)

    if args.version:
        if args.version.endswith('3.1'):  # 3.1, -3.1
            magic_tag = False
        else:
            magic_tag = get_magic_tag_to_remove(getver(args.version))
        d = destroyer(magic_tag)
    else:
        d = destroyer()  # remove everything
    next(d)  # initialize coroutine

    if args.package:
        for pkg in args.package:
            log.info('cleaning package %s', pkg)
            pfiles = set(dpf.from_package(pkg))

    if args.directory:
        log.info('cleaning directories: %s', args.directory)
        files = set(dpf.from_directory(args.directory))
        if args.package:
            files = files & pfiles
    else:
        files = pfiles

    for filename in files:
        d.send(filename)
