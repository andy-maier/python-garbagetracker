
.. _`API reference`:

API reference
=============

This section describes the API of Yagot.

There are two main elements of the API:

* :func:`yagot.leak_check`: A decorator that checks for new
  :term:`uncollectable objects` and optionally :term:`garbage objects` caused
  by the decorated function or method and raises AssertionError if detected.
  This is what a Python developer in search of memory leaks would be using.

* :class:`yagot.GarbageTracker`: A class that detects
  :term:`uncollectable objects` and :term:`garbage objects` created during a
  tracking period. This is a plumbing class the :func:`yagot.leak_check`
  decorator uses and that other packages building on Yagot can also use.


.. autofunction:: yagot.leak_check


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
