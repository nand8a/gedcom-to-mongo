import unittest
from datatests.src_counts import _count, get_death
from io import StringIO


class TestSrcCounts(unittest.TestCase):

    def test_counts_success(self):
        self.assertEqual(1, _count(0, 'item a'))
        self.assertEqual(['item a'], _count([], 'item a'))

    def test_counts_failure(self):
        with self.assertRaises(TypeError):
            _count('a', 60)  # same for None, or any other incompatible type



# def get_death(filename, sub_key=None,):
#     """
#     get a death and date for each individual, there could be a 'PLAC' interspersed
#     :param filename: the source filename we are testing against
#     :return: a single integer count, or a list of individuals for debugging purposes
#     """
#     with open(filename, 'r', encoding='utf-8-sig') as f:
#         for line in f:
#             if bool(re.search('0 @[A-Z0-9]*@ INDI', line)):
#                 indi = line.replace('\n', '')
#             line = f.readline()
#             while not line.startsWith('0'):
#                 if bool(re.search('^[0-9] {}$'.format(sub_key), line)):
#                     _count(counting_obj, indi)
#                     break
#                 line = f.readline()
#     return counting_obj

class TestGetDeath(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.fh = StringIO()  # the filehandler/buffer
        cls.fh.write('0 @I1@ INDI\n1 DEAT\n2 DATE 10 Nov 2020\n2 PLAC Mars')

    def setUp(self):
        self.fh.seek(0)

    # todo decouple this from the _count fellow
    def test_success_trivial(self):
        # death and date occur
        self.assertEqual(get_death(self.fh, sub_key='DEAT', counting_obj=0), 1)
        self.fh.seek(0)
        # death and plac occur
        self.assertEqual(get_death(self.fh, sub_key='PLAC', counting_obj=0), 1)
        # only death count
        self.fh.seek(0)
        self.assertEqual(get_death(self.fh, counting_obj=0), 1)
        # no death
        fh = StringIO()
        fh.write('0 @I1@ INDI\n1 SOME other stuff\n2 MORE other stuff')
        self.assertEqual(get_death(self.fh, counting_obj=0), 0)
        # make sure the list returns too
        self.fh.seek(0)
        self.assertEqual(get_death(self.fh, counting_obj=[]), ['0 @I1@ INDI'])