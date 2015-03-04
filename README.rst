record
======

record is a Python module for creating lightweight custom record classes.

It is similar to collections.namedtuple except that custom record classes have mutable
(i.e. writable) fields and can have more than 256 fields.

Similar to ``collections.namedtuple`` except that a ``record`` can have more than 256 fields and instances are mutable.

Record is a Python package that provides a factory function for making record-like classes. It is similar to ``collections.namedtuple``, with the following differences:

record in 4 points:

* field values are mutable
* a record can have more than 256 fields
* instances are initialised with a sequence or mapping rather than positional and keyword arguments
* lower memory footprint (``record`` objects are based on slots)


+------------------------+---------+-----------+-----------+
| Type                   | Mutable |    Max    | Defaults  |
|                        | fields  |   fields  | supported |
+------------------------+---------+-----------+-----------+
| record                 |    Y    | unlimited |     Y     |
+------------------------+---------+-----------+-----------+
| collections.namedtuple |    N    |    256    |     N     |
+------------------------+---------+-----------+-----------+
| recordtype             |    Y    |    256    |     Y     |
+------------------------+---------+-----------+-----------+


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

However, you cannot add new fields to an instance of a ``record`` type::

    >>> p.height = 1.71
    AttributeError                  Traceback (most recent call last)
    <ipython-input-8-55738ba62948> in <module>()
    ----> 1 p.height = 1.71

    AttributeError: 'Person' object has no attribute 'height'

Fields can also be accessed by index and iterated over::

    >>> p[1]
    42
    >>> p[1] = 29
    >>> p[1]
    29

    >>> for field in p:
    ...     print(field)
    Arthur
    29

Instances of ``record`` classes have a low memory requirement because they use
``__slots__`` rather than a per-instance ``__dict__`` to store attributes::

    >>> from collections import namedtuple
    >>> import sys
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

Despite using ``__slots__``, instances of classes created by
``record.make_type`` can be pickled::

    >>> import pickle
    >>> pickled_rec = pickle.loads(pickle.dumps(p))
    >>> pickled_rec == p
    True

API
---
In addition to the usual sequence methods, records support three additional
methods and one attribute. To prevent conflicts with fieldnames, the method
and attribute names start with an underscore.

*classmethod* somerecord.**_get_defaults**
    Class method that returns ``record.NO_DEFAULT`` if no defaults have been
    set, otherwise a tuple of the default values.

*classmethod* somerecord.**_set_defaults**(defaults)
    Class method that sets new defaults from an existing mapping of the form
    {fieldnameL default}, sequence of (fieldname, default) tuples, instance
    of the class. Alternatively, defaults can be disabled by passing
     ``record.NO_DEFAULT``.

somerecord.**_asdict**()
    Return a new ``OrderedDict`` which maps fieldnames to their corresponding
    values.

somerecord.**_fieldnames**
    Tuple of strings listing the fieldnames. Useful for introspection and
    creating new record types from existing record types.


Benchmarks
----------
The following benchmarks show the relative speed of various operations on
records and namedtuples in Python 3.4. They are intended to give the user a
rough idea of the speed gains and penalties involved with the use of ``record``
over ``namedtuple``.

The benchmarks show that access by field name is faster for a ``record`` than a
``namedtuple`` but all other operations are slower

Choosing a data type
--------------------
Believe it or not, records are not always the best data type to use. Depending
on your use-case other data types may be more appropriate:

* records are a good choice when one or more of the following are true:
    - the data has a static structure but dynamic values
    - the dataset consists of a large number of instances
    - the data has more than 255 fields
* named tuples are suitable for data with a static structure
* dictionaries should be used when the structure of the data is dynamic
* SimpleNamespace (available in in Python 3.3+) is suitable when the structure
of the data is dynamic and attribute access is required
* classes are needed when you need to add methods to objects


Installation
------------


Versions tested
---------------
Python 3.2
Python 3.3
Python 3.4

License
-------
BSD 3-clause "New" or "Revised" License
