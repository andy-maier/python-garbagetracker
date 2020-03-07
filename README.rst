Yagot - Yet Another Garbage Object Tracker for Python
=====================================================

.. image:: https://img.shields.io/pypi/v/yagot.svg
    :target: https://pypi.python.org/pypi/yagot/
    :alt: Version on Pypi

.. image:: https://travis-ci.org/andy-maier/python-yagot.svg?branch=master
    :target: https://travis-ci.org/andy-maier/python-yagot/branches
    :alt: Travis test status (master)

.. image:: https://ci.appveyor.com/api/projects/status/ebqjx5ei8kqc1mf1/branch/master?svg=true
    :target: https://ci.appveyor.com/project/andy-maier/python-yagot/history
    :alt: Appveyor test status (master)

.. image:: https://readthedocs.org/projects/yagot/badge/?version=latest
    :target: https://readthedocs.org/projects/yagot/builds/
    :alt: Docs build status (master)

.. image:: https://coveralls.io/repos/github/andy-maier/python-yagot/badge.svg?branch=master
    :target: https://coveralls.io/github/andy-maier/python-yagot?branch=master
    :alt: Test coverage (master)


Overview
--------

Yagot (Yet Another Garbage Object Tracker) is a tool for Python developers to
help find issues with garbage collection and memory leaks:

* It can determine the set of *collected objects* caused by a function or
  method.

  Collected objects are objects Python could not immediately release when they
  became unreachable and that were eventually released by the Python garbage
  collector. Frequently this is caused by the presence of circular references
  into which the object to be released is involved. The garbage collector is
  designed to handle circular references when releasing objects.

  Collected objects are not a problem per se, but they can contribute to
  large memory use and can often be eliminated.

* It can determine the set of *uncollectable objects* caused by a function or
  method.

  Uncollectable objects are objects Python was unable to release during garbage
  collection, even when running a full collection (i.e. on all generations of
  the Python generational garbage collector).

  Uncollectable objects remain allocated in the last generation of the garbage
  collector. On each run on its last generation, the garbage collector attempts
  to release these objects. It seems to be rare that these continued attempts
  eventually succeed, so these objects can basically be considered memory leaks.

See section
`Background`_
for more detailed explanations about object release in Python.

Yagot is simple to use in either of the following ways:

* It provides a `pytest`_ plugin named ``yagot`` that detects collected and
  uncollectable objects caused by the test cases. This detection is enabled by
  specifying command line options or environment variables and does not require
  modifying the test cases.

* It provides a Python decorator named
  `garbage_checked`_
  that detects collected and uncollectable objects caused by the decorated
  function or method. This allows using Yagot independent of any test framework
  or with other test frameworks such as `nose`_ or `unittest`_.

Yagot works with a normal (non-debug) build of Python.

.. _pytest: https://docs.pytest.org/
.. _nose: https://nose.readthedocs.io/
.. _unittest: https://docs.python.org/3/library/unittest.html
.. _garbage_checked: https://yagot.readthedocs.io/en/latest/apiref.html#yagot.garbage_checked
.. _Background: https://yagot.readthedocs.io/en/latest/background.html#Background


Installation
------------

To install the latest released version of the yagot package into your active
Python environment:

.. code-block:: bash

    $ pip install yagot

This will also install any prerequisite Python packages.

For more details and alternative ways to install, see `Installation`_.

.. _Installation: https://yagot.readthedocs.io/en/latest/intro.html#installation


Usage
-----

Here is an example of how to use Yagot to detect collected objects caused by
pytest test cases using the command line options provided by the
yagot pytest plugin:

.. code-block:: text

    $ cat examples/test_1.py
    def test_selfref_dict():
        d1 = dict()
        d1['self'] = d1

    $ pytest examples --yagot -k test_1.py
    ===================================== test session starts ======================================
    platform darwin -- Python 3.7.5, pytest-5.3.5, py-1.8.1, pluggy-0.13.1
    rootdir: /Users/maiera/PycharmProjects/yagot/python-yagot
    plugins: cov-2.8.1, yagot-0.1.0.dev1
    yagot: Checking for collected and uncollectable objects, ignoring types: (none)
    collected 2 items / 1 deselected / 1 selected

    examples/test_1.py .E                                                                    [100%]

    ============================================ ERRORS ============================================
    ____________________________ ERROR at teardown of test_selfref_dict ____________________________

    item = <Function test_selfref_dict>

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
    >           assert not tracker.garbage, tracker.assert_message(location)
    E           AssertionError:
    E             There were 1 collected or uncollectable object(s) caused by function examples/test_1.py::test_selfref_dict:
    E
    E             1: <class 'dict'> object at 0x10df6ceb0:
    E             {'self': <Recursive reference to dict object at 0x10df6ceb0>}
    E
    E           assert not [{'self': {'self': {'self': {'self': {'self': {...}}}}}}]
    E            +  where [{'self': {'self': {'self': {'self': {'self': {...}}}}}}] = <yagot._garbagetracker.GarbageTracker object at 0x10df15f10>.garbage

    yagot_pytest/plugin.py:148: AssertionError
    =========================== 1 passed, 1 deselected, 1 error in 0.07s ===========================

Here is an example of how to use Yagot to detect collected objects caused by a
function using the
``garbage_checked``
decorator on the function.
The yagot pytest plugin is loaded in this example and it presence is reported
by pytest, but it is not used:

.. code-block:: text

    $ cat examples/test_2.py
    import yagot

    @yagot.garbage_checked()
    def test_selfref_dict():
        d1 = dict()
        d1['self'] = d1

    $ pytest examples -k test_2.py
    ===================================== test session starts ======================================
    platform darwin -- Python 3.7.5, pytest-5.3.5, py-1.8.1, pluggy-0.13.1
    rootdir: /Users/maiera/PycharmProjects/yagot/python-yagot
    plugins: cov-2.8.1, yagot-0.1.0.dev1
    collected 2 items / 1 deselected / 1 selected

    examples/test_2.py F                                                                     [100%]

    =========================================== FAILURES ===========================================
    ______________________________________ test_selfref_dict _______________________________________

    args = (), kwargs = {}, tracker = <yagot._garbagetracker.GarbageTracker object at 0x1078853d0>
    ret = None, location = 'test_2::test_selfref_dict'
    @py_assert1 = [{'self': {'self': {'self': {'self': {'self': {...}}}}}}], @py_assert3 = False
    @py_format4 = "\n~There were 1 collected or uncollectable object(s) caused by function test_2::test_selfref_dict:\n~\n~1: <class 'di...elf': {'self': {'self': {'self': {...}}}}}}] = <yagot._garbagetracker.GarbageTracker object at 0x1078853d0>.garbage\n}"

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
    >       assert not tracker.garbage, tracker.assert_message(location)
    E       AssertionError:
    E         There were 1 collected or uncollectable object(s) caused by function test_2::test_selfref_dict:
    E
    E         1: <class 'dict'> object at 0x1078843c0:
    E         {'self': <Recursive reference to dict object at 0x1078843c0>}
    E
    E       assert not [{'self': {'self': {'self': {'self': {'self': {...}}}}}}]
    E        +  where [{'self': {'self': {'self': {'self': {'self': {...}}}}}}] = <yagot._garbagetracker.GarbageTracker object at 0x1078853d0>.garbage

    yagot/_decorators.py:67: AssertionError
    =============================== 1 failed, 1 deselected in 0.07s ================================

In both usages, Yagot reports that there was one collected or uncollectable
object caused by the test function. The assertion message
provides some details about that object. In this case, we can see that the
object is a ``dict`` object, and that its 'self' item references back to the
same ``dict`` object, so there was a circular reference that caused the object
to become a collectable object.

That circular reference is simple enough for the Python garbage collector to
break it up, so this object does not become uncollectable.

The failure location and source code shown by pytest is the wrapper function of
the ``garbage_checked`` decorator and the ``pytest_runtest_teardown`` function
since this is where it is detected. The decorated function or pytest test case
that caused the objects to be created is reported in the assertion message
using a "module::function" notation.

Knowing the test function ``test_selfref_dict()`` that caused the object to
become a collectable object is a good start for identifying the problem code,
and in our example case it is easy to do because the test function is simple
enough. If the test function is too complex to identify the culprit, it can be
split into multiple simpler test functions, or new test functions can be added
to check out specific types of objects that were used.

As an exercise, test the standard ``dict`` class and the
``collections.OrderedDict`` class by creating empty dictionaries. You will find
that on CPython 2.7, ``collections.OrderedDict`` causes collected objects (see
`issue9825 <https://bugs.python.org/issue9825>`_).

The ``garbage_checked`` decorator can be combined with any other decorators in any
order. Note that it always tracks the next inner function, so unless you want
to track what garbage other decorators create, you want to have it directly on
the test function, as the innermost decorator, like in the following example:

.. code-block:: python

    import pytest
    import yagot

    @pytest.mark.parametrize('parm2', [ ... ])
    @pytest.mark.parametrize('parm1', [ ... ])
    @yagot.garbage_checked()
    def test_something(parm1, parm2):
        pass  # some test code


Documentation
-------------

* `Documentation <https://yagot.readthedocs.io/en/latest/>`_


Change History
--------------

* `Change history <https://yagot.readthedocs.io/en/latest/changes.html>`_


Contributing
------------

For information on how to contribute to the Yagot project, see
`Contributing <https://yagot.readthedocs.io/en/latest/development.html#contributing>`_.


License
-------

The Yagot project is provided under the
`Apache Software License 2.0 <https://raw.githubusercontent.com/andy-maier/python-yagot/master/LICENSE>`_.
