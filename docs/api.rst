===
API
===

-----------------------------------------------------------
:py:func:`make_rectype()` factory function for record types
-----------------------------------------------------------

.. py:function:: make_rectype(typename, fieldnames, rename=False)

    Create a new record class with fields accessible by named attributes.

    The new type is a subclass of ``collections.Sequence`` named *typename*.

    The new subclass is used to create record objects that have fields
    accessible by attribute lookup as well as being indexable and
    iterable. Per-field default values can be set. These are assigned
    to fields that are not supplied a value when new instances of the
    subclass are initialised.

    Basic example::

        >>> from reck import make_rectype
        >>> Point = make_rectype('Point', 'x y')  # create a new record type
        >>> p = Point(x=1, y=2)              # instantiate with keyword arguments
        >>> p.x                              # fields are accessible by name
        1
        >>> p[1]                             # and indexable like lists
        2
        >>> p                                # readable __repr__ with name=value style
        Point(x=1, y=2)
        >>> # Create a new record type with default field values
        >>> Point = make_rectype('Point', [('x', None), ('y', None)])
        >>> p = Point(x=1)                   # fields with defaults do not need to be specified
        >>> p                                # y has been assigned a default value
        Point(x=1, y=None)

    :param typename: Name of the subclass to create, e.g. ``'MyRecord'``.
    :param fieldnames: Specifies the fieldnames and optional per-field
        default values of the record. It cam be a single string with each
        fieldname separated by whitespace and/or commas such as ``'x, y'``;
        a sequence of strings such as ``['x', 'y']`` and/or 2-tuples of the
        form ``(fieldname, default_value)`` such as
        ``[('x', None), ('y', None)]``; a mapping of fieldname-default_value
        pairs such as ``collections.OrderedDict([('x', None), ('y', None)])``.

        Note, it only makes sense to use an ordered mapping (e.g.
        ``OrderedDict``) since access by index or iteration is affected by the
        order of the fieldnames.

        A fieldname may be any valid Python identifier except for names
        starting with an underscore.
    :param rename: If set to ``True``, invalid fieldnames are automatically
        replaced with positional names. For example,
        ('abc', 'def', 'ghi', 'abc') is converted to
        ('abc', '_1', 'ghi', '_3'), eliminating the keyword 'def' and the
        duplicate fieldname 'abc'.
    :returns: A subclass of ``collections.Sequence`` named *typename*.
    :raises: ``ValueError`` if *typename* is invalid or *fieldnames*
        contains an invalid fieldname and *rename* is ``False``.

--------------------------------------
Methods and attributes of record types
--------------------------------------
These are the methods and attributes supported by record types. To prevent
conflicts with fieldnames, the method and attribute names start with an
underscore.

.. py:class:: SomeRecordType(*values_by_field_order, **values_by_fieldname)

    Return a new record object.

    Field values can be passed by field order, fieldname, or both.

    The following examples all return a record equivalent to
    ``Rec(a=1, b=2, c=3)``::

        >>> Rec = make_rectype('Rec', 'a b c')
        >>> rec = Rec(1, 2, 3)                # using positional args
        >>> rec = Rec(a=1, b=2, c=3)          # using keyword args
        >>> rec = Rec(*[1, 2, 3])             # using a sequence
        >>> rec = Rec(**dict(a=1, b=2, c=3))  # using a mapping
        >>> rec = Rec(*[1, 2], c=3)           # using an unpacked sequence and keyword arg
        >>> rec
        Rec(a=1, b=2, c=3)

    Since record objects are iterable they can be used to initialise
    other objects of the same type by unpacking them::

        >>> rec2 = Rec(*rec)
        >>> rec2 == rec
        True

    If a field has not been supplied a value by an argument, its default value
    will be used (if one has been defined).

    :param *values_by_field_order: Field values passed by field order.
    :param **values_by_fieldname: Field values passed by fieldname.
    :raises: ``TypeError`` if the number of positional arguments exceeds the
         number of fields, a keyword argument does not match a fieldname,
         or a keyword argument redefines a positional argument.

         ``ValueError`` if a field has not been defined by the positional
         or keyword arguments and has no default value set.

.. py:function:: somerecord._asdict()

    Return a new ``collections.OrderedDict`` which maps fieldnames to their
    values.

.. py:function:: somerecord._asitems()

    Return a list of ``(fieldname, value)`` 2-tuples.

.. py:function:: somerecord._count(value)

    Return a count of how many times *value* occurs in the record.

.. py:function:: somerecord._index(value)

    Return the index of the first occurrence of *value* in the record.

.. py:attribute:: somerecord._fieldnames

    Tuple of strings listing the fieldnames. Useful for introspection and
    creating new record types from existing record types. Should not be
    changed.

    Example usage::

        >>> Point = make_rectype('Point', 'x y')  # create a new record type
        >>> Point._fieldnames       # view the fieldnames
        ('x', 'y')
        >>> Point3D = make_rectype('Point3D', Point._fieldnames + ('z',))
        >>> Point3D._fieldnames
        ('x', 'y', 'z')

.. py:classmethod:: somerecord._get_defaults()

    Return a dict that maps fieldnames to their corresponding default_value.
    If no default values are set an empty dict is returned.

.. py:classmethod:: somerecord._replace_defaults(*values_by_field_order, **values_by_fieldname)

    Replace the existing per-field default values.

    The new default field values can be passed by field order, fieldname, or
    both.

    Changing the defaults can be useful if you wish to use the same record
    class in different contexts which require different default values.

    Example::

        >>> Point3D = make_rectype('Point3D', [('x', 1), ('y', 2), 'z'])
        >>> Point3D._get_defaults()
        {'x': 1, 'y': 2}
        >>> Point3D._replace_defaults(x=7, z=9)
        >>> Point3D._get_defaults()  # 'y' was not supplied a default so it no longer has one
        {'x': 7, 'z': 9}
        >>> Point3D._replace_defaults()  # Remove all defaults
        >>> Point3D._get_defaults()
        {}

    :param *values_by_field_order: Default field values passed by field order.
    :param **values_by_fieldname: Default field values passed by fieldname.
    :raises: ``TypeError`` if the number of positional arguments exceeds the
         number of fields, a keyword argument does not match a fieldname,
         or a keyword argument redefines a positional argument.

.. py:function:: somerecord._update(*values_by_field_order, **values_by_fieldname)

    Update field values with values passed by field order, fieldname, or both.

    Example::

        >>> Rec = make_rectype('Rec', 'a b c')
        >>> r = Rec(a=1, b=2, c=3)
        >>> r._update(b=5, c=6)   # Using keyword arguments
        >>> r
        Rec(a=1, b=5, c=6)
        >>> r._update(2, 3, c=4)  # Using values by field order and by name
        >>> r
        Rec(a=2, b=3, c=4)

    :param *values_by_field_order: Field values passed by field order.
    :param **values_by_fieldname: Field values passed by fieldname.
    :raises: ``TypeError`` if the number of positional arguments exceeds the
         number of fields, a keyword argument does not match a fieldname,
         or a keyword argument redefines a positional argument.

-------------------------------
Operations supported by records
-------------------------------
The following operations are supported by records:

**len(rec)**

    Return the number of fields in the record *rec*.

**rec[index]**

    Return the field values(s) in *rec* corresponding to the position(s) given
    by *index*. *index* can be an integer or slice object.

**rec[index] = value**

    Set the value of the field corresponding to the position given by
    *index*, which may be an integer or slice object.

    Note, the behaviour of setting field values using slices is
    different from that of lists. If *values* contains more items than
    *slice* the surplus values are discarded, whereas with lists the
    surplus items are inserted into the list. Similarly, if *values* contains
    fewer items than *slice*, the surplus fields in the slice remain
    unaffected, whereas with a list the surplus list items are removed.

    Example::

        >>> Rec = make_rectype('Rec', 'a b c')
        >>> r = Rec(1, 2, 3)
        >>> r[2] = 4            # using an integer index
        >>> r[2]
        4
        >>> r[:2] = [5, 6, 7]   # using a slice
        >>> r                   # the surplus value, 7, was discarded
        Rec(a=5, b=6, c=4)

**value in rec**

    Return ``True`` if record *rec* contains *value*, else ``False``.

**value not in rec**

    Equivalent to ``not value in rec``.

**iter(rec)**

    Return an iterator over the field values of record *rec*.

**reversed(rec)**

    Return a reverse iterator over the field values of record *rec*.

**vars(rec)**
    Return a new ``collections.OrderedDict`` which maps the fieldnames of
    *rec* to their corresponding values. This is equivalent to calling
    ``rec._asdict()``.

--------------
DefaultFactory
--------------
.. py:class:: DefaultFactory(factory_func, args=(), kwargs={})

    Wrap a default factory function.

    Default factory functions must be wrapped using this class so that they
    can be distinguished from non-factory callable default values. The *args*
    and *kwargs* arguments can be used to specify optional positional and
    keyword arguments to be passed to the factory function when it is called.

    Example of setting ``list`` (with no arguments), as a default factory
    during record type creation::

        >>> from reck import DefaultFactory
        >>> Car = make_rectype('Car', [
        ...     'make',
        ...     'model',
        ...     ('colours', DefaultFactory(list))])
        >>> car = Car(make='Lotus', model='Exige')
        >>> car.colours.append('Orange')
        >>> car.colours.append('Green')
        >>> car
        Car(name='Lotus', model='Exige', colours=['Orange', 'Green'])

    An example using ``dict`` with positional and keyword arguments
    as a default factory::

        >>> Rec = make_rectype('Rec', [
        ...     ('a', DefaultFactory(dict, args=[[('b', 2)]], kwargs=dict(c=3)))])
        >>> rec = Rec()       # field will be set using the default factory
        >>> rec.a
       {'b': 2, 'c': 3}

    :param factory_func: the callable object to be invoked as a default
        factory function (with *args* and *kwargs* if provided).
    :param args: a tuple of arguments for the factory function invocation.
    :param kwargs: a dictionary of keyword arguments for the factory function
        invocation.
