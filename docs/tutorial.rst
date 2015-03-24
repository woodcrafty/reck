================
rectype tutorial
================

The basics
==========
First, create a ``rectype`` like you would create a ``namedtuple`` type.

    >>> from rectype import rectype
    >>> Person = rectype('Person', ['name', 'age'])

Next, create an instance of ``Person`` with values for ``name`` and ``age``::

    >>> p = Person(name='Eric', age=42)
    >>> p                           # readable __repr__ with a name=value style
    Person(name='Eric', age=42)

You can also pass field values as positional arguments in field order::

    >>> p = Person('Eric', 42)
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

You can specify per-field default values when creating a ``rectype``::

    >>> Person = rectype('Person', [('name', None), ('age', None)])
    >>> p = Person(name='Eric')   # no value supplied for the 'age' field
    >>> p                         # 'age' has been set to its default value
    Person(name='Eric', age=None)

Multiple field values can be changed with the ``_update()`` method::

    >>> p._update(name='John', age=43)
    >>> p
    Person(name='John', age=43)

Field values can be iterated over::

    >>> for value in p.:
    ...     print(value)
    John
    43

Type creation
=============

New types are created with the ``rectype.rectype()`` factory function::

    >>> Point = rectype(typename='Point', fieldnames=['x', 'y'], rename=False)

Setting fieldnames
------------------
Fieldnames can be specified with a sequence of strings or a single string of
space and/or comma separated fieldnames. These examples are equivalent::

    >>> Point = rectype('Point', ['x',  'y'])
    >>> Point = rectype('Point', 'x y')
    >>> Point = rectype('Point', 'x,y')

Setting defaults
----------------
Per-field defaults can be specified by supplying a ``(fieldname, default)``
tuple in place of a string for a fieldname::

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
otherwise a ``ValueError`` will be raised::

    >>> p = Point3D(x=1)
    ValueError: field 'z' is not defined

Per-field defaults can also be specified for every field using an ordered
mapping such as ``collections.OrderedDict``::

    >>> from collections import OrderedDict
    >>> Point3D = rectype('Point3D', OrderedDict([
    ...     ('x', None),
    ...     ('y', None),
    ...     ('z', None)]))
    >>> p = Point3D(y=99)
    >>> p
    Point3D(x=None, y=99, z=None)

Factory function defaults
-------------------------
As with Python's mutable default arguments, mutable default field values will
be shared amongst all instances of the rectype::

    >>> Rec = rectype('Rec', [('a', [])])
    >>> rec1 = Rec()
    >>> rec2 = Rec()
    >>> rec1.a.append(1)
    >>> rec1.a
    [1]
    >>> rec2.a      # the value of 'a' in rec2 has also been updated
    [1]

To avoid this happening, mutable defaults can be created using a default
factory function. This is done by setting the default to a
``rectype.DefaultFactory`` object, passing in a factory function (along with
any positional and keyword arguments), to the constructor. This example uses
``list`` with no arguments::

    >>> from rectype import rectype, DefaultFactory
    >>> Rec = rectype('Rec', [('a', DefaultFactory(list))])
    >>> rec1 = Rec()
    >>> rec2 = Rec()
    >>> rec1.a.append(1)
    >>> rec1.a
    [1]
    >>> rec2.a           # the value of 'a' remains unmodified
    []

This example uses dict as a default factory, using the ``DefaultFactory()`` args
and kwargs arguments to specify positional and keyword arguments for dict::

    >>> Rec = rectype('Rec', [
    ...     ('a', DefaultFactory(dict, args=[('b', 2)], kwargs=dict(c=3)])
    >>> rec1 = Rec()     # calls dict([('b', 2)], c=3) to initialise field 'a'
    >>> rec2 = Rec()     # calls dict([('b', 2)], c=3) to initialise field 'a'
    >>> rec1.a
    {'b': 2, 'c': 3}
    >>> rec1.a['d'] = 4
    >>> rec1.a
    {'b': 2, 'c': 3, 'd': 4}
    >>> rec2.a           # the value of 'a' remains unmodified
    {'b': 2, 'c': 3}

Renaming invalid fieldnames
---------------------------
Renaming invalid fields

Any valid Python identifier may be used for a fieldname except for names
starting with an underscore. Valid identifiers cannot start with a digit or
underscore and cannot be a keyword such as *class*.

You can set the rename argument to ``True`` to automatically replace invalid
fieldnames with position names::

    >>> Rec = rectype('Rec', ['abc', 'def', 'ghi', 'abc'], rename=True)
    >>> Rec._fieldnames    # keyword 'def' and duplicate fieldname 'abc' have been renamed
    ('abc', '_1', 'ghi', '_3')

Instantiation
=============
When instantiating new *rectype* objects, field values can be passed by
field order, fieldname, or both. The following examples all return a
``rectype`` equivalent to ``Point3D(x=1, y=2, z=3)``::

    >>> p = Point3D(1, 2, 3)                # using values by field order
    >>> p = Point3D(x=1, y=2, z=3)          # using values by fieldname
    >>> p = Point3D(*[1, 2, 3])             # using an unpacked sequence
    >>> p = Point3D(*[1, 2], z=3)           # using an unpacked sequence and values by fieldname
    >>> p = Point3D(**dict(x=1, y=2, z=3))  # using an unpacked mapping
    >>> p
    Point3D(x=1, y=2, z=3)

*rectype* objects are iterable so they can be used to initialise
other *rectype* objects of the same type::

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

The fields of *rectype* objects are are mutable, meaning they can be
modified after creation::

    >>> p.z = 33
    >>> p.z
    33

To get and set a field whose name is stored in a string, use the ``getattr()``
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
    [1, 2]

Setting a slice of fields works as well::

    >>> p[:2] = [10, 11]  # Set field x to 10 and field y to 11
    >>> p
    Point3D(x=10, y=11, z=33)

Note, slice behaviour is different to that of lists. If the iterable being
assigned to the slice is longer than the slice, the excess iterable items are
ignored::

    >>> p[:3] = [1, 2, 3, 4, 5]   # Slice has 3 items, the iterable has 5
    >>> p                         # The last 2 items of the iterable were ignored
    Point3D(x=1, y=2, z=3)

Likewise, if the iterable contains fewer items than the slice, the surplus
fields in the slice remain unaffected::

    >>> p[:3] = [None, None]   # Slice has 3 items, the iterable only 2
    >>> p                      # The last slice item (field z) was unaffected
    Point3D(x=None, y=None, z=3)
        Point3D(x=None, y=None, z=3)

Setting multiple fields
-----------------------
Multiple field values can be updated using the ``_update()`` method, which has
the same call profile as instantiation. The following examples all result in
a record equivalent to ``Point3D(x=4, y=5, z=6)``::

    >>> p._update(x=4, y=5, z=6)        # using keyword arguments
    >>> p._update([4, 5, 6])            # using an iterable
    >>> p._update(dict(x=4, y=5, z=6))  # using a mapping
    >>> p._update([4, 5], c=6)          # using an iterable and keyword args
    >>> p
    Point3D(x=4, y=5, z=6)

Updating defaults
=================
A dictionary of fieldname/default_value pairs can be retrieved with the
``_get_defaults()`` class method::

    >>> Point3D = rectype('Point3D', [('x', 1), ('y', 2), 'z')
    >>> Point3D._get_defaults()
    {'x': 1, 'y': 2}

The existing per-field default values can be replaced by supplying a
fieldname/default_value mapping to the ``_set_defaults()`` class method.
Fields not included in the mapping will no longer have a default value::

    >>> Point3D._set_defaults(dict(x=7, z=9))
    >>> Point3D._get_defaults()   # field 'y' was not supplied a default value so no longer has one
    {'x': 7, 'z': 9}

To remove all default field values just pass in an empty mapping::

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
    >>> # easier, replace the defaults with something more appropriate:
    >>> Rec._set_defaults(dict(body_type='hatchback'))
    >>> Rec._get_defaults()   # note, 'make' no longer has a default value
    {'body_type': 'hatchback'}
    >>> car3 = Car(model='Fiat', model='Panda')
    >>> car4 = Car(model='Volkswagon', model='Golf')

Iteration
---------
Field values can be iterated over::

    >>> p = Point3D(x=1, y=2, z=3)
    >>> for value in p:
    ...     print(value)
    1
    2
    3

If you need the fieldnames as well as values you can use the ``_items()`` method
which returns a list of (fieldname, value) tuples::

    >>> for fieldname, value in p._items():
    ...     print(fieldname, value)
    x 1
    y 2
    z 3

Miscellaneous operations
========================
Rectypes support various operations that are demonstrated below::

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
    >>> p.index(2)          # get the index of the first occurrence of a value
    1
    >>> p._update(x=1, y=3, x=3)
    >>> p.count(3)          # find out how many times does a value occur in the record
    2
    >>> vars(p)             # return an OrderedDict mapping fieldnames to values
    OrderedDict([('x': 1), ('y': 2), ('z': 3)])


Pickling
--------
Instances can be pickled::

    >>> import pickle
    >>> pickled_p = pickle.loads(pickle.dumps(p))
    >>> pickled_p == p
    True

Subclassing
===========
Since rectypes are normal Python classes it is easy to add or change
functionality with a subclass. Here is how to add a calculated field and a
fixed-width print format::

    >>> class Point(rectype('Point', 'x y')):
    ...    __slots__ = ()
    ...    @property
    ...    def hypotenuse(self):
    ...        return (self.x ** 2 + self.y ** 2) ** 0.5
    ...    def __str__(self):
    ...        return 'Point: x={0} y={1} z={2}'.format(self.x, self.y, self.hypotenuse)
    >>> p = Point(x=3, y=4)
    >>> print(p)
    Point: x=3 y=4 z=5.0

The subclass shown above sets ``__slots__`` to an empty tuple. This helps
keep memory requirements low by preventing the creation of instance dictionaries.

Adding fields/attributes
========================
Because *rectype* objects are based on slots, new fields cannot be added after
object creation::

    >>> Point = rectype('Point', 'x y')
    >>> p = Point([1, 2])
    >>> p.new_attribute = 4   # Can't do this!
    AttributeError                  Traceback (most recent call last)
    <ipython-input-8-55738ba62948> in <module>()
    ----> 1 rec.c = 3

    AttributeError: 'Point3D' object has no attribute 'new_attribute'

Subclassing is also not useful for adding new attributes. Instead, simply
create a new rectype from the ``_fieldnames`` class attribute::

    >>> Point3D = rectype('Point3D', Point._fieldnames + ('z',))

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
an equivalent ``namedtuple``. The memory saving can be significant if you
have a large number of instances (e.g. hundreds of thousands).

Choosing a data type
====================
Believe it or not, rectypes are not always the best data type to use.
Depending on your use-case other data types may be more appropriate:

* rectypes may be a good choice when one or more of the following are true:
    - the data has a static structure but dynamic values
    - per field default values (including factory function defaults) are
      required
    - the data set consists of a very large number of instances
    - the data has more than 255 fields
* named tuples are suitable for data with a static structure and static values
  (although the ``_replace()`` method can be used to update values)
* dictionaries should be used when the structure of the data is dynamic, but
  memory use a very large number of instances is required.
* SimpleNamespace (available in in Python 3.3+) is suitable when the structure
  of the data is dynamic and attribute access is required
* classes may be needed when you need to add lots of methods to objects

TODO: More than 255 fields

