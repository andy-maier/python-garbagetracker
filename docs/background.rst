
.. _`Background`:

Background
==========


.. _`Object release in Python`:

Object release in Python
------------------------

This section explains how Python releases objects, the role of the Python
garbage collector, the role of object references, and how memory leaks can
exist in Python. It is a rather brief description just enough to understand
what is relevant to your Python program.
Unless otherwise stated, the description applies to CPython with its
generational garbage collector (introduced in CPython 2.0).

Python has two mechanisms for releasing objects:

* immediate release based on reference counting - if the reference count of
  an object drops to 0, it is immediately attempted to be released. This
  succeeds, if all referenced objects also can be released that way. Circular
  references prevent this mechanism to succeed. If it does not succeed, release
  of the object is left to the garbage collector.

* asynchronous release during garbage collection - Python schedules garbage
  collection based on object allocation and deallocation heuristics. The
  garbage collector is able to release isolated sets of objects with circular
  references (that's why it is sometimes called "cyclic garbage collector").
  As an optimization, the garbage collector has 3 generations (that's why it is
  sometimes called "generational garbage collector"), and the heuristics are
  optimized such that younger generations are collected more often than
  older generations.
  There are circumstances whereby multiple collection runs are necessary to
  release objects, and where objects can end up as uncollectable, meaning they
  normally stay around until the Python process terminates.

When an object is created, Python decides whether or not the object is tracked
by the garbage collector. The :func:`py:gc.is_tracked` function returns
whether a particular object is currently tracked or untracked.

Untracked objects are not listed in any generation of the garbage collector,
and can only be released using the immediate release based on reference
counting, which always succeeds.

Tracked objects are attempted to be released using the immediate release
based on reference counting, which potentially does not succeed. They are
also attempted to be released during garbage collector runs on the
generation they are in.

Whether an object is tracked or not can change over the lifetime of the object,
and has been optimized in Python. For example, non-empty tuples are initially
tracked and will become untracked if during the first garbage collection run
it turns out they have only immutable items. This prevents the check for tuple
items at creation time, and the garbage collector has to examine the items
anyway.

Objects that become tracked (either at object creation or later) are always put
into the first generation of the garbage collector. When a garbage collection
run on a particular generation does not succeed in releasing an object, the
object is moved into the next (older) generation.
During each run on a generation, the garbage collector examines the objects
in that generation to find unreachable sets of objects. If these objects have
circular references, the garbage collector tries to break them up to release
the objects.

Objects in the last (oldest) generation that survive a collection run stay in
the last generation. They are attempted to be released again upon the next run
of the garbage collector on the last generation, and that may or may not
succeed. Unreachable objects in the last generation of the garbage collector are
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

* reference counting bugs in Python modules implemented in native languages
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


.. _`Why this is important and how to address it`:

Why this is important and how to address it
-------------------------------------------

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

The important aspects around object release are:

* :term:`Uncollectable objects` have issues:

  - They usually stay around until the Python process terminates.

  - The garbage collector attempts to release them again and again on every
    collection run of its last generation, causing repeated unnecessary
    processing.

  In Python 3.4 or higher, the reasons for uncollectable objects have diminished
  very much and their presence usually indicates a bug. You should use tools
  that can detect them and then analyze each case to find out what caused the
  object to be uncollectable.

* :term:`Garbage objects` have issues:

  Garbage objects normally can be successfully released by the garbage
  collector (at least starting with Python 3.4). Most of the time, garbage
  objects are caused by circular references. Their presence is less severe
  than the presence of uncollectable objects. Nevertheless, garbage objects
  have some issues:

  - increased processing overhead caused by the collector runs.

  - suspension of all other activity in the Python process when the garbage
    collector runs.

  - the amount of memory bound to these objects until the garbage collector
    will run for the next time. Automatic runs of the garbage collector are
    triggered by heuristics that are based on the number of objects and not on
    the amount of memory bound to these objects.

  You should use tools that can detect garbage objects. Some suitable measures
  to address these issues are:

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

* On Python before 3.4, the presence of a ``__del__()`` method on objects that
  are involved in circular references has issues:

  - The ``__del__()`` methods are not invoked, so the resource cleanup
    designed to be done by them does not happen.

  - In addition, the objects become uncollectable.

  The use of
  `context managers <https://docs.python.org/3/library/stdtypes.html#typecontextmanager>`_
  is a good alternative to the use of the ``__del__()`` method, particularly
  on Python before 3.4.


.. _`Circular reference examples and detection`:

Circular reference examples and detection
-----------------------------------------

This section shows some simple examples of circular references.

Let's first look at a simple way to surface circular references. The
approach is to create an object, make it unreachable, and check whether
it appears in the garbage collector. If it was involved with circular
references, it will appear in the garbage collector because the reference
counting mechanism was not able to release it.

This is basically the approach Yagot uses, although in a more automated fashion.

.. code-block:: text

    $ python
    >>> import gc
    >>> gc.collect()   # Run full garbage collection to have a reference
    0                  # No garbage objects initially (in this simple case)
    >>> obj = dict(); obj['self'] = obj
    >>> obj
    {'self': {...}}
    >>> gc.collect()
    0                  # Still no garbage objects
    >>> del obj        # The dict object becomes unreachable ...
    >>> gc.collect()
    1                  # ... and ended up as a garbage object that could be released

The interesting part happens during the ``del obj`` statement. The ``del obj``
statement removes the name ``obj`` from its namespace. That causes the reference
count of the :class:`dict` object to drop by one, in this case to 0. That causes
Python to try to immediately release the :class:`dict` object. This does not
succeed because of the circular reference. The call to :func:`py:gc.collect`
triggers a full garbage collection run on all generations, which successfully
breaks up the circular reference and releases the object, as reported by its
return value of 1.

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
