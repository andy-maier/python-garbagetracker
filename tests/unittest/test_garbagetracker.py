"""
Test the GarbageTracker class.
"""

from __future__ import absolute_import, print_function

import uuid
import pytest
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


def func_empty():
    "Function without leaks that is empty."
    pass


def func_dict_clean():
    "Function without leaks that has a local dict with a string item."
    _ = dict(a='a')


def func_dict_selfref():
    "Function with leaks that has a local dict with a self-referencing item."
    d = dict()
    d['a'] = d


def func_class_selfref():
    "Function with leaks that has a local object with a self-referencing attr."
    _ = SelfRef()


TESTCASES_GARBAGETRACKER_TRACK = [

    # Testcases for tracking garbage using
    # GarbageTracker.start()/stop()/garbage.

    # Each list item is a testcase tuple with these items:
    # * desc: Short testcase description.
    # * details:
    #   * func: Function that may create leaks.
    #   * exp_garbage_types: List of expected types in the reported garbage.

    (
        "Empty function",
        dict(
            func=func_empty,
            exp_garbage_types=[],
        ),
    ),
    (
        "Function with leak-free local dict with string item",
        dict(
            func=func_dict_clean,
            exp_garbage_types=[],
        ),
    ),
    (
        "Function with leaking dict with self-referencing dict item",
        dict(
            func=func_dict_selfref,
            exp_garbage_types=[dict],
        ),
    ),
    (
        "Function with leaking class with self-referencing attribute",
        dict(
            func=func_class_selfref,
            exp_garbage_types=[SelfRef, dict],
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
    exp_garbage_types = details['exp_garbage_types']

    obj = GarbageTracker('bla')

    if enable:
        obj.enable()

    obj.start()

    func()  # The code that might create leaks

    if ignore:
        obj.ignore()

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
        assert len(obj.garbage) == len(exp_garbage_types)
        for i, item in enumerate(obj.garbage):
            # pylint: disable=unidiomatic-typecheck
            assert type(item) is exp_garbage_types[i]
