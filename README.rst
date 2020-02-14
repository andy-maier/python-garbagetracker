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

It provides a Python decorator named ``garbage_tracked`` which asserts that the
decorated function or method does not create any garbage objects.

Garbage objects are Python objects that cannot be immediately released when
the object becomes unreachable and are therefore put into the generational
Python garbage collector where more elaborated algorithms are used at a later
point in time to release the objects.

This may create problems for your Python application for two reasons:

1. The time delay involved in this approach keeps memory allocated for longer
   than necessary, causing increased memory consumption.

2. There are cases where even the more elaborated algorithms cannot release a
   garbage object. If that happens, it is a memory leak that remains until
   the Python process ends.

The ``garbage_tracked``  decorator can be used on any function or method, but
it makes most sense to use it on test functions. It is a signature-preserving
decorator that supports any number of positional and keyword arguments in the
decorated function or method, and any kind of return value(s).

That decorator can be used with test functions or methods in all test
frameworks, for example `pytest`_, `nose`_, or `unittest`_.

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

.. _Installation: https://yagot.readthedocs.io/en/stable/intro.html#installation


Quick start
-----------

Here is an example of using it with pytest:

In ``examples/test_selfref_dict.py``:

.. code-block:: python

    from yagot import garbage_tracked

    @garbage_tracked
    def test_selfref_dict():

        # Dictionary with self-referencing item:
        d1 = dict()
        d1['self'] = d1

Running pytest on this example reveals the garbage object with a test failure
raised by yagot:

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

    args = (), kwargs = {}, tracker = <yagot._garbagetracker.GarbageTracker object at 0x10e451f90>
    ret = None, location = 'test_selfref_dict::test_selfref_dict'

        def garbage_tracked_wrapper(*args, **kwargs):
            """
            Wrapper function for the @garbage_tracked decorator.
            """
            tracker = GarbageTracker.get_tracker('yagot.garbage_tracked')
            tracker.enable()
            tracker.start()
            ret = func(*args, **kwargs)  # The decorated function
            tracker.stop()
            location = "{module}::{function}".format(
                module=func.__module__, function=func.__name__)
    >       assert not tracker.garbage, tracker.format_garbage(location)
    E       AssertionError:
    E       There was 1 garbage object(s) caused by function test_selfref_dict::test_selfref_dict:
    E
    E       1: <type 'dict'> object at 0x10e514d70:
    E       { 'self': <Recursive reference to dict object at 0x10e514d70>}

    yagot/_decorators.py:43: AssertionError
    =================================== 1 failed in 0.07 seconds ===================================

The AssertionError shows that there was one garbage object detected, and
details about that object. In this case, the garbage object is a ``dict``
object, and we can see that its 'self' item references back to the dict object.

The failure location and source code shown by pytest is the wrapper function of
the ``garbage_tracked`` decorator, since this is where it is detected.
The decorated function that caused the garbage objects to be created is
reported by pytest as a failing test function, and is also mentioned in the
assertion message using a "module::function" notation.

Knowing the test function ``test_selfref_dict()`` that caused the object to
become a garbage object is a good start to identify the problem code, and in
our example case it is easy to do. In more complex situations, it may be helpful
to split the complex test function into multiple simpler test functions.

The ``garbage_tracked`` decorator can be combined with any other decorators.
Note that it always tracks the decorated function, so unless you want to track
what garbage other decorators create, you want to have it directly on the test
function, as the innermost decorator:

.. code-block:: python

    import pytest
    from yagot import garbage_tracked

    @pytest.mark.parametrize('parm2', [ ... ])
    @pytest.mark.parametrize('parm1', [ ... ])
    @garbage_tracked
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
