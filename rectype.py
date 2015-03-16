# Note that the module docstring below contains function descriptions etc.
# because some of the the functions and attributes to be documented
# are added dynamically to a subclass of RecType so is not possible to get
# a reasonable Sphinx generated API doc.
"""
"""

import abc
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
    Return a new ``RecType`` subclass named typename.

    The new subclass is used to create ``RecType`` objects that have
    fields accessible by attribute lookup as well as being indexable
    and iterable. Per-field default values can be set which are assigned
    to fields that are not supplied a value when new instances of the
    subclass are initialised.

    :param typename: Name of the ``RecType`` subclass to create,
        e.g. ``'MyRecord'``.
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
    :raises: ValueError if *typename* is invalid or *fieldnames*
        contains an invalid fieldname and rename is ``False``.

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
    """
    RecType._check_typename(typename)
    if isinstance(fieldnames, collections.Mapping):
        # Convert mapping to a sequence of (fieldname, value) tuples
        fieldnames = list(fieldnames.items())
    elif isinstance(fieldnames, str):
        fieldnames = fieldnames.replace(',', ' ').split()

    fieldnames, defaults = RecType._parse_fieldnames(fieldnames, rename)

    # Create the __dict__ of the Record subclass
    # An operator.attrgetter is stored for each field because it offers
    # a slight speedup over getattr()
    # _fieldnames_set is used to provide fast membership testing
    type_dct = dict(
        __slots__=tuple(fieldnames),
        _fieldnames=tuple(fieldnames),
        _fieldnames_set=frozenset(fieldnames),
        _defaults=defaults,
        _attr_getters=tuple(
            [operator.attrgetter(field) for field in fieldnames])
    )

    rectype = type(typename, (RecType,), type_dct)

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


class RecType(collections.Sequence):
    """
    Base class for new record types. This class is not stand-alone.

    .. note:: To create subclasses of RecType use the :py:func:`rectype.rectype()` factory function.

    ``RecType`` supports the following public methods and attributes. To
    prevent conflicts with fieldnames in subclasses, the method and
    attribute names start with an underscore.

    .. automethod:: _del_defaults
    .. autoattribute:: _fieldnames
    .. automethod:: _get_defaults
    .. automethod:: _update
    .. automethod:: _update_defaults
    .. document private functions
    """

    __slots__ = ()

    #: Tuple of strings listing the fieldnames. Useful for introspection and
    #: creating new record types from existing record types. Should not
    #: be changed directly.
    #:
    #: Example usage::
    #:
    #:     >>> p._fieldnames       # view the fieldnames
    #:     ('x', 'y')
    #:     >>> Point3D = rectype('Point3D', Point._fieldnames + ['z'])
    #:     >>> Point3D(x=1, y=2, z=3)
    #:     Point3D(x=1, y=2, z=3)
    _fieldnames = None

    def __init__(self, *args, **kwargs):
        """
        Return a new ``RecType`` object initialised from an optional positional
        argument and optional keyword arguments:

        | *class* **SomeRecType**\ *(**kwargs)*
        | SomeRecType(mapping, **kwargs)
        | SomeRecType(iterable, **kwargs)

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

        If a default value is not available for a field that has not been
        defined by the positional or keyword arguments a ValueError is
        raised.

        :raises: TypeError if more than one positional argument is passed or
             if *kwargs* contains a keyword that does not match a fieldname.

        """
        if len(args) > 1:
            raise TypeError(
                'expected at most 1 positional argument, got {0}'
                .format(len(args)))
        self._check_kwargs(kwargs)

        # Progressively assemble a dict representation of the record from
        # the field defaults, the positional arg and the keyword args.
        field_values = self._defaults.copy()
        if args:
            arg = args[0]
            if isinstance(arg, collections.Mapping):
                # Can't use update() here because it may not be implemented
                for key in arg:
                    field_values[key] = arg[key]
            else:
                # args should be an iterable so convert it to a mapping
                field_values.update(dict(zip(self._fieldnames, arg)))
        field_values.update(kwargs)

        self._check_all_fields_defined(field_values)

        for fieldname, value in field_values.items():
            setattr(self, fieldname, value)

    def _update(self, *args, **kwargs):
        """
        Update the field values of the record with values from an optional
        positional argument and a possibly empty set of keyword arguments.

        :param *args: Optional positional argument which can be a mapping of
            fieldname/field_value pairs or an iterable of field values which
            are in the same order as the fieldnames in the ``_fieldnames``
            class attribute.
        :param **kwargs: Keyword arguments in which each keyword must match a
            fieldname of the record. Keyword arguments can be supplied on their
            own, or together with the positional argument.

        Example::

            >>> Rec = rectype('Rec', 'a b c')
            >>> r = Rec(a=1, b=2, c=3)
            >>> r._update(b=5, c=6)     # using keyword arguments
            >>> r
            Rec(a=1, b=2, c=3)
            >>> r._update([2, 3], c=4)  # using an iterable and keyword arguments
            >>> r
            Rec(a=2, b=3, c=4)
        """
        if len(args) > 1:
            raise TypeError(
                'expected at most 1 positional argument, got {0}'
                .format(len(args)))
        self._check_kwargs(kwargs)

        # TODO: can this be made faster? e.g. by setattr the positionals
        # then setattr the kwargs? In general use, kwargs probably won't
        # repeat many of the fields from the positionsls.

        # Progressively assemble a dict representation of the record update
        # from the positional arg and the keyword args.
        field_values = {}
        if args:
            arg = args[0]
            if isinstance(arg, collections.Mapping):
               # Can't use update() here because it may not be implemented
                for key in arg:
                    field_values[key] = arg[key]
            else:
                # arg should be an iterable
                field_values.update(zip(self._fieldnames, arg))
        field_values.update(kwargs)

        for fieldname, value in field_values.items():
            setattr(self, fieldname, value)

    @classmethod
    def _get_defaults(cls):
        """
        Return a dict which maps fieldname to their corresponding
        default_values. If no default values are set an empty dict is returned.
        """
        return cls._defaults

    @classmethod
    def _update_defaults(cls, *args, **kwargs):
        """
        Update default field values of the record with values from an optional
        positional argument and a possibly empty set of keyword arguments.

        :param *args: Optional positional argument which can be a mapping of
            fieldname/default_value pairs or an iterable of default values
            which are in the same order as the fieldnames in the
            ``_fieldnames`` class attribute.
        :param **kwargs: Keyword arguments in which each keyword must match a
            fieldname of the record. Keyword arguments can be supplied on their
            own, or together with the positional argument.

        Example::

            >>> Rec = rectype('Rec', [('a', 1), ('b', 2), 'c')
            >>> Rec._get_defaults()
            {'a': 1, 'b': 2}
            >>> Rec._update_defaults([3, 4], c=5)
            >>> # the default for field 'a' and 'b' is replaced and a new
            >>> # default for field 'c' is added
            >>> Rec._get_defaults()
            {'a': 3, 'b': 4, 'c': 5}
        """
        if len(args) > 1:
            raise TypeError(
                'expected at most 1 positional argument, got {0}'
                .format(len(args)))
        cls._check_kwargs(kwargs)

        # Progressively assemble a dict representation of the default update
        # from the positional arg and the keyword args.
        defaults = {}
        if args:
            arg = args[0]
            if isinstance(arg, collections.Mapping):
                for key in arg:
                    defaults[key] = arg[key]
            else:
                # arg should be an iterable
                defaults.update(zip(cls._fieldnames, arg))
        defaults.update(kwargs)
        cls._check_fieldnames_exist(defaults)

        cls._defaults.update(defaults)

    @classmethod
    def _check_fieldname(cls, fieldname, used_names, rename, idx):
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
            cls._common_name_check(fieldname, 'field')
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

    @classmethod
    def _check_typename(cls, typename):
        """
        Raise a ValueError if typename is invalid.
        """
        cls._common_name_check(typename, 'type')

    @staticmethod
    def _common_name_check(name, nametype):
        """
        Perform check common to both typenames and fieldnames.
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

    @classmethod
    def _parse_fieldnames(cls, fieldnames, rename):
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

            fieldname = cls._check_fieldname(fieldname, used_names, rename, idx)
            checked_fieldnames.append(fieldname)
            used_names.add(fieldname)
            if has_default:
                defaults[fieldname] = default
        return checked_fieldnames, defaults

    @classmethod
    def _check_fieldnames_exist(cls, fieldnames):
        """
        Raise a ValueError if a fieldname does not exist in cls._fieldnames.
        """
        for fieldname in fieldnames:
            if fieldname not in cls._fieldnames:
                raise ValueError('field {0!r} is not defined')

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
    def _check_kwargs(cls, kwargs):
        """
        Check that every keyword argument in kwargs matches a fieldname. If
        a keyword does not match a fieldname a ValueError is raised.
        """
        for fieldname in kwargs:
            if fieldname not in cls._fieldnames_set:
                raise TypeError(
                    'keyword argument {0!r} does not match a field'
                    .format(fieldname))

    @classmethod
    def _del_defaults(cls, fieldnames):
        """
        Remove the default values for one or more fields.

        :param fieldnames: Fieldnames of the default values to be removed. Can
            be a single string with each fieldname separated by whitespace
            and/or commas such as ``'x, y'``, or an iterable of strings.
        """
        if isinstance(fieldnames, str):
            fieldnames = fieldnames.replace(',', ' ').split()

        for fieldname in fieldnames:
            try:
                cls._defaults.pop(fieldname)
            except ValueError:
                raise KeyError('field {0!r} is not defined')

        cls._defaults = {
            k: v for k, v in cls._defaults.items() if k not in fieldnames}

    @property
    def __dict__(self):
        """
        Return a new ``OrderedDict`` which maps fieldnames to their values.
        """
        return collections.OrderedDict(
            [(k, getattr(self, k)) for k in self.__slots__])

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

    def __iter__(self):
        """
        Iterate over fields.
        """
        for getter in self._attr_getters:
            yield getter(self)

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
