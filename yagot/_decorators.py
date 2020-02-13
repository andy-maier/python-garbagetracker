"""
Decorators for garbage tracking in specific functions or methods.
"""

from __future__ import absolute_import, print_function
import functools
from ._garbagetracker import GarbageTracker

__all__ = ['garbage_tracked']


def garbage_tracked(func):
    """
    Decorator that performs garbage tracking for the decorated function
    or method.

    This decorator should be used on test functions that specifically test for
    garbage objects.

    The decorated test function or method needs to make sure that any objects it
    creates are either explicitly deleted again before the function returns,
    or by means of their referencing variable going out of scope.

    Any objects Python added to the garbage collector during execution of
    the decorated function or method will be reported by this decorator by
    raising an AssertionError exception.

    The decorator is signature-preserving, and the function or method can have
    any signature.
    """

    def wrapper_func(*args, **kwargs):
        """
        Wrapper function that is invoked instead of the decorated function.

        It puts garbage tracking around the invocation of the decorated function
        and reports any garbage objects by raising an AssertionError exception.
        """

        tracker = GarbageTracker.get_tracker('decorated')
        tracker.enable()
        tracker.start()

        ret = func(*args, **kwargs)

        tracker.stop()
        if tracker.garbage:
            location = "{file}::{func}". \
                format(file=func.__module__, func=func.__name__)
            tracker.assert_no_garbage(location)

        return ret

    return functools.update_wrapper(wrapper_func, func)
