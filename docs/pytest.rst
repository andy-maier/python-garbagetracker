
.. _`Pytest plugin`:

Pytest plugin
=============

This section describes the pytest plugin of Yagot.

The pytest plugin is automatically installed along with the yagot package.
It adds the following group of command line options to pytest:

.. code-block:: text

    Garbage object tracking using Yagot:

    --yagot               Enables checking for collected and uncollectable objects caused by
                          pytest test cases. Default: Env.var YAGOT (set to non-empty), or False.

    --yagot-leaks-only    Limits the checking to only uncollectable (=leak) objects. Default:
                          Env.var YAGOT_LEAKS_ONLY (set to non-empty), or False.

    --yagot-ignore-types=TYPE[,TYPE[...]]
                          Type name or module.path.class name of collected and uncollectable
                          objects for which test cases will be ignored. Multiple comma-separated
                          type names can be specified on each option, and in addition the option
                          can be specified multiple times. The types must be specified as
                          represented by the str(type) function (for example, "int" or
                          "mymodule.MyClass"). Default: Env.var YAGOT_IGNORE_TYPES, or empty list.
