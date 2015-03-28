========
Overview
========
*wrecord* is a an open source, BSD-licensed `Python <https://www.python.org/>`_
module for creating lightweight, easy-to-use
`record <http://en.wikipedia.org/wiki/Record_(computer_science)>`_
types in Python 3.2+ and `PyPy3 <http://pypy.org/>`_.

What problem does *wrecord* solve?
----------------------------------
Python provides a range of data types for handling record-like data including
dictionaries, namedtuples and SimpleNameSpaces, each with their own pros and
cons.

*wrecord* provides a factory function to easily create custom record classes
that have a unique set of properties:

* mutable field values accessible using named attributes
* indexable, sliceable and iterable
* support for per-field default values (including default factory functions)
* no limit on the number of fields (named tuples are limited to 255)
* very low memory footprint

Quick taster
============
::

    >>> from wrecord import wrecord
    >>> Point = wrecord('Point', ['x', 'y'])  # create a new record type
    >>> p = Point(1, y=2)                     # pass values by field order or fieldname
    >>> p                                     # readable __repr__ with a name=value style
    Point(x=1, y=2)
    >>> p.x                                   # fields accessible by name
    1
    >>> p.x = 5                               # fields are mutable
    >>> p.x
    5
    >>> Point3D = wrecord('Point3D',
    ...     ['x', 'y', ('z', None)])          # per-field defaults can be set
    >>> p = Point3D(1, 2)
    >>> p
    Point3D(x=1, y=2, z=None)
    >>> p._update(y=3, z=4)                   # update multiple fields at a time
    >>> p
    Point3D(x=1, y=3, z=4)
    >>> p[0] + p[1]                           # fields are indexable
    4
    >>> p[:2]                                 # and sliceable
    [1, 3]
    >>> p._asdict()                           # Convert the record to an OrderedDict
    OrderedDict([('x', 1), ('y', 3), ('z', 4)])

Interested? Check out the :doc:`tutorial`.
