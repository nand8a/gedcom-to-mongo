import unittest
import embedding_person as ep
from unittest import mock
from unittest.mock import MagicMock, call



class TestProcessorP1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_get_spouses(self):
        parents = ['parentA', 'parentB']
        current_parent = parents[0]
        spouses = ep._get_spouses(parents, current_parent, {})
        self.assertListEqual(spouses, [parents[1]])

        # currently exceptioning on more than one spouse
        with self.assertRaises(Exception) as context:
            ep._get_spouses(['A', 'B', 'C'], 'D', {})

        # let's assume there are already spouses there
        self.assertListEqual(['parentB', 'parentC'],
                             ep._get_spouses(parents, current_parent, {'spouses': ['parentC']}))

    def test_update_parent(self):
        children_count = 2
        spouses = ['A', 'B']
        married_count = 1
        response = {'married_count': married_count,
                    'children_count': children_count,
                    'spouses': spouses}
        self.assertDictEqual(response, ep._get_update_parent_dict({}, children_count, spouses))

        # now test where they are already in the dictionary
        spouses = spouses + ['C', 'D']  # we currently pass it through to the dict builder
        response_2 = {'married_count': married_count + 1,
                      'children_count': children_count + 2,
                      'spouses': spouses}
        self.assertDictEqual(response_2, ep._get_update_parent_dict(response, children_count, spouses))

    def test_get_parents_from_family(self):
        in_dict = {'husb': 'husbandA', 'wife': 'wifeA'}
        self.assertListEqual(['husbandA', 'wifeA'], ep._get_parents_from_family(in_dict))

        self.assertListEqual(['meh'], ep._get_parents_from_family({'wife': 'meh'}))
        self.assertListEqual(['meh'], ep._get_parents_from_family({'husb': 'meh'}))
        self.assertListEqual([], ep._get_parents_from_family({}))

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

    # functional test to rule them all
    def test_processor_with_children(self):
        family_coll = MagicMock()
        person_coll = MagicMock()
        record_1 = {
            "_id": "id",
            "husb": "A",
            "wife": "B",
            "chil": [
                "AB1",
                "AB2",
                "AB3"
            ]}

        # person_coll.read_person - to return the desired value as if hitting mongo
        def c(child_id):
            children = {'AB1': {'_id': 'AB1'},
                        'AB2': {'_id': 'AB2', 'parents': ['C']},
                        'AB3': {'_id': 'AB3'}}
            return children[child_id]
        person_coll.read_person = c

        family_coll.read_unprocessed.return_value = iter([record_1])
        ep.processor(family_coll, person_coll)
        expected_calls_to_person = [
            call('A', {'married_count': 1, 'children_count': 3, 'spouses': ['B']}),
            call('B', {'married_count': 1, 'children_count': 3, 'spouses': ['A']}),
            call('AB1', {'parents': ['A', 'B']}),
            call('AB2', {'parents': ['A', 'B', 'C']}),
            call('AB3', {'parents': ['A', 'B']})
        ]
        person_coll.write_update.assert_has_calls(expected_calls_to_person, any_order=True)

    def test_processor_with_no_children(self):
        family_coll = MagicMock()
        person_coll = MagicMock()
        record_1 = {
            "_id": "id",
            "husb": "A",
            "wife": "B"}

        family_coll.read_unprocessed.return_value = iter([record_1])
        ep.processor(family_coll, person_coll)
        expected_calls_to_person = [
            call('A', {'married_count': 1, 'children_count': 0, 'spouses': ['B']}),
            call('B', {'married_count': 1, 'children_count': 0, 'spouses': ['A']}),
        ]
        person_coll.write_update.assert_has_calls(expected_calls_to_person, any_order=True)

