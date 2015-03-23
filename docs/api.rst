===========
rectype API
===========
--------------------------------------------------------------------------------
:py:func:`rectype` factory function for record classes with mutable field values
--------------------------------------------------------------------------------

Record types allow fields to be accessed by name as well as position index
allowing for more readable, self-documenting code. They are similar to
``collections.namedtuple`` types except that field values are mutable,
per-field default values are supported and they consume slightly less memory.

.. py:function:: rectype(typename, fieldnames, rename=False)

    Return a new ``collections.Sequence`` subclass named *typename*.

    The new subclass is used to create ``rectype`` objects that have
    fields accessible by attribute lookup as well as being indexable
    and iterable. Per-field default values can be set. These are assigned
    to fields that are not supplied a value when new instances of the
    subclass are initialised.

    Basic example::

        >>> Point = rectype('Point', 'x y')  # create a new record type
        >>> p = Point(x=1, y=2)              # instantiate with keyword arguments
        >>> p[0]                             # indexable like lists
        1
        >>> p.y                              # fields also accessible by name
        2
        >>> p                                # readable __repr__ with name=value style
        Point(x=1, y=None)
        >>> # Create a new record type with default field values
        >>> Point = rectype('Point', [('x', None), ('y', None)])
        >>> p = Point(x=1)                   # fields with defaults do not need to be specified
        >>> p                                # y has been assigned a default value
        Point(x=1, y=None)

    :param typename: Name of the subclass to create, e.g. ``'MyRecord'``.
    :param fieldnames: Specifies the fieldnames and optional per-field
        default values of the record. It cam be a single string with each
        fieldname separated by whitespace and/or commas such as ``'x, y'``;
        a sequence of strings such as ``['x', 'y']`` and/or 2-tuples of the
        form ``(fieldname, default_value)`` such as ``[('x', None), ('y', None)]
        ``; a mapping of fieldname-default_value pairs such as
        ``collections.OrderedDict([('x', None), ('y', None)])``.

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
    :raises: ValueError if *typename* is invalid or *fieldnames*
        contains an invalid fieldname and rename is ``False``.

Instances of classes created by ``rectype.rectype()`` are created as follows:

.. py:class:: SomeRecType(*args, **kwargs)

    Return a new ``rectype`` object initialised from an optional positional
    argument and optional keyword arguments. It has the following call
    profiles:

        | *class* **SomeRecType**\ (***kwargs*)
        | *class* **SomeRecType**\ (*mapping, **kwargs*)
        | *class* **SomeRecType**\ (*iterable, **kwargs*)

    The following examples all return a rectype equivalent to
    ``Rec(a=1, b=2, c=3)``::

        >>> rec = Rec(dict(a=1, b=2, c=3))   # using a mapping
        >>> rec = Rec([1, 2, 3])             # using a sequence
        >>> rec = Rec(a=1, b=2, c=3)         # using keyword args
        >>> rec = Rec([1, 2], c=3)           # using a sequence and keyword args
        >>> rec
        Rec(a=1, b=2, c=3)

    Since rectype instances are iterable they can be used to initialise
    other instances of the same type::

        >>> rec2 = Rec(rec)
        >>> rec2 == rec
        True

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
    if one has been defined.

    :raises: ``TypeError`` if more than one positional argument is passed
         or if *kwargs* contains a keyword that does not match a fieldname.
         ``ValueError`` if a field has not been defined by the positional
         or keyword arguments and has no default value set.

Methods and attributes
----------------------

These are the methods and attributes supported by rectypes. To prevent
conflicts with fieldnames, the method and attribute names start with an
underscore.

.. py:attribute:: somerecord._fieldnames

    Tuple of strings listing the fieldnames. Useful for introspection and
    creating new record types from existing record types. Should not be
    changed.

    Example usage::

        >>> Point = rectype('Point', 'x y')  # create a new record type
        >>> Point._fieldnames       # view the fieldnames
        ('x', 'y')
        >>> Point3D = rectype('Point3D', Point._fieldnames + ('z',))
        >>> Point3D._fieldnames
        ('x', 'y', 'z')

.. py:classmethod:: _get_defaults()

    Return a dict that maps fieldnames to their corresponding default_value.
    If no default values are set an empty dict is returned.

.. py:classmethod:: somerecord._set_defaults()

    Replace the existing per-field default values with a new set.

    This can be useful if you wish to use the same record class in
    different contexts which require different default values.

    Example::

    >>> Point3D = rectype('Point3D', [('x', 1), ('y', 2), 'z')
    >>> Point3D._get_defaults()
    {'x': 1, 'y': 2}
    >>> Point3D._set_defaults({})  # Pass an empty set to remove all defaults
    >>> Point3D._get_defaults()
    {}

    :param defaults: A mapping of fieldname/default_value pairs which is
        used to replace the existing per-field default values. If a
        field is not present in *defaults* it will not have a default
        value. To remove all defaults set *defaults* to an empty mapping.
    :raises: ``ValueError`` if a key in *defaults* does not match a
        fieldname.

.. py:function:: somerecord._items()

    Return a list of ``(fieldname, value)`` 2-tuples.

.. py:function:: somerecord._update(*args, **kwargs)

    Update the field values of the record with values from an optional
    positional argument and a possibly empty set of keyword arguments.

    This method has the following call profiles:

        | somerec.\ **_update**\ (***kwargs*)
        | somerec.\ **_update**\ (*mapping, **kwargs*)
        | somerec.\ **_update**\ (*iterable, **kwargs*)

    Example::

        >>> Rec = rectype('Rec', 'a b c')
        >>> r = Rec(a=1, b=2, c=3)
        >>> r._update(b=5, c=6)     # using keyword arguments
        >>> r
        Rec(a=1, b=2, c=3)
        >>> r._update([2, 3], c=4)  # using an iterable and keyword arguments
        >>> r
        Rec(a=2, b=3, c=4)

    :param *args: Optional positional argument which can be a mapping of
        fieldname/field_value pairs or an iterable of field values which
        are in the same order as the fieldnames listed in the ``_fieldnames``
        class attribute.
    :param **kwargs: Keyword arguments in which each keyword must match a
        fieldname of the record. Keyword arguments can be supplied on their
        own, or together with the positional argument.
    :raises: ``TypeError`` if more than one positional argument is
        supplied or a keyword argument does not match a fieldname.

Operations
----------

These are the operations supported by rectypes:

**len(rec)**

    Return the number of fields in the record *rec*.

| **rec[index]**
| **rec[slice]**

    Return the value of the field in *rec* corresponding to the position given
    by integer *index* or position(s) given by slice object *slice*.

| **rec[index] = value**
| **rec[slice] = values**

    Set the value(s) of the field corresponding to the position(s) given by
    integer *index* or slice object *slice*.

    Note, the behaviour of setting field values using slices is
    different from that of lists. If *values* contains more items than
    *slice* the surplus values are discarded, whereas with lists the
    surplus items are inserted into the list. Similarly, if *values* contains
    fewer items than *slice*, the surplus fields in the slice remain
    unaffected, whereas with a list the surplus list items are removed.

**value in rec**

    Return ``True`` if record *rec* contains *value*, else ``False``.

**value not in rec**

    Equivalent to ``not value in rec``.

**iter(rec)**

    Return an iterator over the field values of record *rec*.

**reversed(rec)**

    Return a reverse iterator over the field values of record *rec*.

**rec.index(value)**

    Return the index of the first occurrence of *value* in record *rec*.

**rec.count(value)**

    Return a count of how many times *value* occurs in record *rec*.

**vars(rec)**
    Return a new ``collections.OrderedDict`` which maps the fieldnames of *rec*
    to their corresponding values.

--------------
DefaultFactory
--------------
.. py:class:: DefaultFactory(factory_func, args=(), kwargs={})

    Wrap a default factory function.

    Default factory functions must be wrapped using this class so that they
    can be distinguished from non-factory default values. Optional positional
    and keyword arguments to be set, which will be passed to the factory
    function when it is called.

    Example of setting ``list`` (with no srguments), as a default factory
    during rectype creation::

        >>> Car = rectype.rectype('Car', [
        ...     'make',
        ...     'model',
        ...     ('colours', rectype.DefaultFactory(list))]
        >>> car = Car(make='Lotus', model='Exige')
        >>> car.colours.append('Orange')
        >>> car.colours.append('Green')
        Car(name='Lotus', model='Exige', colours=['Orange', 'Green'])

    An example using ``dict`` with positional and keyword arguments
    as a default factory::

        >>> Rec = rectype('Rec', [('field', DefaultFactory(
        ...     dict, args=[('a', 1)], kwargs={'b': 2, 'c': 3})])
        >>> rec = Rec()       # field will be set using the default factory
        >>> rec
        Rec(field={'a': 1, 'b': 2, 'c': 3})

    :param factory_func: the callable object to be invoked as a default
        factory function (with *args* and *kwargs* if provided).
    :param args: a tuple of arguments for the factory function invocation.
    :param kwargs: a dictionary of keyword arguments for the factory function
        invocation.
