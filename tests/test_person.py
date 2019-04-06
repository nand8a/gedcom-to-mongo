import unittest
from elements import Person
from datetime import datetime
import utils


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

    def test_person_chan(self):
        self.person._i = 13
        local_dict = self.person._parse_chan()
        self.assertEqual({'chan_date':
                          datetime.strptime('13 Sep 2016 20:14:25', '%d %b %Y %H:%M:%S')
                          }, local_dict)

    # todo move this test out to utils test
    def test_person_sub(self):
        # test that works correctly after the BIRT key
        i = 6
        local_dict, res_i = utils.ged_sub_structure(self.lines, i, self.lines[i].split(' ')[0])
        self.assertEqual({'DATE'.lower(): datetime(1693, 1, 1, 0, 0),
                          'PLAC'.lower(): 'Ierland'}, local_dict)
        self.assertEqual(res_i, 8)

    # todo fix this
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
        expect = {'name': 'Judith /du Plessis/', 'surn': 'du Plessis', 'givn': 'Judith'}
        local_dict = self.person._person_name()
        self.assertEqual(expect, local_dict)


class TestPersonName(unittest.TestCase):

    def test_person_strip_key(self):
        lines = ['1 NAME Anna /du Toit/']
        obj = Person(lines)
        output = obj._person_name()
        self.assertEqual({'name': 'Anna /du Toit/'}, output)
