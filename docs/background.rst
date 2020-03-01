
.. _`Background`:

Background
==========


.. _`Understanding object release in Python`:

Understanding object release in Python
--------------------------------------

This section explains how Python releases objects, the role of the Python
garbage collector, the role of object references, and how memory leaks can
exist in Python. It is a rather brief description just enough to understand
what is relevant to your Python program.
Unless otherwise stated, the description applies to CPython with its
generational cyclic garbage collector (introduced in CPython 2.0).

Python has two mechanisms for releasing objects:

* Immediate release based on reference counting:

  If the reference count of an object drops to zero (e.g. because its
  referencing variable goes out of scope), the reference count of all objects
  it references are decreased by one, and the original object is immediately
  released.

  If it triggers, this process always succeeds. If the original object is
  involved in circular references, the process does not trigger in the first
  place, because the reference count of the original object never drops to zero.

  Those referenced objects whose reference count drops to zero as a result of
  being decreased will in turn be immediately released.

* Asynchronous release during garbage collection:

  Objects that can possibly be involved in circular references are tracked by
  the Python garbage collector. Python schedules runs of the garbage collector
  based on object allocation and deallocation heuristics. The garbage collector
  is able to release isolated sets of objects with circular references by
  breaking up these circular references.

  As an optimization, the garbage collector has 3 generations, and the
  heuristics are optimized such that younger generations are collected more
  often than older generations.

  There are circumstances whereby multiple collection runs are necessary to
  release objects, and where objects can end up as uncollectable, meaning they
  normally stay around until the Python process terminates.

When an object is created, Python decides whether or not the object is tracked
by the garbage collector. Whether an object is tracked or not can change over
the lifetime of the object. The :func:`py:gc.is_tracked` function returns
whether a particular object is currently tracked or untracked.

Untracked objects are not listed in any generation of the garbage collector,
so their release can only be done by the reference counting mechanism.
Python guarantees that objects that are untracked are not involved in circular
object references so their reference count does have a chance to drop to zero.

Tracked objects may or may not be involved in circular references. If they are
not, their release happens via the reference counting mechanism. If they are,
a garbage collection run (on the generation they are in) can release them.
During each collection run on a generation, the garbage collector examines the
objects in that generation to find isolated sets of objects with circular
references that are unreachable from outside of themselves. The garbage
collector tries to break up circular references to release such sets of objects.

Objects that become tracked (either at object creation or later) are always put
into the first generation of the garbage collector. When a garbage collection
run on a particular generation does not succeed in releasing an unreachable
isolated set of objects, the objects are moved into the next (older) generation.

Objects in the last (oldest) generation that survive a collection run stay in
the last generation. They will be attempted to be released again and again
during future runs of the garbage collector on the last generation. In most
cases, that will not succeed, but there are cases where it will. Unreachable
isolated set of objects in the last generation of the garbage collector are
called *uncollectable objects* and unless a future run succeeds in releasing
them, they remain allocated until the Python process terminates.

Uncollectable objects may be considered memory leaks, but this distinction is
not black and white because they may be successfully released in a future run
of the garbage collector on the last generation.

Among the possible reasons for objects to become uncollectable are:

* Before Python 3.4, the presence of the
  `__del__() method <https://docs.python.org/3/reference/datamodel.html>`_
  in a set of unreachable objects involved in circular references caused these
  objects to be uncollectable.
  The reason is that Python cannot safely decide for an order in which the
  ``__del__()`` methods should be invoked, because they might be using the
  reference to another object in the cycle. In Python 3.4,
  `PEP 442 -- Safe object finalization <https://www.python.org/dev/peps/pep-0442/>`_
  was implemented which ensures that the ``__del__()`` methods are invoked
  exactly once in all cases, but in a set of objects that has reference cycles,
  the order of invocation is undefined. Also, this change no longer causes
  objects with circular references to become uncollectable just because they
  have a ``__del__()`` method.

* Reference counting bugs in Python modules implemented in native languages
  such as C may cause objects to be uncollectable. For example, a Python module
  implemented in C could properly increase an object reference upon creation but
  forget to decrease it upon deletion. That will prevent the reference count
  from dropping to zero and thus will successfully prevent not only the
  immediate object release but also any future attempt of the garbage collector
  to release it.

If you want to understand this in more detail, here are a few good resources:

- `Garbage collection in Python: things you need to know (Artem Golubin) <https://rushter.com/blog/python-garbage-collector/>`_
- `Design of CPython’s Garbage Collector (Pablo Galindo Salgado) <https://devguide.python.org/garbage_collector/>`_
- `Python garbage collection (Digi.com) <https://www.digi.com/resources/documentation/digidocs/90001537/references/r_python_garbage_coll.htm>`_
- `Garbage Collection for Python (Neil Schemenauer) <http://arctrix.com/nas/python/gc/>`_
- `Safely using destructors in Python (Eli Bendersky) <https://eli.thegreenplace.net/2009/06/12/safely-using-destructors-in-python>`_
- `Python destructor and garbage collection notes (Ferry Boender) <https://www.electricmonk.nl/log/2008/07/07/python-destructor-and-garbage-collection-notes/>`_
- `Finalizer (Wikipedia) <https://en.wikipedia.org/wiki/Finalizer>`_
- `Object resurrection (Wikipedia) <https://en.wikipedia.org/wiki/Object_resurrection>`_


.. _`The issues with collected and uncollectable objects`:

The issues with collected and uncollectable objects
---------------------------------------------------

For short-running Python programs (e.g. command line utilities), it is mostly
not so important if there are some memory leaks and other resource leaks. On
most operating systems, resource cleanup at process termination is very thorough
and resources such as open files are cleaned up properly. I'm not advocating to
be careless there, in fact I would always recommend to also keep short-running
Python programs clean, but the negative effect is less severe compared to
long-running programs.

If your Python package provides modules for use by other code, you usually
cannot predict whether it will be used in short-running or long-running
programs. Therefore, resource usage in a Python module should be designed with
the worst case assumption in mind, i.e. that it is used by an infinitely running
piece of code.

The remainder of this section explains the issues with collected and
uncollectable objects caused during object release and how to address them:

* Issues with :term:`uncollectable objects`:

  - They often stay around until the Python process terminates, and thus can be
    considered memory leaks.

  - The garbage collector attempts to release them again and again on every
    collection run of its last generation, causing repeated unnecessary
    processing.

  In Python 3.4 or higher, the reasons for uncollectable objects have diminished
  very much and their presence usually indicates a bug. You should use tools
  that can detect uncollectable objects and then analyze each case to find out
  what caused the object to be uncollectable.

* Issues with :term:`collected objects`:

  - Increased processing overhead caused by the collector runs (compared to
    immediate release based on reference counting).

  - Suspension of all other activity in the Python process when the garbage
    collector runs.

  - The amount of memory bound to these objects until the garbage collector
    will run for the next time. Automatic runs of the garbage collector are
    triggered by heuristics that are based on the number of objects and not on
    the amount of memory bound to these objects, so it is possible to have
    a small number of collectable objects with large amounts of memory
    allocated, that are still not triggering a garbage collector run.

  Suitable measures to address these issues with collected objects:

  - Redesign to avoid circular references.

  - Replacement of normal references with
    `weak references <https://docs.python.org/3/library/weakref.html>`_ to
    get rid of circular references. Using weak references requires to be able
    to handle the case where the referenced object is unexpectedly gone, which
    can be properly detected.

  - Manually triggering additional garbage collector runs via
    :func:`py:gc.collect`. There are very few cases though where this actually
    improves anything. One reasonable case might be to trigger a collection
    after application startup to release the many objects that have been used
    temporarily during configuration and initial startup processing.

* Issues with the ``__del__()`` method on objects that are involved in circular
  references on Python before 3.4:

  - The ``__del__()`` methods are not invoked, so the resource cleanup
    designed to be done by them does not happen.

  - In addition, the objects become uncollectable.

  Suitable measures to address these issues with the ``__del__()`` method:

  - The use of
    `context managers <https://docs.python.org/3/library/stdtypes.html#typecontextmanager>`_
    is a good alternative to the use of the ``__del__()`` method, particularly
    on Python before 3.4.


.. _`Circular reference examples and detection`:

Circular reference examples and detection
-----------------------------------------

This section shows some simple examples of circular references.

Let's first look at a simple way to surface circular references. The
approach is to create an object, make it unreachable, and check whether a run
of the garbage collector releases an object. If the object is involved in
circular references, its reference count will not drop to zero when it becomes
unreachable, but the garbage collector will be able to break up the circular
references and release it. If the object is not involved in circular references,
it will be released when it becomes it unreachable, and the garbage collector
does not have anything to do with it (even when it was tracked).

This is basically the approach Yagot uses, although in a more automated fashion.

.. code-block:: text

    $ python
    >>> import gc
    >>> gc.collect()   # Run full garbage collection to have a reference
    0                  # No objects collected initially (in this simple case)
    >>> obj = dict()
    >>> len(gc.get_referrers(obj))
    1                 # The dict object has one referrer (the 'obj' variable)
    >>> obj['self'] = obj
    >>> len(gc.get_referrers(obj))
    2                 # The dict object now in addition has its 'self' item as a referrer
    >>> gc.collect()
    0                  # Still no new objects collected
    >>> del obj        # The dict object becomes unreachable ...
    >>> gc.collect()
    1                  # ... and was released by the next garbage collection run

The interesting part happens during the ``del obj`` statement. The ``del obj``
statement removes the name ``obj`` from its namespace. That causes the reference
count of the :class:`dict` object to drop by one. Because of the circular
reference back from its 'self' item, the reference count is still 1, so it will
not be released at that point. The call to :func:`py:gc.collect` triggers a full
garbage collection run on all generations, which successfully breaks up the
circular reference and releases the object, as reported by its return value
of 1.

Here are some examples for circular references. You can inspect them using
the approach described above:

* List with a self-referencing item. This is not really useful code,
  but just a simple way to demonstrate a circular reference:

  .. code-block:: python

      obj = list()
      obj.append(obj)

* Class with a self-referencing attribute. Another simple example for
  demonstration purposes:

  .. code-block:: python

      class SelfRef(object):

          def __init__(self):
              self.ref = self

      obj = SelfRef()

* A tree node class that knows its parent and children. This is a more practical
  example and is very similar to what is done in
  `xml.dom.minidom <https://docs.python.org/3/library/xml.dom.minidom.html>`_:

  .. code-block:: python

      class Node(object):

          def __init__(self):
              self.parentNode = None
              self.childNodes = []

          def appendChild(self, node):
              node.parentNode = self
              self.childNodes.append(node)

      obj = Node()
      obj.appendChild(Node())


.. _`Tools`:

Tools
-----

This section lists some tools that can be used to detect memory leaks, garbage
objects, and memory usage in Python.

**TODO: Write section**
