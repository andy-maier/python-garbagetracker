"""
Yagot - Yet Another Garbage Object Tracker for Python.

If the objects that are created and deleted again cannot be completely
released if their reference count drops to zero (e.g. in the presence of
circular references), Python puts them into the garbage collector for
subsequent, more elaborate treatment. That more elaborate treatment is able
to release some of these objects, but not all of them. The objects that can
eventually be released only create a delay in being released, while objects
that cannot be released with the more elaborate treatment keep their
memory permanently (i.e. as long as the Python process lives), representing
a memory leak.
"""

from __future__ import absolute_import, print_function

# There are submodules, but users shouldn't need to know about them.
# Importing just this module is enough.
from ._decorators import *  # noqa: F403,F401
from ._garbagetracker import *  # noqa: F403,F401
from ._version import __version__  # noqa: F401
