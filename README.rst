record
======

``record`` is a Python module for creating lightweight custom record classes.

A records class is similar to a ``collections.namedtuple`` except that it has
mutable (i.e. writable) fields and is are not limited to 255 fields. Records
are based on slots (they do not have a per-instance dictionary), so are
lightweight, requiring slightly less memory than a ``namedtuple`` and much less
than a ``dict``.

Like namedtuples, ``record`` classes have fields accessible by attribute lookup
as well as being indexable and iterable.

+------------------------+---------+------------+------------+
| Type                   | Mutable | Max fields | Defaults   |
|                        | fields? |            | supported? |
+------------------------+---------+------------+------------+
| record                 |    Y    | unlimited  |      Y     |
+------------------------+---------+------------+------------+
| collections.namedtuple |    N    |     256    |      N     |
+------------------------+---------+------------+------------+
| recordtype             |    Y    |     256    |      Y     |
+------------------------+---------+------------+------------+


Typical usage
-------------
First, create a ``record`` type like you would create a ``namedtuple`` type::

    >>> import record
    >>> Person =  record.make_type('Person', ['name', 'age'])

Next, create an instance of ``Person`` with values for ``name`` and ``age``::

    >>> p = Person(['Arthur', 42])

You can also initialise the instance using a mapping instead of a sequence::

    >>> p = Person(dict(name='Arthur', age=42))
    >>> p
    Person(name='Arthur', age=42)

You can retrieve field values as you would with a ``namedtuple``::

    >>>  p.name
    'Arthur'
    >>> p.age
    42
   
Unlike the tuple-based objects created by ``collections.namedtuple``, the
fields of an object created by ``record.make_type`` are mutable, meaning they
can be modified after creation::

    >>> p.age = 31
    >>> p.age
    31

However, because classes created by ``record.make_type()`` are based on slots,
you cannot add new fields to an instance::

    >>> p.height = 1.71
    AttributeError                  Traceback (most recent call last)
    <ipython-input-8-55738ba62948> in <module>()
    ----> 1 p.height = 1.71

    AttributeError: 'Person' object has no attribute 'height'

Fields are also indexable and iterable::

    >>> p[1]
    42
    >>> p[1] = 29
    >>> p[1]
    29

    >>> for field in p:
    ...     print(field)
    Arthur
    29

Instances of classes created by ``record.make_type`` can be pickled::

    >>> import pickle
    >>> pickled_rec = pickle.loads(pickle.dumps(p))
    >>> pickled_rec == p
    True

TODO:
demo type creation with defaults
demo get and set defsults
demo _fieldnames
demo _make


API
---
record.\ **make_type**\ (*typename, fieldnames, rename=False*)

    Returns a new custom record class named *typename*. The new class is used
    to create record objects that have fields accessible by attribute
    lookup as well as being indexable and iterable.

    The *fieldnames* are a single string with each fieldname separated by
    whitespace and/or commas, for example ``'x y'`` or ``'x, y'``.
    Alternatively, *fieldnames* can be a sequence of strings such as
    ``['x', 'y']``.

    Default values can also be specified along with the fieldnames if
    *fieldnames* is a mapping for the form ``{fieldname: default}`` such as
    ``{'x': 1, 'y': 2}`` or a sequence of tuples of the form
    ``[(x, 1), (y, 2)]``.

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

*classmethod* somerecord.\ **_make**\ (*\*args, \*\*kwargs*)

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

    Class method that sets new defaults from an existing mapping of the form
    {fieldname: default}, sequence of (fieldname, default) tuples, or
    instance of the class. Alternatively, defaults can be disabled by
    passing ``record.NO_DEFAULT``.

somerecord.\ **_asdict**\ ()

    Return a new ``OrderedDict`` which maps fieldnames to their corresponding
    values.

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
