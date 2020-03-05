"""
Testcases for the pytest plugin of Yagot.

Note: 'testdir' is a fixture provided by the pytester plugin of pytest.
See https://docs.pytest.org/en/latest/reference.html#testdir for details.
"""

import pytest


def test_help_message(testdir):
    """
    Test that the Yagot plugin's options appear in the pytest help message.
    """
    result = testdir.runpytest(
        '--help',
    )
    result.stdout.fnmatch_lines([
        '*Yagot:',
        '* --yagot*',
        '* --yagot-leaks-only*',
        '* --yagot-ignore-types=*',
    ])
    assert result.ret == 0


def test_disabled(testdir):
    """
    Test with the Yagot plugin disabled.
    """
    test_code = """
    def test_clean():
        _ = dict()
    """
    testdir.makepyfile(test_code)
    result = testdir.runpytest()
    assert result.ret == 0


def test_collected_clean(testdir):
    """
    Test with the Yagot plugin enabled for collected objects but no collected
    objects produced.
    """
    test_code = """
    def test_clean():
        _ = dict()
    """
    testdir.makepyfile(test_code)
    result = testdir.runpytest('--yagot')
    assert result.ret == 0


def test_uncollectable_clean(testdir):
    """
    Test with the Yagot plugin enabled for uncollectable objects but no
    uncollectable objects produced.
    """
    test_code = """
    def test_clean():
        _ = dict()
    """
    testdir.makepyfile(test_code)
    result = testdir.runpytest('--yagot', '--yagot-leaks-only')
    assert result.ret == 0


def test_collected_selfref(testdir):
    """
    Test with the Yagot plugin enabled for collected objects and collected
    objects produced as self-referencing dict.
    """
    test_code = """
    def test_clean():
        d1 = dict()
        d1['self'] = d1
    """
    testdir.makepyfile(test_code)
    result = testdir.runpytest('--yagot')
    result.stdout.fnmatch_lines([
        '*There were 1 collected or uncollectable object(s) '
        'caused by function test_collected_selfref.py::test_clean*',
    ])
    assert result.ret == 1


def test_collected_selfref_ignored(testdir):
    """
    Test with the Yagot plugin enabled for collected objects and collected
    objects produced as self-referencing dict, ignoring dict types.
    """
    test_code = """
    def test_clean():
        d1 = dict()
        d1['self'] = d1
    """
    testdir.makepyfile(test_code)
    result = testdir.runpytest('--yagot', '--yagot-ignore-types=dict,list')
    assert result.ret == 0


def test_collected_selfref_failed(testdir):
    """
    Test with the Yagot plugin enabled for collected objects and collected
    objects produced as self-referencing dict, but testcase failed.
    """
    test_code = """
    def test_fail():
        d1 = dict()
        d1['self'] = d1
        assert False
    """
    testdir.makepyfile(test_code)
    result = testdir.runpytest('--yagot')
    result.stdout.fnmatch_lines([
        '*test_collected_selfref_failed.py:4: AssertionError*',
    ])
    assert result.ret == 1


@pytest.mark.xfail(reason="Increased reference count is not detected")
def test_uncollectable_incref(testdir):
    """
    Test with the Yagot plugin enabled for uncollectable objects and
    uncollectable object produced with increased reference count.
    """
    test_code = """
    import sys
    import gc
    import yagot
    import test_leaky

    def test_leak():
        l1 = [1, 2]
        assert gc.is_tracked(l1)
        assert sys.getrefcount(l1) == 2
        test_leaky.incref(l1)
        assert sys.getrefcount(l1) == 3
    """
    testdir.makepyfile(test_code)
    result = testdir.runpytest('--yagot', '--yagot-leaks-only')
    result.stdout.fnmatch_lines([
        '*There were 1 uncollectable object(s) '
        'caused by function test_leak.py::test_leak*',
    ])
    assert result.ret == 1
