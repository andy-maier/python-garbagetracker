"""
garbagetracker - Tracker for memory leaks written in pure Python
"""

# There are submodules, but users shouldn't need to know about them.
# Importing just this module is enough.

from __future__ import absolute_import
import sys
from ._version import __version__  # noqa: F401

_PY_M = sys.version_info[0]
_PY_N = sys.version_info[1]

# Keep these Python versions in sync with setup.py
if _PY_M == 2 and _PY_N < 7:
    raise RuntimeError(
        "On Python 2, garbagetracker requires "
        "Python 2.7")
elif _PY_M == 3 and _PY_N < 5:
    raise RuntimeError(
        "On Python 3, garbagetracker requires "
        "Python 3.5 or higher")
