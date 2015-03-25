========
Overview
========
*wrecord* is a an open source, BSD-licensed module for creating lightweight,
easy-to-use `record <http://en.wikipedia.org/wiki/Record_(computer_science)>`_
types in `Python <https://www.python.org/>`_ 3.2+ and PyPy3.

What problem does *wrecord* solve?
----------------------------------
Python provides a range of data types for handling record-like data including
dictionaries, namedtuples and SimpleNameSpaces, each with their own pros and
cons.

*wrecord* provides a factory function to easily create custom record classes
that have a unique set of properties:

* mutable field values accessible using named attributes
* indexable, sliceable and iterable
* support for optional per-field default values (including default factory
  functions)
* can have more than 255 fields
* very low memory footprint

Interested? Check out the `tutorial <TODO: insert tutorial link>'_

