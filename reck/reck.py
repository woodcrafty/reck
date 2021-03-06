"""
This module implements the recktype() factory function and DefaultFactory
class for creating lightweight record classes with mutable fields and optional
per-field defaults.

:copyright: (c) 2015 by Mark Richards.
:license: BSD 3-Clause, see LICENSE.txt for more details.
"""

import collections
import keyword
import operator
import sys

__license__ = 'BSD 3-clause'
__version__ = '0.0.0'
__author__ = 'Mark Richards'
__email__ = 'mark.l.a.richardsREMOVETHIS@gmail.com'


def recktype(typename, fieldnames, rename=False):
    """
    Create a new record class with fields accessible by named attributes.

    The new type is a subclass of ``collections.Sequence`` named *typename*.

    The new subclass is used to create record objects that have fields
    accessible by attribute lookup as well as being indexable and
    iterable. Per-field default values can be set. These are assigned
    to fields that are not supplied a value during instantiation.

    Basic example::

        >>> from reck import recktype
        >>> Point3D = recktype('Point3D', 'x y z')  # Create new record type
        >>> p = Point3D(x=1, y=2, z=3)
        >>> # Make a new Point3D class in which 'z' defaults to zero
        >>> Point3D = recktype('Point3D', ['x', 'y', ('z', 0)])
        >>> p = Point3D(x=1, y=2)
        >>> p                                   # z has been assigned its default value
        Point3D(x=1, y=2, z=0)

    :param typename: Name of the subclass to create, e.g. ``'MyRecord'``.
    :param fieldnames:  Specifies the fieldnames and optional per-field
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
    :returns: A subclass of of collections.Sequence named *typename*.
    :raises ValueError: if *typename* is invalid; *fieldnames* contains
        an invalid fieldname and rename is ``False``; *fieldnames*
        contains a sequence that is not length 2.
    :raises TypeError: if a fieldname is neither a string or a sequence.
    """
    _validate_typename(typename)
    if isinstance(fieldnames, collections.Mapping):
        # Convert mapping to a sequence of (fieldname, value) tuples
        fieldnames = list(fieldnames.items())
    elif isinstance(fieldnames, str):
        fieldnames = fieldnames.replace(',', ' ').split()

    fieldnames, defaults = _parse_fieldnames(fieldnames, rename)
    default_factory_fields = _get_default_factory_fields(defaults)

    # Create the __dict__ of the new record type:
    # The new type is composed from module-level functions rather than
    # by subclassing a predefined Record base class because this offers
    # approach offer greater flexibility for contructing different types
    # in the future.
    # _fieldnames_set is used to provide fast membership testing
    type_dct = dict(
        # API methods and attributes:
        __init__=__init__,
        _fieldnames=tuple(fieldnames),
        _update=_update,
        _get_defaults=_get_defaults,
        _replace_defaults=_replace_defaults,
        _asdict=_asdict,
        _asitems=_asitems,
        # Need to set _count and _index to the baseclass implementation in case
        # a fieldname attribute overwrites count or index
        _count=collections.Sequence.count,
        _index=collections.Sequence.index,

        # Internal methods and attributes:
        __slots__=tuple(fieldnames),
        _fieldnames_set=frozenset(fieldnames),  # For fast membership testing
        # isintance() testing is slow so store names of fields with default
        # factories in a set for fast membership testing.
        _default_factory_fields=frozenset(default_factory_fields),
        _nfields=len(fieldnames),  # For speed
        # An operator.attrgetter is stored for each field because it offers
        # a slight speedup over getattr(). TODO: test that this holds true
        # across platforms and python verions
        _attr_getters=tuple(
            [operator.attrgetter(field) for field in fieldnames]),
        _defaults=defaults,
        _check_args=_check_args,

        # Special methods
        __dict__=property(_asdict),
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
    Return a new record object.

    Field values can be passed by field order, fieldname, or both.

    The following examples all return a record equivalent to
    ``Rec(a=1, b=2, c=3)``::

        >>> Rec = recktype('Rec', 'a b c')
        >>> rec = Rec(1, 2, 3)                # using positional args
        >>> rec = Rec(a=1, b=2, c=3)          # using keyword args
        >>> rec = Rec(*[1, 2, 3])             # using an unpacked sequence
        >>> rec = Rec(**dict(a=1, b=2, c=3))  # using an unpacked mapping
        >>> rec = Rec(*[1, 2], c=3)           # using an unpacked sequence and a keyword arg
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
    :param **kwargs: Field values passed by fieldname.
    :raises TypeError: if the number of positional arguments exceeds the
         number of fields, a keyword argument does not match a fieldname,
         or a keyword argument redefines a positional argument.
    :raises ValueError: if a field has not been defined by the positional
         or keyword arguments and has no default value set.
    """
    self._check_args(values_by_field_order, values_by_fieldname)

    for fieldname, value in zip(self._fieldnames, values_by_field_order):
        setattr(self, fieldname, value)

    for fieldname in values_by_fieldname:
        setattr(self, fieldname, values_by_fieldname[fieldname])

    for fieldname in self._fieldnames:
        if not hasattr(self, fieldname):
            if fieldname in self._defaults:
                if fieldname in self._default_factory_fields:
                    # Call the default factory function (value)
                    setattr(self, fieldname, self._defaults[fieldname]())
                else:
                    setattr(self, fieldname, self._defaults[fieldname])
            else:
                raise ValueError('field {0!r} is not defined'.format(fieldname))


def _update(self, *values_by_field_order, **values_by_fieldname):
    """
    Update field values.

    Update field values with values passed by field order, fieldname, or both.

    Example::

        >>> Rec = recktype('Rec', 'a b c')
        >>> r = Rec(a=1, b=2, c=3)
        >>> r._update(b=5, c=6)   # using keyword arguments
        >>> r
        Rec(a=1, b=2, c=3)
        >>> r._update(2, 3, c=4)  # using positional and keyword arguments
        >>> r
        Rec(a=2, b=3, c=4)

    :param *values_by_field_order: Field values passed by field order.
    :param **values_by_fieldname: Field values passed by fieldname.
    :raises TypeError: if the number of positional arguments exceeds the
         number of fields, a keyword argument does not match a fieldname,
         or a keyword argument redefines a positional argument.
    """
    self._check_args(values_by_field_order, values_by_fieldname)

    for fieldname, value in zip(self._fieldnames, values_by_field_order):
        setattr(self, fieldname, value)

    for fieldname in values_by_fieldname:
        setattr(self, fieldname, values_by_fieldname[fieldname])


def _asdict(self):
    """
    Return a new ``collections.OrderedDict`` which maps fieldnames to their
    values.
    """
    return collections.OrderedDict(zip(self._fieldnames, self))


def _asitems(self):
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
        >>> Point = recktype('Point', [('x', None), ('y', None)])
        >>> Point._get_defaults()
        {'x': None, 'y': None}
    """
    return cls._defaults


@classmethod
def _replace_defaults(cls, *values_by_field_order, **values_by_fieldname):
    """
    Replace the existing per-field default values.

    The new default field values can be passed by field order, fieldname, or
    both.

    Changing the defaults can be useful if you wish to use the same record
    class in different contexts which require different default values.

    :param *values_by_field_order: Default field values passed by field order.
    :param **values_by_fieldname: Default field values passed by fieldname.
    :raises TypeError: if the number of positional arguments exceeds the
         number of fields, a keyword argument does not match a fieldname,
         or a keyword argument redefines a positional argument.
    """
    cls._check_args(values_by_field_order, values_by_fieldname)
    defaults = {}
    defaults.update(zip(cls._fieldnames, values_by_field_order))
    defaults.update(values_by_fieldname)
    cls._defaults = defaults

    cls._default_factory_fields = frozenset(
        _get_default_factory_fields(defaults))


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
    for _, fieldname, in zip(values_by_field_order, cls._fieldnames):
        if fieldname in values_by_fieldname:
            raise TypeError(
                'got multiple values for argument {0!r}'.format(fieldname))


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
        setattr(self, self._fieldnames[index], value)
    else:  # Slice object
        fields = self._fieldnames[index]
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
    for attr, value in zip(self._fieldnames, state):
        setattr(self, attr, value)


def __len__(self):
    return self._nfields


def __repr__(self):
    return '{}({})'.format(
        self.__class__.__name__, ', '.join('{}={}'.format(
            attr, repr(getattr(self, attr))) for attr in self._fieldnames))


def __str__(self):
    return '{}({})'.format(
        self.__class__.__name__, ', '.join('{}={}'.format(
            attr, str(getattr(self, attr))) for attr in self._fieldnames))


# ------------------------------------------------------------------------------
# Helper functions

def _get_default_factory_fields(defaults):
    """
    Return a list of fieldnames that have a factory function default.

    :param defaults: a fieldname/default_value mapping.
    """
    default_factory_fields = []
    for fieldname, default_value in defaults.items():
        if isinstance(default_value, DefaultFactory):
            default_factory_fields.append(fieldname)
    return default_factory_fields


def _parse_fieldnames(fieldnames, rename):
    """
    Process a sequence of fieldname strings and/or (fieldname, default) tuples,
    creating a list of corrected fieldnames and a map of fieldname to
    default-values.
    """
    defaults = {}
    validated_fieldnames = []
    used_names = set()
    for idx, fieldname in enumerate(fieldnames):
        if isinstance(fieldname, str):
            has_default = False
        else:
            try:
                if len(fieldname) != 2:
                    raise ValueError(
                        'fieldname should be a (fieldname, default_value) '
                        '2-tuple'.format(fieldname))
            except TypeError:
                raise TypeError(
                    'fieldname should be a string, or a '
                    '(fieldname, default_value) 2-tuple'.format(fieldname))
            has_default = True
            default = fieldname[1]
            fieldname = fieldname[0]

        fieldname = _validate_fieldname(fieldname, used_names, rename, idx)
        validated_fieldnames.append(fieldname)
        used_names.add(fieldname)
        if has_default:
            defaults[fieldname] = default
    return validated_fieldnames, defaults


def _validate_fieldname(fieldname, used_names, rename, idx):
    """
    Return fieldname if it is valid, a renamed fieldname if it is invalid
    and *rename* is True, else raise a ValueError.

    :param fieldname: fieldname to validate.
    :param used_names:: set of fieldnames that have already been used.
    :param rename: If True invalid fieldnames are replaced with a valid name.
    :param idx: integer index of fieldname in the class fieldnames sequence.
        Used in the renaming of invalid fieldnames.
    :returns: The fieldname, which may have been renamed if it was invalid and
        rename is True.
    :raises ValueError: if the fieldname is invalid and rename is False.
    """
    try:
        _validate_name(fieldname, 'field')
        # Validation specific to fieldnames:
        if fieldname.startswith('_'):
            raise ValueError(
                'fieldname cannot start with an underscore: {0!r}'
                .format(fieldname))
        if fieldname in used_names:
            raise ValueError(
                'encountered duplicate fieldname: {0!r}'.format(fieldname))
    except (ValueError, TypeError):
        if rename:
            return '_{0}'.format(idx)
        else:
            raise
    return fieldname


def _validate_typename(typename):
    """
    Raise a ValueError if typename is invalid.
    """
    _validate_name(typename, 'type')


def _validate_name(name, nametype):
    """
    Perform name validation common to both type names and fieldnames.
    """
    if not name.isidentifier():
        raise ValueError(
            '{0}name must be a valid identifiers: {1:!r}'
            .format(nametype, name))
    if keyword.iskeyword(name):
        raise ValueError(
            '{0}name cannot be a keyword: {1!r}'.format(nametype, name))


class DefaultFactory(object):
    """
    Wrap a default factory function.

    Default factory functions must be wrapped using this class so that they
    can be distinguished from non-factory callable default values. The *args*
    and *kwargs* arguments can be used to specify optional positional and
    keyword arguments to be passed to the factory function when it is called.

    Example of setting ``list`` as a default factory during record type
    creation::

        >>> from reck import DefaultFactory
        >>> Car = recktype('Car', [
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

        >>> Rec = recktype('Rec', [
        ...     ('a', DefaultFactory(dict, args=[[('b', 2)]], kwargs=dict(c=3)))])
        >>> rec = Rec()       # field 'a' will be set using the default factory
        >>> rec.a
       {'b': 2, 'c': 3}

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
