"""
Mock objects for tests of the modern implementation.
"""
try:
    from pathlib import Path
    from unittest.mock import Mock
except ImportError:  # Python 2.7, PyPy2
    import pytest
    pytest.importorskip("pathlib")


class FilesystemObjectMock(Mock):

    def __init__(self, *args, **kwargs):
        name = kwargs['name'] if 'name' in kwargs else args[0]
        super().__init__(autospec=Path(name), **kwargs)
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def is_file(self):
        return False

    def is_dir(self):
        return False

    def is_symlink(self):
        return False


class DirectoryMock(FilesystemObjectMock):

    def __init__(self, **kwargs):
        super().__init__('a-dir', **kwargs)

    def is_dir(self):
        return True


class FileMock(FilesystemObjectMock):

    def __init__(self, **kwargs):
        super().__init__('a-file', **kwargs)

    def is_file(self):
        return True


class SymlinkMock(FilesystemObjectMock):

    def __init__(self, **kwargs):
        super().__init__('a-symlink', **kwargs)

    def is_symlink(self):
        return True
