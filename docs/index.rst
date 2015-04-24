======
*reck*
======

:Author: `Mark Richards <http://www.abdn.ac.uk/staffnet/profiles/m.richards/>`_
:License: `BSD 3-Clause <http://reck.readthedocs.org/en/latest/license.html>`_
:Latest version: `1.0rc1`

*Reck* is a package for creating lightweight,
`record <http://en.wikipedia.org/wiki/Record_(computer_science)>`_
classes (aka 'struct' in C) in Python v3.x. The record classes are similar to
`named tuples <https://docs.python.org/3.4/library/collections.html#collections.namedtuple>`_,
but have a unique set of properties:

* mutable field values accessible using named attributes
* indexable, sliceable and iterable
* support for per-field default values (including default factory functions)
* no limit on the number of fields (named tuples are limited to 255)
* very low memory footprint

Depending on your use-case, records may be a better choice than named tuples,
dictionaries or manually coded custom classes.

*Reck* provides a factory function to easily create custom record classes -
it's the "REcord Creation Kit". The factory function saves you having to
manually write classes full of boilerplate, just to hold record data.

What does it look like? Here is a quick taster::

    >>> from reck import make_rectype
    >>> Point = recktype('Point', ['x', 'y'])  # create a new record type
    >>> p = Point(1, y=2)              # pass values by field order or fieldname
    >>> p                              # readable __repr__ with a name=value style
    Point(x=1, y=2)
    >>> p.x                            # fields accessible by name
    1
    >>> p.x = 5                        # fields are mutable
    >>> p.x
    5
    >>> Point3D = recktype('Point3D', ['x', 'y', ('z', 0)])  # default field values can be set
    >>> p = Point3D(x=1, y=2)
    >>> p
    Point3D(x=1, y=2, z=0)
    >>> p._update(y=3, z=4)            # update multiple fields at a time
    >>> p
    Point3D(x=1, y=3, z=4)
    >>> p[0] + p[1]                    # fields are indexable...
    4
    >>> p[:2]                          # ...and sliceable
    [1, 3]
    >>> p._asdict()                    # Convert the record to an OrderedDict
    OrderedDict([('x', 1), ('y', 3), ('z', 4)])

You can install the package directly from PyPI::

    pip install --pre reck

or download the `GitHub source <https://github.com/woodcrafty/reck>`_.

Documentation contents
----------------------

.. toctree::
   :maxdepth: 2

   tutorial
   memory_usage
   benchmarks
   changelog
   license

API Reference
-------------
If you are looking for information on a specific class or function, this part
of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api
