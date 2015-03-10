"""
Create custom record classes that have mutable field values.

TODO:
Confirm docstring examples are correct.
"""

import collections
import keyword
import operator
import sys

__license__ = 'BSD 3-clause'
__version__ = '0.0.0'
__author__ = 'Mark Richards'
__email__ = 'mark.l.a.richardsREMOVETHIS@gmail.com'


class BaseRecord(collections.Sequence):
    """Base class for record types"""

    __slots__ = ()

    @classmethod
    def _maketype(cls, typename, fieldnames, defaults):
        type_dct = dict(
            __slots__=tuple(fieldnames),
            _fieldnames=tuple(fieldnames),
            _defaults=defaults,
            _attr_getters=tuple(
                [operator.attrgetter(field) for field in fieldnames]),
        )
        record_type = type(typename, (cls,), type_dct)
        # For pickling to work, the __module__ variable needs to be set to the
        # frame where the record type is created.  Bypass this step in
        # environments where sys._getframe is not defined (Jython for example)
        # or sys._getframe is not defined for arguments greater than 0
        # (e.g. IronPython).
        #record_type.__module__ = _get_client_module_name()
        #record_type.__module__ = '__main__'
        # try:
        #     record_type.__module__ = sys._getframe(2).f_globals.get(
        #         '__name__', '__main__')
        # except (AttributeError, ValueError):
        #     pass
        record_type.__module__ = _get_client_module_name()
        # This suggestion from
        # http://stackoverflow.com/questions/13624603/python-how-to-register-dynamic-class-in-module

        return record_type


    @classmethod
    def _check_fieldname(cls, fieldname, used_names, rename, idx):
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
        cls._common_name_check(typename, 'type')

    @classmethod
    def _parse_fieldnames(cls, fieldnames, rename):
        # Process fieldnames sequence, creating a list of corrected fieldnames
        # and a map of fieldnames to default values.
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

    @staticmethod
    def _common_name_check(name, nametype):
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
    def _del_defaults(cls, fieldnames):
        """Remove the default value for one or more fieldnames

        Args:
            fieldnames: string or sequence of strings
                Fieldname(s) whose default value is to be removed.
        """
        if isinstance(fieldnames, str):
            fieldnames = [fieldnames]
        cls._defaults = {
            k: v for k, v in cls._defaults.items() if k not in fieldnames}

    @property
    def __dict__(self):
        return self._asdict()

    # @__dict__.setter
    # def __dict__(self):
    #     """Redirect the setting of __dict__ to __slots__"""
    #     for k, v in dct.items():
    #         setattr(self, k, v)

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
        # Slice object
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

    # def __getnewargs__(self):
    #     """Return self as a plain tuple. Used by copy and pickle."""
    #     return tuple()

    def __getstate__(self):
        """Return self as a picklable object (a tuple).

        Returns:
            A tuple to allow the __slots__ based object to be pickled.
        """
        return tuple(self)
        #return tuple(getattr(self, name) for name in self._fieldnames)

    def __setstate__(self, state):
        """Re-populate the record's attributes with the unpickled tuple."""
        for attr, value in zip(self.__slots__, state):
            setattr(self, attr, value)

    def __iter__(self):
        """Iterate over fields."""
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
        """Return a new OrderedDict which maps field names to their values."""
        return collections.OrderedDict(
            [(k, getattr(self, k)) for k in self.__slots__])

    # def _set__dict__(self, dct):
    #     """Redirect the setting of __dict__ to __slots__"""
    #     for k, v in dct.items():
    #         setattr(self, k, v)


class Record(BaseRecord):
    """
    Base class for custom record types.
    """
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        """Initialise a new instance from positional and keyword arguments.

        Field values can be passed by positional and/or keyword arguments.
        Positional arguments should be provided in the same order as the
        fields in the record type.
        """
        self._check_field_value_args(args, kwargs)

        # Check that a value has been defined for every field
        field_values = self._defaults.copy()
        field_values.update(dict(zip(self._fieldnames, args)))
        field_values.update(kwargs)
        for fieldname in self._fieldnames:
            if fieldname not in field_values:
                raise ValueError('field {0!r} is not defined')

        for fieldname, value in field_values.items():
            setattr(self, fieldname, value)

    @classmethod
    def _maketype(cls, typename, fieldnames, rename=False):
        """
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
        cls._check_typename(typename)
        if isinstance(fieldnames, collections.Mapping):
            # Convert mapping to a sequence of (fieldname, value) tuples
            fieldnames = list(fieldnames.items())
        elif isinstance(fieldnames, str):
            fieldnames = fieldnames.replace(',', ' ').split()

        fieldnames, defaults = cls._parse_fieldnames(fieldnames, rename)

        return super()._maketype(typename, fieldnames, defaults)


    def _update(self, *args, **kwargs):
        """Update the record with positional and/or keyworda arguments.

        Args:
            *args: positional arguments
                Positional arguments are used to provide field values by
                field position/order.
            **kwargs: keyword arguments
                Keyword arguments are used to provide field values by
                fieldname.
        """
        self._check_field_value_args(args, kwargs)

        field_values = dict(zip(self._fieldnames, args))
        field_values.update(kwargs)
        for fieldname, value in field_values.items():
            setattr(self, fieldname, value)

    @classmethod
    def _update_defaults(cls, *args, **kwargs):
        cls._check_field_value_args(args, kwargs)

        # Check that a value has been defined for every field
        defaults = cls._defaults.copy()
        defaults.update(dict(zip(cls._fieldnames, args)))
        defaults.update(kwargs)
        for fieldname in defaults.keys():
            if fieldname not in cls._fieldnames:
                raise ValueError('field {0!r} is not defined')
        cls._defaults = defaults

    @classmethod
    def _check_field_value_args(
            cls, values_by_field_order, values_by_fieldname):
        """
        Check that the number of positional args does not exceed the
        number of fields and that only one value has been supplied per field.
        """
        # Check that there are not more positional args than there are fields
        if len(values_by_field_order) > len(cls._fieldnames):
            raise TypeError(
                'takes up to {0} positional arguments but {1} were given'
                .format(len(cls._fieldnames), len(values_by_field_order)))

        # Check that only one value has been supplied per field.
        fields_with_values = set(cls._fieldnames[:len(values_by_field_order)])
        for fieldname in fields_with_values:
            if fieldname in values_by_fieldname:
                raise TypeError(
                    'got multiple values for field {0!r}'.format(fieldname))


    # # This getter and setter is required because you can't use @property and
    # # @setter._defaults on a class method
    # @classmethod
    # def _get_defaults(cls):
    #     """Get a tuple of the default field values."""
    #     return cls._defaults
    #
    # @classmethod
    # def _set_defaults(cls, defaults):
    #     """Set the default field values for new instances of the record class.
    #
    #     Args:
    #         defaults: mapping, sequence of 2-tuples, class instance or NO_DEFAULT
    #             Can be a {fieldname: default} mapping, a sequence of
    #             (fieldname, default) tuples, an instance of this class,
    #             or NO_DEFAULT. The default values are used when new instances
    #             of the record class are instantiated without passing in field
    #             values. If default is set to NO_DEFAULT, field values must be
    #             passed in when a new record object is instantiated.
    #     """
    #     if defaults == NO_DEFAULT:
    #         cls._defaults = defaults
    #         return
    #
    #     try:
    #         _ = iter(defaults)
    #     except TypeError:
    #         raise TypeError(
    #             'defaults is not iterable or equal to record.NO_DEFAULT')
    #
    #     if isinstance(defaults, cls):
    #         cls._defaults = tuple(defaults[:])
    #         return
    #
    #     if isinstance(defaults, collections.Mapping):
    #         if not all([name in defaults for name in cls._fieldnames]):
    #             raise ValueError(
    #                 "when defaults is a mapping its keys must contain all of "
    #                 "the record's fieldnames")
    #         cls._defaults = tuple([defaults[name] for name in cls._fieldnames])
    #         return
    #
    #     if (not all([isinstance(v, collections.Sequence) for v in defaults])
    #             or not all(
    #                 [len(v) == 2 and not isinstance(v, str) for v in defaults])):
    #         raise ValueError(
    #             'when defaults is a sequence it must contain (fieldname, '
    #             'default) tuples')
    #
    #     # Must be a sequence of 2-tuples (or other 2-element non-string sequences!)
    #     fieldnames, default_values = zip(*defaults)
    #     if not all([name in fieldnames for name in cls._fieldnames]):
    #         raise ValueError("defaults must contain all of the record's fieldnames")
    #
    #     _defaults = []
    #     for fieldname in cls._fieldnames:
    #         i = fieldnames.index(fieldname)
    #         _defaults.append(default_values[i])
    #     cls._defaults = tuple(_defaults)
    #     return


class LongRecord(BaseRecord):
    """
    Base class for long record types (records that can have more than
    255 fields).
    """

    __slots__ = ()

    def __init__(self, values):
        """Initialise a new instance from positional and keyword arguments.
        """
        if instance(values, collections.Sequence):
            values = dict(zip(seld._fieldnames, values))

        # Check that a value has been defined for every field
        field_values = self._defaults.copy()
        field_values.update(values)
        for fieldname in self._fieldnames:
            if fieldname not in defined_fields:
                raise ValueError('field {0!r} is not defined')

        for fieldname, value in field_values.items():
            setattr(self, fieldname, value)

    @classmethod
    def _maketype(cls, typename, fieldnames, rename=False):
        """
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
        cls._check_typename(typename)
        if isinstance(fieldnames, collections.Mapping):
            # Convert mapping to a sequence of (fieldname, value) tuples
            fieldnames = list(fieldnames.items())
        elif isinstance(fieldnames, str):
            fieldnames = fieldnames.replace(',', ' ').split()

        fieldnames, defaults = cls._parse_fieldnames(fieldnames, rename)

        return super()._maketype(typename, fieldnames, defaults)



def _get_client_module_name():
    client_module_name = None
    for stack_index in range(1, 5):
        frame = sys._getframe(stack_index)
        module_name = frame.f_globals.get('__name__')
        if module_name != __name__:
            client_module_name = module_name
            break

    assert client_module_name, 'Could not find name of module using Record'
    return client_module_name

# Rec = Record._maketype('Rec', ['a', 'b'])
# rec = Rec(1, b=2)
# print(rec)
# rec._update(b=9)
# print(rec)
# print()
# Rec = Record._maketype('Rec', collections.OrderedDict(a=None, b=None))
# rec = Rec()
# print(rec)
# rec._update(b=9)
# print(rec)

# import pickle
# Rec = Record._maketype('Rec', ['a', 'b'])
# print(Rec.__module__)
# rec = Rec(1, 2)
# for protocol in 0, 1:  #, 2, 3:
#     _ = pickle.dumps(rec, protocol)
#     pickled_rec = pickle.loads(_)
#     #pickled_rec = pickle.loads(pickle.dumps(rec, protocol))
#     assert(rec == pickled_rec)


