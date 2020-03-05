
.. _`API reference`:

API reference
=============

This section describes the API of Yagot.

There are two main elements of the API:

* :func:`yagot.garbage_checked`: A decorator that checks for
  :term:`uncollectable objects` and optionally for :term:`collected objects`
  caused by the decorated function or method and raises AssertionError if
  detected.

* :class:`yagot.GarbageTracker`: A class that checks for
  :term:`uncollectable objects` and optionally for :term:`collected objects`
  caused during a tracking period. This is a plumbing class the
  :func:`yagot.garbage_checked` decorator and the pytest plugin of Yagot use, and
  that other packages building on Yagot can also use.


yagot.garbage_checked
---------------------

.. autofunction:: yagot.garbage_checked


yagot.GarbageTracker
--------------------

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


yagot.__version__
-----------------

The version of the yagot package can be accessed by
programs using the ``yagot.__version__`` variable:

.. autodata:: yagot._version.__version__

Note: For tooling reasons, the variable is shown as
``yagot._version.__version__``, but it should be used as
``yagot.__version__``.
