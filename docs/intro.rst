
.. _`Introduction`:

Introduction
============

Yagot (Yet Another Garbage Object Tracker) is a tool for Python developers to
help find issues with garbage collection and memory leaks:

* It can determine the set of *collected objects* caused by a function or
  method.

  Collected objects are objects Python could not immediately release when they
  became unreachable and that were eventually released by the Python garbage
  collector. Frequently this is caused by the presence of circular references
  into which the object to be released is involved. The garbage collector is
  designed to handle circular references when releasing objects.

* It can determine the set of *uncollectable objects* caused by a function or
  method.

  Uncollectable objects are objects Python was unable to release during garbage
  collection, even when running a full collection (i.e. on all generations of
  the Python generational garbage collector). Uncollectable objects remain
  allocated in the last generation of the garbage collector. On each run on
  its last generation, the garbage collector attempts to release these objects.
  It seems to be rare that these continued attempts eventually succeed, so
  these objects can basically be considered memory leaks.

See section
:ref:`Background`
for more detailed explanations about object release in Python.

Yagot is simple to use in either of the following ways:

* It provides a `pytest`_ plugin that detects collected and uncollectable
  objects caused by the test cases. This detection is enabled by specifying
  command line options or environment variables and does not require modifying
  the test cases.

* It provides a Python decorator named
  :func:`~yagot.garbage_checked`
  that detects collected and uncollectable objects caused by the decorated
  function or method. This allows using Yagot independent of any test framework
  or with other test frameworks such as `nose`_ or `unittest`_.

Yagot works with a normal (non-debug) build of Python.

.. _pytest: https://docs.pytest.org/
.. _nose: https://nose.readthedocs.io/
.. _unittest: https://docs.python.org/3/library/unittest.html


.. _`Usage`:

Usage
-----

Here is an example of how to use Yagot to detect collected objects caused by
pytest test cases using the command line options provided by the pytest plugin
of Yagot:

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
function using the ``garbage_checked`` decorator of Yagot on the function:

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
