"""
Modern, cross-platform, pure-Python pyclean implementation.
"""
import logging

try:
    from pathlib import Path
except ImportError:  # Python 2.7, PyPy2
    from warnings import warn
    warn("Python 3 required for modern implementation. Python 2 is obsolete.")

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

    for directory in args.directory:
        log.info("Cleaning directory %s", directory)
        descend_and_clean_bytecode(Path(directory))

    log.info("Total %d files, %d directories %s.",
             Runner.unlink_count, Runner.rmdir_count,
             "would be removed" if args.dry_run else "removed")

    if Runner.unlink_failed or Runner.rmdir_failed:
        log.debug("%d files, %d directories could not be removed.",
                  Runner.unlink_failed, Runner.rmdir_failed)


def descend_and_clean_bytecode(directory):
    """
    Walk and descend a directory tree, cleaning up bytecode files along
    the way. Only delete bytecode folders if they are empty in the end.
    """
    for child in directory.iterdir():
        if child.is_file():
            if child.suffix in ['.pyc', '.pyo']:
                Runner.unlink(child)
        elif child.is_dir():
            if child.name in Runner.ignore:
                log.debug("Skipping %s", child)
            else:
                descend_and_clean_bytecode(child)

            if child.name == '__pycache__':
                Runner.rmdir(child)
        else:
            log.debug("Ignoring %s", child)
