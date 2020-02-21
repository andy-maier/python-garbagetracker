"""
Test the leak_check decorator.
"""

from __future__ import absolute_import, print_function

import pytest
from yagot import leak_check


class SelfRef(object):
    # pylint: disable=too-few-public-methods
    """
    A self-referencing class, for testing memory leaks.

    Due to the circular reference it creates, objects of this class cannot be
    deleted by the reference count based cleanup mechanism of Python, and
    Pythion will put them into the garbage where the garbage tracker will
    detect them.
    """
    def __init__(self):
        self.ref = self


@leak_check()
def test_leaks_empty():
    """
    Empty test function.
    """
    pass


@pytest.mark.xfail(raises=AssertionError, strict=True)
@leak_check()
def test_leaks_selfref_1():
    """
    Test function with SelfRef garbage object (that intentionally fails).
    """
    _ = SelfRef()


@leak_check(ignore_garbage=True)
def test_leaks_selfref_2():
    """
    Test function with SelfRef garbage object while ignoring all garbage
    objects.
    """
    _ = SelfRef()


@leak_check(ignore_garbage_types=[SelfRef])
def test_leaks_selfref_2():
    """
    Test function with SelfRef garbage object while ignoring SelfRef types.
    """
    _ = SelfRef()
