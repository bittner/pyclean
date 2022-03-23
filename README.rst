pyclean |latest-version|
========================

|checks-status| |tests-status| |scrutinizer| |codacy| |metabob| |python-support| |license|

Worried about ``.pyc`` files and ``__pycache__`` directories? Fear not!
Pyclean is here to help. Finally the single-command clean up for Python
bytecode files in your favorite directories. On any platform.

|video|

`Presented at PyConX`_, Firenze 2019.

.. |latest-version| image:: https://img.shields.io/pypi/v/pyclean.svg
   :target: https://pypi.org/project/pyclean
   :alt: Latest version on PyPI
.. |checks-status| image:: https://img.shields.io/github/workflow/status/bittner/pyclean/Checks/main?label=Checks&logo=github
   :target: https://github.com/bittner/pyclean/actions/workflows/check.yml
   :alt: GitHub Workflow Status
.. |tests-status| image:: https://img.shields.io/github/workflow/status/bittner/pyclean/Tests/main?label=Tests&logo=github
   :target: https://github.com/bittner/pyclean/actions/workflows/test.yml
   :alt: GitHub Workflow Status
.. |scrutinizer| image:: https://img.shields.io/scrutinizer/build/g/bittner/pyclean/main?logo=scrutinizer&label=%22
   :target: https://scrutinizer-ci.com/g/bittner/pyclean/
   :alt: Scrutinizer
.. |codacy| image:: https://img.shields.io/codacy/grade/69de1364a09f41b399f95afe901826eb/main.svg?logo=codacy&label=%22
   :target: https://app.codacy.com/gh/bittner/pyclean/dashboard
   :alt: Code health
.. |metabob| image:: https://img.shields.io/badge/⦿-✓-59bfbf.svg?logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAADIAAAA8CAMAAAAT6xnzAAAAz1BMVEUAAAAAAAD%2F%2F%2F%2BPj4%2BqqqpERET6%2BvqJiYn09PTr6%2BuCgoLS0tJqampQUFAkJCQKCgrg4ODFxcVycnJiYmLLy8tnZ2dMTEw7Ozs2NjalpaWfn593d3daWlpWVlZUVFQsLCwcHBwODg7w8PDc3NzDw8O8vLw%2FPz8fHx8ZGRn39%2Ffm5ubY2NjV1dXPz8%2FIyMi0tLSZmZmFhYUyMjIwMDDj4%2BOUlJRtbW1ISEgiIiISEhLt7e3AwMCvr6%2BdnZ2Hh4ddXV0qKioUFBStra1%2Bfn56enphvz08AAAAAXRSTlMAQObYZgAAArJJREFUSMfVlteWqjAARXPoVaqIvTs69u7c6eX%2Fv%2BkiIkME29Nddz%2BQFcgmyeIkgfz39O4VSktUyTk4VrRtUSxxv3dmWh6ATrJQ%2FF4DRz77u4eA%2FicOfGcIDi5ipwQRV2ieGmVcZUYbeVyHpZXC3cocN7CjlApuwEsaXdzAkiTRcJ3mK6WwuA5P7u6lRCs8riPSSg6XyBW7OlCjlV3ybWO51TLdoo0DxmuLYYZP2NJK%2FfeNLnNEUjlNz0%2FlsLI5XWF6rHSYFMIguLygTivfiLD3TaSkoLKOozxL6mnE3hBhMR2n4G%2FZ9rEH0YDRMFCZGLFDB8ZYlQFfbwLFg8KC77bbJtfgm8BH1nKplVGzLHfIAV97Ywi9vQF8120iICHUeh9RjqAPNYBXXeAxUGaY%2FISJlBVKoeKihs9ykoiSOZ54udECezoTSqHiIiHEnSCkYB4ejsf0svQT2ZAO2RmqeOLf7QpMDgHOICzymeteLoZNBA6sIAhucJ3y9bc%2Fkk4rtVjoYSZwNW%2FekgqHHGj4EoKiVcYHpXix8lLFi8AIzKMGZ7BX%2FrzjvTRd%2B3gtUnOxY4VbFVBdF5Ul%2BMcomxwPoGIJXfq79OPgM7KSA5Cby7%2BplM195RnwsrYkPkikPFJHoUDjAmWSAEfUuMlANttqx7I6I7O1r1uAllTi2ZSZcNIW6%2FD1hoGQvp%2BfSkw3UtIBGAUjE5Eip66jgaX70SVzAWQ4DWpboqaz0XGKEZU%2FKSXNU90TufGjhQMLcn7361eNnqZwanvA7Jki4sJR%2BfC8kgTmyGp7RplRo%2FfWVpQYk1sk9lgaPzWTqj13dvTJR6PcdFjS3LT533tipH9gmncrpIfLOCSNh0v0SRbbC0aDI5nUcA6dnIOtIIPPDbnIW%2BHBSA6ooJTIDRSVyqJeX1aVOflX%2FAUMXjWVQWa95AAAAABJRU5ErkJggg%3D%3D
   :target: https://metabob.com/github/bittner/pyclean
   :alt: Visualizer
.. |python-support| image:: https://img.shields.io/pypi/pyversions/pyclean.svg
   :target: https://pypi.org/project/pyclean
   :alt: Python versions
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

Use pyclean with Tox
--------------------

If you want to avoid installing ``pyclean`` you can add it to your
``tox.ini`` file as follows:

.. code:: ini

    [testenv:clean]
    skip_install = true
    deps = pyclean
    commands = pyclean {posargs:.}

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
