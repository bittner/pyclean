#!/usr/bin/env python3
"""
Packaging setup for pyclean
"""
from os.path import abspath, dirname, join
from setuptools import find_packages, setup

import pyclean as package


def read_file(filename):
    """Get the contents of a file"""
    with open(join(abspath(dirname(__file__)), filename)) as file:
        return file.read()


setup(
    name=package.__name__,
    version=package.__version__,
    license=package.__license__,
    author=package.__author__,
    author_email=package.__email__,
    description=package.__doc__.strip(),
    long_description=read_file('README.rst'),
    long_description_content_type='text/x-rst',
    url=package.__url__,
    packages=find_packages(exclude=['test*']),
    include_package_data=True,
    keywords=['python', 'bytecode', 'cli', 'tools'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'pyclean = pyclean.cli:main',
            'py2clean = pyclean.cli:py2clean',
            'py3clean = pyclean.cli:py3clean',
            'pypyclean = pyclean.cli:pypyclean',
        ],
    },
)
