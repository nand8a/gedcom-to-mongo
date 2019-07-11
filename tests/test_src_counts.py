import unittest
from datatests.src_counts import _count, count_subs
from io import StringIO


class TestSrcCounts(unittest.TestCase):

    def test_counts_success(self):
        self.assertEqual(1, _count(0, 'item a'))
        self.assertEqual(['item a'], _count([], 'item a'))

    def test_counts_failure(self):
        with self.assertRaises(TypeError):
            _count('a', 60)  # same for None, or any other incompatible type


class TestCountSub(unittest.TestCase):

    def setUp(self):
        self.fh = StringIO()

    def tearDown(self):
        self.fh.close()

    def test_success_trivial_fixed_key(self):
        self.fh.write('0 @I1@ INDI\n1 DEAT\n2 DATE 10 Nov 2020\n2 PLAC Mars')
        self.fh.seek(0)
        # death and date occur
        self.assertEqual(count_subs(self.fh, key='DEAT', sub_key='DATE', counting_obj=0), 1)
        self.fh.seek(0)
        # death and plac occur
        self.assertEqual(count_subs(self.fh, key='DEAT', sub_key='PLAC', counting_obj=0), 1)
        # only death count
        self.fh.seek(0)
        self.assertEqual(count_subs(self.fh, key='DEAT', counting_obj=0), 1)
        # make sure the list returns too
        self.fh.seek(0)
        self.assertEqual(count_subs(self.fh, key='DEAT', counting_obj=[]), ['0 @I1@ INDI'])

    def test_success_no_count(self):
        # no death
        self.fh.write('0 @I1@ INDI\n1 SOME other stuff\n2 MORE other stuff')
        self.assertEqual(count_subs(self.fh, key='DEAT', counting_obj=0), 0)

    def test_nested_sub_key(self):
        self.fh.write('0 @I1@ INDI\n1 BIRT\n1 DEAT\n2 DATE 10 Nov 2020\n2 PLAC Mars')
        self.fh.seek(0)
        self.assertEqual(count_subs(self.fh, key='BIRT', sub_key='DATE', counting_obj=0), 0)
        self.fh.seek(0)
        self.assertEqual(count_subs(self.fh, key='BIRT', sub_key='BLES', counting_obj=0), 0)
        self.fh.seek(0)
        self.assertEqual(count_subs(self.fh, key='DEAT', sub_key='DATE', counting_obj=0), 1)
        self.fh.seek(0)
        self.assertEqual(count_subs(self.fh, key='DEAT', sub_key='PLAC', counting_obj=0), 1)


