import unittest
import ingest


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
            '2 DATE 1693',
            '2 PLAC Ierland',
            '1 _UID 5CB8557F5530F54C8A3A0FB66935E5E09AA6',
            '1 FAMS @F5@',
            '1 FAMS @F4@',
            '1 FAMS @F6@',
            '1 FAMC @F7@',
            '1 CHAN',
            '2 DATE 13 Sep 2016',
            '3 TIME 20:14:25',
            '0 @I4@ INDI'
        ]

    def test_person_sub(self):
        # test that works correctly after the BIRT key
        i = 6
        local_dict, res_i = ingest._person_sub(self.lines, i, self.lines[i].split(' ')[0])
        self.assertEqual({'DATE'.lower(): '1693', 'PLAC'.lower(): 'Ierland'}, local_dict)
        self.assertEqual(res_i, 8)

    def test_person_sub_level_1(self):
        # assuming '1 KEY VALUE' returns as ({KEY: VALUE}, int), whilst '1 KEY' returns as ({KEY: None})
        i = 9
        local_dict, res_i = ingest._person_sub(self.lines, i, self.lines[i].split(' ')[0])
        self.assertEqual({'fams': '@F5@'}, local_dict)
        self.assertEqual(res_i, i+1)

        i = 5
        local_dict, res_i = ingest._person_sub(self.lines, i, self.lines[i].split(' ')[0])
        self.assertEqual({'BIRT'.lower(): None}, local_dict)
        self.assertEqual(res_i, i+1)

