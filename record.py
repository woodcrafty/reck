"""
Similar to namedtuple, but is writable and is not limited to 256 fields.

TODO:
Finish/polish docstrings
Add _set___dict__ to the __dict__ property?

Add url to setup.py
Add test option to setup.py
Create Git repo
Clone to GitHub

Test on all versions of Python 3x
"""

import collections
import keyword
import operator
import sys

__license__ = 'BSD 3-clause'
__version__ = '0.1.0'
__author__ = 'Mark Richards'
__email__ = 'mark.l.a.richardsREMOVETHIS@gmail.com'


def make_type(typename, fieldnames, rename=False):
    """Make a custom record class.

    Class factory for creating a custom record class with attributes
    corresponding to the names given in the fieldnames argument. The
    custom record class is used to create record objects with mutable
    fields that are accessible by attribute lookup or by index, and are
    iterable. There is no restriction on the number of fields, unlike
    named tuples which are limited to 255 fields.

    Record objects do not have per-instance dictionaries. They store
    attributes in __slots__, so they are lightweight, requiring one
    less byte of memory than an equivalent tuple or namedtuple. However,
    this means that instances of record objects cannot be assigned new
    fields/attributes not listed in the custom record class definition.

    Args:
        typename: str
            Name of the record-like class to create, e.g. 'MyRecord'.
        fieldnames: sequence of strings
            Names of the fields in the record, e.g. ['name', 'age'].
            Any valid Python identifier may be used as a fieldname,
            except for names starting with an underscore.
        rename: logical
            If rename is True, invalid fieldnames are automatically replaced
            with positional names. For example, ('abc', 'def', 'ghi', 'abc')
            is converted to ('abc', '_1', 'ghi', '_3'), eliminating the
            keyword def and the duplicate fieldname abc.
    Returns:
        A custom record class.
    """
    if rename:
        used_names = set()
        for i, name in enumerate(fieldnames):
            if (not all(c.isalnum() or c == '_' for c in name)
                    or keyword.iskeyword(name)
                    or not name
                    or name[0].isdigit()
                    or name.startswith('_')
                    or name in used_names):
                fieldnames[i] = '_{0}'.format(i)
            used_names.add(name)

    for name in [typename] + fieldnames:
        if not isinstance(name, str):
            raise TypeError('Type names and fieldnames must be strings')
        if not all(c.isalnum() or c == '_' for c in name):
            raise ValueError(
                'Type names and fieldnames can only contain alphanumeric '
                'characters and underscores: {0!r}'.format(name))
        if keyword.iskeyword(name):
            raise ValueError(
                'Type names and fieldnames cannot be a keyword: {0!r}'.format(
                    name))
        if name[0].isdigit():
            raise ValueError(
                'Type names and fieldnames cannot start with a number: {0!r}'
                .format(name))

    used_names = set()
    for name in fieldnames:
        if name.startswith('_') and not rename:
            raise ValueError(
                'Fieldnames cannot start with an underscore: {0!r}'.format(
                    name))
        if name in used_names:
            raise ValueError(
                'Encountered duplicate fieldname: {0!r}'.format(name))
        used_names.add(name)

    # _attr_getters is included because operator.attrgetter offers a
    # slight speed up over using getattr()
    dct = dict(
        __slots__=tuple(fieldnames),
        _fieldnames=tuple(fieldnames),
        _attr_getters=[operator.attrgetter(field) for field in fieldnames],
        __init__=__init__,
        # Allow __dict__ to reflect __slots__
        __dict__=property(_get__dict__),
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


def __init__(self, values):
    """Make a new instance from an existing sequence or mapping.

    Args:
        values: iterable
            Values with which to populate the record. The values should be
            in the same order as _fieldnames, unless it is a mapping,
            in which case the keys are used to identify the fields.
    """
    try:
        _ = iter(values)
    except TypeError:
        raise TypeError('values is not iterable')

    # If values is a mapping then use the keys for attribute lookup
    if (isinstance(values, collections.Mapping) or
            (hasattr(values, 'keys') and hasattr(values, '__getitem__'))):
        # The mapping's keys should be a superset of _fieldnames.
        # Keys that do not match a fieldname are ignored.
        if all([name in values for name in self._fieldnames]):
            for k, v in values.items():
                try:
                    setattr(self, k, v)
                except AttributeError:
                    # The keys of the values mapping is allowed to be a
                    # superset of _fieldnames, so Attribute Errors are
                    # allowed.
                    pass
        else:
            raise ValueError(
                "when values is a mapping its keys must contain all of"
                "the record's fieldnames")
    else:
        if len(values) < len(self.__slots__):
            raise ValueError('Too few items in values')
        for attr, value in zip(self.__slots__, values):
            setattr(self, attr, value)


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
    """
    if isinstance(index, int):
        return self._attr_getters[index](self)
    else:  # Slice object
        return [getter(self) for getter in self._attr_getters[index]]


def __setitem__(self, index, value):
    """
    TODO: Should slice support be removed? Because the number of fields
    is immutable, list-style slice behaviour cannot be supported - see
    below:

    Note: if index is a slice and value is longer than the slice then
    the surplus values are discarded. This behaviour differs from that
    of list.__setitem__ which inserts the surplus values into the list.
    Similarly, if value contains too few values, the surplus fields are
    left unaffected. With a list, the surplus items are deleted.

    Args:
        index: int or slice object
            Index/slice to be set.
        value: anything
            Value to set.
    """
    if isinstance(index, int):
        return setattr(self, self.__slots__[index], value)
    else:  # Slice object
        fields = self.__slots__[index]
        return [setattr(self, field, v) for field, v in zip(fields, value)]


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


def _get__dict__(self):
    """Return an OrderedDict which maps field names to their values.

    This function is used internally to provide a dictionary
    representation of the attributes when __dict__ is called.
    This enables the vars() built-in to return a dict even
    though the record's attributes are stored in __slots__.
    """
    return collections.OrderedDict(
        [(k, getattr(self, k)) for k in self.__slots__])


def _set__dict__(self, dct):
    """Redirect the setting of __dict__ to __slots__"""
    for k, v in dct.items():
        setattr(self, k, v)
