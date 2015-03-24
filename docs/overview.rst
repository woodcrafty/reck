========
Overview
========
*rectype* is a `Python <https://www.python.org/>`_ module for creating
lightweight, flexible data types designed to make working with
`record <http://en.wikipedia.org/wiki/Record_(computer_science)>`_-like
data both easy and intuitive. *rectype* is open source, BSD-licensed and works
on Python 3.2+ and PyPy3.

*rectype* is a an open source, BSD-licensed module for creating lightweight,
easy-to-use `record <http://en.wikipedia.org/wiki/Record_(computer_science)>`_
types in `Python <https://www.python.org/>`_ versions 3.2+.

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

