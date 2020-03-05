"""
A pytest plugin for Yagot.
"""

from __future__ import absolute_import, print_function

import os
import pytest

# We import yagot in a deferred manner, because importing it globally causes
# the coverage to go down. Apparently the pytest coverage plugin does not
# honor any module global code as being covered when the module is already
# loaded by pytest.


def pure_list(comma_list):
    """
    Transform a list with items that can be comma-separated strings, into
    a pure list where the comma-separated strings become multiple items.
    """
    pure_items = []
    for comma_item in comma_list:
        for item in comma_item.split(','):
            pure_items.append(item)
    return pure_items


def pytest_addoption(parser):
    """
    Add command line options and config (ini) parameters for this plugin.

    group.addoption() supports the same arguments as argparse.add_argument().
    """
    group = parser.getgroup('yagot')
    group.description = "Garbage object tracking using Yagot"
    # pytest.set_trace()
    group.addoption(
        '--yagot',
        dest='yagot',
        action='store_true',
        default=bool(os.getenv('YAGOT', False)),
        help="""\
Enables checking for collected and uncollectable objects caused by pytest test
cases.
Default: Env.var YAGOT (set to non-empty), or False.
""")
    group.addoption(
        '--yagot-leaks-only',
        dest='yagot_leaks_only',
        action='store_true',
        default=bool(os.getenv('YAGOT_LEAKS_ONLY', False)),
        help="""\
Limits the checking to only uncollectable (=leak) objects.
Default: Env.var YAGOT_LEAKS_ONLY (set to non-empty), or False.
""")
    group.addoption(
        '--yagot-ignore-types',
        dest='yagot_ignore_types',
        metavar="TYPE[,TYPE[...]]",
        action='append',
        default=os.getenv('YAGOT_IGNORE_TYPES', list()),
        help="""\
Type name or module.path.class name of collected and uncollectable objects for
which test cases will be ignored. Multiple comma-separated type names can be
specified on each option, and in addition the option can be specified multiple
times. The types must be specified as represented by the str(type) function
(for example, "int" or "mymodule.MyClass").
Default: Env.var YAGOT_IGNORE_TYPES, or empty list.
""")


@pytest.hookimpl(hookwrapper=True)
def pytest_sessionstart(session):
    """
    py.test hook wrapper around the session start hook which is called when
    the test session starts.

    We print the Yagot configuration after the test session start hooks
    (including the default one propvided by pytest) have been called. This
    places our print along with the other information pytest prints (e.g.
    platform, rootdir, plugins).
    """
    yield  # causes the session start hooks to be called
    config = session.config
    enabled = config.getvalue('yagot')
    leaks_only = config.getvalue('yagot_leaks_only')
    ignore_types = pure_list(config.getvalue('yagot_ignore_types'))
    if enabled:
        kind_str = "uncollectable" if leaks_only \
            else "collected and uncollectable"
        ignore_str = ', '.join(ignore_types) or "(none)"
        print("yagot: Checking for {} objects, ignoring types: {}".
              format(kind_str, ignore_str))


def pytest_runtest_setup(item):
    """
    py.test hook that is called when setting up a test item.

    We use this hook to start tracking.
    """
    config = item.config
    enabled = config.getvalue('yagot')
    leaks_only = config.getvalue('yagot_leaks_only')
    ignore_types = pure_list(config.getvalue('yagot_ignore_types'))
    if enabled:
        import yagot
        tracker = yagot.GarbageTracker.get_tracker()
        tracker.enable(leaks_only=leaks_only)
        tracker.start()
        tracker.ignore_types(type_list=ignore_types)


@pytest.hookimpl(trylast=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    py.test hook (actually a Python coroutine) that is called when the setup,
    call and teardown phase has its result.

    We use this hook in the call phase to ignore garbage tracking for skipped
    and failed test case outcomes, because pytest creates many collectable
    objects that would distract from the garbage produced by the tested code.
    """
    report = (yield).get_result()  # pytest.TestReport
    config = item.config
    enabled = config.getvalue('yagot')
    if enabled:
        if report.when == "call" and not report.passed:
            import yagot
            tracker = yagot.GarbageTracker.get_tracker()
            tracker.ignore()


def pytest_runtest_teardown(item):
    """
    py.test hook that is called when tearing down a test item.

    We use this hook to stop tracking and check the track result.
    """
    config = item.config
    enabled = config.getvalue('yagot')
    if enabled:
        import yagot
        tracker = yagot.GarbageTracker.get_tracker()
        tracker.stop()
        location = "{file}::{func}". \
            format(file=item.location[0], func=item.name)
        assert not tracker.garbage, tracker.assert_message(location)
