Contributing
============

You can contribute to this project by opening a ticket or a pull request.
Feel free to ask for clarification or help by creating a ticket before you
start with a pull request!

Development
-----------

You only need Python 3 standard tools, Python 2 for backward compatibility,
including Tox, for contributing code and running linting and tests.

PyClean has no specific runtime dependencies, only for running the test
suite you need packages such as `cli_test_helpers`. Those are installed
automatically when you run `tox`.

Tests are fundamental. When adding new features or changing existing
functionality, you must add or adapt tests in the test suite. Please ask
for help in your ticket or the pull request if you struggle with that.

Running tests
-------------

Run the linters and our test suite using Tox, e.g.

```console
# show all Tox targets
tox -lv
```
```console
# run just flake8 and the test for Python 3.7
tox -e flake8,py37
```
```console
# run entire test suite
tox
```

The entire suite will run against all supported target operating systems
and Python versions when you create a PR on GitHub.
Make sure all tests pass, otherwise the PR will likely not get merged.

Developing locally
------------------

You can try out the CLI by running the application as a module, e.g.

```console
python3 -m pyclean
```

or you can make a so-called "editable install", for development:

```console
python3 setup.py develop
# or:
python3 -m pip install -e .
```

Then run as usual:

```console
pyclean --help
```

Install from repository
-----------------------

If you only want to install `pyclean` off the Git repository, e.g. in order
to try out a feature branch, you can install it on your machine like this:

```console
python3 -m pip install git+https://github.com/bittner/pyclean#egg=pyclean
```

Or, for a specific branch:

```console
python3 -m pip install git+https://github.com/bittner/pyclean@feature-branch#egg=pyclean
```
