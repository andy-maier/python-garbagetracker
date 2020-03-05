"""
Decorators for garbage tracking in specific functions or methods.
"""

from __future__ import absolute_import, print_function
import functools
from ._garbagetracker import GarbageTracker

__all__ = ['garbage_checked']


def garbage_checked(leaks_only=False, ignore_types=None):
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

        @yagot.garbage_checked()
        test_something():
            # do some tests

    Parameters:

        leaks_only (bool): Boolean to limit the checks to only
          :term:`uncollectable objects`. By default, :term:`collected objects`
          and :term:`uncollectable objects` are checked for.

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

    def decorator_garbage_checked(func):
        "Decorator function for the garbage_checked decorator"

        @functools.wraps(func)
        def wrapper_garbage_checked(*args, **kwargs):
            "Wrapper function for the garbage_checked decorator"
            tracker = GarbageTracker.get_tracker()
            tracker.enable(leaks_only=leaks_only)
            tracker.start()
            tracker.ignore_types(type_list=ignore_types)
            ret = func(*args, **kwargs)  # The decorated function
            tracker.stop()
            location = "{module}::{function}".format(
                module=func.__module__, function=func.__name__)
            assert not tracker.garbage, tracker.assert_message(location)
            return ret

        return wrapper_garbage_checked

    return decorator_garbage_checked
