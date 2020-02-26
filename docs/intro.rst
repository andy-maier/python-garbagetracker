
.. _`Introduction`:

Introduction
============

Yagot (Yet Another Garbage Object Tracker) is a tool for Python developers to
help you finding issues with garbage collection and memory leaks:

* It can determine the set of new *garbage objects* caused by a function or
  method.

  Garbage objects are objects Python cannot immediately release when they
  become unreachable (e.g. when their variable goes out of scope). Frequently
  this is caused by the presence of circular references into which the
  object to be released is involved. The garbage collector, which is designed
  to handle circular references, attempts to release garbage objects.

* It can determine the number of new *uncollectable objects* caused by a
  function or method.

  Uncollectable objects are objects Python was unable to release during garbage
  collection, even when running a full collection (i.e. on all generations of
  the Python generational garbage collector). Uncollectable objects remain
  allocated in the last generation of the garbage collector. On each run on
  its last generation, the garbage collector attempts to release these objects.
  It seems to be rare that these continued attempts eventually succeed, so
  these objects can basically be considered memory leaks.

See section
:ref:`Background`
for more detailed explanations.

Yagot is designed to be useable independent of any test framework, but it can
also be used with test frameworks such as `pytest`_, `nose`_, or `unittest`_.

Yagot works with a normal (non-debug) build of Python.

Yagot is simple to use: It provides a Python decorator named
:func:`~yagot.leak_check`
which validates that the decorated function or method does not create any
uncollectable objects or garbage objects, and raises an
:exc:`~py:exceptions.AssertionError`
otherwise. Simply use the decorator on a function you want to check. It can be
used on any function or method, but it makes most sense to use it on test
functions.

.. _pytest: https://docs.pytest.org/
.. _nose: https://nose.readthedocs.io/
.. _unittest: https://docs.python.org/3/library/unittest.html


.. _`Usage`:

Usage
-----

Here is an example of how to use Yagot with a pytest testcase:

Consider an example test file ``examples/test_selfref_dict.py``:

.. code-block:: python

    import yagot

    @yagot.leak_check()
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

    args = (), kwargs = {}, tracker = <yagot._garbagetracker.GarbageTracker object at 0x106d94290>
    ret = None, location = 'test_selfref_dict::test_selfref_dict', no_leaks = True
    no_garbage = False

        @functools.wraps(func)
        def wrapper_leak_check(*args, **kwargs):
            "Wrapper function for the leak_check decorator"
            tracker = GarbageTracker.get_tracker('yagot.leak_check')
            tracker.enable()
            tracker.start()
            tracker.ignore_garbage_types(ignore_garbage_types)
            ret = func(*args, **kwargs)  # The decorated function
            tracker.stop()
            location = "{module}::{function}".format(
                module=func.__module__, function=func.__name__)
            no_leaks = not tracker.uncollectable_count
            no_garbage = ignore_garbage or not tracker.garbage
    >       assert no_leaks and no_garbage, tracker.assert_message(location)
    E       AssertionError:
    E       There were 0 uncollectable object(s) and 1 garbage object(s) caused by function test_selfref_dict::test_selfref_dict:
    E
    E       1: <type 'dict'> object at 0x106d8ae88:
    E       { 'self': <Recursive reference to dict object at 0x106d8ae88>}

    yagot/_decorators.py:59: AssertionError
    =================================== 1 failed in 0.07 seconds ===================================

The :exc:`~py:exceptions.AssertionError` raised by Yagot shows that there were
no uncollectable objects caused by the decorated test function, but one garbage
object. The assertion message provides some details about that object.
In this case, we can see that the garbage object is a :class:`py:dict` object, and that
its 'self' item references back to the same :class:`py:dict` object, so there was
a circular reference that caused the object to become a garbage object.

That circular reference is simple enough for the Python garbage collector to break
it up, so this garbage object does not become an uncollectable object.

The failure location and source code shown by pytest is the wrapper function of
the :func:`~yagot.leak_check` decorator, since this is where it is detected.
The decorated function that caused the garbage objects to be created is
reported by pytest as a failing test function, and is also mentioned in the
assertion message using a "module::function" notation.

Knowing the test function :func:`test_selfref_dict` that caused the object to
become a garbage object is a good start for identifying the problem code, and in
our example case it is easy to do because the test function is simple enough.
If the test function is too complex to identify the culprit, it can be split
into multiple simpler test functions, or new test functions can be added to
check out specific types of objects that were used.

As an exercise, test the standard :class:`py:dict` class and the
:class:`py:collections.OrderedDict` class by creating empty dictionaries. You
will find that on Python 2.7, :class:`py:collections.OrderedDict` causes
garbage objects (in the CPython implementation, see
`issue9825 <https://bugs.python.org/issue9825>`_).

The :func:`~yagot.leak_check` decorator can be combined with any other
decorators in any order. Note that it always tracks the next inner function,
so unless you want to track what garbage other decorators create, you want to
have it directly on the test function, as the innermost decorator, like in the
following example:

.. code-block:: python

    import pytest
    import yagot

    @pytest.mark.parametrize('parm2', [ ... ])
    @pytest.mark.parametrize('parm1', [ ... ])
    @yagot.leak_check()
    def test_something(parm1, parm2):
        pass  # some test code


.. _`Installation`:

Installation
------------

.. _`Supported environments`:

Supported environments
^^^^^^^^^^^^^^^^^^^^^^

Yagot is supported in these environments:

* Operating Systems: Linux, Windows (native, and with UNIX-like environments),
  OS-X

* Python: 2.7, 3.4, and higher


.. _`Installing`:

Installing
^^^^^^^^^^

* Prerequisites:

  - The Python environment into which you want to install must be the current
    Python environment, and must have at least the following Python packages
    installed:

    - setuptools
    - wheel
    - pip

* Install the yagot package and its prerequisite Python packages into the
  active Python environment:

  .. code-block:: bash

      $ pip install yagot


.. _`Installing a different version`:

Installing a different version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The examples in the previous sections install the latest version of Yagot that
is released on `PyPI`_. This section describes how different versions of Yagot
can be installed.

* To install an older released version of Yagot, Pip supports specifying a
  version requirement. The following example installs Yagot version 0.1.0 from
  PyPI:

  .. code-block:: bash

      $ pip install yagot==0.1.0

* If you need to get a certain new functionality or a new fix that is
  not yet part of a version released to PyPI, Pip supports installation from a
  Git repository. The following example installs yagot
  from the current code level in the master branch of the
  `python-yagot repository`_:

  .. code-block:: bash

      $ pip install git+https://github.com/andy-maier/python-yagot.git@master#egg=yagot

.. _python-yagot repository: https://github.com/andy-maier/python-yagot

.. _PyPI: https://pypi.python.org/pypi


.. _`Verifying the installation`:

Verifying the installation
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can verify that yagot is installed correctly by
importing the package into Python (using the Python environment you installed
it to):

.. code-block:: bash

    $ python -c "import yagot; print('ok')"
    ok

In case of trouble with the installation, see the :ref:`Troubleshooting`
section.
