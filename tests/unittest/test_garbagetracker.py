"""
Test the GarbageTracker class.
"""

from __future__ import absolute_import, print_function

import six
import pytest
from collections import OrderedDict
from xml.dom.minidom import Document
from yagot import GarbageTracker
from .test_decorator import SelfRef


def test_GarbageTracker_get_tracker():
    """
    Test function for GarbageTracker.get_tracker().
    """
    tracker1 = GarbageTracker.get_tracker()
    tracker2 = GarbageTracker.get_tracker()
    assert tracker1 is tracker2


def test_GarbageTracker_init():
    """
    Test function for GarbageTracker.__init__().
    """

    # The code to be tested
    obj = GarbageTracker()

    assert obj.enabled is False
    assert obj.ignored is False
    assert obj.check_collected is False
    assert obj.ignored_type_names == []
    assert obj.garbage == []


@pytest.mark.parametrize(
    "kwargs", [
        dict(),
        dict(check_collected=False),
        dict(check_collected=True),
    ])
def test_GarbageTracker_enable(kwargs):
    """
    Test function for GarbageTracker.enable().
    """
    exp_check_collected = kwargs.get('check_collected', False)
    obj = GarbageTracker()
    assert obj.enabled is False

    # The code to be tested
    obj.enable(**kwargs)

    assert obj.enabled is True
    assert obj.check_collected == exp_check_collected

    # Check that otherwise nothing happened
    assert obj.ignored is False
    assert obj.ignored_type_names == []
    assert obj.garbage == []


@pytest.mark.parametrize(
    "enable", [True, False])
def test_GarbageTracker_disable(enable):
    """
    Test function for GarbageTracker.disable().
    """
    obj = GarbageTracker()
    if enable:
        obj.enable()
    assert obj.enabled == enable

    # The code to be tested
    obj.disable()

    assert obj.enabled is False


@pytest.mark.parametrize(
    "enable", [True, False])
def test_GarbageTracker_ignore(enable):
    """
    Test function for GarbageTracker.ignore().
    """
    obj = GarbageTracker()
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
    #   * ignore_types: List of types to ignore, or None.
    #   * exp_collected_types: List of expected object types when checking
    #     for uncollectable and collected objects.
    #   * exp_uncollectable_types: List of expected object types when checking
    #     for uncollectable objects.

    (
        "Empty test function",
        dict(
            func=func_pass,
            ignore_types=None,
            exp_collected_types=[],
            exp_uncollectable_types=[],
        ),
    ),
    (
        "Standard dict with string",
        dict(
            func=func_dict_string,
            ignore_types=None,
            exp_collected_types=[],
            exp_uncollectable_types=[],
        ),
    ),
    (
        "Empty OrderedDict creating garbage on Python 2.7",
        dict(
            func=func_ordereddict_empty,
            ignore_types=None,
            exp_collected_types=[list] if six.PY2 else [],
            exp_uncollectable_types=[],
        ),
    ),
    (
        "Self-referencing dict, ignoring no garbage",
        dict(
            func=func_dict_selfref,
            ignore_types=None,
            exp_collected_types=[dict],
            exp_uncollectable_types=[],
            pdb=False,
        ),
    ),
    (
        "Self-referencing dict, ignoring incorrect 'list' type obj as garbage",
        dict(
            func=func_dict_selfref,
            ignore_types=[list],
            exp_collected_types=[dict],
            exp_uncollectable_types=[],
        ),
    ),
    (
        "Self-referencing dict, ignoring correct 'dict' type obj as garbage",
        dict(
            func=func_dict_selfref,
            ignore_types=[dict],
            exp_collected_types=[],
            exp_uncollectable_types=[],
        ),
    ),
    (
        "Self-referencing dict, ignoring correct 'dict' type name as garbage",
        dict(
            func=func_dict_selfref,
            ignore_types=['dict'],
            exp_collected_types=[],
            exp_uncollectable_types=[],
        ),
    ),
    (
        "SelfRef class, ignoring no garbage",
        dict(
            func=func_class_selfref,
            ignore_types=None,
            exp_collected_types=[SelfRef, dict],
            exp_uncollectable_types=[],
        ),
    ),
    (
        "SelfRef class, ignoring correct 'SelfRef' type obj as garbage",
        dict(
            func=func_class_selfref,
            ignore_types=[SelfRef],
            exp_collected_types=[],
            exp_uncollectable_types=[],
        ),
    ),
    (
        "SelfRef class, ignoring correct 'SelfRef' type name as garbage",
        dict(
            func=func_class_selfref,
            ignore_types=['tests.unittest.test_decorator.SelfRef'],
            exp_collected_types=[],
            exp_uncollectable_types=[],
        ),
    ),
]


@pytest.mark.parametrize(
    "ignore", [True, False])
@pytest.mark.parametrize(
    "enable", [True, False])
@pytest.mark.parametrize(
    "check_collected", [True, False])
@pytest.mark.parametrize(
    "desc, details",
    TESTCASES_GARBAGETRACKER_TRACK)
def test_GarbageTracker_track(desc, details, check_collected, enable, ignore):
    # pylint: disable=unused-argument
    """
    Test function for tracking garbage using
    GarbageTracker.start()/stop()/garbage.
    """
    func = details['func']
    ignore_types = details['ignore_types']
    exp_collected_types = details['exp_collected_types']
    exp_uncollectable_types = details['exp_uncollectable_types']
    use_pdb = details.get('pdb', False)

    if use_pdb:
        import pdb
        pdb.set_trace()

    obj = GarbageTracker()

    if enable:
        obj.enable(check_collected)

    obj.start()

    func()  # The code that might create leaks

    if ignore:
        obj.ignore()

    if ignore_types is not None:
        obj.ignore_types(ignore_types)

    obj.stop()

    if not enable:
        # If the tracker was not enabled, we should not see any garbage
        # reported.
        assert obj.garbage == []
    elif ignore:
        # If the tracker was enabled but then ignored, we should also see no
        # garbage reported.
        assert obj.garbage == []
    else:
        # If the tracker was enabled and not ignored, we will see garbage
        # reported (if there is expected garbage).
        if check_collected:
            exp_garbage_types = exp_collected_types
        else:
            exp_garbage_types = exp_uncollectable_types
        if isinstance(exp_garbage_types, int):
            # We just check the number of objects
            assert len(obj.garbage) == exp_garbage_types
        else:
            assert isinstance(exp_garbage_types, list)
            # We check the types of the objects
            garbage_types = [type(o) for o in obj.garbage]
            assert garbage_types == exp_garbage_types, \
                "Garbage objects: {}".format(obj.garbage)
