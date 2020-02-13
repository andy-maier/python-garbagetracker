"""
GarbageTracker class.
"""

from __future__ import absolute_import, print_function

import sys
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

    Gargabe objects are objects that are already out of use but still have some
    sort of cyclic references that prevent them from being freed.
    """

    trackers = dict()

    def __init__(self, name):
        """
        Parameters:

            name (string): Name of the garbage tracker.
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

        Parameters:

            name (string): Name of the garbage tracker.
        """
        if name not in GarbageTracker.trackers:
            GarbageTracker.trackers[name] = GarbageTracker(name)
        return GarbageTracker.trackers[name]

    def enable(self, enabled=True):
        """
        Enable or disable the garbage tracker.

        Parameters:

            enabled (bool): Boolean enabling the garbage tracking if True,
              and disabling the garbage tracking if False.
        """
        self._enabled = enabled

    @property
    def name(self):
        """
        Name of this garbage tracker.
        """
        return self._name

    @property
    def enabled(self):
        """
        Boolean indicating the enablement status of the garbage tracker.
        """
        return self._enabled

    @property
    def garbage(self):
        """
        List of new garbage objects that emerged during the tracking period,
        i.e. between start() and stop().
        """
        return self._garbage

    @property
    def ignored(self):
        """
        Return whether the current tracking period should be ignored.
        """
        return self._ignored

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

    def ignore(self):
        """
        Ignore the current tracking period for this garbage tracker.
        """
        if self.enabled:
            self._ignored = True

    def print_if_garbage(self, location=None, max=10, stream=sys.stdout):
        # pylint: disable=redefined-builtin
        """
        If there were garbage objects found during the last tracking period,
        print the garbage objects.

        Parameters:

            location (string): Location of the testcase (file::func).

            max (int): Maximum number of objects to be printed.

            stream: Stream to be printed on.
        """
        if self.enabled and self.garbage:
            print("\n{num} garbage objects left by {loc}:".
                  format(num=len(self.garbage), loc=location))
            for i, obj in enumerate(self.garbage):
                if i >= max:
                    print("...", file=stream)
                    break
                obj_str = self._format(obj)
                print(obj_str, file=stream)
                stream.flush()

    def assert_no_garbage(self, location=None, max=10):
        # pylint: disable=redefined-builtin
        """
        Assert that there were no garbage objects found during the last
        tracking period. Raise AssertionError with a message that describes
        the location of the testcase and the garbage objects (up to a maximum
        number), otherwise.

        Parameters:

            location (string): Location of the testcase (file::func).

            max (int): Maximum number of garbage bjects to be included.
        """
        if self.enabled and self.garbage:
            ass_str = "{num} garbage objects left by {loc}:\n". \
                format(num=len(self.garbage), loc=location)
            for i, obj in enumerate(self.garbage):
                # self._generate_objgraph(obj)
                if i >= max:
                    ass_str += "...\n"
                    break
                ass_str += "{}: {}\n".format(i + 1, self._format(obj))
            raise AssertionError(ass_str)

    @staticmethod
    def _format(obj):
        """
        Return a formatted string for the garbage object.

        Parameters:

            obj (object): Garbage object.
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
        ret = "{type} object at 0x{addr:0x}:\n{obj}". \
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
    Regexp substituion function to reformat pprint recursion text
    """
    ret = "<Recursive reference to {type} object at 0x{addr:0x}>". \
        format(type=matchobj.group(1), addr=int(matchobj.group(2)))
    return ret
