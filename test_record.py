
import pickle
import unittest

import record

Rec = record.make_recordtype('Rec', ['a', 'b'])


class RecordTestCase(unittest.TestCase):


    def setUp(self):
        #self.Rec = record.make_recordtype('Rec', ['a', 'b'])
        self.rec = Rec([1, 2])

    def test_contains(self):
        self.assertEqual(1 in self.rec, True)
        self.assertEqual(2 in self.rec, True)
        self.assertEqual(3 in self.rec, False)

    def test_instantiation_with_sequence(self):
        self.assertEqual(self.rec.a, 1)
        self.assertEqual(self.rec.b, 2)

    def test_instantiation_with_mapping(self):
        rec = Rec(dict(a=1, b=2))
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)

    def test_instantiation_with_invalid_mapping(self):
        # A mapping whose keys do not contain all the fieldnames
        # should raise an AttributeError
        with self.assertRaises(ValueError):
            rec = Rec(dict(a=1, c=2))

    def test_instantiation_with_string(self):
        # Strings are iterable so each character should be assigned to the
        # corresponding field
        rec = Rec('12')
        self.assertEqual(rec.a, '1')
        self.assertEqual(rec.b, '2')

    def test_instantiation_with_too_few_values(self):
        with self.assertRaises(ValueError):
            rec = Rec([1])

    def test_instantiation_with_more_values_than_fields(self):
        # When instantiating a record with more values than there are
        # fields, the surplus values should be ignored without raising
        # an error
        rec = Rec([1, 2, 3])
        self.assertEqual(rec.a, 1)
        self.assertEqual(rec.b, 2)

    def test_creation_with_more_than_256_fields(self):
        fieldnames = ['f{0}'.format(i) for i in range(1000)]
        R = record.make_recordtype('R', fieldnames)
        rec = R(list(range(1000)))
        self.assertEqual(rec.f0, 0)
        self.assertEqual(rec.f999, 999)

    def test_fieldname_starting_with_underscore(self):
        with self.assertRaises(ValueError):
            R = record.make_recordtype('R', ['a', '_b'])

    def test_duplicate_fieldnames(self):
        with self.assertRaises(ValueError):
            R = record.make_recordtype('R', ['a', 'a'])

    def test_non_string_typename_and_fieldname(self):
        with self.assertRaises(TypeError):
            R = record.make_recordtype([1], ['a', 'b'])
        with self.assertRaises(TypeError):
            R = record.make_recordtype('R', ['a', [1]])

    def test_keyword_typename_and_fieldname(self):
        with self.assertRaises(ValueError):
            R = record.make_recordtype('for', ['a', 'b'])
        with self.assertRaises(ValueError):
            R = record.make_recordtype('R', ['a', 'for'])

    def test_non_alphanumeric_typename_and_fieldname(self):
        with self.assertRaises(ValueError):
            R = record.make_recordtype('-R', ['a', 'b'])
        with self.assertRaises(ValueError):
            R = record.make_recordtype('R', ['a', '-b'])

    def test_typename_and_fieldname_starting_with_number(self):
        with self.assertRaises(ValueError):
            R = record.make_recordtype('1R', ['a', 'b'])
        with self.assertRaises(ValueError):
            R = record.make_recordtype('R', ['1a', 'b'])

    def test_rename(self):
        # Use some invalid fieldnames and check that they are renamed
        # appropriately
        # [keyword, evaluates to not, digit, starts with underscore]
        fieldnames = ['for', 'None', '1', '_']
        R = record.make_recordtype('R', fieldnames, rename=True)
        for i, fieldname in enumerate(fieldnames):
            self.assertEqual(R._fieldnames[i], '_{0}'.format(i))

        # Test that duplicate fieldname is renamed
        fieldnames = ['a', 'a']
        R = record.make_recordtype('R', fieldnames, rename=True)
        self.assertEqual(R._fieldnames[1], '_1')

    def test_index(self):
        self.assertEqual(self.rec.index(2), 1)

    def test_count(self):
        R = record.make_recordtype('R', ['a', 'b', 'c'])
        rec = R([1, 2, 2])
        self.assertEqual(rec.count(1), 1)
        self.assertEqual(rec.count(2), 2)

    # def test_next(self):
    #     self.assertEqual(next(self.rec), 1)

    def test_reverse_iteration(self):
        reverse_iterator = reversed(self.rec)
        self.assertEqual(next(reverse_iterator), 2)
        self.assertEqual(next(reverse_iterator), 1)

    def test_set_value_after_instantiation(self):
        self.rec.a = 'a'
        self.assertEqual(self.rec.a, 'a')
        self.assertEqual(self.rec.b, 2)
        self.rec.a = 3
        self.rec.b = 4
        self.assertEqual(self.rec.a, 3)
        self.assertEqual(self.rec.b, 4)

    def test_attribute_not_defined_in__slots__(self):
        with self.assertRaises(AttributeError):
            _ = self.rec.c
        with self.assertRaises(AttributeError):
            self.rec.c = 3

    def test_pickle(self):
        # Note: Only classes defined at the top level of a module can be
        # pickled, hence the use of Rec here.
        rec = Rec([1, 2])
        for protocol in 0, 1, 2, 3:
            s = pickle.dumps(rec, protocol)
            pickled_rec = pickle.loads(pickle.dumps(rec, protocol))
            self.assertEqual(rec, pickled_rec)
            self.assertEqual(rec._fieldnames, pickled_rec._fieldnames)

    def test___dict__(self):
        # These assertions are necessary because record uses __slots__
        # to store attributes rather than a per-instance __dict__. To
        # allow __dict__ to reflect the record attributes a class
        # __dict__ property which calls record._asdict() when it is
        # accessed.
        self.assertEqual(self.rec.__dict__, {'a': 1, 'b': 2})
        self.assertEqual(vars(self.rec), {'a': 1, 'b': 2})

    def test___eq__(self):
        rec = Rec([1, 2])
        self.assertEqual(rec, self.rec)

    def test___ne__(self):
        rec = Rec([1, 3])
        self.assertNotEqual(rec, self.rec)

    def test_field_order(self):
        # Checks that the order in which fields are specified in the
        # fields argument of the constructor are preserved in __slots__
        fields = (
            ['field_b', 'field_d', 'field_c', 'field_f', 'field_e', 'field_a'])
        Rec = record.make_recordtype('Rec', fields)
        rec = Rec(list(range(len(fields))))
        self.assertEqual(rec.field_b, 0)
        self.assertEqual(rec.field_d, 1)
        self.assertEqual(rec.field_c, 2)
        self.assertEqual(rec.field_f, 3)
        self.assertEqual(rec.field_e, 4)
        self.assertEqual(rec.field_a, 5)

    def test___getitem__(self):
        R = record.make_recordtype('R', ['a', 'b', 'c', 'd'])
        rec = R([1, 2, 3, 4])

        # Test access by numerical index
        self.assertEqual(self.rec[0], 1)

        # Test slicing
        slice = rec[:3]
        self.assertEqual(slice, [1, 2, 3])

        # Test that passing an non-int/str/slice object raises a TypeError
        with self.assertRaises(TypeError):
            slice = rec[object]

        # A value outside the set of indexes for the sequence should
        # raise an IndexError
        with self.assertRaises(IndexError):
            _ = rec[99999]

    def test___setitem__(self):
        R = record.make_recordtype('R', ['a', 'b', 'c', 'd', 'e'])
        rec = R([1, 2, 3, 4, 5])

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

    def test_iteration(self):
        self.assertEqual([value for value in self.rec], [1, 2])

    def test___repr__(self):
        self.rec.a = '1'
        self.assertEqual(repr(self.rec), "Rec(a='1', b=2)")

    def test___str__(self):
        self.rec.a = '1'
        self.assertEqual(str(self.rec), "Rec(a=1, b=2)")

if __name__ == '__main__':
    unittest.main()