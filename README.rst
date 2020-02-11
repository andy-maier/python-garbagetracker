garbagetracker - Tracker for memory leaks written in pure Python
===============================

.. image:: https://img.shields.io/pypi/v/garbagetracker.svg
    :target: https://pypi.python.org/pypi/garbagetracker/
    :alt: Version on Pypi

.. # .. image:: https://img.shields.io/pypi/dm/garbagetracker.svg
.. #     :target: https://pypi.python.org/pypi/garbagetracker/
.. #     :alt: Pypi downloads

.. image:: https://travis-ci.org/garbagetracker/garbagetracker.svg?branch=master
    :target: https://travis-ci.org/garbagetracker/garbagetracker
    :alt: Travis test status (master)

.. image:: https://ci.appveyor.com/api/projects/status/i022iaeu3dao8j5x/branch/master?svg=true
    :target: https://ci.appveyor.com/project/andy-maier/garbagetracker
    :alt: Appveyor test status (master)

.. image:: https://readthedocs.org/projects/garbagetracker/badge/?version=latest
    :target: https://garbagetracker.readthedocs.io/en/latest/
    :alt: Docs build status (master)

.. image:: https://img.shields.io/coveralls/garbagetracker/garbagetracker.svg
    :target: https://coveralls.io/r/garbagetracker/garbagetracker
    :alt: Test coverage (master)


Overview
--------

TBD

Installation
------------

To install the latest released version of the garbagetracker
package into your active Python environment:

.. code-block:: bash

    $ pip install garbagetracker

This will also install any prerequisite Python packages.

For more details and alternative ways to install, see
`Installation`_.

.. _Installation: https://garbagetracker.readthedocs.io/en/stable/intro.html#installation

Documentation
-------------

* `Documentation for latest released version <https://garbagetracker.readthedocs.io/en/stable/>`_

Change History
--------------

* `Change history for latest released version <https://garbagetracker.readthedocs.io/en/stable/changes.html>`_

Quick Start
-----------

The following simple example script lists the namespaces and the Interop
namespace in a particular WBEM server:

.. code-block:: python

    #!/usr/bin/env python

    import garbagetracker

    ... (tbd) ...

Contributing
------------

For information on how to contribute to the garbagetracker
project, see
`Contributing <https://garbagetracker.readthedocs.io/en/stable/development.html#contributing>`_.


License
-------

The garbagetracker project is provided under the
`Apache Software License 2.0 <https://raw.githubusercontent.com/andy-maier/garbagetracker/master/LICENSE>`_.
