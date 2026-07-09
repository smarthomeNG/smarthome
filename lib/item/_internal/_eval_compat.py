#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-2025   Martin Sinn                         m.sinn@gmx.de
#########################################################################
#  This file is part of SmartHomeNG.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

"""
lib/item/_eval_compat.py
========================

.. warning:: DEPRECATED COMPATIBILITY SHIM — scheduled for removal.

Before the eval logic was extracted from ``lib/item/item.py`` into
``lib/item/_eval.py``, every ``eval()`` call ran inside ``item.py``
and inherited that module's full namespace as an unintended side-effect.
This made modules such as ``datetime``, ``time``, ``os``, ``re`` and
others silently available to user-written eval expressions, even though
they were never part of the documented API.

The refactored code now passes an *explicit* namespace to ``eval()`` via
:func:`_make_eval_env` (defined in ``_eval.py``).  User configurations
that relied on the previously leaked names may therefore raise
``NameError`` with the new code.

This module provides a single fallback function —
:func:`_eval_with_legacy_fallback` — that catches those failures, retries
with the wide legacy namespace, logs a deprecation warning, and returns
the result so that the item continues working.  Each call site is marked
with ``# COMPAT-SHIM`` so it is easy to locate.

Removal procedure
-----------------
When the project is ready to enforce the explicit namespace:

1. **Delete this file** (``_eval_compat.py``).

2. In ``_eval.py`` — remove the import line marked ``# COMPAT-SHIM``
   and every ``except`` block whose body is marked ``# COMPAT-SHIM``;
   in each case the block can simply be deleted because primary-eval
   failures are already handled by the surrounding try/except that was
   there before.

3. In ``_casting.py`` — same as step 2.

After removal, any user expression that references an undocumented name
will produce a plain error log (the same message that already appears as
the second line of the fallback warning today).
"""

import logging

logger = logging.getLogger('lib.item')

# ---------------------------------------------------------------------------
# Sentinel
# ---------------------------------------------------------------------------

#: Returned by :func:`_eval_with_legacy_fallback` when the legacy namespace
#: also fails to evaluate the expression.  Callers check
#: ``if result is _EVAL_FAILED`` to distinguish this from a legitimate
#: ``None`` result.
_EVAL_FAILED = object()

# ---------------------------------------------------------------------------
# Deprecation notice (single string so it prints consistently everywhere)
# ---------------------------------------------------------------------------

_COMPAT_NOTE = (
    'This compatibility retry will be removed in a future release. '
    'Please update your configuration to use only the documented eval '
    'variables: sh, shtime, items, math, uf, env, value, datetime, time.'
)

# ---------------------------------------------------------------------------
# _make_legacy_namespace
# ---------------------------------------------------------------------------


def _make_legacy_namespace(base_ns: dict) -> dict:
    """
    .. deprecated::
        Remove together with :func:`_eval_with_legacy_fallback`.

    Return a copy of *base_ns* extended with every module that was
    previously reachable via ``item.py``'s module globals.

    The most commonly needed additions are ``datetime`` and ``time`` (both
    referenced in the official documentation examples).  The remaining
    modules (``os``, ``re``, ``sys``, …) were technically accessible but
    undocumented; they are included here so that any expression which
    happened to rely on them continues to work during the transition.
    """
    import time
    import datetime
    import os
    import re
    import sys
    import json
    import copy
    import threading
    import ast
    import inspect
    import dateutil.tz as tz

    extended = dict(base_ns)
    extended.update(
        {
            # explicitly noted in item.py as intended for eval expressions
            'time': time,
            'datetime': datetime,
            # other item.py globals — undocumented but previously reachable
            'os': os,
            're': re,
            'sys': sys,
            'json': json,
            'copy': copy,
            'threading': threading,
            'ast': ast,
            'inspect': inspect,
            'tz': tz,
        }
    )
    return extended


# ---------------------------------------------------------------------------
# _eval_with_legacy_fallback
# ---------------------------------------------------------------------------


def _eval_with_legacy_fallback(expr: str, primary_ns: dict, item, context: str, original_exc: Exception):
    """
    .. deprecated::
        Remove this function, :func:`_make_legacy_namespace`, and all call
        sites marked ``# COMPAT-SHIM`` in a future release.

    Retry ``eval(expr)`` using the legacy wide namespace when the
    primary explicit-namespace eval failed.

    :param expr:         The expression string that failed.
    :param primary_ns:   The explicit namespace that was tried first.
    :param item:         The ``Item`` instance (used for logging only).
    :param context:      Short label for log messages (e.g. ``'eval'``).
    :param original_exc: The exception raised by the primary eval attempt.
    :returns:            The evaluated result, or :data:`_EVAL_FAILED` when
                         the legacy namespace also cannot evaluate *expr*.
    """
    # The legacy namespace only adds module names (datetime, re, os, …).
    # Runtime errors (ZeroDivisionError, KeyError, TypeError, …) will fail
    # identically in both namespaces, so retrying is pointless — and logging
    # a "failed with both namespaces" warning is misleading noise.
    # Only NameError can be fixed by the wider namespace.
    if not isinstance(original_exc, NameError):
        return _EVAL_FAILED

    legacy_ns = _make_legacy_namespace(primary_ns)
    try:
        result = eval(expr, legacy_ns)
    except Exception as legacy_exc:
        logger.warning(
            f"Item '{item._path}': {context}: "
            f'eval failed with both the explicit namespace '
            f'({original_exc.__class__.__name__}: {original_exc}) '
            f'and the legacy namespace '
            f'({legacy_exc.__class__.__name__}: {legacy_exc}).'
        )
        return _EVAL_FAILED

    # Legacy eval succeeded — log the deprecation notice and return.
    if isinstance(original_exc, NameError):
        missing = (str(original_exc).split("'")[1:2] or ['?'])[0]
        logger.warning(
            f"Item '{item._path}': {context}: "
            f"name '{missing}' is not in the standard eval environment "
            f'but was found via the legacy namespace. {_COMPAT_NOTE}'
        )
    else:
        logger.warning(
            f"Item '{item._path}': {context}: "
            f'primary eval raised {original_exc.__class__.__name__} '
            f'({original_exc}) but the legacy namespace succeeded. '
            f'{_COMPAT_NOTE}'
        )
    return result
