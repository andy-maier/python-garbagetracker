"""
Decorators for garbage tracking in specific functions or methods.
"""

from __future__ import absolute_import, print_function
import functools
from ._garbagetracker import GarbageTracker

__all__ = ['leak_check']


def leak_check(ignore_garbage=False, ignore_garbage_types=None):
    """
    Decorator that checks for new :term:`uncollectable objects` and
    :term:`garbage objects` caused by the decorated function or method, and
    raises AssertionError if such objects are detected.

    The decorated function or method needs to make sure that any objects it
    creates are deleted again, either implicitly (e.g. by a local variable
    going out of scope upon return) or explicitly. Ideally, no garbage is
    created that way, but whether that is actually the case is exactly what the
    decorator tests for. Also, it is possible that your code is clean but
    other modules your code uses are not clean, and that will surface this way.

    Note that this decorator has arguments, so it must be specified with
    parenthesis, even when relying on the default argument values::

        @yagot.leak_check()
        test_something():
            # do some tests

    Parameters:

        ignore_garbage (bool): Don't check for garbage objects at all.

        ignore_garbage_types (:term:`py:iterable`): Iterable of Python types,
          or `None`. Ignore garbage objects that are instances of any of the
          specified types. `None` or an empty iterable means not to ignore any
          types (except for :class:`py:frame` and :class:`py:code` that are
          always ignored).
    """

    def decorator_leak_check(func):
        "Decorator function for the leak_check decorator"

        @functools.wraps(func)
        def wrapper_leak_check(*args, **kwargs):
            "Wrapper function for the leak_check decorator"
            tracker = GarbageTracker.get_tracker('yagot.leak_check')
            tracker.enable()
            tracker.start()
            tracker.ignore_garbage_types(ignore_garbage_types)
            ret = func(*args, **kwargs)  # The decorated function
            tracker.stop()
            location = "{module}::{function}".format(
                module=func.__module__, function=func.__name__)
            no_leaks = not tracker.uncollectable_count
            no_garbage = ignore_garbage or not tracker.garbage
            assert no_leaks and no_garbage, tracker.assert_message(location)
            return ret

        return wrapper_leak_check

    return decorator_leak_check
