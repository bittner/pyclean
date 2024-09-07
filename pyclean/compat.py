# SPDX-FileCopyrightText: 2019 Peter Bittner <django@bittner.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Cross-Python version compatibility.
"""

from argparse import _AppendAction as AppendAction


class ExtendAction(AppendAction):  # pragma: no-cover-gt-py37
    """
    Argparse "extend" action for Python < 3.8.
    A simplified backport from the Python standard library.
    """

    def __call__(self, parser, namespace, values, option_string=None):  # noqa: ARG002
        items = getattr(namespace, self.dest, None)
        items = [] if items is None else items[:]
        items.extend(values)
        setattr(namespace, self.dest, items)
