
from collections import OrderedDict
import pickle
from sys import version_info
import unittest

import rectype

Rec = rectype.rectype('Rec', ['a', 'b'])


class TestDefaultFactory(unittest.TestCase):

    def test_call(self):
        # With no args
        df = rectype.DefaultFactory(list)
        self.assertEqual(df(), [])
        df = rectype.DefaultFactory(dict)
        self.assertEqual(df(), {})

        # With an arg
        df = rectype.DefaultFactory(list, args=[(1, 2, 3)])
        self.assertEqual(df(), [1, 2, 3])
        df = rectype.DefaultFactory(dict, args=[[('a', 1), ('b', 2)]])
        self.assertEqual(df(), {'a': 1, 'b': 2})

        # With kwargs
        df = rectype.DefaultFactory(dict, kwargs={'a': 1, 'b': 2})
        self.assertEqual(df(), {'a': 1, 'b': 2})

        # With args and kwargs
        df = rectype.DefaultFactory(
            dict, args=[[('a', 1)]], kwargs={'b': 2, 'c': 3})
        self.assertEqual(df(), {'a': 1, 'b': 2, 'c': 3})

    def test_repr(self):
        # no args/kwargs
        df = rectype.DefaultFactory(list)
        self.assertEqual(
            repr(df), 'DefaultFactory({0!r}, args=(), kwargs={{}})'.format(list))

        # with an arg
        df = rectype.DefaultFactory(list, args=([1, 2],))
        self.assertEqual(
            repr(df),
            'DefaultFactory({0!r}, args=([1, 2],), kwargs={{}})'.format(list))
        # multiple args
        df = rectype.DefaultFactory(list, args=(1,2))
        self.assertEqual(
            repr(df),
            'DefaultFactory({0!r}, args=(1, 2), kwargs={{}})'.format(list))

        # with args & kwargs
        kwargs = dict(b=2, c=3)
        df = rectype.DefaultFactory(
            dict, args=[[('a', 1)]], kwargs=kwargs)
        self.assertEqual(
            repr(df),
            "DefaultFactory({0!r}, args=[[('a', 1)]], "
                "kwargs={1!r})".format(dict, kwargs))


class TestRecType(unittest.TestCase):
    # ==========================================================================
    # Test record type creation

    def test_rectype_with_sequence(self):
        # Simple sequence
        Rec = rectype.rectype('Rec', ['a', 'b'])
        rec = Rec(1, 2)
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)

        # Sequence of 2-tuples
        Rec = rectype.rectype('Rec', [('a', None), ('b', None)])
        rec = Rec(1, 2)
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)

        # Simple sequence with some 2-tuples
        Rec = rectype.rectype('Rec', ['a', ('b', None)])
        rec = Rec(1, 2)
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)

        # String sequence
        Rec = rectype.rectype('Rec', 'a b,c, d')
        rec = Rec(1, 2, 3, 4)
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)
        self.assertEqual(rec.c, 3)
        self.assertEqual(rec.d, 4)
        Rec = rectype.rectype('Rec', 'ab')
        rec = Rec(1)
        self.assertEqual(rec.ab, 1)

        # With DefaultFactory with no args/kwargs
        Rec = rectype.rectype('Rec', ['a', ('b', rectype.DefaultFactory(list))])
        rec1 = Rec(a=1)
        rec2 = Rec(a=1)
        self.assertEqual(rec1.a, 1)
        self.assertEqual(rec1.b, [])
        rec1.b.append(2)
        rec1.b.append(3)
        self.assertEqual(rec1.b, [2, 3])
        # Check rec2 doesn't share the list with rec1
        self.assertEqual(rec2.b, [])

        # With DefaultFactory with args
        Rec = rectype.rectype('Rec', [
            ('a', rectype.DefaultFactory(list, args=[[1, 2]]))])
        rec1 = Rec()
        rec2 = Rec()
        self.assertEqual(rec1.a, [1, 2])
        rec1.a.append(3)
        self.assertEqual(rec1.a, [1, 2, 3])
        # Check rec2 doesn't share the list with rec1
        self.assertEqual(rec2.a, [1, 2])

        # With DefaultFactory with kwargs
        kwargs = {'a': 1}
        Rec = rectype.rectype('Rec', [
            ('a', rectype.DefaultFactory(dict, kwargs=kwargs))])
        rec1 = Rec()
        rec2 = Rec()
        self.assertEqual(rec1.a, kwargs)
        rec1.a['b'] = 2
        self.assertEqual(rec1.a, {'a': 1, 'b': 2})
        # Check rec2 doesn't share the list with rec1
        self.assertEqual(rec2.a, kwargs)

        # With DefaultFactory with args and kwargs
        args = [[('a', 1), ('b', 2)]]
        kwargs = {'c': 3}
        dct = dict(*args, **kwargs)
        Rec = rectype.rectype('Rec', [
            ('a', rectype.DefaultFactory(dict, args=args, kwargs=kwargs))])
        rec1 = Rec()
        rec2 = Rec()
        self.assertEqual(rec1.a, dct)
        rec1.a['d'] = 4
        # Check rec2 doesn't share the list with rec1
        self.assertEqual(rec2.a, dct)
        dct.update(d=4)
        self.assertEqual(rec1.a, dct)

    def test_rectype_with_mapping(self):
        # Use lots of fields to check that field order is preserved
        nfields = 50
        fieldnames = ['f{0}'.format(i) for i in range(nfields)]
        tuples = [(name, None) for name in fieldnames]
        Rec = rectype.rectype('Rec', OrderedDict(tuples))
        rec = Rec(*list(range(nfields)))
        for i in range(nfields):
            self.assertEqual(rec[i], i)
            fieldname = 'f{0}'.format(i)
            self.assertEqual(getattr(rec, fieldname), i)

    def test_rectype_with_bad_sequence(self):
        with self.assertRaises(ValueError):
            # 3-tuple instead of 2-tuple
            Rec = rectype.rectype('Rec', [('a', 1, 2)])
            # 1-tuple instead of 2-tuple
            Rec = rectype.rectype('Rec', [('a',)])

    def test_rectype_with_defaults(self):
        Rec = rectype.rectype('Rec', dict(a=1))
        rec = Rec()
        self.assertEqual(rec.a, 1)

        Rec = rectype.rectype('Rec', [('a', 1), 'b', ('c', 3)])
        rec = Rec(b=2)
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)
        self.assertEqual(rec.c, 3)

    def test_rectype_with_default_factory(self):
        # default factory with no args/kwargs
        Rec = rectype.rectype('Rec', ['a', ('b', rectype.DefaultFactory(list))])
        rec1 = Rec(a=1)
        rec2 = Rec(a=1)
        self.assertEqual(rec1.a, 1)
        self.assertEqual(rec1.b, [])
        rec1.b.append(2)
        rec1.b.append(3)
        self.assertEqual(rec1.b, [2, 3])
        self.assertNotEqual(rec1.b, rec2.b)
        self.assertEqual(rec2.b, [])

        # default factory with args
        Rec = rectype.rectype('Rec', [
            'a',
            ('b', rectype.DefaultFactory(list, args=([1, 2],)))])
        rec1 = Rec(a=1)
        rec2 = Rec(a=1)
        self.assertEqual(rec1.a, 1)
        self.assertEqual(rec1.b, [1, 2])
        rec1.b.append(3)
        self.assertEqual(rec1.b, [1, 2, 3])
        self.assertNotEqual(rec1.b, rec2.b)
        self.assertEqual(rec2.b, [1, 2])

        # default factory with kwargs
        Rec = rectype.rectype('Rec', [
            'a',
            ('b', rectype.DefaultFactory(dict, kwargs=dict(val1=1, val2=2)))])
        rec1 = Rec(a=1)
        rec2 = Rec(a=1)
        self.assertEqual(rec1.a, 1)
        self.assertEqual(rec1.b, {'val1': 1, 'val2': 2})
        rec1.b['val3'] = 3
        self.assertEqual(rec1.b, dict(val1=1, val2=2, val3=3))
        self.assertNotEqual(rec1.b, rec2.b)
        self.assertEqual(rec2.b, dict(val1=1, val2=2))

        # default factory with args and kwargs
        Rec = rectype.rectype('Rec', [
            'a',
            ('b', rectype.DefaultFactory(
                dict, args=([('val1', 1)],), kwargs=dict(val2=2)))])
        rec1 = Rec(a=1)
        rec2 = Rec(a=1)
        self.assertEqual(rec1.a, 1)
        self.assertEqual(rec1.b, {'val1': 1, 'val2': 2})
        rec1.b['val3'] = 3
        self.assertEqual(rec1.b, dict(val1=1, val2=2, val3=3))
        self.assertNotEqual(rec1.b, rec2.b)
        self.assertEqual(rec2.b, dict(val1=1, val2=2))

    def test_bad_typename(self):
        with self.assertRaises(ValueError):
            # Typename is a keyword
            R = rectype.rectype('for', ['a', 'b'])

            # Typename with a leading digit
            R = rectype.rectype('1R', ['a', 'b'])

            # Typename contains a non alpha-numeric/underscore character
            R = rectype.rectype('R-', ['a', 'b'])

    def test_bad_fieldname(self):
        with self.assertRaises(ValueError):
            # Duplicate fieldname
            R = rectype.rectype('R', ('a', 'a', 'b', 'a'))

            # Fieldname with leading underscore
            R = rectype.rectype('R', ('a', '_b'))

            # Fieldname is a keyword
            R = rectype.rectype('R', ('a', 'for'))

            # Fieldname with a leading digit
            R = rectype.rectype('R', ('a', '1b'))

            # Fieldname contains a non alpha-numeric character/underscore char
            R = rectype.rectype('R', ('a', 'b!'))

    def test_rename(self):
        # Duplicate fieldname
        R = rectype.rectype('R', ('a', 'a', 'b', 'a'), rename=True)
        self.assertEqual(R._fieldnames, ('a', '_1', 'b', '_3'))

        # Fieldname with leading underscore
        R = rectype.rectype('R', ('a', '_b'), rename=True)
        self.assertEqual(R._fieldnames, ('a', '_1'))

        # Fieldname is a keyword
        R = rectype.rectype('R', ('a', 'for'), rename=True)
        self.assertEqual(R._fieldnames, ('a', '_1'))

        # Fieldname with a leading digit
        R = rectype.rectype('R', ('a', '1b'), rename=True)
        self.assertEqual(R._fieldnames, ('a', '_1'))

        # Fieldname contains a non alpha-numeric chanacter/underscore char
        R = rectype.rectype('R', ('a', 'b!'), rename=True)
        self.assertEqual(R._fieldnames, ('a', '_1'))

        # Multiple rename required
        R = rectype.rectype(
            'R', ('a', 'a', 'b!', 'c', 'for'), rename=True)
        self.assertEqual(R._fieldnames, ('a', '_1', '_2', 'c', '_4'))

        # Rename should not break anything when all fieldnames are valid
        R = rectype.rectype('R', ('a', 'b', 'c'), rename=True)
        self.assertEqual(R._fieldnames, ('a', 'b', 'c'))

        # Rename with defaults
        R = rectype.rectype('R', [('_a', 1), ('b!', 2)], rename=True)
        r = R()
        self.assertEqual(r._0, 1)
        self.assertEqual(r._1, 2)

    def test_field_order(self):
        # Checks that the order in which fields are specified in the
        # fields argument of the constructor are preserved in __slots__
        fields = (
            ['field_b', 'field_d', 'field_c', 'field_f', 'field_e', 'field_a'])
        Rec = rectype.rectype('Rec', fields)
        rec = Rec(*list(range(len(fields))))
        self.assertEqual(rec.field_b, 0)
        self.assertEqual(rec.field_d, 1)
        self.assertEqual(rec.field_c, 2)
        self.assertEqual(rec.field_f, 3)
        self.assertEqual(rec.field_e, 4)
        self.assertEqual(rec.field_a, 5)

    # ==========================================================================
    # Test initialisation

    def test_init_with_args(self):
        rec = Rec(1, 2)
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)

    def test_init_with_kwargs(self):
        rec = Rec(a=1, b=2)
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)

    def test_init_with_args_and_kwargs(self):
        rec = Rec(1, b=2)
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)

    def test_init_with_unpacked_args_and_kwargs(self):

        # Unpacked sequence
        rec = Rec(*[1, 2])
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)

        # Unpacked rectyp
        rec1 = Rec(1, 2)
        rec2 = Rec(*rec1)
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)

        # Unpacked sequence and keyword arg
        rec = Rec(*[1], b=2)
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)

        # Unpacked mapping
        rec = Rec(**dict(a=1, b=2))
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)

        # Unpacked sequence and mapping
        rec = Rec(*[1], **dict(b=2))
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)

    def test_init_with_bad_values(self):
        with self.assertRaises(ValueError):
            # Initialisation without a value when there are no defaults
            rec = Rec()

        with self.assertRaises(TypeError):
            # Initialisation with too many positional arguments
            rec = Rec(1, 2, 3)

            # Initialisation with a non-existent kwarg
            rec = Rec(1, c=2)

    def test_init_with_duplicate_fields(self):
        # The last field value is the one that the field gets initialised too

        # With args and kwargs
        rec = Rec(1, 2, a=5)
        self.assertEqual(rec.a, 5)

        # # With unpacked mapping and kwargs
        # rec = Rec(**dict(a=1, b=2), a=5)
        # self.assertEqual(rec.a, 5)

    def test_init_with_more_than_255_fields(self):
        nfields = 5000
        fieldnames = ['f{0}'.format(i) for i in range(nfields)]
        values = [i for i in range(nfields)]
        kwargs = {k: v for k, v in zip(fieldnames, values)}

        # With values unpacked to positional arguments
        Rec = rectype.rectype('Rec', fieldnames)
        rec = Rec(*values)
        self.assertEqual(rec.f0, 0)
        self.assertEqual(getattr(rec, 'f{0}'.format(nfields - 1)),  nfields - 1)

        # With values unpacked to keyword arguments
        Rec = rectype.rectype('Rec', fieldnames)
        rec = Rec(**kwargs)
        self.assertEqual(rec.f0, 0)
        self.assertEqual(rec.f0, 0)
        self.assertEqual(getattr(rec, 'f{0}'.format(nfields - 1)),  nfields - 1)

    # ==========================================================================
    # Test getting and setting of defaults

    def test_get_defaults(self):
        Rec = rectype.rectype('Rec', ['a', ('b', 2), ('c', 3)])
        self.assertEqual(Rec._get_defaults(), dict(b=2, c=3))

    def test_set_defaults(self):
        Rec = rectype.rectype('Rec', ['a', ('b', 2), ('c', 3)])
        self.assertEqual(Rec._get_defaults(), dict(b=2, c=3))
        Rec._set_defaults(dict(a=1, b=2))
        self.assertEqual(Rec._get_defaults(), dict(a=1, b=2))

        # Non-existent fieldname in defaults dict
        with self.assertRaises(ValueError):
            Rec._set_defaults(dict(a=1, d=4))

    # ==========================================================================
    # Test sequence features

    def test_contains(self):
        rec = Rec(1, 2)
        self.assertTrue(1 in rec)
        self.assertTrue(2 in rec)
        self.assertFalse(3 in rec)

    def test_index(self):
        rec = Rec(1, 2)
        self.assertEqual(rec.index(2), 1)
        R = rectype.rectype('R', 'a b c d')
        rec = R(1, 2, 2, 3)
        self.assertEqual(rec.index(2), 1)  # 1st occurrence of 2
        self.assertEqual(rec.index(3), 3)

    def test_count(self):
        R = rectype.rectype('R', 'a b c')
        rec = R(1, 2, 2)
        self.assertEqual(rec.count(1), 1)
        self.assertEqual(rec.count(2), 2)

    def test_reverse_iteration(self):
        rec = Rec(1, 2)
        reverse_iterator = reversed(rec)
        self.assertEqual(next(reverse_iterator), 2)
        self.assertEqual(next(reverse_iterator), 1)

    def test_iteration(self):
        rec = Rec(1, 2)
        self.assertEqual([value for value in rec], [1, 2])

    # ==========================================================================
    # Test getting and setting field values

    def test_set_value_by_attribute(self):
        rec = Rec(1, 2)
        rec.a = 'a'
        self.assertEqual(rec.a, 'a')
        self.assertEqual(rec.b, 2)
        rec.a = 3
        rec.b = 4
        self.assertEqual(rec.a, 3)
        self.assertEqual(rec.b, 4)

    def test_get_attribute_not_defined_in_slots(self):
        rec = Rec(1, 2)
        with self.assertRaises(AttributeError):
            _ = rec.c

    # Version 3.2 seems to have a bug whereby assignment to an attribute that
    # doesn't exist does NOT throw an Exception of any kind. After the
    # assignment rec does not contain the attribute assigned too.
    @unittest.skipIf(
        version_info.major == 3 and version_info.minor == 2,
        'Python 3.2 does not throw an Exception when assigning to an attribute'
        'that does not exist in a slots based object.')
    def test_set_attribute_not_defined_in_slots(self):
        rec = Rec(1, 2)
        with self.assertRaises(AttributeError):
            rec.c = 3

    def test_getitem(self):
        R = rectype.rectype('R', ['a', 'b', 'c', 'd'])
        rec = R(1, 2, 3, 4)

        # Test access by numerical index
        self.assertEqual(rec[0], 1)

        # Test slicing
        slice = rec[:3]
        self.assertEqual(slice, [1, 2, 3])
        slice = rec[:3:2]
        self.assertEqual(slice, [1, 3])

        # Test that passing an non-int/str/slice object raises a TypeError
        with self.assertRaises(TypeError):
            slice = rec[object]

        # A value outside the set of indexes for the sequence should
        # raise an IndexError
        with self.assertRaises(IndexError):
            _ = rec[99999]

    def test_setitem(self):
        R = rectype.rectype('R', ['a', 'b', 'c', 'd', 'e'])
        rec = R(1, 2, 3, 4, 5)

        # Test __setitem__ by numerical index
        rec[0] = 99
        self.assertEqual(rec.a, 99)

        # Test __setitem__ by slice with correct number of values
        rec[2:] = [101, 102, 103]
        self.assertEqual(rec.c, 101)
        self.assertEqual(rec.d, 102)
        self.assertEqual(rec.e, 103)

        # Test __setitem__ by slice with too many values
        rec[:2] = [1000, 1001, 1002]
        self.assertEqual(rec.a, 1000)
        self.assertEqual(rec.b, 1001)
        self.assertEqual(rec.c, 101)  # Should remain unchanged

        # Test __setitem__ by slice with too few values
        rec[:2] = [2000]
        self.assertEqual(rec.a, 2000)
        self.assertEqual(rec.b, 1001)
        self.assertEqual(rec.c, 101)  # Should remain unchanged

    def test_update(self):
        rec = Rec(1, 2)

        # With positional sequence
        rec._update(3)
        self.assertEqual(rec.a, 3)

        # With keyword arg
        rec._update(a=5)
        self.assertEqual(rec.a, 5)

        # With positional and keyword arg
        rec._update(6, b=7)
        self.assertEqual(rec.a, 6)
        self.assertEqual(rec.b, 7)

        # With 2 kwargs
        rec._update(b=9, a=8)
        self.assertEqual(rec.a, 8)
        self.assertEqual(rec.b, 9)

        # With unpacked mapping
        rec._update(**dict(a=4))
        self.assertEqual(rec.a, 4)

        # With unpacked sequence
        rec._update(*[3, 4])
        self.assertEqual(rec.a, 3)
        self.assertEqual(rec.b, 4)

    def test__dict__(self):
        # These assertions are necessary because record uses __slots__
        # to store attributes rather than a per-instance __dict__. To
        # allow __dict__ to reflect the record __dict__ has been set to
        # a read-only property that returns an OrderedDict of the fields.
        rec = Rec(1, 2)
        self.assertIsInstance(rec.__dict__, OrderedDict)
        self.assertEqual(rec.__dict__, {'a': 1, 'b': 2})

        # Test that vars() works
        self.assertEqual(vars(rec), {'a': 1, 'b': 2})

        # Test that dict is read-only
        with self.assertRaises(AttributeError):
            rec.__dict__ = {'a': 3, 'b': 4}

    # ==========================================================================
    # Miscellaneous tests

    def test_items(self):
        rec = Rec(1, 2)
        items = rec._items()
        self.assertEqual(items, [('a', 1), ('b', 2)])

    def test_pickle(self):
        # Note: Only classes defined at the top level of a module can be
        # pickled, hence the use of Rec here.
        rec = Rec(1, 2)
        for protocol in 0, 1, 2, 3:
            pickled_rec = pickle.loads(pickle.dumps(rec, protocol))
            self.assertEqual(rec, pickled_rec)
            self.assertEqual(rec._fieldnames, pickled_rec._fieldnames)

    def test_equality(self):
        rec1 = Rec(1, 2)
        rec2 = Rec(1, 2)
        self.assertEqual(rec1, rec2)
        rec3 = Rec(**dict(b=2, a=1))
        self.assertEqual(rec1, rec3)
        rec4 = Rec(b=2, a=1)
        self.assertEqual(rec1, rec4)

    def test_inequality(self):
        rec1 = Rec(1, 2)
        rec2 = Rec(2, 1)
        rec3 = Rec(1, 3)
        self.assertNotEqual(rec1, rec2)
        self.assertNotEqual(rec1, rec3)

    def test_repr(self):
        rec = Rec('1', 2)
        self.assertEqual(repr(rec), "Rec(a='1', b=2)")

    def test_str(self):
        rec = Rec('1', 2)
        self.assertEqual(str(rec), "Rec(a=1, b=2)")


if __name__ == '__main__':
    unittest.main()