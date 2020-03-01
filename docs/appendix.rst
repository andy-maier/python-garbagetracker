
.. _`Appendix`:

Appendix
========

This section contains information that is referenced from other sections,
and that does not really need to be read in sequence.


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


.. _`Troubleshooting`:

Troubleshooting
---------------

Here are some trouble shooting hints for ...


.. _`Glossary`:

Glossary
--------

.. glossary::

    collectable objects
       objects Python cannot immediately release when they become unreachable
       (e.g. when their variable goes out of scope) and that are therefore
       supposed to be released by the Python garbage collector. Most of the
       time, this is caused by the presence of circular references into which
       the object to be released is involved. The Python garbage collector is
       designed to handle circular references.

    collected objects
       :term:`collectable objects` that have successfully been released by the
       Python garbage collector.

    uncollectable objects
       :term:`collectable objects` that could not be released by the Python
       garbage collector, even when running a full collection. Uncollectable
       objects remain allocated in the last generation of the garbage collector
       and their memory remains allocated until the Python process terminates.
       They can be considered memory leaks.

    string
       a :term:`unicode string` or a :term:`byte string`

    unicode string
       a Unicode string type (:func:`unicode <py2:unicode>` in
       Python 2, and :class:`py3:str` in Python 3)

    byte string
       a byte string type (:class:`py2:str` in Python 2, and
       :class:`py3:bytes` in Python 3). Unless otherwise
       indicated, byte strings in this project are always UTF-8 encoded.

    number
       one of the number types :class:`py:int`, :class:`py2:long` (Python 2
       only), or :class:`py:float`.

    integer
       one of the integer types :class:`py:int` or :class:`py2:long` (Python 2
       only).

    callable
       a callable object; for example a function, a class (calling it returns a
       new object of the class), or an object with a :meth:`~py:object.__call__`
       method.

    hashable
       a hashable object. Hashability requires an object not only to be able to
       produce a hash value with the :func:`py:hash` function, but in addition
       that objects that are equal (as per the ``==`` operator) produce equal
       hash values, and that the produced hash value remains unchanged across
       the lifetime of the object. See `term "hashable"
       <https://docs.python.org/3/glossary.html#term-hashable>`_
       in the Python glossary, although the definition there is not very crisp.
       A more exhaustive discussion of these requirements is in
       `"What happens when you mess with hashing in Python"
       <https://www.asmeurer.com/blog/posts/what-happens-when-you-mess-with-hashing-in-python/>`_
       by Aaron Meurer.


.. _`References`:

References
----------

.. glossary::

   Python Glossary
      * `Python 2.7 Glossary <https://docs.python.org/2.7/glossary.html>`_
      * `Python 3.4 Glossary <https://docs.python.org/3.4/glossary.html>`_
