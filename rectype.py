"""
Create custom record classes with mutable field values.

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


def rectype(typename, fieldnames, rename=False):
        """
        Return a new Record subclass named typename.

        The new subclass is used to create record objects that have fields
        accessible by attribute lookup as well as being indexable and
        iterable.

        Args:
            typename: string
                Name of the Record subclass class to create, e.g. 'MyRecord'.
            fieldnames: various (see below)
                Fieldnames can be any of the following:
                * Single string with each fieldname separated by whitespace
                  and/or commas such as 'x, y'.
                * A sequence of strings such as ['x', 'y'] and/or 2-tuples of
                  the form (fieldname, default-value) such as
                  [('x', None), ('y', None)].
                * An mapping of fieldname-default value pairs such as
                  dict(x=None, y=None). Note that it only makes sense to use
                  an ordered mapping (e.g. OrderedDict) since access by
                  index or iteration is affected by the order of the
                  fieldnames.
                A fieldname may be any valid Python identifier except for
                names starting with an underscore.
            rename: boolean
                If rename is True, invalid fieldnames are automatically replaced
                with positional names. For example, ('abc', 'def', 'ghi', 'abc')
                is converted to ('abc', '_1', 'ghi', '_3'), eliminating the
                keyword 'def' and the duplicate fieldname 'abc'.
        Returns:
            A subclass of Record named typename.
        Raises:
            ValueError:
                If typename is invalid.
                If a fieldname is invalid and rename is False.
        """
        Record._check_typename(typename)
        if isinstance(fieldnames, collections.Mapping):
            # Convert mapping to a sequence of (fieldname, value) tuples
            fieldnames = list(fieldnames.items())
        elif isinstance(fieldnames, str):
            fieldnames = fieldnames.replace(',', ' ').split()

        fieldnames, defaults = Record._parse_fieldnames(fieldnames, rename)

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
                [operator.attrgetter(field) for field in fieldnames]),
        )

        rectype = type(typename, (Record,), type_dct)

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


class Record(collections.Sequence):
    """
    Base class for record types.
    """

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        """
        Return a new record initialised from an optional positional
        argument and optional keyword arguments:

        Rec(**kwargs)
        Rec(mapping, **kwargs)
        Rec(iterable, **kwargs)

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
        if one has been defined in the _defaults class attribute of the
        record-type.

        If a default value is not available for a field that has not been
        defined by the positional or keyword arguments a ValueError is
        raised.

        Raises:
            TypeError:
             If more than one positional argument is passed.
             If kwargs contains a keyword that does not match a fieldname.
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
            if isinstance(args[0], collections.Mapping):
                field_values.update(args[0])
            else:
                # args[0] should be an iterable so convert it to a mapping
                field_values.update(dict(zip(self._fieldnames, args[0])))
        field_values.update(kwargs)

        self._check_all_fields_defined(field_values)

        for fieldname, value in field_values.items():
            setattr(self, fieldname, value)

    def _update(self, *args, **kwargs):
        """
        Update fields with new values.

        somerec._update(**kwargs)
        somerec._update(mapping, **kwargs)
        somerec._update(iterable, **kwargs)

        See the __init__ for a full description of args and kwargs.
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
            if isinstance(args[0], collections.Mapping):
                field_values.update(args[0])
            else:
                # args[0] should be an iterable
                field_values.update(zip(self._fieldnames, args[0]))
        field_values.update(kwargs)

        for fieldname, value in field_values.items():
            setattr(self, fieldname, value)

    @classmethod
    def _update_defaults(cls, *args, **kwargs):
        """
        Update the default field values.

        somerec._update_defaults(**kwargs)
        somerec._update_defaults(mapping, **kwargs)
        somerec._update_defaults(iterable, **kwargs)
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
            if isinstance(args[0], collections.Mapping):
                defaults.update(args[0])
            else:
                # args[0] should be an iterable
                defaults.update(zip(cls._fieldnames, args[0]))
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
        Remove the default value for one or more fieldnames

        Args:
            fieldnames: string or iterable of strings
                Fieldname(s) whose default value is to be removed.
        """
        if isinstance(fieldnames, str):
            fieldnames = [fieldnames]
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
        Return a new OrderedDict which maps fieldnames to their values.
        """
        return self._asdict()

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

    def _asdict(self):
        """
        Return a new OrderedDict which maps fieldnames to their values.
        """
        return collections.OrderedDict(
            [(k, getattr(self, k)) for k in self.__slots__])


Rec = rectype('Rec', ['a', 'b', ('c', 3)])
rec = Rec([0], a=1, b=2)
print(rec)