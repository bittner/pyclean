"""
Modern, cross-platform, pure-Python pyclean implementation.

Copyright © 2020 James P. Hansen <jphansen@gmail.com>
"""


import os
from os.path import join as os_join


def find_files(start_dir):
    """Find all .pyc[o] files as well as all __pycache__ directories.

    Returns a tuple consisting of:
        - a list of directories found that are called __pycache__
        - a list of .pyc[o] files to remove
        - a list of directories that can be removed after the files
          are removed

    Note that the first and third lists may not be equal.
    """
    dirs_to_check = list()

    for root, dirs, _ in os.walk(start_dir):
        if '__pycache__' in dirs:
            dirs_to_check.append(os_join(root, '__pycache__'))

    files_to_remove = list()
    dirs_to_remove = list()

    for directory in dirs_to_check:
        with os.scandir(directory) as dir_it:
            pyc_count = 0
            dir_count = 0
            for item in dir_it:
                dir_count += 1
                if item.name.endswith('.pyc') or item.name.endswith('.pyco'):
                    pyc_count += 1
                    files_to_remove.append(os_join(directory, item.name))
            if dir_count == pyc_count:
                dirs_to_remove.append(directory)

    return dirs_to_check, files_to_remove, dirs_to_remove


def remove_files_and_dirs(files, dirs):
    """Removes the named files and directories.

    Note, this will swallow OSErrors raised if permissions are
    wrong or something else fails in the remove operations.
    It will print an error.
    """
    for f_name in files:
        try:
            os.remove(f_name)
        except OSError as os_err:
            print(f"Failed to remove {f_name}")
            print(f"    {str(os_err)}")

    for dir_name in dirs:
        try:
            os.rmdir(dir_name)
        except OSError as os_err:
            print(f"Failed to remove {dir_name}")
            print(f"    {str(os_err)}")


def pyclean(args):
    """Cross-platform cleaning of Python bytecode"""
    if not args:
        return
    dirs_to_check, files_to_remove, dirs_to_remove = list(), list(), list()
    for directory in args.directory:
        check_dirs, files, dirs = find_files(directory)
        dirs_to_check.extend(check_dirs)
        files_to_remove.extend(files)
        dirs_to_remove.extend(dirs)
    if files_to_remove or dirs_to_remove:
        # pylint: disable=line-too-long
        msg = "Found {} files to remove in {} directories. Can remove {} directories.".format(len(files_to_remove),  # noqa: E501
                                                                                              len(dirs_to_check),  # noqa: E501
                                                                                              len(dirs_to_remove))  # noqa: E501
        print(msg)
        remove_files_and_dirs(files_to_remove, dirs_to_remove)
