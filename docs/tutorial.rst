========
Tutorial
========

The basics
==========
First, create a *wrecord* type like you would create a namedtuple type.

    >>> from wrecord import wrecord
    >>> Person = wrecord('Person', ['name', 'age'])

Next, create an instance of ``Person`` with values for ``name`` and ``age``::

    >>> p = Person(name='Eric', age=42)
    >>> p                           # readable __repr__ with a name=value style
    Person(name='Eric', age=42)

You can also pass field values as positional arguments in field order::

    >>> p2 = Person('John', 44)
    >>> p2
    Person(name='John', age=44)

Fields are accessible by attribute lookup and by index::

    >>> p.name
    'Eric'
    >>> p[0]
    'Eric'

Field values are mutable::

    >>> p.name = 'Idle'
    >>> p.name
    'Idle'

You can specify per-field default values when creating a *wrecord*::

    >>> Person = wrecord('Person', [('name', None), ('age', None)])
    >>> p = Person(name='Eric')   # no value supplied for the 'age' field
    >>> p                         # so 'age' has been set to its default value
    Person(name='Eric', age=None)

Multiple field values can be changed using the ``_update()`` method::

    >>> p._update(name='John', age=44)
    >>> p
    Person(name='John', age=44)

Field values can be iterated over::

    >>> for value in p:
    ...     print(value)
    John
    44

*wrecords* are very useful for assigning fieldnames to sequences of data
returned by the ``csv`` module::

    import csv
    reader = csv.reader(open('employees.csv', newline=''))
    fieldnames = next(reader)   # Get the fieldnames from the first row of the file
    Employee = wrecord('Employee', fieldnames)
    for row in reader:
        emp = Employee(*row)
        print(emp.name, emp.title)

Type creation
=============
New types are created with the ``wrecord()`` factory function::

    >>> Point = wrecord(typename='Point', fieldnames=['x', 'y'])

Setting fieldnames
------------------
Fieldnames can be specified with a sequence of strings or a single string of
space and/or comma separated fieldnames. These examples are equivalent::

    >>> Point = wrecord('Point', ['x',  'y'])
    >>> Point = wrecord('Point', 'x y')
    >>> Point = wrecord('Point', 'x,y')

Setting defaults
----------------
Per-field defaults can be set by supplying a ``(fieldname, default)`` tuple
in place of a string for a fieldname::

    >>> Point3D = wrecord('Point3D', [('x', None), ('y', None), ('z', None)])
    >>> p = Point3D()
    >>> p
    Point3D(x=None, y=None, z=None)

A default does not have to be supplied for every field::

    >>> Point3D = wrecord('Point3D', ['x', ('y', None), 'z'])
    >>> p = Point3D(x=1, z=3)
    >>> p
    Point3D(x=1, y=None, z=3)

All fields without a default value must be given a value during instantiation,
otherwise a ``ValueError`` will be raised::

    >>> p = Point3D(x=1)
    ValueError: field 'z' is not defined

Per-field defaults can also be specified for every field using an ordered
mapping such as ``collections.OrderedDict``::

    >>> from collections import OrderedDict
    >>> Point3D = wrecord('Point3D', OrderedDict([
    ...     ('x', None),
    ...     ('y', None),
    ...     ('z', None)]))
    >>> p = Point3D(y=99)
    >>> p
    Point3D(x=None, y=99, z=None)

Factory function defaults
-------------------------
As with Python's mutable default arguments, mutable default field values will
be shared amongst all instances of the *wrecord*::

    >>> Rec = wrecord('Rec', [('a', [])])
    >>> rec1 = Rec()
    >>> rec2 = Rec()
    >>> rec1.a.append(1)
    >>> rec1.a
    [1]
    >>> rec2.a      # the value of 'a' in rec2 has also been updated
    [1]

To avoid this behaviour, mutable defaults can be created by setting the
default value to a factory function wrapped with a ``wrecord.DefaultFactory``
object. Here is an example using the ``list`` factory with no arguments::

    >>> from wrecord import DefaultFactory
    >>> Rec = wrecord('Rec', [('a', DefaultFactory(list))])
    >>> rec1 = Rec()     # calls list() to initialise field 'a'
    >>> rec2 = Rec()     # calls list() to initialise field 'a'
    >>> rec1.a.append(1)
    >>> rec1.a
    [1]
    >>> rec2.a           # the value of 'a' remains unmodified
    []

A default factory function can also be called with positional and keyword
arguments using the *args* and *kwargs* arguments of ``DefaultFactory()``.
Here is an example using ``dict``::

    >>> Rec = wrecord('Rec', [
    ...     ('a', DefaultFactory(dict, args=[[('b', 2)]], kwargs=dict(c=3)))])
    >>> rec1 = Rec()     # calls dict([('b', 2)], c=3) to initialise field 'a'
    >>> rec2 = Rec()     # calls dict([('b', 2)], c=3) to initialise field 'a'
    >>> rec1.a
    {'b': 2, 'c': 3}
    >>> rec1.a['d'] = 4
    >>> rec1.a
    {'b': 2, 'c': 3, 'd': 4}
    >>> rec2.a           # the value of 'a' in rec2 remains unmodified
    {'b': 2, 'c': 3}

Renaming invalid fieldnames
---------------------------
Any valid Python identifier may be used for a fieldname except keywords
such as *class* or *def* for names starting with an underscore. Valid cannot
be a keyword such as *class* or *def*.

You can set the *rename* argument of ``wrecord()`` to ``True`` to automatically
replace invalid fieldnames with position names::

    >>> Rec = wrecord('Rec', ['abc', 'def', 'ghi', 'abc'], rename=True)
    >>> Rec._fieldnames    # keyword 'def' and duplicate fieldname 'abc' have been renamed
    ('abc', '_1', 'ghi', '_3')

Instantiation
=============
When instantiating *wrecords*, field values can be passed by
field order, fieldname, or both. The following examples all return a
*wrecord* equivalent to ``Point3D(x=1, y=2, z=3)``::

    >>> p = Point3D(1, 2, 3)                # using values by field order
    >>> p = Point3D(x=1, y=2, z=3)          # using values by fieldname
    >>> p = Point3D(*[1, 2, 3])             # using an unpacked sequence
    >>> p = Point3D(*[1, 2], z=3)           # using an unpacked sequence and values by fieldname
    >>> p = Point3D(**dict(x=1, y=2, z=3))  # using an unpacked mapping
    >>> p
    Point3D(x=1, y=2, z=3)

*wrecord* objects are iterable so they can be used to initialise
other *wrecord* objects of the same type::

    >>> p2 = Point3D(*p)
    >>> p2 == p
    True

Getting and setting fields
==========================
By attribute
------------
Fields are accessible by named attribute::

    >>> p = Point3D(x=1, y=2, z=3)
    >>> p.z
    3

The fields of *wrecord* objects are are mutable, meaning they can be
modified after creation::

    >>> p.z = 33
    >>> p.z
    33

To get or set a field whose name is stored in a string, use the ``getattr()``
and ``setattr()`` built-ins::

    >>> getattr(p, 'z')
    33
    >>> setattr(p, 'z', 22)
    >>> getattr(p, 'z')
    22

By index
--------
Fields are also accessible by integer index::

    >>> p[1]              # Get the value of field y
    2

Setting works as well::

    >>> p[1] = 22         # Set the value of field y to 22
    >>> p[1]
    22

By slice
--------
Fields can also be accessed using slicing::

    >>> p[:2]   # Slicing returns a list of field values
    [1, 22]

Setting a slice of fields works as well::

    >>> p[:2] = [10, 11]  # Set field x to 10 and field y to 11
    >>> p
    Point3D(x=10, y=11, z=22)

Note, *wrecord* slice behaviour is different to that of lists. If the iterable
being assigned to the slice is longer than the slice, the surplus iterable
items are ignored (with a list the surplus items are inserted into the list)::

    >>> p[:3] = [1, 2, 3, 4, 5]   # Slice has 3 items, the iterable has 5
    >>> p                         # The last 2 items of the iterable were ignored
    Point3D(x=1, y=2, z=3)

Likewise, if the iterable contains fewer items than the slice, the surplus
fields in the slice remain unaffected (with a list the surplus items are
deleted)::

    >>> p[:3] = [None, None]   # Slice has 3 items, the iterable only 2
    >>> p                      # The last slice item (field z) was unaffected
    Point3D(x=None, y=None, z=3)

By iteration
------------
Field values can be iterated over::

    >>> p = Point3D(1, 2, 3)
    >>> for value in p:
    ...     print(value)
    1
    2
    3

Setting multiple fields
-----------------------
Multiple field values can be updated using the ``_update()`` method, with field
values passed by field order, fieldname, or both (as with instantiation). The
following examples all result in a record equivalent to
``Point3D(x=4, y=5, z=6)``::

    >>> p._update(4, 5, 6)               # using values by field order
    >>> p._update(x=4, y=5, z=6)         # using values by fieldname
    >>> p._update(*[4, 5, 6])            # using an unpacked sequence
    >>> p._update(**dict(x=4, y=5, z=6)) # using an unpacked mapping
    >>> p
    Point3D(x=4, y=5, z=6)


Replacing defaults
==================
A dictionary of fieldname/default_value pairs can be retrieved with the
``_get_defaults()`` class method::

    >>> Point3D = wrecord('Point3D', [('x', 1), ('y', 2), 'z'])
    >>> Point3D._get_defaults()
    {'x': 1, 'y': 2}

The existing per-field default values can be replaced by supplying the
``_replace_defaults()`` class method with new default values by field order,
fieldname, or both::

    >>> Point3D._replace_defaults(x=7, z=9)
    >>> Point3D._get_defaults()   # 'y' was not supplied a default so it no longer has one
    {'x': 7, 'z': 9}

To remove all default field values just call ``_replace_defaults()`` with no
arguments::

    >>> Point3D._replace_defaults()
    >>> Point3D._get_defaults()
    {}

Replacing the default values can be useful if you wish to use the same record
class in different contexts that require different default values::

    >>> Car = wrecord('Car', [('make', 'Ford'), 'model', 'body_type'])
    >>> Car._get_defaults()
    {'make': 'Ford'}
    >>> # Create some Ford cars:
    >>> car1 = Car(model='Focus', body_type='coupe')
    >>> car2 = Car(model='Mustang', body_type='saloon')
    >>> # Now create hatchback cars of different makes. To make life
    >>> # easier, replace the defaults with something more appropriate:
    >>> Car._replace_defaults(body_type='hatchback')
    >>> Car._get_defaults()   # note, 'make' no longer has a default value
    {'body_type': 'hatchback'}
    >>> car3 = Car(make='Fiat', model='Panda')
    >>> car4 = Car(make='Volkswagon', model='Golf')

Other methods/attributes
========================
The ``_fieldnames`` class attribute provides a tuple of fieldnames::

    >>> p._fieldnames
    ('x', 'y', 'z')

You can easily convert the *wrecord* to a list of (fieldname, default_value)
tuples::

    >>> p._asitems()
    [('x', 1), ('y', 2), ('z', 3)]

You can convert the record to an ``OrderedDict`` using ``_asdict()``::

    >>> p._asdict()
    OrderedDict([('x', 1), ('y', 2), ('z', 3)])

Miscellaneous operations
========================
*wrecord* types support various operations that are demonstrated below::

    >>> p = Point3D(x=1, y=2, z=3)
    >>> len(p)              # get the number of fields in the record
    3
    >>> 4 in p              # supports membership testing using the in operator
    False
    >>> 4 not in p
    True
    >>> iterator = iter(p)  # supports iterators
    >>> next(iterator)
    1
    >>> next(iterator)
    2
    >>> reverse_iterator = reversed(p)  # iterate in reverse
    >>> next(reverse_iterator)
    3
    >>> next(reverse_iterator)
    2
    >>> p._index(2)         # get the index of the first occurrence of a value
    1
    >>> p._update(x=1, y=3, z=3)
    >>> p._count(3)         # find out how many times a value occurs in the record
    2
    >>> vars(p)             # return an OrderedDict mapping fieldnames to values
    OrderedDict([('x': 1), ('y': 3), ('z': 3)])


Pickling
--------
Instances can be pickled::

    >>> import pickle
    >>> pickled_p = pickle.loads(pickle.dumps(p))
    >>> pickled_p == p
    True

Subclassing
===========
Since *wrecords* are normal Python classes it is easy to add or change
functionality with a subclass. Here is how to add a calculated field and a
fixed-width print format::

    >>> class Point(wrecord('Point', 'x y')):
    ...     __slots__ = ()
    ...     @property
    ...     def hypotenuse(self):
    ...         return (self.x ** 2 + self.y ** 2) ** 0.5
    ...     def __str__(self):
    ...         return ('Point: x={0:6.3f} y={1:6.3f} hypotenuse={2:6.3f}'
    ...             .format(self.x, self.y, self.hypotenuse))
    >>> p = Point(x=3, y=4.5)
    >>> print(p)
    Point: x= 3.000 y= 4.500 hypotenuse= 5.408

The subclass shown above sets ``__slots__`` to an empty tuple. This helps
keep memory requirements low by preventing the creation of per-instance
dictionaries.

Adding fields/attributes
========================
Because *wrecord* objects are based on slots, new fields cannot be added after
object creation::

    >>> Point = wrecord('Point', 'x y')
    >>> p = Point(1, 2)
    >>> p.new_attribute = 4   # Can't do this!
    AttributeError                  Traceback (most recent call last)
    <ipython-input-8-55738ba62948> in <module>()
    ----> 1 rec.c = 3

    AttributeError: 'Point' object has no attribute 'new_attribute'

Subclassing is also not useful for adding new attributes. Instead, simply
create a new *wrecord* type from the ``_fieldnames`` class attribute::

    >>> Point3D = wrecord('Point3D', Point._fieldnames + ('z',))

More than 255 fields
====================
*wrecord* types have no limit on the number of fields whereas named tuples
are limited to 255 fields::

    >>> fieldnames = ['f{0}'.format(i) for i in range(1000)]
    >>> values = [i for i in range(1000)]
    >>> from collections import namedtuple
    >>> NT = namedtuple('NT', fieldnames)
    SyntaxError: more than 255 fields
    >>> Rec = wrecord('Rec', fieldnames)
    >>> rec = Rec(*values)
    >>> rec.f0
    0
    >>> rec.f999
    999

Whilst it is unusual to require more than 255 fields it can sometimes be handy
if reading data from a csv file (or similar) that has a lot of columns.
