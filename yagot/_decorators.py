"""
Decorators for garbage tracking in specific functions or methods.
"""

from __future__ import absolute_import, print_function
import functools
from ._garbagetracker import GarbageTracker

__all__ = ['assert_no_garbage']


def assert_no_garbage(func):
    """
    Decorator that performs garbage tracking for the decorated function or
    method and that asserts that the decorated function or method does not
    cause any additional :term:`garbage objects` or
    :term:`uncollectable objects` to emerge during its invocation.

    The decorator is signature-preserving, and the decorated function or method
    can have any signature.

    The decorated function or method needs to make sure that any objects it
    creates are deleted again, either implicitly (e.g. by a local variable
    going out of scope upon return) or explicitly. Ideally, no garbage is
    created that way, but whether that is actually the case is exactly what the
    decorator tests for. Also, it is possible that your code is clean but
    other modules your code uses are not clean, and that will surface this way.
    """

    def assert_no_garbage_wrapper(*args, **kwargs):
        """
        Wrapper function for the assert_no_garbage decorator.
        """
        tracker = GarbageTracker.get_tracker('yagot.assert_no_garbage')
        tracker.enable()
        tracker.start()
        ret = func(*args, **kwargs)  # The decorated function
        tracker.stop()
        location = "{module}::{function}".format(
            module=func.__module__, function=func.__name__)
        assert not tracker.garbage and not tracker.uncollectable_count, \
            tracker.assert_message(location)
        return ret

    return functools.update_wrapper(assert_no_garbage_wrapper, func)
