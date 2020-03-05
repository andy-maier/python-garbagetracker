"""
GarbageTracker class.
"""

from __future__ import absolute_import, print_function

import types
import re
import gc
import pprint
import inspect
from datetime import datetime
import six
try:
    import objgraph
except ImportError:
    objgraph = None

__all__ = ['GarbageTracker']

# Regexp pattern for pprint recursion text
PPRINT_RECURSION_PATTERN = re.compile(r"<Recursion on (.*) with id=([0-9]+)>")


class GarbageTracker(object):
    """
    The GarbageTracker class provides a singleton garbage tracker that can track
    :term:`uncollectable objects` and optionally :term:`collected objects`
    that emerged during a tracking period.
    """

    # The singleton GarbageTracker object
    _tracker = None

    def __init__(self):
        self._enabled = False
        self._leaks_only = False
        self._ignored = False
        self._ignored_type_names = []
        self._saved_thresholds = None
        self._garbage_index = 0
        self._garbage = []

    @staticmethod
    def get_tracker():
        """
        Returns the singleton garbage tracker object.

        The object is created when accessed through this method for the first
        time.
        """
        if GarbageTracker._tracker is None:
            GarbageTracker._tracker = GarbageTracker()
        return GarbageTracker._tracker

    @property
    def enabled(self):
        """
        bool: Boolean indicating the enablement status of the garbage tracker.
        """
        return self._enabled

    @property
    def ignored(self):
        """
        bool: Boolean indicating whether the current tracking period should be
        ignored.

        This flag is set via :meth:`~yagot.GarbageTracker.ignore`.
        """
        return self._ignored

    @property
    def leaks_only(self):
        """
        bool: Boolean indicating whether the tracker limits the checks to
        :term:`uncollectable objects` (= leaks) only.

        This flag can be set via :meth:`~yagot.GarbageTracker.enable`.
        """
        return self._leaks_only

    @property
    def garbage(self):
        """
        list: List of new :term:`collected objects` or
        :term:`uncollectable objects` that emerged during the last tracking
        period.
        """
        return self._garbage

    @property
    def ignored_type_names(self):
        """
        Return the Python type names to be ignored as :term:`collected objects`
        or :term:`uncollectable objects`.

        The types :class:`py:frame` and :class:`py:code` that are always
        ignored are included in the returned list.

        Returns:

            list: List of Python type names to be ignored as represented by
              the ``str(type)`` function (for example "int" or
              "mymodule.MyClass").
        """
        return self._ignored_type_names

    def enable(self, leaks_only=False):
        """
        Enable the garbage tracker and control what objects it checks for.

        Parameters:

            leaks_only (bool): Boolean limiting the checks to
              :term:`uncollectable objects` (=leaks) only.
        """
        self._enabled = True
        self._leaks_only = leaks_only

    def disable(self):
        """
        Disable the garbage tracker.
        """
        self._enabled = False

    def ignore(self):
        """
        Ignore the current tracking period for this garbage tracker, if it is
        enabled. This causes :attr:`~yagot.GarbageTracker.ignored` to be set.
        """
        if self.enabled:
            self._ignored = True

    def ignore_types(self, type_list):
        """
        Set additional Python types to be ignored as :term:`collected objects`
        or :term:`uncollectable objects`.

        The specified types are in addition to the following list of types that
        are aways ignored because they often appear as collectable objects
        when catching exceptions (e.g. when using :func:`pytest.raises`):

        * :class:`py:frame`
        * :class:`py:code`

        If the list of collected or uncollectable objects detected during the
        tracking period contains an object with a type that is to be ignored,
        the entire tracking period is ignored.

        Parameters:

            type_list (:term:`py:iterable`): Iterable of Python types, or
              `None`.

              Each type can be specified as a type object or as a string with
              the type name as represented by the ``str(type)`` function (for
              example, "int" or "mymodule.MyClass").

              `None` or an empty iterable means not to set additional types.
        """
        self._ignored_type_names = [
            _type2name(types.FrameType),
            _type2name(types.CodeType),
        ]
        if type_list:
            for t in type_list:
                if isinstance(t, type):
                    type_name = _type2name(t)
                else:
                    assert isinstance(t, six.string_types)
                    type_name = t
                self._ignored_type_names.append(type_name)

    def start(self):
        """
        Start the tracking period for this garbage tracker.

        Must be called before the code to be tracked is run.
        """
        if self.enabled:
            self._ignored = False
            self._garbage = []
            self._saved_thresholds = gc.get_threshold()
            gc.set_threshold(0, 0, 0)
            gc.set_debug(0)
            gc.collect()
            if not self.leaks_only:
                gc.set_debug(gc.DEBUG_SAVEALL)
            # If we delete the gc.garbage items, they will re-appear, so we
            # remember the last position.
            self._garbage_index = len(gc.garbage)

    def stop(self):
        """
        Stop the tracking period for this garbage tracker.

        Must be called after the code to be tracked is run.
        """
        if self.enabled:
            gc.collect()
            gc.set_debug(0)
            gc.set_threshold(*self._saved_thresholds)

            # Eliminate previous content of the gc.garbage list in order to
            # show just the garbage added since start(). New uncollectable
            # objects are always appended to the end of the gc.garbage list,
            # so we only need to remember the previous index into the list.
            if self._ignored:
                # If the testcase execution has decided to ignore this tracking
                # period, do so.
                self._garbage = []
            else:
                ignore = False
                for i in range(self._garbage_index, len(gc.garbage)):
                    # There are cases with weakly referenced objects where
                    # isinstance(item, ...) fails with ReferenceError.
                    # Therefore, we use direct type comparison. Also, we
                    # don't want to match object of subclasses anyway.
                    type_name = _type2name(type(gc.garbage[i]))
                    if type_name in self.ignored_type_names:
                        ignore = True
                        break
                if ignore:
                    self._garbage = []
                else:
                    self._garbage = gc.garbage[self._garbage_index:]

    def assert_message(self, location=None, max=10):
        # pylint: disable=redefined-builtin
        """
        Return a formatted multi-line string for the assertion message for
        the :term:`collected objects` or :term:`uncollectable objects`
        detected during the tracking period.

        Parameters:

            location (:term:`string`): Location of the function that created
              the objects, e.g. in the notation "module::function".

            max (int): Maximum number of objects to be included in the
              returned string.

        Returns:

            :term:`unicode string`: Formatted multi-line string.
        """
        kind_str = "uncollectable" if self.leaks_only \
            else "collected or uncollectable"
        ret_str = u"\nThere were {num} {kind} object(s) caused by function " \
            u"{loc}:\n". \
            format(num=len(self.garbage), kind=kind_str, loc=location)
        for i, obj in enumerate(self.garbage):
            # self._generate_objgraph(obj)
            if i >= max:
                ret_str += u"\n...\n"
                break
            ret_str += u"\n{}: {}\n".format(i + 1, self.format_obj(obj))
        return ret_str

    @staticmethod
    def format_obj(obj):
        """
        Return a formatted string for a single object.

        Parameters:

            obj (object): The object.

        Returns:

            :term:`unicode string`: Formatted string for the object.
        """
        try:
            obj_str = pprint.pformat(obj, indent=2)
        except Exception:  # pylint: disable=broad-except
            # Try repr() directly
            try:
                obj_str = repr(obj)
            except Exception as exc:  # pylint: disable=broad-except
                # Give up
                obj_str = "<Formatting error: repr() raises {type}: {msg}>". \
                    format(type=exc.__class__.__name__, msg=exc)

        # Post-format possible pprint recursion text
        obj_str = PPRINT_RECURSION_PATTERN.sub(_id2addr, obj_str)
        ret = u"{type} object at 0x{addr:0x}:\n{obj}". \
              format(type=type(obj), addr=id(obj), obj=obj_str)
        return ret

    @staticmethod
    def _generate_objgraph(obj):
        """
        If the objgraph package is installed, generate a .png file with the
        references the specified object has.
        """
        if objgraph:

            def _extra_info(obj):
                "extra_info function used for objgraph.show_refs()"
                return "at 0x{:08x}".format(id(obj))

            def _filter(obj):
                "filter function used for objgraph.show_refs()"
                excluded = inspect.isclass(obj) \
                    or inspect.isroutine(obj) \
                    or obj is None
                return not excluded

            dt = datetime.now()
            fname = 'objgraph_{}_{}_0x{:08x}.png'. \
                format(dt.strftime('%H.%M.%S'), obj.__class__.__name__, id(obj))
            objgraph.show_refs(
                obj, max_depth=8, too_many=20, filename=fname,
                extra_info=_extra_info, filter=_filter, shortnames=True,
                refcounts=True)


def _id2addr(matchobj):
    """
    Regexp substituion function to reformat pprint recursion text.
    """
    ret = "<Recursive reference to {type} object at 0x{addr:0x}>". \
        format(type=matchobj.group(1), addr=int(matchobj.group(2)))
    return ret


def _type2name(type_obj):
    """
    Return type name of a type object, as represented by `str(type_obj)`.
    """
    m = re.match(r"<(class|type) '(.*)'>", str(type_obj))
    assert m is not None
    type_name = m.group(2)
    return type_name
