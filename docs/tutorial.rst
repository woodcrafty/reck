================
rectype tutorial
================

The basics
==========
First, create a ``rectype`` like you would create a ``namedtuple`` type.

    >>> from rectype import rectype
    >>> Person = rectype('Person', ['name', 'age'])

Next, create an instance of ``Person`` with values for ``name`` and ``age``::

    >>> p = Person(name='Eric', age=42)  # instantiate with keyword arguments
    >>> p                                # readable __repr__ with a name=value style
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
    >>> p  # a value for age was not supplied so it was assigned it's default value
    Person(name='Eric', age=None)

Multiple field values can be changed with the ``_update()`` method::

    >>> p._update(name='John', age=43)
    >>> p
    Person(name='John', age=43)

Fieldnames and field values can be iterated over::

    >>> for value in p.:
    ...     print(value)
    John
    43

Type creation
=============

New types are created with the ``rectype.rectype()`` factory function, e.g.::

    >>> Point = rectype(typename='Point', fieldnames=['x', 'y'], rename=False)

Setting fieldnames without defaults
-----------------------------------
If no default values are required *fieldnames* can be a sequence
of strings or a single string of space and/or comma separated fieldnames. These
3 examples are equivalent::

    >>> Point = rectype('Point', ['x',  'y'])  # fieldnames is a sequence of strings
    >>> Point = rectype('Point', 'x y')        # fieldnames is a string of space separated fieldnames
    >>> Point = rectype('Point', 'x,y')        # fieldnames is a string of comma separated fieldnames
    >>> Point._fieldnames                      # Display a tuple of the record's fieldnames
    ('x', 'y')

Any valid Python identifier may be used for a fieldname except for names
starting with an underscore. Valid identifiers consist of letters, digits,
and underscores but do not start with a digit or underscore and cannot be a
keyword such as *class*, *for*, *return*, or *print*.

You can set the *rename* argument to True to automatically replace invalid
fieldnames with position names::

    >>> Rec = rectype('Rec', ['abc', 'def', 'ghi', 'abc'], rename=True)
    >>> Rec._fieldnames    # keyword 'def' and duplicate fieldname 'abc' have been renamed
    ('abc', '_1', 'ghi', '_3')

Setting fieldnames with defaults
--------------------------------
If per-field default values are required the *fieldnames* can be a sequence
of (fieldname, default_value) 2-tuples::

    >>> Point3D = rectype('Point3D', [('x', None), ('y', None), ('z', None])
    >>> p = Point3D()
    >>> p
    Point3D(x=None, y=None, z=None)

A default does not have to be supplied for every field::

    >>> Point3D = rectype('Point3D', ['x', ('y', None), 'z'])
    >>> p = Point3D(x=1, z=3)
    >>> p
    Point3D(x=1, y=None, z=3)

All fields without a default value must be given a value during instantiation,
otherwise a ValueError will be raised::

    >>> p = Point3D(z=1)
    ValueError: field 'z' is not defined

Per-field defaults can also be specified using an ordered mapping such as
an ``collections.OrderedDict``::

    >>> from collections import OrderedDict
    >>> Point3D = rectype('Point3D', OrderedDict([
    ...     ('x', None),
    ...     ('y', None),
    ...     ('z', None)]))
    >>> p = Point3D(y=99)
    >>> p
    Point3D(x=None, y=99, z=None)

Instantiation
=============

So far objects have been instantiated using keyword arguements to specify the
field values. However, rectype instances can be initialised in the same way as
a dict, by using a mapping, an iterable, keyword arguments, or a combination of
a mapping/iterable and keyword arguments. The following examples all return a
``rectype`` equivalent to ``Point3D(x=1, y=2, z=3)``::

    >>> p = Point3D(dict(x=1, y=2, z=3))   # using a mapping
    >>> p = Point3D([1, 2, 3])             # using a sequence
    >>> p = Point3D(x=1, y=2, z=3)         # using keyword args
    >>> p = Point3D([1, 2], z=3)           # using a sequence and keyword args
    >>> p
    Point3D(x=1, y=2, z=3)

``rectype`` instances are iterable so they can be used to initialise
other ``rectype`` instances::

    >>> p2 = Point3D(p)
    >>> p2 == p
    True

Note that when this happens, values are matched by position rather than
fieldname, a record of one type can be used to initialise a record of another
type, even of the fields have different names and meanings.

Field selection
===============
Selection by attribute lookup
-----------------------------
Fields are accessible by attribute lookup::

    >>> p = Point3D(x=1, y=2, z=3)
    >>> p.c
    3

The fields of ``rectype`` instances are are mutable, meaning they can be
modified after creation::

    >>> p.c = 33
    >>> p.c
    33

Selection by position
---------------------
Fields are also accessible by integer based indexing and slicing::

    >>> p[1]    # Get the value of field y
    2
    >>> p[:2]   # Slicing returns a list of field values
    [1, 2]

Setting works as well::

    >>> p[1] = 22         # Set field y to 22
    >>> p[1]
    22
    >>> p[:2] = [10, 11]  # Set field x to 10 and field y to 11
    >>> p
    Point3D(x=10, y=11, z=33)

If the iterable being assigned to the slice is longer than the slice, the
excess iterable items are ignored::

    >>> p[:3] = [1, 2, 3, 4, 5]   # Slice has 3 items, the iterable has 5
    >>> p                         # The last 2 items were discarded
    Point3D(x=1, y=2, z=3)

Likewise, if the iterable contains fewer items than the slice, the surplus
fields in the slice remain unaffected::

    >>> p[:3] = [None, None]   # Slice has 3 items, the iterable only 2
    >>> p                      # The last slice item (field z) was unaffected
    Point3D(x=None, y=None, z=3)

Setting multiple field values
-----------------------------
Multiple field values can be changed using the ``_update()`` method which
has the same call profile as instantiation. The following examples all
result in a record equivalent to ``Point3D(x=4, y=5, z=6)``::

    >>> p._update(x=4, y=5, z=6)        # using keyword arguments
    >>> p._update([4, 5, 6])            # using an iterable
    >>> p._update(dict(x=4, y=5, z=6))  # using a mapping
    >>> p._update([4, 5], c=6)          # using an iterable and keyword args
    >>> p
    Point3D(x=4, y=5, z=6)

Changing default values
=======================
A dictionary of fieldname/default_value pairs can be obtained with the
``_get_defaults()`` class method::

    >>> Point3D = rectype('Point3D', [('x', 1), ('y', 2), 'z')
    >>> Point3D._get_defaults()
    {'x': 1, 'y': 2}

The existing per-field default values can be replaced using the
``_set_defaults()`` class method. Just supply it with a mapping of the
fieldnames to their default values::

    >>> Point3D._set_defaults(dict(x=7, y=8)
    >>> Point3D._get_defaults()   # field 'z' was not supplied a default
    {'x': 7, 'y': 8}

To remove all default field value just pass in an empty mapping::

    >>> Point3D._set_defaults({})
    >>> Point3D._get_defaults()
    {}

Replacing the default values can be useful if you wish to use the same record
class in different contexts that require different default values::

        >>> Car = rectype('Car', [('make', 'Ford'), 'model', 'body_type')
        >>> Car._get_defaults()
        {'make': 'Ford'}
        >>> # Create some Ford cars:
        >>> car1 = Car(model='Focus', body_type='coupe')
        >>> car2 = Car(model='Mustang', body_type='saloon')
        >>> # Now create hatchback cars of different makes. To make life
        >>> # easier replace the defaults with something more appropriate:
        >>> Rec._set_defaults(dict(body_type='hatchback'))
        >>> Rec._get_defaults()   # note, 'make' no longer has a default value
        {'body_type': 'hatchback'}
        >>> car3 = Car(model='Fiat', model='Panda')
        >>> car4 = Car(model='Volkswagon', model='Golf')

Operations
==========
Iteration
---------
Field values can be iterated over::

    >>> p = Point3D(x=1, y=2, z=3)
    >>> for value in p:
    ...     print(value)
    1
    2
    3

If you need the fieldnames as well as values you can use the ``_items`` method
which returns a list of (fieldname, value) tuples::

    >>> for fieldname, value in p._items():
    ...     print(fieldname, value)
    x 1
    y 2
    z 3

Pickling
--------
Instances can be pickled::

    >>> import pickle
    >>> pickled_p = pickle.loads(pickle.dumps(p))
    >>> pickled_p == p
    True

Immutable structure
===================
Objects of ``rectype`` classes are based on slots, so new fields cannot be
added after object creation::

    >>> p.new_attribute = 4   # Can't do this!
    AttributeError                  Traceback (most recent call last)
    <ipython-input-8-55738ba62948> in <module>()
    ----> 1 rec.c = 3

    AttributeError: 'Point3D' object has no attribute 'new_attribute'

Memory usage
============
``rectype`` objects have a low memory footprint because they use slots
rather than a per-instance dictionary to store attributes::

    >>> from rectype import rectype
    >>> from collections import namedtuple
    >>> import sys
    >>> Rec = rectype('Rec', ['a', 'b'])
    >>> rec = Rec(a=1, b=2)
    >>> NT = namedtuple('NT', ['a', 'b'])
    >>> nt = NT(a=1, b=2)
    >>> dct = dict(a=1, b=2)
    >>> sys.getsizeof(rec)    # Number of bytes used by a rectype
    56
    >>> sys.getsizeof(nt)     # Number of bytes used by a namedtuple
    64
    >>> sys.getsizeof(dct)    # Number of bytes used by a dict
    288

They use much less memory than an equivalent ``dict`` and slightly less than
an equivalent ``namedtuple``.

TODO:
adding new field
subclassing
operations (in brief using single lines of code with comments)

