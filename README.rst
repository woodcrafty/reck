=======
rectype
=======

:Author: `Mark Richards <http://www.abdn.ac.uk/staffnet/profiles/m.richards/>`
:License: BSD 3-clause
:Status: Pre-alpha

**THIS README IS A WORK IN PROGRESS!!**

Overview
========
``rectype`` is a Python package for creating lightweight custom
`record <http://en.wikipedia.org/wiki/Record_(computer_science)>` types.

``rectype`` provides a factory function ``rectype.rectype`` which is similar
to ``collections.namedtuple``, with the following differences:

* ``rectype`` field values are mutable.
* ``rectype`` supports optional per-field default values.
* ``rectype`` classes can have more than 255 fields.
* ``rectype`` instances are based on slots so require slightly less memory

Like namedtuples, classes created by ``rectype`` have fields accessible by
attribute lookup as well as being indexable and iterable.

Typical usage
=============
First, create a ``rectype`` like you would create a ``namedtuple`` type::

    >>> from rectype import rectype
    >>> Person = rectype('Person', ['name', 'age'])

Next, create an instance of ``Person`` with values for ``name`` and ``age``::

    >>> p = Person(name='Eric', age=42)
    >>> p
    Person(name='Eric', age=42)

You can specify per-field default values::

    >>> Person = rectype('Person', [('name', None), ('age', None)])
    >>> p = Person(name='Eric')
    >>> p
    Person(name='Eric', age=None)

You can also specify the per-field defaults with a mapping. Note that it
usually only makes sense to use an ordered mapping such as an OrderedDict::

    >>> from collections import OrderedDict
    >>> Person = rectype('Person', OrderedDict([('name', None), ('age', None)]))
    >>> p = Person()
    >>> p
    Person(name=None, age=None)


API
===


Creating types
==============

Specifying fields
-----------------

Fields can be specified using a non-string sequence or a string of space and/or
comma separated fieldnames. These 3 examples are equivalent::

    >>> Rec = rectype('Rec', ['a',  'b'])
    >>> Rec = rectype('Rec', 'a b')
    >>> Rec = rectype('Rec', 'a,b')

Specifying fields with defaults
-------------------------------

Per-field defaults can be specified by supplying a sequence of
(fieldname, default_value) 2-tuples::

    >>> Rec = rectype('Rec', [('a', None), ('b', None)])
    >>> rec = Rec()
    >>> rec
    Rec(a=None, b=None)

A default does not have to be supplied for every field::

    >>> Rec = rectype('Rec', ['a', ('b', None)])
    >>> rec = Rec(a=1)
    >>> rec
    Rec(a=1, b=None)

Per-field defaults can also be specified using an ordered mapping such as
an ``OrderedDict``::

    >>> from collections import OrderedDict
    >>> Rec = rectype('Rec', OrderedDict([
    ...     ('a', None),
    ...     ('b', None)]))
    >>> rec = Rec(b=99)
    >>> rec
    Rec(a=None, b=99)


Initialising rectypes
=====================

A ``rectype`` instance can be initialised in the same way as a dict: using a
mapping, an iterable, keyword arguments, or a combination of a mapping/
iterable and keyword arguments::

    >>> rec = Rec(dict(a=1, b=2))   # using a mapping
    >>> rec = Rec([1, 2])           # using a sequence
    >>> rec = Rec(a=1, b=2)         # using keyword args
    >>> rec = Rec(dict(a=1), b=2)   # using a mapping and keyword args

Accessing fields
================

Fields are accessible by attribute lookup::

    >>> rec.a
    1
    >>> rec.b
    2
   
The fields of ``rectype`` instances are are mutable, meaning they can be
modified after creation::

    >>> rec.a = 2
    >>> rec.a
    2

However, because classes created by ``rectype.rectype`` are based on slots,
you cannot add new fields to an instance::

    >>> rec.c = 3
    AttributeError                  Traceback (most recent call last)
    <ipython-input-8-55738ba62948> in <module>()
    ----> 1 rec.c = 3

    AttributeError: 'Rec' object has no attribute 'c'

Fields are also indexable and iterable::

    >>> rec[1]
    2
    >>> rec[1] = 3
    >>> rec[1]
    3

    >>> for field in rec:
    ...     print(field)
    2
    3

Instances of classes created by ``rectype.rectype`` can be pickled::

    >>> import pickle
    >>> pickled_rec = pickle.loads(pickle.dumps(rec))
    >>> pickled_rec == rec
    True

Updating defaults
=================

Default field values can be altered using _update_defaults() which is similar
to dict.update(). These are all equivalent::

    >>> Rec._update_defaults(dict(a=1, b=2))   # using a mapping
    >>> Rec._update_defaults([1, 2])           # using a sequence
    >>> Rec._update_defaults(a=1, b=2)         # using keyword args
    >>> Rec._update_defaults(dict(a=1), b=2)   # using a mapping and keyword args

Defaults values can also be removed for specific fields using _del_defaults()

TODO:
demo get and set defsults
demo _fieldnames
demo _make


API
===
rectype.\ **rectype**\ (*typename, fieldnames, rename=False*)

    Return a new record class named *typename*. The new class is used
    to create record objects that have fields accessible by attribute
    lookup as well as being indexable and iterable.

    The *fieldnames* are a single string with each fieldname separated by
    whitespace and/or commas, for example ``'x y'`` or ``'x, y'``.
    Alternatively, *fieldnames* can be a sequence of strings such as
    ``['x', 'y']``.

    Default values can also be specified along with the fieldnames if
    *fieldnames* is a mapping of fieldname-default_value pairs such as
    ``{'x': 1, 'y': 2}`` or a sequence of 2-tuples of the form
    ``[('x', 1), ('y', 2)]``. In the latter case, not all fieldnames need
    to have a default provided, e.g. ``['x', ('y', 2)]``.

    Any valid Python identifier may be used for a fieldname except for names
    starting with an underscore. Valid identifiers consist of letters, digits,
    and underscores but do not start with a digit or underscore and cannot be
    a ``keyword`` such as *class*, *for*, *return*, *global*, *pass*, or
    *raise*.

    If *rename* is true, invalid fieldnames are automatically replaced with
    positional names. For example, ``['abc', 'def', 'ghi', 'abc']``
    is converted to ``['abc', '_1', 'ghi', '_3']``, eliminating the keyword
    ``def`` and the duplicate fieldname ``abc``.

In addition to the usual sequence methods, records support four additional
methods and one attribute. To prevent conflicts with fieldnames, the method
and attribute names start with an underscore.

*class* **SomeRecType**\ (*\*\*kwargs*)
*class* **SomeRecType**\ (*mapping, \*\*kwargs*)
*class* **SomeRecType**\ (*iterable, \*\*kwargs*)

    Return a new record initialised from an optional positional argument and
    optional keyword arguments.

    If a positional argument is given and it is a mapping object, a
    record is created with values assigned to fields identified by
    keys of the mapping. Keys pairs that do not match a fieldname are
    ignored.

    The positional argument can also be an iterable object whose items
    are in the same order as the fieldnames of the record type. If the
    iterable provides too many values for the field the excess values
    are ignored.

    Keyword arguments can also be given to provide field values by
    name. If a keyword argument provides a value for a field that
    has already received a value, the value from the keyword argument
    replaces the value from the positional argument. Keywords that
    do not match a filename are ignored.

    Any fields that do not have values defined by the positional or
    keyword arguments will be assigned a field-specific default value,
    provided one has been defined.

    If a default value is not available for a field that has not been
    defined by the positional or keyword arguments a ValueError is
    raised.

    To illustrate, the following examples all return a record equal to
    Rec(a=1, b=2, c=3)::

        >>> from rectype import rectype
        >>> Rec = rectype('Rec', ['a', 'b', 'c'])
        >>> rec = Rec(dict(a=1, b=2, c=3))  # using a mapping
        >>> rec = Rec([1, 2, 3])            # using a sequence
        >>> rec = Rec(a=1, b=2, c=3)        # using keyword args
        >>> rec = Rec([1, 2], c=2)          # using a sequence and keyword args

These are the operations that rectypes support:

**len(rec)**
    Return the number of fields in the rectype *rec*.

**rec[index]**
**rec[slice]**
    Return the value of the field in *rec* corresponding to *index*, or the
    fields in *rec* corresponding to *slice*. The index of a each field value
    corresponds to the index of the fieldname in the _fieldnames class
    attribute::

        >>> Rec = rectype('Rec', [('a', 0) ('b', 1), ('c', 2)])
        >>> Rec._fieldnames
        ('a', 'b', 'c')
        >>> rec[0]          # get the value of field 'a'
        0

    All slice operations return a list containing the requested field values::

        >>> rec[:2]
        [0, 1]

**rec[index] = value**
**rec[slice] = values**
    Set ``rec[index]`` to value or ``rec[slice]`` to values.
    Sert the field of *rec* corresponding to *index* to *value* or set the
    fields of *rec* corresponding to *slice* to *values*.

    Please note* that the behaviour of setting field values using *slicing*
    is different from that of lists. If *values* contains more items than
    *slice* then the surplus values are discarded, whereas with lists the
    surplus items are inserted into the list. Similarly, if *values* contains
    fewer items than *slice*, the surplus fields remain unaffected, whereas
    with a list the surplus list items are removed. This behaviour is necessary
    because the structure of a ``rectype`` is immutable since it is based on
    *slots*.

**value in rec**
    Return ``True`` if *value* matches any of the field values in *rec*, else
    ``False``.

**iter(rec)**
    Return an iterator over the field values of *rec*.

**_asdict()**
    Return a new ``collections.OrderedDict`` which maps fieldnames to their
    values.

**_del_defaults(fieldnames)**
    Remove the default values for one or more fields. If *fieldnames*
    is a single string then the default value is removed for that field.
    If *fieldnames* is an iterable of strings then the default values are
    removed for each fieldname.

**_update(kwargs)**
**_update(mapping, kwargs)**
**_update(iterable, kwargs)**
    Update the field values of the record. ``_update()`` accepts either:
    keyword arguments in which each keyword must match a fieldname of the
    record; a mapping of fieldname/field_value pairs; an iterable whose
    items are in the same order as the fields in the ``_fieldnames`` class
    attribute; or a combination of mapping/iterable and kwargs.

*classmethod* **_update_defaults(kwargs)**
*classmethod* **_update_defaults(mapping, kwargs)**
*classmethod* **_update_defaults(iterable, kwargs)**
    Update the default field values of the record. ``_update_defaults()``
    accepts either keyword arguments in which each keyword must match a
    fieldname of the record; a mapping of fieldname/default_value pairs;
    an iterable whose default values are in the same order as the fields
    in the ``_fieldnames`` class attribute; or a combination of
    mapping/iterable and kwargs.


*classmethod* somerectype.\ **_update**\ (*\*args, \*\*kwargs*)

    Convenience function for making a new instance from positional and/or
    keyword arguments::

        >>> MyRec = record.make_type('MyRec', ['a', 'b', 'c', 'd'])
        >>> rec = MyRec._make(1, 2, d=4, c=3)
        MyRec(a=1, b=2, c=3, d=4)

    Note that this method can only be used to create new instances of
    record types that have fewer than 256 fields.

*classmethod* somerecord.\ **_get_defaults**\ ()\.

    Class method that returns a tuple of the default values or
    ``record.NO_DEFAULT`` if no defaults have been set.

*classmethod* somerecord.\ **_set_defaults**\ (*defaults*)

    Class method that sets new defaults from an existing mapping of
    fieldname-default_value pairs, or sequence of (fieldname, default)
    tuples, or instance of the class. Alternatively, defaults can be
    disabled by passing ``record.NO_DEFAULT``.

somerecord.\ **_asdict**\ ()

    Return a new ``collections.OrderedDict`` which maps fieldnames to their
    corresponding values.

somerecord.\ **_fieldnames**

    Tuple of strings listing the fieldnames. Useful for introspection and
    creating new record types from existing record types.


Memory usage and speed benchmarks
---------------------------------
Instances of ``record`` classes have a low memory footprint because they use
``__slots__`` rather than a per-instance ``__dict__`` to store attributes::

    >>> from collections import namedtuple
    >>> import sys
    >>> import record
    >>> RecordPerson =  record.make_type('Person', ['name', 'age'])
    >>> record_p = RecordPerson(['Brian', 20])
    >>> NamedTuplePerson = namedtuple('NamedTuplePerson', ['name', 'age'])
    >>> namedtuple_p = NamedTuplePerson(name='Brian', age=20)
    >>> dict_p = dict(name='Brian', age=20)
    >>> sys.getsizeof(record_p)
    56
    >>> sys.getsizeof(namedtuple_p)
    64
    >>> sys.getsizeof(dict_p)
    288

They are therefore much smaller than an equivalent ``dict`` and slightly smaller
than an equivalent ``namedtuple``.

The following benchmarks show the relative speed of various operations on
records and namedtuples in Python 3.4. They are intended to give the user a
rough idea of the speed gains and penalties involved with the use of ``record``
over ``namedtuple``.

TODO: insert benchmarks table here

The benchmarks show that access by field name is slightly faster for a
``record`` than a ``namedtuple``, but all other operations are significantly
slower.

Choosing a data type
--------------------
Believe it or not, records are not always the best data type to use. Depending
on your use-case other data types may be more appropriate:

* records may be a good choice when one or more of the following are true:
    - the data has a static structure but dynamic values
    - the data set consists of a very large number of instances
    - the data has more than 255 fields
* named tuples are suitable for data with a static structure
* dictionaries should be used when the structure of the data is dynamic
* SimpleNamespace (available in in Python 3.3+) is suitable when the structure of the data is dynamic and attribute access is required
* classes are needed when you need to add methods to objects

Installation
------------


Versions tested
---------------
* Python 3.2
* Python 3.3
* Python 3.4

License
-------
BSD 3-clause "New" or "Revised" License
