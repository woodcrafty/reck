
import collections
import keyword
import operator
import sys

__license__ = 'BSD 3-clause'
__version__ = '0.0.0'
__author__ = 'Mark Richards'
__email__ = 'mark.l.a.richardsREMOVETHIS@gmail.com'


def rectype(typename, fieldnames, rename=False):
    """
    Return a new subclass of ``collections.Sequence`` named typename.

    The new subclass is used to create ``rectype`` objects that have
    fields accessible by attribute lookup as well as being indexable
    and iterable. Per-field default values can be set which are assigned
    to fields that are not supplied a value when new instances of the
    subclass are initialised.

    Basic example::

        >>> Point = rectype('Point', 'x y')  # create a new record type
        >>> p = Point(x=1, y=2)              # instantiate with keyword arguments
        >>> p[0]                             # indexable like lists
        1
        >>> p.y                              # fields also accesible by name
        2
        >>> p                                # readable __repr__ with name=value style
        Point(x=1, y=None)
        >>> # Create a new record type with default field values
        >>> Point = rectype('Point', [('x', None), ('y', None)])
        >>> p = Point(x=1)                   # fields with defaults do not need to be specified
        >>> p                                # y has been assigned a default value
        Point(x=1, y=None)

    :param typename: Name of the subclass to create, .g. ``'MyRecord'``.
    :param fieldnames: Can be a single string with each fieldname separated by
        whitespace and/or commas such as ``'x, y'``; a sequence of strings such
        as ``['x', 'y']`` and/or 2-tuples of the form ``(fieldname,
        default-value)`` such as ``[('x', None), ('y', None)]``; a mapping of
        fieldname-default_value pairs such as
        ``collections.OrderedDict([('x', None), ('y', None)])``. Note, it
        only makes sense to use an ordered mapping (e.g. ``OrderedDict``) since
        access by index or iteration is affected by the order of the
        fieldnames. A fieldname may be any valid Python identifier except for
        names starting with an underscore.
    :param rename: If set to ``True``, invalid fieldnames are automatically
        replaced with positional names. For example,
        ('abc', 'def', 'ghi', 'abc') is converted to
        ('abc', '_1', 'ghi', '_3'), eliminating the keyword 'def' and the
        duplicate fieldname 'abc'.
    :returns: A subclass of ``RecType`` named *typename*.
    :raises: ``ValueError`` if *typename* is invalid; *fieldnames*
        contains an invalid fieldname and rename is ``False``; *fieldnames*
        does not contain a 2-tuple when one was expected.
    """
    _check_typename(typename)
    if isinstance(fieldnames, collections.Mapping):
        # Convert mapping to a sequence of (fieldname, value) tuples
        fieldnames = list(fieldnames.items())
    elif isinstance(fieldnames, str):
        fieldnames = fieldnames.replace(',', ' ').split()

    fieldnames, defaults = _parse_fieldnames(fieldnames, rename)

    # Create the __dict__ of the Record subclass:
    # The new type is composed from module-level functions rather than
    # by subclassing a predefined Record base class because this offers
    # approach offer greater flexibility for contructing different types
    # in the future.
    # _fieldnames_set is used to provide fast membership testing
    type_dct = dict(
        # API methods and attributes:
        __init__=__init__,
        _fieldnames=tuple(fieldnames),
        _nfields = len(fieldnames),  # For speed
        _update=_update,
        _get_defaults=_get_defaults,
        _set_defaults=_set_defaults,
        _items=_items,
        # Protected/internal methods and attributes:
        __slots__=tuple(fieldnames),
        _fieldnames_set=frozenset(fieldnames),
        # An operator.attrgetter is stored for each field because it offers
        # a slight speedup over getattr(). TODO: test that this holds true
        # across platforms and python verions
        _attr_getters=tuple(
            [operator.attrgetter(field) for field in fieldnames]),
        _defaults=defaults,
        _check_fieldnames_exist=_check_fieldnames_exist,
        _check_all_fields_defined=_check_all_fields_defined,
        _check_args=_check_args,
        __dict__=__dict__,
        __eq__=__eq__,
        __ne__=__ne__,
        __getstate__=__getstate__,
        __setstate__=__setstate__,
        __repr__=__repr__,
        __str__=__str__,
        # Sequence-like methods:
        __getitem__=__getitem__,
        __setitem__=__setitem__,
        __len__=__len__,
    )

    rectype = type(typename, (collections.Sequence,), type_dct)

    # Explanation from collections.namedtuple:
    # For pickling to work, the __module__ variable needs to be set to the
    # frame where the record type is created.  Bypass this step in
    # environments where sys._getframe is not defined (Jython for example)
    # or sys._getframe is not defined for arguments greater than 0
    # (e.g. IronPython).
    try:
        rectype.__module__ = sys._getframe(1).f_globals.get(
            '__name__', '__main__')
    except (AttributeError, ValueError):
        pass

    return rectype


def __init__(self, *values_by_field_order, **values_by_fieldname):
    """
    Return a new ``rectype`` object.

    Field values can be passed by field order, fieldname, or both.

    The following examples all return a rectype equivalent to
    ``Rec(a=1, b=2, c=3)``::

        >>> Rec = rectype('Rec', 'a b c')
        >>> rec = Rec(1, 2, 3)                # using positional args
        >>> rec = Rec(a=1, b=2, c=3)          # using keyword args
        >>> rec = Rec(*[1, 2, 3])             # using an unpacked sequence
        >>> rec = Rec(**dict(a=1, b=2, c=3))  # using an unpacked mapping
        >>> rec = Rec(*[1, 2], c=3)           # using an unpacked sequence and a keyword arg
        >>> rec
        Rec(a=1, b=2, c=3)

    Since rectype instances are iterable they can be used to initialise
    other instances of the same type by unpacking them::

        >>> rec2 = Rec(*rec)
        >>> rec2 == rec
        True

    If a field has not been supplied a value by an argument, its default value
    will be used (if one has been defined).

    :param *values_by_field_order: Field values passed by field order.
    :param **kwargs: Field values passed by fieldname.
    :raises: ``TypeError`` if the number of positional arguments exceeds the
         number of fields, a keyword argument does not match a fieldname,
         or a keyword argument redefines a positional argument.
         ``ValueError`` if a field has not been defined by the positional
         or keyword arguments and has no default value set.
    """
    self._check_args(values_by_field_order, values_by_fieldname)

    # Progressively assemble a dict representation of the record from
    # the field defaults, the positional arg and the keyword args.
    field_values = self._defaults.copy()
    field_values.update(zip(self._fieldnames, values_by_field_order))
    field_values.update(values_by_fieldname)

    self._check_all_fields_defined(field_values)

    for fieldname, value in field_values.items():
        if isinstance(value, DefaultFactory):
            # Call the default factory function
            setattr(self, fieldname, value())
        else:
            setattr(self, fieldname, value)


def _update(self, *values_by_field_order, **values_by_fieldname):
    """
    Update field values.

    Update field values with values passed by field order, fieldname, or both.

    Example::

        >>> Rec = rectype('Rec', 'a b c')
        >>> r = Rec(a=1, b=2, c=3)
        >>> r._update(b=5, c=6)     # using keyword arguments
        >>> r
        Rec(a=1, b=2, c=3)
        >>> r._update(2, 3, c=4)  # using positional and keyword arguments
        >>> r
        Rec(a=2, b=3, c=4)

    :param *values_by_field_order: Field values passed by field order.
    :param **values_by_fieldname: Field values passed by fieldname.
    :raises: ``TypeError`` if the number of positional arguments exceeds the
         number of fields, a keyword argument does not match a fieldname,
         or a keyword argument redefines a positional argument.
    """
    self._check_args(values_by_field_order, values_by_fieldname)

    # Progressively assemble a dict representation of the record from
    # the field defaults, the positional arg and the keyword args.
    field_values = {}
    field_values.update(zip(self._fieldnames, values_by_field_order))
    field_values.update(values_by_fieldname)

    for fieldname, value in field_values.items():
        setattr(self, fieldname, value)


def _items(self):
    """
    Return a list of ``(fieldname, value)`` 2-tuples.
    """
    return list(zip(self._fieldnames, self))


@classmethod
def _get_defaults(cls):
    """
    Return a ``dict`` which maps fieldnames to their corresponding
    default value (if they have one). If no default values are set an empty
     ``dict`` is returned.
    ::
        >>> Point = rectype('Point', [('x', None), ('y', None)])
        >>> Point._get_defaults()
        {'x': None, 'y': None}
    """
    return cls._defaults


@classmethod
def _set_defaults(cls, *values_by_field_order, **values_by_fieldname):
    """
    Replace the existing per-field default values.

    Default field values can be passed by field order, fieldname, or both.

    Changing the defaults can be useful if you wish to use the same record
    class in different contexts which require different default values.

    :param *values_by_field_order: Default field values passed by field order.
    :param **values_by_fieldname: Default field values passed by fieldname.
    :raises: ``TypeError`` if the number of positional arguments exceeds the
         number of fields, a keyword argument does not match a fieldname,
         or a keyword argument redefines a positional argument.
    """
    cls._check_args(values_by_field_order, values_by_fieldname)
    defaults = {}
    defaults.update(zip(cls._fieldnames, values_by_field_order))
    defaults.update(values_by_fieldname)
    cls._defaults = defaults


@classmethod
def _check_fieldnames_exist(cls, fieldnames):
    """
    Raise a ValueError if a fieldname does not exist in cls._fieldnames.
    """
    for fieldname in fieldnames:
        if fieldname not in cls._fieldnames:
            raise ValueError('field {0!r} is not defined'.format(fieldname))


@classmethod
def _check_all_fields_defined(cls, fieldnames):
    """
    Raise a ValueError if fieldnames does not contain all of the
    fieldnames in cls._fieldnames.
    """
    for fieldname in cls._fieldnames:
        if fieldname not in fieldnames:
            raise ValueError('field {0!r} is not defined'.format(fieldname))


@classmethod
def _check_args(cls, values_by_field_order, values_by_fieldname):
    """
    Check validity of positional and keyword arguments.
    """
    if len(values_by_field_order) > cls._nfields:
        raise TypeError(
            'takes up to {0} positional arguments but {1} were given'
            .format(cls._nfields, len(values_by_field_order)))

    # Check that every keyword argument in kwargs matches a fieldname.
    for fieldname in values_by_fieldname:
        if fieldname not in cls._fieldnames_set:
            raise TypeError(
                'keyword argument {0!r} does not match a field'
                .format(fieldname))

    # Check that none of the keyword args are redefining a positional arg
    positional_fields = frozenset(cls._fieldnames[:len(values_by_field_order)])
    for fieldname in values_by_fieldname:
        if fieldname in positional_fields:
            raise TypeError(
                'got multiple values for argument {0!r}'.format(fieldname))


@property
def __dict__(self):
    """
    Return a new ``OrderedDict`` which maps fieldnames to their values.
    """
    return collections.OrderedDict(zip(self._fieldnames, self))


def __eq__(self, other):
    return (isinstance(other, self.__class__)
        and self.__dict__ == other.__dict__)


def __ne__(self, other):
    return not self.__eq__(other)


def __getitem__(self, index):
    """
    Retrieve a field or slice of fields from the record using an index.

    Args:
        index: int or slice object
            Index can be an integer or slice object for normal sequence
            item access.
    Returns:
        If index is an integer the value of the field corresponding to
        the index is returned. If index is a slice a list of field values
        corresponding to the slice indices is returned.
    """
    if isinstance(index, int):
        return self._attr_getters[index](self)
    # Slice object
    return [getter(self) for getter in self._attr_getters[index]]


def __setitem__(self, index, value):
    """
    Note: if index is a slice and value is longer than the slice then
    the surplus values are discarded. This behaviour differs from that
    of list.__setitem__ which inserts the surplus values into the list.
    Similarly, if value contains too few values, the surplus fields are
    left unaffected. With a list, the surplus items are deleted.

    Args:
        index: int or slice object
            Index/slice to be set.
        value: any
            Value to set.
    """
    if isinstance(index, int):
        setattr(self, self.__slots__[index], value)
    else:  # Slice object
        fields = self.__slots__[index]
        for field, v in zip(fields, value):
            setattr(self, field, v)


def __getstate__(self):
    """
    Return self as a tuple to allow the record to be pickled.
    """
    return tuple(self)


def __setstate__(self, state):
    """
    Re-initialise the record from the unpickled tuple representation.
    """
    for attr, value in zip(self.__slots__, state):
        setattr(self, attr, value)


def __len__(self):
    return len(self.__slots__)


def __repr__(self):
    return '{}({})'.format(
        self.__class__.__name__, ', '.join('{}={}'.format(
            attr, repr(getattr(self, attr))) for attr in self.__slots__))


def __str__(self):
    return '{}({})'.format(
        self.__class__.__name__, ', '.join('{}={}'.format(
            attr, str(getattr(self, attr))) for attr in self.__slots__))

# ------------------------------------------------------------------------------
# Helper functions

def _parse_fieldnames(fieldnames, rename):
    """
    Process a sequence of fieldnames/(fieldname, default) tuples,
    creating a list of corrected fieldnames and a map of fieldname to
    default-values.
    """
    defaults = {}
    checked_fieldnames = []
    used_names = set()
    for idx, fieldname in enumerate(fieldnames):
        if isinstance(fieldname, str):
            has_default = False
        else:
            try:
                if len(fieldname) != 2:
                    raise ValueError(
                        'fieldname {0!r} must be a 2-tuple of the form '
                        '(fieldname, default_value)'.format(fieldname))
            except TypeError:
                raise ValueError(
                    'fieldname {0!r} must be a 2-tuple of the form '
                    '(fieldname, default_value)'.format(fieldname))
            has_default = True
            default = fieldname[1]
            fieldname = fieldname[0]

        fieldname = _check_fieldname(fieldname, used_names, rename, idx)
        checked_fieldnames.append(fieldname)
        used_names.add(fieldname)
        if has_default:
            defaults[fieldname] = default
    return checked_fieldnames, defaults


def _check_fieldname(fieldname, used_names, rename, idx):
    """
    Raise a ValueError if fieldname is invalid or optionally rename it.

    Args:
        fieldname: string
            The fieldname to check.
        used_names: set
            Set of fieldnames that have already been used.
        rename: boolean
            If True invalid fieldnames are replaced with a valid name.
        idx: integer
            Index of fieldname in the class fieldnames sequence. Used
            in the renaming of invalid fieldnames.
    Returns:
        The fieldname, which may have been renamed if it was invalid and
        rename is True.
    Raises:
        ValueError if the fieldname is invalid and rename is False.
    """
    try:
        _common_name_check(fieldname, 'field')
        if fieldname.startswith('_'):
            raise ValueError(
                'fieldnames cannot start with an underscore: {0!r}'
                .format(fieldname))
        if fieldname in used_names:
            raise ValueError(
                'encountered duplicate fieldname: {0!r}'.format(fieldname))
    except ValueError:
        if rename:
            return '_{0}'.format(idx)
        raise
    return fieldname


def _check_typename(typename):
    """
    Raise a ValueError if typename is invalid.
    """
    _common_name_check(typename, 'type')


def _common_name_check(name, nametype):
    """
    Perform name checks common to both typenames and fieldnames.
    """
    # if not isinstance(name, str):
    #     raise TypeError(
    #         '{0}names must be strings: {1:!r}'.format(nametype, name))
    if not name.isidentifier():
        raise ValueError(
            '{0}names must be valid identifiers: {1:!r}'
            .format(nametype, name))
    if keyword.iskeyword(name):
        raise ValueError(
            '{0}names cannot be a keyword: {1!r}'.format(nametype, name))


class DefaultFactory(object):
    """
    Wrap a default factory function.

    Default factory functions must be wrapped with this class so that they can
    be distinguished from non-factory default values. The class also allows
    optional positional and keyword arguments to be set, which will be passed
    to the factory function when it is called. To call the wrapped factory
    function (with the optional positional and keyword arguments), the
    DefaultFactory instance should be called.

    Example of setting ``list`` as a default factory during rectype creation::

        >>> from rectype import rectype, DefaultFactory
        >>> Car = rectype('Car', [
        ...     'make',
        ...     'model',
        ...     ('colours', DefaultFactory(list))]
        >>> car = Car(make='Lotus', model='Exige')
        >>> car.colours.append('Orange')
        >>> car.colours.append('Green')
        Car(name='Lotus', model='Exige', colours=['Orange', 'Green'])

    Example using ``dict`` as a default factory with positional and keyword
    arguments::

        >>> Rec = rectype.rectype('Rec', ['field1',
        ...     ('field2', DefaultFactory(
        ...         dict, args=[('a', 1)], kwargs={'b': 2, 'c': 3})])
        >>> rec = Rec(field1=1)   # field2 will be set using the default factory
        >>> rec
        Rec(field1=1, field2={'a': 1, 'b': 2, 'c': 3})

    :param factory_func: the callable object to be invoked as a default
        factory function (with *args* and *kwargs* if provided).
    :param args: a tuple of arguments for the factory function invocation.
    :param kwargs: a dictionary of keyword arguments for the factory function
        invocation.
    """
    def __init__(self, factory_func, args=(), kwargs={}):
        self._factory_func = factory_func
        self._args = args
        self._kwargs = kwargs

    def __call__(self):
        return self._factory_func(*self._args, **self._kwargs)

    def __repr__(self):
        return ('DefaultFactory({0!r}, args={1!r}, kwargs={2!r})'
            .format(self._factory_func, self._args, self._kwargs))
