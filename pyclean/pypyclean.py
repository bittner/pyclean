#!/usr/bin/pypy

import argparse
import collections
import itertools
import os
import shutil
import subprocess
import sys


def abort(message):
    print >> sys.stderr, message
    sys.exit(1)


def package_modules(package):
    '''Iterate through all python modules in an installed Debian package'''
    p = subprocess.Popen(('dpkg', '-L', package), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    files, stderr = p.communicate()
    if p.returncode != 0:
        abort('Unable to list files in %s. Is it installed?' % package)

    for fn in files.splitlines():
        if fn.endswith('.py'):
            if fn.startswith('/usr/share/doc/'):
                continue
            yield fn


def installed_namespaces():
    '''Return a dictionary of package: frozenset(namespaces)'''
    ns_dir = '/usr/lib/pypy/ns'
    ns_by_pkg = {}
    for pkg in os.listdir(ns_dir):
        ns_file = os.path.join(ns_dir, pkg)
        with open(ns_file) as f:
            contents = f.read().decode('utf-8').strip()
            namespaces = [line.strip() for line in contents.splitlines()]
            ns_by_pkg[pkg] = frozenset(namespaces)
    return ns_by_pkg


def cleanup_namespaces(package, verbose):
    '''Check if a namespace is still being used and, if not:
    Remove the __init__.py.
    Remove any pycs related to it.
    '''
    ns_by_pkg = installed_namespaces()
    pkg_namespaces = ns_by_pkg.pop(package, None)
    if not pkg_namespaces:
        return
    foreign_namespaces = reduce(lambda a, b: a | b, ns_by_pkg.values(), set())
    orphan_namespaces = pkg_namespaces - foreign_namespaces
    inits_to_remove = []
    for namespace in orphan_namespaces:
        init = os.path.join('/usr/lib/pypy/dist-packages',
                            namespace.replace('.', '/'),
                            '__init__.py')
        if not os.path.exists(init):
            print 'Missing namespace init: %s' % init
            continue
        if os.path.getsize(init) != 0:
            print 'Non-empty init, ignoring: %s' % init
            continue
        inits_to_remove.append(init)

    clean_modules(inits_to_remove, verbose)
    for init in inits_to_remove:
        os.unlink(init)


def cleanup_package_modules(package, verbose):
    '''Iterate through all python modules in an installed Debian package that
    were in /usr/share/doc/, and previously byte-compiled by
    pypy << 6.0.0+dfsg-2. See #904521

    Can be removed once every pypy library has been re-uploaded, since this was
    added.
    '''
    p = subprocess.Popen(('dpkg', '-L', package), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    files, stderr = p.communicate()
    if p.returncode != 0:
        abort('Unable to list files in %s. Is it installed?' % package)

    modules = [
        fn for fn in files.splitlines()
        if fn.startswith('/usr/share/doc/') and fn.endswith('.py')]

    try:
        clean_modules(modules, verbose)
    except IOError as e:
        if e.errno != errno.ENOENT:
            raise


def find_modules(root):
    '''Iterate through all python modules in directory tree root'''
    if os.path.isfile(root):
        yield root
        return

    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith('.py'):
                yield os.path.join(dirpath, fn)


def clean_modules(modules, verbose):
    '''Remove all .pyc files for every module specified'''
    clean = collections.defaultdict(list)
    for module in modules:
        dir_, basename = os.path.split(module)
        clean[dir_].append(os.path.splitext(basename)[0])

    for dir_, basenames in clean.iteritems():
        pycache = os.path.join(dir_, '__pycache__')
        if not os.path.exists(pycache):
            continue

        empty = True
        for fn in os.listdir(pycache):
            if fn.endswith('.pyc') and fn.rsplit('.', 2)[0] in basenames:
                if verbose:
                    print 'Removing %s' % os.path.join(pycache, fn)
                os.unlink(os.path.join(pycache, fn))
            else:
                empty = False

        if empty:
            if verbose:
                print 'Pruning %s' % pycache
            os.rmdir(pycache)


def clean_directories(directories, verbose):
    '''Indiscriminately remove __pycache__ directories'''
    for root in directories:
        for dirpath, dirnames, filenames in os.walk(root):
            for dir_ in dirnames:
                if dir_ == '__pycache__':
                    if verbose:
                        print 'Removing %s' % os.path.join(dirpath, dir_)
                    shutil.rmtree(os.path.join(dirpath, dir_))


def main():
    parser = argparse.ArgumentParser(
        description='Remove byte-compiled files for a package')
    parser.add_argument('-p', '--package', metavar='PACKAGE',
                        action='append', default=[],
                        help='Debian package to byte-compile '
                             '(may be specified multiple times)')
    parser.add_argument('directory', nargs='*',
                        help='Directory tree (or file) to byte-compile')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Be more verbose')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Be quiet')
    args = parser.parse_args()

    if not (args.package or args.directory):
        parser.error('Either a package or a directory must be specified')
    if args.quiet and args.verbose:
        parser.error('--quiet and --verbose cannot both be specified')

    modules_p = set(itertools.chain(*(
        package_modules(package) for package in args.package)))
    modules_d = set(itertools.chain(*(
        find_modules(dir_) for dir_ in args.directory)))

    if args.package and args.directory:
        modules = modules_d & modules_p
    elif args.package:
        modules = modules_p
    else:
        # Split files from directories, so that we can completely clean any
        # specified directories.
        modules = set()
        directories = set()
        for fn in args.directory:
            if os.path.isfile(fn) and fn.endswith('.py'):
                modules.add(fn)
            else:
                directories.add(fn)
        clean_directories(directories, args.verbose)

    clean_modules(modules, args.verbose)

    for package in args.package:
        cleanup_namespaces(package, args.verbose)
        cleanup_package_modules(package, args.verbose)


if __name__ == '__main__':
    main()

# vim: ft=python
