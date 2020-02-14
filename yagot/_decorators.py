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

    def garbage_tracked_wrapper(*args, **kwargs):
        """
        Wrapper function for the @garbage_tracked decorator.
        """
        tracker = GarbageTracker.get_tracker('yagot.garbage_tracked')
        tracker.enable()
        tracker.start()
        ret = func(*args, **kwargs)  # The decorated function
        tracker.stop()
        location = "{module}::{function}".format(
            module=func.__module__, function=func.__name__)
        assert not tracker.garbage, tracker.format_garbage(location)
        return ret

    return functools.update_wrapper(garbage_tracked_wrapper, func)
