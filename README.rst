=======
wrecord
=======

.. image:: https://travis-ci.org/woodcrafty/wrecord.png?branch=master
    :target: https://travis-ci.org/woodcrafty/wrecord
    :alt: Build Status

.. image:: https://coveralls.io/repos/woodcrafty/wrecord/badge.png?branch=master
    :target: https://coveralls.io/r/woodcrafty/wrecord?branch=master
    :alt: Coverage Status

:Author: `Mark Richards <http://www.abdn.ac.uk/staffnet/profiles/m.richards/>`_
:Email: mark.l.a.richardsREMOVETHIS@gmail.com
:License: `BSD 3-Clause <http://opensource.org/licenses/BSD-3-Clause>`_
:Status: Pre-alpha

*wrecord* is a Python module for creating lightweight, flexible data types
designed to make working with
`record <http://en.wikipedia.org/wiki/Record_(computer_science)>`_-like
data both easy and intuitive.

What problem does *wrecord* solve?
==================================
Python provides a range of data types for handling record-like data including
dictionaries, namedtuples and SimpleNameSpaces, each with their own pros and
cons.

*wrecord* provides a factory function to easily create custom record classes
that have a unique set of properties:

* mutable field values accessible using named attributes
* indexable, sliceable and iterable
* support for per-field default values (including default factory functions)
* can have more than 255 fields
* very low memory footprint

The documentation is available at
`http://wrecord.readthedocs.org/en/latest/index.html`

Quick taster
============
::

    >>> from wrecord import wrecord
    >>> Point = wrecord('Point', ['x', 'y'])  # create a new record type
    >>> p = Point(1, y=2)                     # pass values by field order or fieldname
    >>> p                                     # readable __repr__ with a name=value style
    Point(x=1, y=2)
    >>> p.name                                # fields accessible by name
    'Eric'
    >>> p[0] + p[1]                           # fields are also indexable
    3
    >>> p.x = 5                               # fields are mutable
    >>> Point3D = wrecord('Point3D',
    ...     ['x', 'y', ('z', None)])          # per-field defaults can be set
    >>> p = Point3D(1, 2)
    >>> p
    Point3D(x=1, y=2, z=None)
    >>> p._update(y=3, z=4)                   # update multiple fields
    >>> p
    Point3D(x=1, y=3, z=4)
    >>> p._asdict()                           # Covert the record to an OrderedDict
    OrderedDict([('x', 1), ('y', 3), ('z', 4)])

Want to see more? Check out the
`tutorial <http://wrecord.readthedocs.org/en/latest/tutorial.html>`_.

Installation
============

TODO: complete this section

Versions tested
===============
* Python 3.2
* Python 3.3
* Python 3.4
* PyPy3

License
=======
BSD 3-Clause "New" or "Revised" License
