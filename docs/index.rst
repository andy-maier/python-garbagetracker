
Yagot - Yet Another Garbage Object Tracker for Python
*****************************************************

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

.. toctree::
   :maxdepth: 2
   :numbered:

   intro.rst
   development.rst
   appendix.rst
   changes.rst
