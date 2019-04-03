import unittest
import embedding_person as ep


class TestProcessorP1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_get_spouses(self):
        parents = ['parentA', 'parentB']
        current_parent = parents[0]
        person_record = {'_id': 'parentA'}
        spouses = ep._get_spouses(parents, current_parent, person_record)
        self.assertListEqual(spouses, [parents[1]])

