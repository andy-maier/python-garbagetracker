
.. _`Introduction`:

Introduction
============

Yagot is Yet Another Garbage Object Tracker for Python.

It provides a Python decorator named ``garbage_tracked`` which asserts that the
decorated function or method does not create any garbage objects.

Garbage objects are Python objects that cannot be immediately released when
the object becomes unreachable and are therefore put into the *generational
Python garbage collector* where more elaborated algorithms are used at a later
point in time to release the objects.

Garbage objects may create problems for your Python application for two reasons:

1.  The time delay caused by the asynchronous processing of the Python garbage
    collector causes the memory of the garbage objects to be allocated for longer
    than necessary, causing increased memory consumption. The severity of this
    problem increases with the amount and frequency of garbage objects created.

2.  There are cases where even the more elaborated algorithms of the Python
    garbage collector cannot release a garbage object. In such a case, the
    memory for the garbage garbage objects remains allocated within the Python
    process, causing a memory leak that remains until the Python process ends.

The ``garbage_tracked``  decorator can be used on any function or method, but
it makes most sense to use it on test functions. It is a signature-preserving
decorator that supports any number of positional and keyword arguments in the
decorated function or method, and any kind of return value(s).

That decorator can be used with test functions or methods in all test
frameworks, for example `pytest`_, `nose`_, or `unittest`_.

.. _pytest: https://docs.pytest.org/
.. _nose: https://nose.readthedocs.io/
.. _unittest: https://docs.python.org/3/library/unittest.html


.. _`Usage`:

Usage
-----

Here is an example of how to use Yagot with a pytest testcase:

In an example test file ``examples/test_selfref_dict.py``, you would have:

.. code-block:: python

    import yagot

    @yagot.garbage_tracked
    def test_selfref_dict():
        d1 = dict()
        d1['self'] = d1

Running pytest on this example test file reveals the presence of garbage objects
because it raises a test failure:

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

The AssertionError raised by Yagot shows that there was one garbage object
detected in the decorated test function, and some details about that object.
In this case, we can see that the garbage object is a ``dict`` object, and that
its 'self' item references back to the same ``dict`` object, so there was
a reference cycle that caused the object to become a garbage object.

The failure location and source code shown by pytest is the wrapper function of
the ``garbage_tracked`` decorator, since this is where it is detected.
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
that on Python 2, ``collections.OrderedDict`` causes garbage objects (in the
CPython implementation).

The ``garbage_tracked`` decorator can be combined with any other decorators in
any order. Note that it always tracks the next inner function, so unless you
want to track what garbage other decorators create, you want to have it
directly on the test function, as the innermost decorator, like in the following
example:

.. code-block:: python

    import pytest
    import yagot

    @pytest.mark.parametrize('parm2', [ ... ])
    @pytest.mark.parametrize('parm1', [ ... ])
    @yagot.garbage_tracked
    def test_something(parm1, parm2):
        pass  # some test code


.. _`Reference cycles`:

Reference cycles
----------------

In probably all cases, such garbage objects are caused by cyclic references
between objects. Here are some simple cases of objects with reference cycles:

.. code-block:: python

    # Dictionary with self-referencing item:
    d1 = dict()
    d1['self'] = d1

    # Object of a class with self-referencing attribute:
    class SelfRef(object):
         def __init__(self):
             self.ref = self
    obj = SelfRef()

The garbage objects created as a result can be inspected by the standard Python
module ``gc`` that provides access to the garbage collector:

.. code-block:: text

    $ python
    >>> import gc
    >>> gc.collect()
    0                  # No garbage objects initially (in this simple case)
    >>> d1 = dict(); d1['self'] = d1
    >>> d1
    {'self': {...}}
    >>> gc.collect()
    0                  # Still no garbage objects
    >>> del d1         # The dict object becomes unreachable ...
    >>> gc.collect()
    1                  # ... and ends up as one garbage object

The interesting part happens during the ``del d1`` statement, but let's first
level set on names vs. objects in Python: A variable (``d1``) is not an object
but a name that is bound to an object (of type ``dict``). The ``del d1``
statement removes the name ``d1`` from its namespace. That causes the reference
count of the ``dict`` object to drop to 0 (in this case, where there is no other
variable name bound to it and no other object referencing it). The object is
then said to be "unreachable". That causes Python to try to immediately release
the ``dict`` object. This does not work because of the self-reference, so it is
put into the garbage collector for later treatment.


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

The examples in the previous sections install the latest version of
yagot that is released on `PyPI`_.
This section describes how different versions of yagot
can be installed.

* To install an older released version of yagot,
  Pip supports specifying a version requirement. The following example installs
  yagot version 0.1.0
  from PyPI:

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


.. _`Package version`:

Package version
---------------

The version of the yagot package can be accessed by
programs using the ``yagot.__version__`` variable:

.. autodata:: yagot._version.__version__

Note: For tooling reasons, the variable is shown as
``yagot._version.__version__``, but it should be used as
``yagot.__version__``.


.. _`Compatibility and deprecation policy`:

Compatibility and deprecation policy
------------------------------------

The Yagot project uses the rules of
`Semantic Versioning 2.0.0`_ for compatibility between versions, and for
deprecations. The public interface that is subject to the semantic versioning
rules and specificically to its compatibility rules are the APIs and commands
described in this documentation.

.. _Semantic Versioning 2.0.0: https://semver.org/spec/v2.0.0.html

The semantic versioning rules require backwards compatibility for new minor
versions (the 'N' in version 'M.N.P') and for new patch versions (the 'P' in
version 'M.N.P').

Thus, a user of an API or command of the Yagot project
can safely upgrade to a new minor or patch version of the
yagot package without encountering compatibility
issues for their code using the APIs or for their scripts using the commands.

In the rare case that exceptions from this rule are needed, they will be
documented in the :ref:`Change log`.

Occasionally functionality needs to be retired, because it is flawed and a
better but incompatible replacement has emerged. In the
Yagot project, such changes are done by deprecating
existing functionality, without removing it immediately.

The deprecated functionality is still supported at least throughout new minor
or patch releases within the same major release. Eventually, a new major
release may break compatibility by removing deprecated functionality.

Any changes at the APIs or commands that do introduce
incompatibilities as defined above, are described in the :ref:`Change log`.

Deprecation of functionality at the APIs or commands is
communicated to the users in multiple ways:

* It is described in the documentation of the API or command

* It is mentioned in the change log.

* It is raised at runtime by issuing Python warnings of type
  ``DeprecationWarning`` (see the Python :mod:`py:warnings` module).

Since Python 2.7, ``DeprecationWarning`` messages are suppressed by default.
They can be shown for example in any of these ways:

* By specifying the Python command line option: ``-W default``
* By invoking Python with the environment variable: ``PYTHONWARNINGS=default``

It is recommended that users of the Yagot project
run their test code with ``DeprecationWarning`` messages being shown, so they
become aware of any use of deprecated functionality.

Here is a summary of the deprecation and compatibility policy used by
the Yagot project, by version type:

* New patch version (M.N.P -> M.N.P+1): No new deprecations; no new
  functionality; backwards compatible.
* New minor release (M.N.P -> M.N+1.0): New deprecations may be added;
  functionality may be extended; backwards compatible.
* New major release (M.N.P -> M+1.0.0): Deprecated functionality may get
  removed; functionality may be extended or changed; backwards compatibility
  may be broken.
