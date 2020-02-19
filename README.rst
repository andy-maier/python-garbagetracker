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

Yagot is Yet Another Garbage Object Tracker for Python.

Here is what can you do with it:

* Find memory leaks.

  More specifically, determine the number of *uncollectable objects* caused by
  a function or method.

  Uncollectable objects are objects Python was unable to release during garbage
  collection, even when running a full collection (i.e. on all generations of
  the Python generational garbage collector). Uncollectable objects remain
  allocated in the last generation of the garbage collector and cause memory
  leaks that are only resolved when the Python process terminates.

  Among the possible reasons for objects to become uncollectable are:

  * more complicated cases of cyclic references between objects,

  * reference counting bugs in Python modules implemented in native languages
    such as C.

* Reduce unnecessary memory usage caused by deferred release of objects that
  have cyclic references.

  More specifically, determine the set of *garbage objects* caused by a function
  or method.

  Garbage objects are objects Python cannot immediately release when they
  become unreachable (e.g. when their variable goes out of scope). They
  are put into the Python garbage collector for processing at a later point in
  time using more sophisticated approaches. For example, Python attempts to
  break up reference cycles during garbage collection.

  Garbage objects cause increased memory usage because they are released only
  at a later point in time. In the worst case, a garbage object needs to pass
  through all three generations of the Python garbage collector, and each
  subsequent generation is collected less frequently than the previous one.
  Note that garbage objects do not necessarily cause permanent memory leaks,
  except if they cannot be released in the last generation of the garbage
  collector. At that point, a garbage object is also an uncollectable object.

  The overall severity of the issue of increased memory usage depends on the
  number and size of garbage objects.

Yagot is designed to be useable independent of any test framework, but it can
also be used with test frameworks such as `pytest`_, `nose`_, or `unittest`_.

Yagot provides a Python decorator named ``assert_no_garbage`` which validates
that the decorated function or method does not create any uncollectable objects
or garbage objects, and raises an AssertionError otherwise.

The ``assert_no_garbage`` decorator can be used on any function or method, but
it makes most sense to use it on test functions.

.. _pytest: https://docs.pytest.org/
.. _nose: https://nose.readthedocs.io/
.. _unittest: https://docs.python.org/3/library/unittest.html


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

Here is an example of how to use Yagot with a pytest testcase:

Consider an example test file ``examples/test_selfref_dict.py``:

.. code-block:: python

    import yagot

    @yagot.assert_no_garbage
    def test_selfref_dict():
        d1 = dict()
        d1['self'] = d1

Running pytest on this example test file reveals the presence of garbage objects
by raising a test failure:

.. code-block:: text

    $ pytest examples -k test_selfref_dict.py

    ===================================== test session starts ======================================
    platform darwin -- Python 2.7.16, pytest-4.6.9, py-1.8.1, pluggy-0.13.1
    rootdir: /Users/maiera/PycharmProjects/python-yagot
    plugins: cov-2.8.1
    collected 1 item

    examples/test_selfref_dict.py F                                                          [100%]

    =========================================== FAILURES ===========================================
    ______________________________________ test_selfref_dict _______________________________________


    args = (), kwargs = {}, tracker = <yagot._garbagetracker.GarbageTracker object at 0x108353250>
    ret = None, location = 'test_selfref_dict::test_selfref_dict'

        def assert_no_garbage_wrapper(*args, **kwargs):
            """
            Wrapper function for the assert_no_garbage decorator.
            """
            tracker = GarbageTracker.get_tracker('yagot.assert_no_garbage')
            tracker.enable()
            tracker.start()
            ret = func(*args, **kwargs)  # The decorated function
            tracker.stop()
            location = "{module}::{function}".format(
                module=func.__module__, function=func.__name__)
            assert not tracker.garbage and not tracker.uncollectable_count, \
    >           tracker.assert_message(location)
    E       AssertionError:
    E       There were 0 uncollectable object(s) and 1 garbage object(s) caused by function test_selfref_dict::test_selfref_dict:
    E
    E       1: <type 'dict'> object at 0x10834ee88:
    E       { 'self': <Recursive reference to dict object at 0x10834ee88>}

    yagot/_decorators.py:42: AssertionError
    =================================== 1 failed in 0.07 seconds ===================================

The AssertionError raised by Yagot shows that there were no uncollectable
objects caused by the decorated test function, but one garbage object.
The assertion message provides some details about that object.
In this case, we can see that the garbage object is a ``dict`` object, and that
its 'self' item references back to the same ``dict`` object, so there was
a reference cycle that caused the object to become a garbage object.

That reference cycle is simple enough for the Python garbage collector to break
it up, so this garbage object does not become an uncollectable object.

The failure location and source code shown by pytest is the wrapper function of
the ``assert_no_garbage`` decorator, since this is where it is detected.
The decorated function that caused the garbage objects to be created is
reported by pytest as a failing test function, and is also mentioned in the
assertion message using a "module::function" notation.

Knowing the test function ``test_selfref_dict()`` that caused the object to
become a garbage object is a good start for identifying the problem code, and in
our example case it is easy to do because the test function is simple enough.
If the test function is too complex to identify the culprit, it can be split
into multiple simpler test functions, or new test functions can be added to
check out specific types of objects that were used.

As an exercise, check out the standard ``dict`` class and the
``collections.OrderedDict`` class by creating empty dictionaries. You will find
that on Python 2.7, ``collections.OrderedDict`` causes garbage objects
(in the CPython implementation, see
`issue9825 <https://bugs.python.org/issue9825>`_).

The ``assert_no_garbage`` decorator can be combined with any other decorators in
any order. Note that it always tracks the next inner function, so unless you
want to track what garbage other decorators create, you want to have it
directly on the test function, as the innermost decorator, like in the following
example:

.. code-block:: python

    import pytest
    import yagot

    @pytest.mark.parametrize('parm2', [ ... ])
    @pytest.mark.parametrize('parm1', [ ... ])
    @yagot.assert_no_garbage
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
