<!--
SPDX-FileCopyrightText: 2020 Peter Bittner <django@bittner.it>

SPDX-License-Identifier: GPL-3.0-or-later
-->

Contributing
============

You can contribute to this project by opening an issue or a pull request.
Feel free to ask for clarification or help by creating an issue before
you start with a pull request!

Development
-----------

You only need popular Python 3 standard tooling, including [Tox][tox],
for contributing code and running linting and tests.

PyClean has no specific runtime dependencies, only for running the test
suite you need packages such as `cli-test-helpers`. Those are installed
automatically when you run `tox`.

Tests are fundamental. When adding new features or changing existing
functionality, you must add or adapt tests in the test suite. Please ask
for help in your issue or the pull request if you struggle with that.

Running tests
-------------

Run the linters and our test suite using Tox, e.g.

```shell
# show all Tox targets
tox list
```

```shell
# run just linting and the tests for Python 3.12
tox -e lint,py312
```

```shell
# run tests with your default Python (the one executing Tox)
tox -e py
```

```shell
# run entire test suite
tox
```

The entire suite will run against all supported target operating systems
and Python versions when you create a PR on GitHub.
Make sure all tests pass, otherwise the PR will likely not get merged.

If you want to test against the various Python versions locally before
pushing take a look at [uv][uv] or [pyenv][pyenv], which both allow you
to install different Python versions on your computer in parallel.

Developing locally
------------------

You can try out the CLI by running the application as a module, e.g.

```shell
python3 -m pyclean
```

or you can make a so-called "editable install", for development:

```shell
python3 -m pip install -e .
```

Then run as usual:

```shell
pyclean --help
```

Install from repository
-----------------------

If you only want to install `pyclean` off the Git repository, e.g. in order
to try out a feature branch, you can install it on your machine like this:

```shell
pip install git+https://github.com/bittner/pyclean#egg=pyclean
```

Or, for a specific branch:

```shell
pip install git+https://github.com/bittner/pyclean@feature-branch#egg=pyclean
```

[pyenv]: https://github.com/pyenv/pyenv#installation
[tox]: https://tox.wiki/
[uv]: https://docs.astral.sh/uv/
