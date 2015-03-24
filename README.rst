=======
rectype
=======

:Author: `Mark Richards <http://www.abdn.ac.uk/staffnet/profiles/m.richards/>`_
:Email: mark.l.a.richardsREMOVETHIS@gmail.com
:License: `BSD 3-Clause <http://opensource.org/licenses/BSD-3-Clause>`_
:Status: Pre-alpha

*rectype* is a Python module for creating lightweight, flexible data types
designed to make working with
`record <http://en.wikipedia.org/wiki/Record_(computer_science)>`_-like
data both easy and intuitive.

What problem does *rectype* solve?
----------------------------------
Python provides a range of data types for handling record-like data including
dictionaries, namedtuples and SimpleNameSpace, each with their own pros and
cons.

*rectype* provides a factory function to easily create custom record classes
that have a unique set of properties:

* mutable field values accessible using named attributes
* indexable, sliceable and iterable
* support for optional per-field default values (including default factory
  functions).
* can have more than 255 fields.
* very low memory footprint

Interested? Check out the `tutorial <TODO: insert tutorial link>'_

Quick start
===========
First, create a ``rectype`` like you would create a ``namedtuple`` type::

    >>> from rectype import rectype
    >>> Person = rectype('Person', ['name', 'age'])

Next, create an instance of ``Person`` with values for ``name`` and ``age``::

    >>> p = Person(name='Eric', age=42)
    >>> p
    Person(name='Eric', age=42)

Fields are accessible by attribute lookup and by index::

    >>> p.name
    'Eric'
    >>> p[0]
    'Eric'

Field values are mutable::

    >>> p.name = 'Idle'
    >>> p
    Rec(name='Idle', age=42)

You can specify per-field default values when creating the type::

    >>> Person = rectype('Person', [('name', None), ('age', None)])
    >>> p = Person(name='Eric')
    >>> p
    Person(name='Eric', age=None)

Multiple field values can be changed with the ``_update()`` method::

    >>> p._update(name='John', age=43)
    >>> p
    Person(name='John', age=43)

Fieldnames and field values can be iterated over::

    >>> for fieldname, field_value in zip(p._fieldnames, p):
    ...     print(fieldname, field_value)
    name John
    age 43

Installation
------------

TODO: complete this section

Versions tested
---------------
* Python 3.2
* Python 3.3
* Python 3.4
* PyPy3

License
-------
BSD 3-Clause "New" or "Revised" License
