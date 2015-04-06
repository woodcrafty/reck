====
Reck
====

.. image:: https://travis-ci.org/woodcrafty/reck.png?branch=master
    :target: https://travis-ci.org/woodcrafty/reck
    :alt: Build Status

.. image:: https://coveralls.io/repos/woodcrafty/reck/badge.png?branch=master
    :target: https://coveralls.io/r/woodcrafty/reck?branch=master
    :alt: Coverage Status

:Author: `Mark Richards <http://www.abdn.ac.uk/staffnet/profiles/m.richards/>`_
:Email: mark.l.a.richardsREMOVETHIS@gmail.com
:License: `BSD 3-Clause <http://reck.readthedocs.org/en/latest/license.html>`_
:Status: Alpha

*Reck* is a Python package for creating lightweight,
`record <http://en.wikipedia.org/wiki/Record_(computer_science)>`_
classes. It is the "REcord Creation Kit".

It aims to make working with record data easy and intuitive while removing
the need to manually code record classes.

What problem does *Reck* solve?
===============================
Python provides a range of data types that can handle record-like data
including dictionaries, named tuples and SimpleNameSpaces, each with their own
pros and cons.

*Reck* provides a factory function to easily create custom record classes
that have a unique set of properties:

* mutable field values accessible using named attributes
* indexable, sliceable and iterable
* support for per-field default values (including default factory functions)
* no limit on the number of fields (named tuples are limited to 255)
* very low memory footprint

The documentation is available at `http://reck.readthedocs.org`

Quick taster
============
::

    >>> from reck import make_rectype
    >>> Point = make_rectype('Point', ['x', 'y'])  # create a new record type
    >>> p = Point(1, y=2)              # pass values by field order or fieldname
    >>> p                              # readable __repr__ with a name=value style
    Point(x=1, y=2)
    >>> p.x                            # fields accessible by name
    1
    >>> p.x = 5                        # fields are mutable
    >>> p.x
    5
    >>> Point3D = make_rectype('Point3D',
    ...     ['x', 'y', ('z', None)])   # per-field defaults can be set
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

Want to see more? Check out the
`tutorial <http://reck.readthedocs.org/en/latest/tutorial.html>`_.

Installation
============
::
    pip install --pre reck

or download the `GitHub source <https://github.com/woodcrafty/reck>`_.


Versions tested
===============
* Python 3.2
* Python 3.3
* Python 3.4
* PyPy3

License
=======
BSD 3-Clause "New" or "Revised" License. See LICENSE.txt for the full text.
