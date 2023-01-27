pyclean |latest-version|
========================

|checks-status| |tests-status| |scrutinizer| |codacy| |python-versions| |python-impl| |license|

Worried about ``.pyc`` files and ``__pycache__`` directories? Fear not!
PyClean is here to help. Finally the single-command clean up for Python
bytecode files in your favorite directories. On any platform.

|video|

`Presented at PyConX`_, Firenze 2019.

.. |latest-version| image:: https://img.shields.io/pypi/v/pyclean.svg
   :target: https://pypi.org/project/pyclean
   :alt: Latest version on PyPI
.. |checks-status| image:: https://img.shields.io/github/actions/workflow/status/bittner/pyclean/check.yml?branch=main&label=Checks&logo=github
   :target: https://github.com/bittner/pyclean/actions/workflows/check.yml
   :alt: GitHub Workflow Status
.. |tests-status| image:: https://img.shields.io/github/actions/workflow/status/bittner/pyclean/test.yml?branch=main&label=Tests&logo=github
   :target: https://github.com/bittner/pyclean/actions/workflows/test.yml
   :alt: GitHub Workflow Status
.. |scrutinizer| image:: https://img.shields.io/scrutinizer/build/g/bittner/pyclean/main?logo=scrutinizer&label=%22
   :target: https://scrutinizer-ci.com/g/bittner/pyclean/
   :alt: Scrutinizer
.. |codacy| image:: https://img.shields.io/codacy/grade/69de1364a09f41b399f95afe901826eb/main.svg?logo=codacy&label=%22
   :target: https://app.codacy.com/gh/bittner/pyclean/dashboard
   :alt: Code health
.. |python-versions| image:: https://img.shields.io/pypi/pyversions/pyclean.svg
   :target: https://pypi.org/project/pyclean
   :alt: Python versions
.. |python-impl| image:: https://img.shields.io/pypi/implementation/pyclean.svg
   :target: https://pypi.org/project/pyclean
   :alt: Python implementations
.. |license| image:: https://img.shields.io/pypi/l/pyclean.svg
   :target: https://github.com/bittner/pyclean/blob/main/LICENSE
   :alt: Software license
.. |video| image:: https://asciinema.org/a/g8Q2ljghA7W4RD9cb3Xz100Tl.svg
   :target: https://asciinema.org/a/g8Q2ljghA7W4RD9cb3Xz100Tl
   :alt: PyClean and its future
.. _Presented at PyConX: https://slides.com/bittner/pyconx-pyclean/

Wait! What is bytecode?
-----------------------

Bytecode is opcodes for the `Python Virtual Machine`_. -- Confused?

If you want to deep-dive into the topic watch the 2013 EuroPython talk
`"All Singing All Dancing Python Bytecode"`_ by Larry Hastings.
Otherwise James Bennett's `"Introduction to Python bytecode"`_ should
provide you with just the sound understanding of what it is all about.

.. _Python Virtual Machine: https://www.ics.uci.edu/~brgallar/week9_3.html
.. _"All Singing All Dancing Python Bytecode":
    https://www.youtube.com/watch?v=0IzXcjHs-P8
.. _"Introduction to Python bytecode":
    https://opensource.com/article/18/4/introduction-python-bytecode

Why not simply use ``rm **/*.pyc`` or ``find -name '*.py?' -delete``?
---------------------------------------------------------------------

If you're happy with ``rm`` or ``find``, go for it! When I was `looking
for a simple, concise solution for everybody`_ I figured people are
struggling, and simple things are more complicated than they appear at
first sight.

Also, there is a ``pyclean`` command (and its siblings) on Debian. And,
well, only on Debian as it turns out. Not that I'm a big fan of Mircosoft
Windos, but why ignore the biggest Python population on this planet?
(As if they weren't punished enough already using this unfree piece of
software!)

.. _looking for a simple, concise solution for everybody:
    https://stackoverflow.com/questions/785519/how-do-i-remove-all-pyc-files-from-a-project

Debian
------

Just for reference, the Python scripts Debian ships with its
`python-minimal`_ and `python3-minimal`_ packages can be found at:

- pyclean: `salsa.debian.org/cpython-team/python-defaults
  <https://salsa.debian.org/cpython-team/python-defaults/blob/master/pyclean>`__
- py3clean: `salsa.debian.org/cpython-team/python3-defaults
  <https://salsa.debian.org/cpython-team/python3-defaults/blob/master/py3clean>`__
- pypyclean: `salsa.debian.org/debian/pypy
  <https://salsa.debian.org/debian/pypy/blob/debian/debian/scripts/pypyclean>`__

.. _python-minimal: https://packages.debian.org/stable/python-minimal
.. _python3-minimal: https://packages.debian.org/stable/python3-minimal

Installation
============

.. code:: console

    $ pip install pyclean

Usage
=====

.. code:: console

    $ pyclean --help

If you want to explicitly operate the Debian-specific implementation:

.. code:: console

    $ py2clean --help
    $ py3clean --help
    $ pypyclean --help

Clean up all bytecode in the current directory tree, and explain verbosely:

.. code:: console

    $ pyclean -v .

Clean up all bytecode for a Debian package: (may require root permissions)

.. code:: console

    $ pyclean -p python3-keyring --legacy

Clean up debris
---------------

PyClean can clean up leftovers, generated data and temporary files from
popular Python development tools in their default locations, along with
Python bytecode. The following topics are currently covered:

- Cache (general purpose folder for several tools, e.g. Python eggs, legacy Pytest)
- Coverage (coverage database, and supported file formats)
- Packaging (build files and folders)
- Pytest (build files and folders)
- Jupyter (notebook checkpoints) – *optional*
- Tox (tox environments) – *optional*

*Example:* Dry-run a cleanup of bytecode and tool debris in verbose mode
(to see what would be deleted):

.. code:: console

    $ pyclean . --debris --verbose --dry-run

Remove arbitrary file system objects
------------------------------------

PyClean also lets you remove free-form targets using globbing. Note that
this is **potentially dangerous**: You can delete everything anywhere in
the file system, including the entire project you're working on. For this
reason, the ``--erase`` option has a few artificial constraints:

- It doesn't do recursive deletion by itself, which means that you have
  to specify the directory and its contents, separately and explicitly.
- The above entails that you're responsible for the deletion order, i.e.
  removal of a directory will only work if you asked to delete all files
  inside first.
- You're prompted interactively to confirm deletion, unless you add the
  ``--yes`` option, in addition.

.. code:: console

    $ pyclean . --erase tmp/**/* tmp/

The above would delete the entire ``tmp/`` directory with all subdirectories
inside the current folder. If you omit the final ``tmp/`` you'll leave the
empty ``tmp`` directory in place. (**WARNING!** Don't put the ``.`` *after*
the ``--erase`` option! Obviously, your project files will all be deleted.)

Use pyclean with Tox
--------------------

If you want to avoid installing ``pyclean`` you can add it to your
``tox.ini`` file as follows:

.. code:: ini

    [testenv:clean]
    skip_install = true
    deps = pyclean
    commands = pyclean {posargs:. --debris}

You'll then be able to run it with `Tox`_ like this:

.. code:: console

    $ tox -e clean

.. _Tox: https://tox.readthedocs.io/

Development
===========

If you want to help out please see our `contribution guide`_.

.. _contribution guide: https://github.com/bittner/pyclean/blob/main/CONTRIBUTING.md

Roadmap (for v3.0.0)
--------------------

#. Replace original Debian scripts (current ``--legacy``) by a single,
   pure Python, Python 3-only code base that serves all target platforms.
#. Reduce the package dependencies to an absolute minimum for maximum
   portability.
#. Add additional CLI options to delete debris from builds, testing and
   packaging (build/, .cache/, dist/, .pytest_cache/, .tox/ and
   free-form targets).
