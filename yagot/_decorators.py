"""
Decorators for garbage tracking in specific functions or methods.
"""

from __future__ import absolute_import, print_function
import functools
from ._garbagetracker import GarbageTracker

__all__ = ['leak_check']


def leak_check(check_collected=False, ignore_types=None):
    """
    Decorator that checks for :term:`uncollectable objects` and optionally for
    :term:`collected objects` caused by the decorated function or method, and
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

        check_collected (bool): Boolean adding checks for
          :term:`collected objects` (in addition to
          :term:`uncollectable objects` that are always checked for).

        ignore_types (:term:`py:iterable`): `None` or iterable of Python
          types or type names that are set as additional garbage types to
          ignore, in addition to :class:`py:frame` and :class:`py:code` that
          are always ignored.

          If any detected object has one of the types to be ignored, the entire
          set of objects caused by the decorated function or method is ignored.

          Each type can be specified as a type object or as a string with
          the type name as represented by the ``str(type)`` function (for
          example, "int" or "mymodule.MyClass").

          `None` or an empty iterable means not to ignore any types.
    """

    def decorator_leak_check(func):
        "Decorator function for the leak_check decorator"

        @functools.wraps(func)
        def wrapper_leak_check(*args, **kwargs):
            "Wrapper function for the leak_check decorator"
            tracker = GarbageTracker.get_tracker()
            tracker.enable(check_collected)
            tracker.start()
            tracker.ignore_types(ignore_types)
            ret = func(*args, **kwargs)  # The decorated function
            tracker.stop()
            location = "{module}::{function}".format(
                module=func.__module__, function=func.__name__)
            assert not tracker.garbage, tracker.assert_message(location)
            return ret

        return wrapper_leak_check

    return decorator_leak_check
