pyclean |latest-version|
========================

|build-status| |health| |python-support| |license|

Worried about ``.pyc`` files and ``__pycache__`` directories? Fear not!
Pyclean is here to help. Finally the single-command clean up for Python
bytecode files in your favorite directories. On any platform.

.. |latest-version| image:: https://img.shields.io/pypi/v/pyclean.svg
   :alt: Latest version on PyPI
   :target: https://pypi.org/project/pyclean
.. |build-status| image:: https://img.shields.io/travis/bittner/pyclean/master.svg
   :alt: Build status
   :target: https://travis-ci.org/bittner/pyclean
.. |health| image:: https://img.shields.io/codacy/grade/69de1364a09f41b399f95afe901826eb/master.svg
   :target: https://www.codacy.com/app/bittner/pyclean
   :alt: Code health
.. |python-support| image:: https://img.shields.io/pypi/pyversions/pyclean.svg
   :alt: Python versions
   :target: https://pypi.org/project/pyclean
.. |license| image:: https://img.shields.io/pypi/l/pyclean.svg
   :alt: Software license
   :target: https://github.com/bittner/pyclean/blob/master/LICENSE

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

The Python scripts Debian ships with its `python-minimal`_ and
`python3-minimal`_ packages can be found at:

- `salsa.debian.org/cpython-team/python-defaults
  <https://salsa.debian.org/cpython-team/python-defaults/blob/master/pyclean>`__
- `salsa.debian.org/cpython-team/python3-defaults
  <https://salsa.debian.org/cpython-team/python3-defaults/blob/master/py3clean>`__
- `salsa.debian.org/debian/pypy
  <https://salsa.debian.org/debian/pypy/blob/debian/debian/scripts/pypyclean>`__

.. _python-minimal: https://packages.debian.org/stable/python-minimal
.. _python3-minimal: https://packages.debian.org/stable/python3-minimal

Installation
============

.. code:: console

    $ pip install pyclean

Use pyclean with Tox
--------------------

If you want to avoid installing ``pyclean`` you can add it to your
``tox.ini`` file as follows:

.. code:: ini

    [testenv:clean]
    deps = pyclean
    commands = pyclean {toxinidir}

You'll then be able to run it with `Tox`_ like this:

.. code:: console

    tox -e clean

.. _Tox: https://tox.readthedocs.io/
