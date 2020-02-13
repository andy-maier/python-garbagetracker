"""
Test the garbage_tracked decorator.
"""

from __future__ import absolute_import, print_function

import pytest
from yagot import garbage_tracked


class SelfRef(object):
    # pylint: disable=too-few-public-methods
    """
    A self-referencing class, for testing memory leaks.

    Due to the reference circle it creates, objects of this class cannot be
    deleted by the reference count based cleanup mechanism of Python, and
    Pythion will put them into the garbage where the garbage tracker will
    detect them.
    """
    def __init__(self):
        self.ref = self


@garbage_tracked
def test_leaks_empty():
    """
    Empty test function.
    """
    pass


@pytest.mark.xfail(raises=AssertionError, strict=True)
@garbage_tracked
def test_leaks_selfref():
    """
    Test function with SelfRef object that intentionally fails.
    """
    _ = SelfRef()
