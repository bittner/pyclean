# coding=utf-8
"""
Python 3 pyclean implementation.

Copyright 2020 James Hansen
"""

import os
import argparse
from os.path import join as os_join

def find_files(start_dir: str) -> tuple:
    """Find all .pyc[o] files as well as all __pycache__ directories.

    : param start_dir:
        * The starting directory to walk through to find files
          and directories.
    :type start_dir: str

    Returns a tuple of:
        - a list of directories found that are called __pycache__
        - a list of .pyc[o] files to remove
        - a list of directories that can be removed after the files
          are removed
    
    Note that the first and third lists may not be equal.
    """
    dirs_to_check = list()

    # Walk the tree and find any directory named __pycache__
    for root, dirs, files in os.walk(start_dir):
        if '__pycache__' in dirs:
            dirs_to_check.append(os_join(root, '__pycache__'))

    files_to_remove = list()
    dirs_to_remove = list()

    # In the found directories, look for .pyc or .pyco files.
    for d in dirs_to_check:
        with os.scandir(d) as dir_it:
            pyc_count = 0
            dir_count = 0
            for item in dir_it:
                dir_count += 1
                if item.name.endswith('.pyc') or item.name.endswith('.pyco'):
                    pyc_count += 1
                    files_to_remove.append(os_join(d, item.name))
            # If this is true, we can also unlink the directory
            # since it will be empty
            if dir_count == pyc_count:
                dirs_to_remove.append(d)

    return dirs_to_check, files_to_remove, dirs_to_remove

def remove_files_and_dirs(files: list, dirs: list) -> None:
    """Removes the named files and directories.

    :param files:
        * List of files to remove.
    :param dirs:
        * List of directories to remove.
    :type files: list
    :type dirs: list

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

def _make_arg_parser() -> argparse.ArgumentParser:
    """Makes the parser for the command line arguments.
    """
    parser = argparse.ArgumentParser(description="Removes .pyc files and __pycache__ directories from a tree")
    parser.add_argument("root_dir",
                        metavar="ROOT_PATH",
                        help="Path to start searching for file in.")
    return parser    

def main(args: argparse.Namespace) -> None:
    """Entry point for Python 3"""
    dirs_to_check, files_to_remove, dirs_to_remove = find_files(args.root_dir)
    print(f"Found {len(files_to_remove)} files to remove in {len(dirs_to_check)} directories. Can remove {len(dirs_to_remove)} directories.")
    remove_files_and_dirs(files_to_remove, dirs_to_remove)

if __name__ == "__main__":
    parser = _make_arg_parser()
    args = parser.parse_args()
    main(args)
