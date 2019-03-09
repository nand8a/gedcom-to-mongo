import unittest
import person
from datetime import datetime


class TestPerson(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
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
            '2 DATE 13 Sep 2016',
            '3 TIME 20:14:25',
            '0 @I4@ INDI'
        ]

    def test_person_chan(self):
        i = 13
        print('test_person')
        print(self.lines)
        local_dict, res_i = person._parse_chan(self.lines, i)
        self.assertEqual({'chan_date':
                          datetime.strptime('13 Sep 2016 20:14:25', '%d %b %Y %H:%M:%S')
                          }, local_dict)
        self.assertEqual(res_i, 16)

    def test_person_sub(self):
        # test that works correctly after the BIRT key
        i = 6
        local_dict, res_i = person._person_sub(self.lines, i, self.lines[i].split(' ')[0])
        self.assertEqual({'DATE'.lower(): '1693', 'PLAC'.lower(): 'Ierland'}, local_dict)
        self.assertEqual(res_i, 8)

    def test_person_sub_level_1(self):
        # assuming '1 KEY VALUE' returns as ({KEY: VALUE}, int), whilst '1 KEY' returns as ({KEY: None})
        i = 9
        local_dict, res_i = person._person_sub(self.lines, i, self.lines[i].split(' ')[0])
        self.assertEqual({'fams': '@F5@'}, local_dict)
        self.assertEqual(res_i, i+1)

        i = 5
        local_dict, res_i = person._person_sub(self.lines, i, self.lines[i].split(' ')[0])
        self.assertEqual({'BIRT'.lower(): None}, local_dict)
        self.assertEqual(res_i, i+1)

