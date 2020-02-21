"""
Test the GarbageTracker class.
"""

from __future__ import absolute_import, print_function

import six
import uuid
import pytest
from collections import OrderedDict
from xml.dom.minidom import Document
from yagot import GarbageTracker
from .test_decorator import SelfRef


def test_GarbageTracker_get_tracker():
    """
    Test function for GarbageTracker.get_tracker().
    """
    # Since the trackers are module-global, other testcases may have already
    # created trackers. We just check the additional ones this testcase creates.

    name = "test_{}".format(uuid.uuid4())
    assert name not in GarbageTracker.trackers

    tracker1 = GarbageTracker.get_tracker(name)

    assert name in GarbageTracker.trackers

    tracker2 = GarbageTracker.get_tracker(name)

    assert tracker1 is tracker2


TESTCASES_GARBAGETRACKER_INIT = [

    # Testcases for GarbageTracker.__init__()

    # Each list item is a testcase tuple with these items:
    # * desc: Short testcase description.
    # * details:
    #   * args: List of positional arguments for __init__().
    #   * kwargs: Dict of keyword arguments for __init__().
    #   * exp_attrs: Dict of expected attributes of the generated object or None
    #   * exp_exc_types: Expected exception type(s), or None.

    (
        "No init arguments",
        dict(
            args=[],
            kwargs=dict(),
            exp_attrs=None,
            exp_exc_types=TypeError,
        ),
    ),
    (
        "Only the required arguments",
        dict(
            args=[],
            kwargs=dict(
                name='bla',
            ),
            exp_attrs=dict(
                name='bla',
                garbage=[],
                ignored=False,
                enabled=False,
            ),
            exp_exc_types=None,
        ),
    ),
]


@pytest.mark.parametrize(
    "desc, details",
    TESTCASES_GARBAGETRACKER_INIT)
def test_GarbageTracker_init(desc, details):
    # pylint: disable=unused-argument
    """
    Test function for GarbageTracker.__init__().
    """
    args = details['args']
    kwargs = details['kwargs']
    exp_attrs = details['exp_attrs']
    exp_exc_types = details['exp_exc_types']

    if exp_exc_types:
        with pytest.raises(exp_exc_types):

            # The code to be tested
            GarbageTracker(*args, **kwargs)

    else:

        # The code to be tested
        obj = GarbageTracker(*args, **kwargs)

        for name in exp_attrs:
            exp_attr = exp_attrs[name]
            assert getattr(obj, name) == exp_attr


def test_GarbageTracker_enable():
    """
    Test function for GarbageTracker.enable().
    """
    obj = GarbageTracker('bla')
    assert obj.enabled is False

    # The code to be tested
    obj.enable()

    assert obj.enabled is True
    # Check that otherwise nothing happened
    assert obj.ignored is False
    assert obj.garbage == []


@pytest.mark.parametrize(
    "enable", [True, False])
def test_GarbageTracker_ignore(enable):
    """
    Test function for GarbageTracker.ignore().
    """
    obj = GarbageTracker('bla')
    assert obj.enabled is False
    if enable:
        obj.enable()

    # The code to be tested
    obj.ignore()

    if enable:
        assert obj.ignored is True
    else:
        assert obj.ignored is False


def func_pass():
    "Function that does nothing"
    pass


def func_dict_string():
    "Function that has a local dict with a string item"
    _ = dict(a='a')


def func_ordereddict_empty():
    "Function that has a local empty collections.OrderedDict"
    _ = OrderedDict()


def func_dict_selfref():
    "Function that has a local dict with a self-referencing item"
    d = dict()
    d['a'] = d


def func_class_selfref():
    "Function that has a local instance with self-referencing attribute"
    _ = SelfRef()


def func_minidom_document():
    "Function that has a local xml.minidom.Document object"
    doc = Document()
    elem = doc.createElement('FOO')
    elem.setAttribute('BAR', 'bla')
    doc.appendChild(elem)


TESTCASES_GARBAGETRACKER_TRACK = [

    # Testcases for tracking garbage using
    # GarbageTracker.start()/stop()/garbage.

    # Each list item is a testcase tuple with these items:
    # * desc: Short testcase description.
    # * details:
    #   * func: Function that may create leaks.
    #   * ignore_garbage_types: List of types to ignore, or None.
    #   * exp_garbage_types: List of expected types in the reported garbage.
    #   * exp_uncollectable_count: Expected number of uncollectable objects.

    (
        "Empty test function",
        dict(
            func=func_pass,
            ignore_garbage_types=None,
            exp_garbage_types=[],
            exp_uncollectable_count=0,
        ),
    ),
    (
        "Standard dict with string",
        dict(
            func=func_dict_string,
            ignore_garbage_types=None,
            exp_garbage_types=[],
            exp_uncollectable_count=0,
        ),
    ),
    (
        "Empty OrderedDict creating garbage on Python 2.7",
        dict(
            func=func_ordereddict_empty,
            ignore_garbage_types=None,
            exp_garbage_types=[list] if six.PY2 else [],
            exp_uncollectable_count=0,
        ),
    ),
    (
        "Self-referencing class, ignoring no garbage",
        dict(
            func=func_dict_selfref,
            ignore_garbage_types=None,
            exp_garbage_types=[dict],
            exp_uncollectable_count=0,
        ),
    ),
    (
        "Self-referencing dict, ignoring incorrect 'list' type obj as garbage",
        dict(
            func=func_dict_selfref,
            ignore_garbage_types=[list],
            exp_garbage_types=[dict],
            exp_uncollectable_count=0,
        ),
    ),
    (
        "Self-referencing dict, ignoring correct 'dict' type obj as garbage",
        dict(
            func=func_dict_selfref,
            ignore_garbage_types=[dict],
            exp_garbage_types=[],
            exp_uncollectable_count=0,
        ),
    ),
    (
        "Self-referencing dict, ignoring correct 'dict' type name as garbage",
        dict(
            func=func_dict_selfref,
            ignore_garbage_types=['dict'],
            exp_garbage_types=[],
            exp_uncollectable_count=0,
        ),
    ),
    (
        "SelfRef class, ignoring no garbage",
        dict(
            func=func_class_selfref,
            ignore_garbage_types=None,
            exp_garbage_types=[SelfRef, dict],
            exp_uncollectable_count=0,
        ),
    ),
    (
        "SelfRef class, ignoring correct 'SelfRef' type obj as garbage",
        dict(
            func=func_class_selfref,
            ignore_garbage_types=[SelfRef],
            exp_garbage_types=[],
            exp_uncollectable_count=0,
        ),
    ),
    (
        "SelfRef class, ignoring correct 'SelfRef' type name as garbage",
        dict(
            func=func_class_selfref,
            ignore_garbage_types=['tests.unittest.test_decorator.SelfRef'],
            exp_garbage_types=[],
            exp_uncollectable_count=0,
        ),
    ),
    (
        "xml.dom.minidom.Document, ignoring no garbage",
        dict(
            func=func_minidom_document,
            ignore_garbage_types=None,
            exp_garbage_types=13 if six.PY2 else 10,  # not listed specifically
            exp_uncollectable_count=0,
        ),
    ),
]


@pytest.mark.parametrize(
    "ignore", [True, False])
@pytest.mark.parametrize(
    "enable", [True, False])
@pytest.mark.parametrize(
    "desc, details",
    TESTCASES_GARBAGETRACKER_TRACK)
def test_GarbageTracker_track(desc, details, enable, ignore):
    # pylint: disable=unused-argument
    """
    Test function for tracking garbage using
    GarbageTracker.start()/stop()/garbage.
    """
    func = details['func']
    ignore_garbage_types = details['ignore_garbage_types']
    exp_garbage_types = details['exp_garbage_types']
    exp_uncollectable_count = details['exp_uncollectable_count']

    obj = GarbageTracker('bla')

    if enable:
        obj.enable()

    obj.start()

    func()  # The code that might create leaks

    if ignore:
        obj.ignore()

    if ignore_garbage_types is not None:
        obj.ignore_garbage_types(ignore_garbage_types)

    obj.stop()

    if not enable:
        # If the tracker was not enabled, we should not see any garbage
        # reported.
        assert obj.garbage == []
        assert obj.uncollectable_count == 0
    elif ignore:
        # If the tracker was enabled but then ignored, we should also see no
        # garbage reported.
        assert obj.garbage == []
        assert obj.uncollectable_count == 0
    else:
        # If the tracker was enabled and not ignored, we will see garbage
        # reported (if there is expected garbage).
        if isinstance(exp_garbage_types, int):
            # We just check the number of garbage objects
            assert len(obj.garbage) == exp_garbage_types
        else:
            assert isinstance(exp_garbage_types, list)
            # We check the types of the garbage objects
            garbage_types = [type(o) for o in obj.garbage]
            assert garbage_types == exp_garbage_types
        assert obj.uncollectable_count == exp_uncollectable_count
