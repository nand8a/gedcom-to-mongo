import unittest
from datetime import datetime

import utils
from elements import Person



class TestFam(unittest.TestCase):


    def test_no_fam(self):
        with self.assertRaises(ValueError):
            obj = Person(['1 CHR'])
            obj._parse_fam()

    def test_fams_only(self):
        obj = Person(['1 FAMS FamilyHere'])
        self.assertEqual(obj._parse_fam(), {'fams': {'FamilyHere'}})

    def test_famc_only(self):
        obj = Person(['1 FAMC FamilyHere'])
        self.assertEqual(obj._parse_fam(), {'famc': {'FamilyHere'}})


    def test_already_populated(self):
        with self.assertRaises(KeyError):
            obj = Person(['1 FAMC FamilyHere'])
            obj._parsed_dict = {'famc': None}
            obj._parse_fam()


    # self.individual._i = 1
        # local_dict = self.individual._parse_chan()
        # self.assertEqual({'chan_date':
        #                   datetime.strptime('13 Sep 2016 20:14:25', '%d %b %Y %H:%M:%S')
        #                   }, local_dict)


class TestChanDate(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.lines = ['0 @I3@ INDI',
                     '1 CHAN',
                     '2 DATE 13 Sep 2016',
                     '3 TIME 20:14:25',
                     '1 NOTE {}'.format(':D'),
                     '0 @I4@ INDI']
        cls.individual = Person(cls.lines)


    # todo move this to it's own test case
    def test_individual_chan(self):
        self.individual._i = 1
        local_dict = self.individual._parse_chan()
        self.assertEqual({'chan_date':
                          datetime.strptime('13 Sep 2016 20:14:25', '%d %b %Y %H:%M:%S')
                          }, local_dict)

    def test_individual_chan_failure(self):
        self.individual._i = 2
        with self.assertRaises(ValueError) as context:
            self.individual._parse_chan()

    # the calls to date are functional - change to isolate # todo
    def test_chan_date(self):
        # todo fix these tests and isolate them as far as possible from an annoying global structure
        # test first next() conditional
        local_individual = Person(['1 CHAN'])
        self.assertEqual({}, local_individual._parse_chan())
        # test second next() conditional
        local_individual = Person(['1 CHAN', '0 @I4@ INDI'])
        self.assertEqual({}, local_individual._parse_chan())
        # test '3 time' conditional
        local_individual = Person(['1 CHAN', '2 DATE 13 Sep 2016', '0 @I4@ INDI'])
        self.assertEqual({'chan_date' : datetime(2016, 9, 13, 0, 0)}, local_individual._parse_chan())
        # test time only
        # test '3 time' conditional
        local_individual = Person(['1 CHAN', '3 TIME 20:14:25', '0 @I4@ INDI'])
        self.assertEqual({'chan_date': {'error': True, 'raw': '20:14:25'}}, local_individual._parse_chan())



class TestBirt(unittest.TestCase):
    """
    explicit test for bug with SOUR tag
    """

    @classmethod
    def setUpClass(cls):

        cls.lines = ['0 @I158@ INDI',
                     '1 NAME Elisabeth Blignaut',
                     '2 SURN Blignaut',
                     '2 GIVN Elisabeth',
                     '1 SEX F',
                     '1 BIRT',
                     '2 DATE ABT 1756',
                     '2 PLAC Paarl',
                     '2 SOUR @S27@',
                     '3 PAGE Hansie Brummer',
                     '1 DEAT',
                     '2 SOUR @S27@',
                     '3 PAGE Hansie Brummer',
                     '1 _UID 8754D1BB8A284FE580409AD7C1BA861D9C86',
                     '0 @I4@ INDI']
        cls.person = Person(cls.lines)
        cls.birt_contents = {'date': {'raw': 'ABT 1756', 'error': True},
                             'plac': 'Paarl',
                             'sour': '@S27@',
                             'page': 'Hansie Brummer'}

        # todo move this test out to utils test

    def test_person_sub(self):
        # test that works correctly after the BIRT key where the line integer value in the
        # file increases in the substructure
        i = 6
        local_dict, res_i = utils.ged_sub_structure(self.lines, i, self.lines[i].split(' ')[0])
        self.assertEqual(self.birt_contents, local_dict)

        i = 11
        local_dict, res_i = utils.ged_sub_structure(self.lines, i, self.lines[i].split(' ')[0])
        self.assertEqual({'sour': '@S27@', 'page': 'Hansie Brummer'}, local_dict)

    def test_person_birt(self):
        self.person._i = 5
        self.assertEqual(self.person._parse_birt(), {'birt': self.birt_contents})

    def test_person_failure(self):
        self.person._i = 6
        with self.assertRaises(ValueError) as context:
            self.person._parse_birt()

    def test_person_birth_exists(self):
        self.person._i = 5
        self.person._parsed_dict = {'_id': 'billybob', 'birt': self.birt_contents}
        self.assertEqual(self.person._parse_birt(), {})

        # make sure that the parser also doesn't do weird stuff here
        # insert another birth
        double_birth = self.lines[0:-1] + ['1 BIRT'] + self.lines[-1:]
        self.assertTrue(double_birth.count('1 BIRT') == 2)  # a check for the list logic
        double_person = Person(double_birth)
        parsed = double_person.parser()
        self.assertEqual(parsed['birt'], self.birt_contents)

class TestPerson(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conc_1 = 'There is plenty of commentary here'
        cls.conc_2 = 'and more here.....'
        cls.lines = [
            '0 @I3@ INDI',  # 0
            '1 NAME Judith /du Plessis/',  # 1
            '2 SURN du Plessis',  # 2
            '2 GIVN Judith',  # 3
            '1 SEX F',  # 4
            '1 BIRT',  # 5
            '2 DATE 1693', #6
            '2 PLAC Ierland',  #7
            '1 _UID 5CB8557F5530F54C8A3A0FB66935E5E09AA6',  #8
            '1 FAMS @F5@',  #9
            '1 FAMS @F4@',  #10
            '1 FAMS @F6@',  #11
            '1 FAMC @F7@',  #12
            '1 CHAN',   #13
            '2 DATE 13 Sep 2016',  #14
            '3 TIME 20:14:25',  #15
            '1 NOTE {}'.format(cls.conc_1),  #16
            '2 CONC {}'.format(cls.conc_2),
            '0 @I4@ INDI'
        ]
        cls.person = Person(cls.lines)

    def test_person_note(self):
        self.person._i = 16
        ret_string = self.person._person_note()
        self.assertEqual(ret_string, '{} {}'.format(self.conc_1, self.conc_2))

    # todo move this test out to utils test
    def test_person_sub(self):
        # test that works correctly after the BIRT key
        i = 6
        local_dict, res_i = utils.ged_sub_structure(self.lines, i, self.lines[i].split(' ')[0])
        self.assertEqual({'DATE'.lower(): datetime(1693, 1, 1, 0, 0),
                          'PLAC'.lower(): 'Ierland'}, local_dict)
        self.assertEqual(res_i, 8)

    # todo fix this - (ah, think it means move to utils tests)
    def test_person_sub_level_1(self):
        # assuming '1 KEY VALUE' returns as ({KEY: VALUE}, int), whilst '1 KEY' returns as ({KEY: None})
        i = 9
        local_dict, res_i = utils.ged_sub_structure(self.lines, i, self.lines[i].split(' ')[0])
        self.assertEqual({'fams': '@F5@'}, local_dict)
        self.assertEqual(res_i, i+1)

        i = 5
        local_dict, res_i = utils.ged_sub_structure(self.lines, i, self.lines[i].split(' ')[0])
        self.assertEqual({'BIRT'.lower(): None}, local_dict)
        self.assertEqual(res_i, i+1)

    def test_person_name(self):
        self.person._i = 1
        expect = {'name': 'Judith du Plessis', 'surn': 'du Plessis', 'givn': 'Judith'}
        local_dict = self.person._person_name()
        self.assertEqual(expect, local_dict)
        # now let's that newlines aren't present
        expect = {'name': 'Judith du Plessis\n'}
        local_person = Person(['1 NAME Judith /du Plessis/'])
        local_dict = local_person._person_name()
        self.assertFalse(local_dict['name'].endswith('\n'))

    def test_is_person(self):

        self.assertTrue(Person.is_person('0 @11111111@ INDI'))
        self.assertFalse(Person.is_person('@11@ INDI'))
        self.assertFalse(Person.is_person('0 @11@ IND'))
        self.assertFalse(Person.is_person(''))

    def test_parser(self):
        # functional test
        parsed_output = {'_id': '@I3@',
                         'name': {
                             'name': 'Judith du Plessis',
                             'surn': 'du Plessis',
                             'givn': 'Judith'},
                         'sex': 'F',
                         'birt': {
                                'date': datetime(1693, 1, 1, 0, 0), 'plac': 'Ierland'},
                         '_uid': '5CB8557F5530F54C8A3A0FB66935E5E09AA6',
                         'fams': {'@F6@', '@F5@', '@F4@'},
                         'famc': '@F7@',
                         'chan_date': datetime(2016, 9, 13, 20, 14, 25),
                         'note': 'There is plenty of commentary here and more here.....'
                         }

        self.person._i = 0
        self.assertEqual(self.person.parser(), parsed_output)


class TestPersonName(unittest.TestCase):

    def test_person_strip_key(self):
        lines = ['1 NAME Anna du Toit']
        obj = Person(lines)
        output = obj._person_name()
        self.assertEqual({'name': 'Anna du Toit'}, output)
