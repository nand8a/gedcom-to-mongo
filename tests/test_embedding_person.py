import unittest
import embedding_person as ep
from unittest import mock
from unittest.mock import MagicMock


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

        with self.assertRaises(Exception) as context:
            ep._get_spouses(['A', 'B', 'C'], 'D', person_record)


    # todo this test is not satisfactory - must be integration test
    @mock.patch('pymongo.collection.Collection')
    def test_update_children(self, coll):
        coll.find_one = MagicMock()
        coll.find_one.return_value = []
        parents = ['A', 'B']
        children = ['a', 'b']
        # todo modify the code to separate the mongo write so unittest easier
        # we can check what the mongo function was called with, but that seems
        ep._update_children(coll, parents, children)
        # other conditional
        coll.find_one.return_value = ['C']
        ep._update_children(coll, parents, children)
