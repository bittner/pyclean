"""
Modern, cross-platform, pure-Python pyclean implementation.
"""
import logging

try:
    from pathlib import Path
except ImportError:  # Python 2.7, PyPy2
    from warnings import warn
    warn("Python 3 required for modern implementation. Python 2 is obsolete.")

BYTECODE_FILES = ['.pyc', '.pyo']
BYTECODE_DIRS = ['__pycache__']
DEBRIS_TOPICS = {
    'build': [
        'dist/**/*',
        'dist/',
        'sdist/**/*',
        'sdist/',
        '*.egg-info/**/*',
        '*.egg-info/',
    ],
    'cache': [
        '.cache/**/*',
        '.cache/',
    ],
    'coverage': [
        '.coverage',
        'coverage.json',
        'coverage.lcov',
        'coverage.xml',
        'htmlcov/**/*',
        'htmlcov/',
    ],
    'jupyter': [
        '.ipynb_checkpoints/**/*',
        '.ipynb_checkpoints/',
    ],
    'pytest': [
        '.pytest_cache/**/*',
        '.pytest_cache/',
        'pytestdebug.log',
    ],
    'tox': [
        '.tox/**/*',
        '.tox/',
    ],
}

log = logging.getLogger(__name__)


class Runner:  # pylint: disable=too-few-public-methods
    """Module-level configuration and value store."""
    rmdir_count = 0
    rmdir_failed = 0
    unlink_count = 0
    unlink_failed = 0


def remove_file(fileobj):
    """Attempt to delete a file object for real."""
    log.debug("Deleting file: %s", fileobj)
    try:
        fileobj.unlink()
        Runner.unlink_count += 1
    except OSError as err:
        log.debug("File not deleted. %s", err)
        Runner.unlink_failed += 1


def remove_directory(dirobj):
    """Attempt to remove a directory object for real."""
    log.debug("Removing directory: %s", dirobj)
    try:
        dirobj.rmdir()
        Runner.rmdir_count += 1
    except OSError as err:
        log.debug("Directory not removed. %s", err)
        Runner.rmdir_failed += 1


def print_filename(fileobj):
    """Only display the file name, used with --dry-run."""
    log.debug("Would delete file: %s", fileobj)
    Runner.unlink_count += 1


def print_dirname(dirobj):
    """Only display the directory name, used with --dry-run."""
    log.debug("Would delete directory: %s", dirobj)
    Runner.rmdir_count += 1


def pyclean(args):
    """Cross-platform cleaning of Python bytecode."""
    Runner.unlink = print_filename if args.dry_run else remove_file
    Runner.rmdir = print_dirname if args.dry_run else remove_directory
    Runner.ignore = args.ignore

    for dir_name in args.directory:
        directory = Path(dir_name)

        log.info("Cleaning directory %s", directory)
        descend_and_clean(directory, BYTECODE_FILES, BYTECODE_DIRS)

    for topic in args.debris:
        remove_debris_for(topic, directory)

    log.info("Total %d files, %d directories %s.",
             Runner.unlink_count, Runner.rmdir_count,
             "would be removed" if args.dry_run else "removed")

    if Runner.unlink_failed or Runner.rmdir_failed:
        log.debug("%d files, %d directories could not be removed.",
                  Runner.unlink_failed, Runner.rmdir_failed)


def descend_and_clean(directory, file_types, dir_names):
    """
    Walk and descend a directory tree, cleaning up files of a certain type
    along the way. Only delete directories if they are empty, in the end.
    """
    for child in sorted(directory.iterdir()):
        if child.is_file():
            if child.suffix in file_types:
                Runner.unlink(child)
        elif child.is_dir():
            if child.name in Runner.ignore:
                log.debug("Skipping %s", child)
            else:
                descend_and_clean(child, file_types, dir_names)

            if child.name in dir_names:
                Runner.rmdir(child)
        else:
            log.debug("Ignoring %s", child)


def remove_debris_for(topic, directory):
    """
    Clean up debris for a specific topic.

    Note that we sort the file system objects in *reverse order* and first
    delete *all files* before removing directories. This way we make sure
    that the directories that are deepest down in the hierarchy are empty
    when we attempt to remove them.
    """
    log.debug("Scanning for debris of %s ...", topic.title())

    for path_glob in DEBRIS_TOPICS[topic]:

        all_names = sorted(directory.glob(path_glob), reverse=True)
        dirs = (name for name in all_names if name.is_dir() and not name.is_symlink())
        files = (name for name in all_names if not name.is_dir() or name.is_symlink())

        for file_object in files:
            Runner.unlink(file_object)

        for dir_object in dirs:
            Runner.rmdir(dir_object)
