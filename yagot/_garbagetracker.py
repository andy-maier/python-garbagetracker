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
try:
    import objgraph
except ImportError:
    objgraph = None

__all__ = ['GarbageTracker']

# Regexp pattern for pprint recursion text
PPRINT_RECURSION_PATTERN = re.compile(r"<Recursion on (.*) with id=([0-9]+)>")


class GarbageTracker(object):
    """
    The GarbageTracker class provides named garbage trackers that can track
    garbage objects that emerged during a tracking period.

    Garbage objects are Python objects that cannot be immediately released when
    the object becomes unreachable and are therefore put into the generational
    Python garbage collector where more elaborated algorithms are used at a
    later point in time to release the objects.
    """

    #: dict: Global dict of existing garbage trackers, by name.
    trackers = dict()

    def __init__(self, name):
        """
        Parameters:

            name (:term:`string`): Name of the garbage tracker.
        """
        self._name = name
        self._ignored = False
        self._enabled = False
        self._garbage = []
        self._start_garbage_index = 0

    @staticmethod
    def get_tracker(name):
        """
        Return the garbage tracker with the specified name.

        If a garbage tracker does not yet exist with that name, create one.

        If a garbage tracker already exists with that name, return that garbage
        tracker object. Subsequent calls to this function for the same name
        will return the same garbage tracker object.

        Parameters:

            name (:term:`string`): Name of the garbage tracker.

        Returns:

            GarbageTracker: The garbage tracker with the specified name.
        """
        if name not in GarbageTracker.trackers:
            GarbageTracker.trackers[name] = GarbageTracker(name)
        return GarbageTracker.trackers[name]

    @property
    def name(self):
        """
        :term:`string`: Name of this garbage tracker.
        """
        return self._name

    @property
    def garbage(self):
        """
        list: List of new garbage objects that emerged during the tracking
        period, i.e. between :meth:`~yagot.GarbageTracker.start` and
        :meth:`~yagot.GarbageTracker.stop`.
        """
        return self._garbage

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
        ignored. This flag is set via :meth:`~yagot.GarbageTracker.ignore`.
        """
        return self._ignored

    def enable(self, enabled=True):
        """
        Enable or disable the garbage tracker.

        Parameters:

            enabled (bool): Boolean enabling the garbage tracking if True,
              and disabling the garbage tracking if False.
        """
        self._enabled = enabled

    def ignore(self):
        """
        Ignore the current tracking period for this garbage tracker, if it is
        enabled. This causes :attr:`~yagot.GarbageTracker.ignored` to be set.
        """
        if self.enabled:
            self._ignored = True

    def start(self):
        """
        Start the tracking period for this garbage tracker.

        Must be called before the code to be tracked is run.
        """
        if self.enabled:
            self._ignored = False
            gc.set_debug(0)
            gc.collect()
            self._start_garbage_index = len(gc.garbage)
            gc.set_debug(gc.DEBUG_SAVEALL)

    def stop(self):
        """
        Stop the tracking period for this garbage tracker.

        Must be called after the code to be tracked is run.
        """
        if self.enabled:
            gc.collect()
            gc.set_debug(0)

            # Eliminate previous content of the gc.garbage list in order to
            # show just the garbage added since start(). New uncollectable
            # objects are always appended to the end of the gc.garbage list,
            # so we only need to remember the previous index into the list.
            if self._ignored:
                # If the testcase execution has decided to ignore this tracking
                # period, do so.
                self._garbage = []
            else:
                tmp_garbage = gc.garbage[self._start_garbage_index:]
                ignore = False
                for item in tmp_garbage:
                    # pytest.raises() leaves garbage around, which normally
                    # contains frame and code objects. This is a poor man's
                    # solution to detecting that and subsequently ignoring the
                    # tracking period.
                    if isinstance(item, (types.FrameType, types.CodeType)):
                        ignore = True
                if ignore:
                    self._garbage = []
                else:
                    self._garbage = tmp_garbage

    def format_garbage(self, location=None, max=10):
        # pylint: disable=redefined-builtin
        """
        Return a formatted multi-line string for all garbage objects detected
        during the tracking period, up to a maximum number.

        Parameters:

            location (:term:`string`): Location of the function that created
              the garbage objects, e.g. in the notation "module::function".

            max (int): Maximum number of garbage objects to be included in the
              returned string.

        Returns:

            :term:`unicode string`: Formatted multi-line string.
        """
        ret_str = u"\nThere was {num} garbage object(s) caused by function " \
            u"{loc}:\n".format(num=len(self.garbage), loc=location)
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
        Return a formatted string for a single garbage object.

        Parameters:

            obj (object): Garbage object.

        Returns:

            :term:`unicode string`: Formatted string for the garbage object.
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
