
.. _`API reference`:

API reference
=============

This section describes the API of Yagot.

There are two main elements of the API:

* :func:`yagot.assert_no_garbage`: A decorator that asserts there was no garbage
  created in the decorated function or method. This is what a Python developer
  in search of memory leaks would be using.

* :class:`yagot.GarbageTracker`: A class that detects garbage objects created
  during a tracking period. This is a kind of plumbing class that other packages
  building on Yagot would be using.


.. autofunction:: yagot.assert_no_garbage


.. autoclass:: yagot.GarbageTracker
   :members:

   .. rubric:: Methods

   .. autoautosummary:: yagot.GarbageTracker
      :methods:
      :nosignatures:

   .. rubric:: Attributes

   .. autoautosummary:: yagot.GarbageTracker
      :attributes:

   .. rubric:: Details
