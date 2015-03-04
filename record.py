"""
Create custom record classes that have mutable field values.

TODO:
"""

import collections
import keyword
import operator
import sys

__license__ = 'BSD 3-clause'
__version__ = '0.0.0'
__author__ = 'Mark Richards'
__email__ = 'mark.l.a.richardsREMOVETHIS@gmail.com'

NO_DEFAULT = object()


def make_type(typename, fieldnames, rename=False):
    """Make a custom record class.

    Class factory for creating a custom record class with attributes
    corresponding to the names given in the fieldnames argument. The
    custom record class is used to create record objects with mutable
    fields that are accessible by attribute lookup or by index, and are
    iterable. There is no restriction on the number of fields.

    Record objects do not have per-instance dictionaries. They store
    attributes in __slots__, so they are lightweight, requiring one
    less byte of memory than an equivalent tuple or namedtuple. However,
    this means that instances of record objects cannot be assigned new
    fields/attributes.

    Args:
        typename: str
            Name of the record-like class to create, e.g. 'MyRecord'.
        fieldnames: iterable
            Must be a string or sequence of fieldnames, or a mapping
            of the form fieldname: default or a sequence of tuples of
            the form (fieldname, default). Note that it only makes sense
            to pass an ordered mapping (e.g. OrderedDict) since acces by
            index or iteration is affected by the order of the fieldnames.
            If fieldnames is a string each fieldname should be separated
            by a space and/or comma, e.g. 'field1 field2 field3'. A
            fieldname may be any valid Python identifier except for names
            starting with an underscore.
        rename: boolean
            If rename is True, invalid fieldnames are automatically replaced
            with positional names. For example, ('abc', 'def', 'ghi', 'abc')
            is converted to ('abc', '_1', 'ghi', '_3'), eliminating the
            keyword 'def' and the duplicate fieldname 'abc'.
    Returns:
        A custom record class.
    """
    try:
        _ = iter(fieldnames)
    except TypeError:
        raise TypeError('fieldnames is not iterable')

    # Parse fieldnames into a list of fieldnames and a list of defaults
    if isinstance(fieldnames, str):
        _fieldnames = fieldnames.replace(',', ' ').split()
        _defaults = NO_DEFAULT
    elif isinstance(fieldnames, collections.Mapping):
        _fieldnames = list(fieldnames.keys())
        _defaults = tuple(fieldnames.values())
    # Fieldnames could be a sequence of strings
    elif all([isinstance(item, str) for item in fieldnames]):
        _fieldnames = fieldnames
        _defaults = NO_DEFAULT
    # Must be a sequence of 2-tuples (or other 2-element non-string sequences!)
    elif (all([isinstance(v, collections.Sequence) for v in fieldnames])
            and all(
                [len(v) == 2 and not isinstance(v, str) for v in fieldnames])):
        _fieldnames, _defaults = zip(*fieldnames)
        _fieldnames = list(_fieldnames)
        _defaults = tuple(_defaults)
    else:
        raise TypeError(
            'fieldnames must be a sequence of strings or sequence of '
            '(fieldname, default-value) tuples')

    # # If a default value is specified this takes precedence over any defaults
    # # set via the fieldnames arg. The default value is used for every field.
    # if default != NO_DEFAULT:
    #     _defaults = [default] * len(_fieldnames)

    if rename:
        # Rename any bad names with a sanitised name
        used_names = set()
        for i, name in enumerate(_fieldnames):
            if (not all(c.isalnum() or c == '_' for c in name)
                    or keyword.iskeyword(name)
                    or not name
                    or name[0].isdigit()
                    or name.startswith('_')
                    or name in used_names):
                _fieldnames[i] = '_{0}'.format(i)
            used_names.add(name)

    # Validate typename and fieldnames
    for name in [typename] + _fieldnames:
        if not isinstance(name, str):
            raise TypeError(
                'type names and fieldnames must be strings: {0!r}'.format(name))
        if not all(c.isalnum() or c == '_' for c in name):
            raise ValueError(
                'type names and fieldnames can only contain alphanumeric '
                'characters and underscores: {0!r}'.format(name))
        if keyword.iskeyword(name):
            raise ValueError(
                'type names and fieldnames cannot be a keyword: {0!r}'.format(
                    name))
        if name[0].isdigit():
            raise ValueError(
                'type names and fieldnames cannot start with a number: {0!r}'
                .format(name))

    # Further validation of fieldnames
    used_names = set()
    for name in _fieldnames:
        if name.startswith('_') and not rename:
            raise ValueError(
                'fieldnames cannot start with an underscore: {0!r}'.format(
                    name))
        if name in used_names:
            raise ValueError(
                'encountered duplicate fieldname: {0!r}'.format(name))
        used_names.add(name)

    # _attr_getters is included because operator.attrgetter offers a
    # slight speed up over using getattr()
    dct = dict(
        __slots__=tuple(_fieldnames),
        _fieldnames=tuple(_fieldnames),
        _defaults=_defaults,
        _asdict=_asdict,
        _get_defaults=_get_defaults,
        _set_defaults=_set_defaults,
        _attr_getters=[operator.attrgetter(field) for field in _fieldnames],
        __init__=__init__,
        # _asdict() is used to provide a dictionary representation of the
        # record when __dict__ is called.  This enables the vars() built-in
        # to return a dict even though the record's attributes are stored
        # in __slots__.
        __dict__=property(_asdict, _set__dict__),
        __iter__=__iter__,
        __getitem__=__getitem__,
        __setitem__=__setitem__,
        __getnewargs__=__getnewargs__,
        __getstate__=__getstate__,
        __len__=_len__,
        __setstate__=__setstate__,
        __repr__=__repr__,
        __str__=__str__,
        __eq__=__eq__,
        __ne__=__ne__,
    )
    # For pickling to work, the __module__ variable needs to be set to the
    # frame where the named tuple is created.  Bypass this step in
    # environments where sys._getframe is not defined (Jython for example)
    # or sys._getframe is not defined for arguments greater than 0
    # (e.g. IronPython).
    cls = type(typename, (collections.Sequence,), dct)
    try:
        cls.__module__ = sys._getframe(1).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass

    return cls


def __init__(self, values=None):
    """Make a new instance from an existing sequence or mapping.

    Args:
        values: iterable or None
            Values with which to populate the record. The values should be
            in the same order as _fieldnames, unless it is a mapping,
            in which case the keys are used to identify the appropriate
            fields. If values is None then the instance is initialised
            using default values. If no defaults are set then values must
            be an iterable.
    """
    if values is None:
        if self._defaults != NO_DEFAULT:
            values = list(self._defaults)
        else:
            raise ValueError(
                'values must be specified when no defaults have been set')

    try:
        _ = iter(values)
    except TypeError:
        raise TypeError('values is not iterable')

    if isinstance(values, collections.Mapping):
        # The keys of the values mapping is allowed to be a superset
        # of self._fieldnames, so Attribute Errors are allowed
        if not all([name in values for name in self._fieldnames]):
            raise ValueError(
                "when values is a mapping its keys must contain all of "
                "the record's fieldnames")
        for fieldname in self._fieldnames:
            setattr(self, fieldname, values[fieldname])
    else:  # values must be a sequence
        if len(values) < len(self._fieldnames):
            raise ValueError('too few items in values')
        for attr, value in zip(self._fieldnames, values):
            setattr(self, attr, value)


@classmethod
def _get_defaults(cls):
    return cls._defaults


@classmethod
def _set_defaults(cls, defaults):
    """Set the default field values for new instances of the record class.

    Args:
        defaults: mapping, sequence of 2-tuples, class instance or NO_DEFAULT
            Can be a {fieldname: default} mapping, a sequence of
            (fieldname, default) tuples, an instance of this class,
            or NO_DEFAULT. The default values are used when new instances
            of the record class are instantiated without passing in field
            values. If default is set to NO_DEFAULT, field values must be
            passed in when a new record object is instantiated.
    """
    if defaults == NO_DEFAULT:
        cls._defaults = defaults
        return

    try:
        _ = iter(defaults)
    except TypeError:
        raise TypeError(
            'defaults is not iterable or equal to record.NO_DEFAULT')

    # if defaults is an instance of this class
    if isinstance(defaults, cls):
        cls._defaults = tuple(defaults[:])
        return

    if isinstance(defaults, collections.Mapping):
        if not all([name in defaults for name in cls._fieldnames]):
            raise ValueError(
                "when defaults is a mapping its keys must contain all of "
                "the record's fieldnames")
        cls._defaults = tuple([defaults[name] for name in cls._fieldnames])
        return

    if (not all([isinstance(v, collections.Sequence) for v in defaults])
            or not all(
                [len(v) == 2 and not isinstance(v, str) for v in defaults])):
        raise ValueError(
            'when defaults is a sequence it must contain (fieldname, default-'
            'value) tuples')

    # Must be a sequence of 2-tuples (or other 2-element non-string sequences!)
    fieldnames, default_values = zip(*defaults)
    if not all([name in fieldnames for name in cls._fieldnames]):
        raise ValueError("defaults must contain all of the record's fieldnames")

    _defaults = []
    for fieldname in cls._fieldnames:
        i = fieldnames.index(fieldname)
        _defaults.append(default_values[i])
    cls._defaults = tuple(_defaults)
    return


def __eq__(self, other):
    return (isinstance(other, self.__class__)
        and self.__dict__ == other.__dict__)


def __ne__(self, other):
    return not self.__eq__(other)


def __getitem__(self, index):
    """Retrieve a field or slice of fields from the record.

    Args:
        index: int or slice object
            Index can be an integer or slice object for normal sequence
            item access.
    Returns:
        The value of the field corresponding to the index or a list of values
        corresponding to slice indices.
    """
    if isinstance(index, int):
        return self._attr_getters[index](self)
    else:  # Slice object
        return [getter(self) for getter in self._attr_getters[index]]


def __setitem__(self, index, value):
    """Note: if index is a slice and value is longer than the slice then
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


def __getnewargs__(self):
    """Return self as a plain tuple. Used by copy and pickle."""
    return tuple(self)


def __getstate__(self):
    """Return a picklable object.

    Returns:
        A tuple to allow the __slots__ based object to be pickled.
    """
    return tuple(self)


def __setstate__(self, state):
    """Re-populate the record's attributes with the unpickled tuple."""
    for attr, value in zip(self.__slots__, state):
        setattr(self, attr, value)


def __iter__(self):
    """Iterate over fields."""
    for getter in self._attr_getters:
        yield getter(self)


def _len__(self):
    return len(self.__slots__)


def __repr__(self):
    return '{}({})'.format(
        self.__class__.__name__, ', '.join('{}={}'.format(
            attr, repr(getattr(self, attr))) for attr in self.__slots__))


def __str__(self):
    return '{}({})'.format(
        self.__class__.__name__, ', '.join('{}={}'.format(
            attr, str(getattr(self, attr))) for attr in self.__slots__))


def _asdict(self):
    """Return a new OrderedDict which maps field names to their values."""
    return collections.OrderedDict(
        [(k, getattr(self, k)) for k in self.__slots__])


def _set__dict__(self, dct):
    """Redirect the setting of __dict__ to __slots__"""
    for k, v in dct.items():
        setattr(self, k, v)
