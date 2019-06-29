import unittest
import elements
from datetime import datetime


class TestFamily(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fam_id = '@F2628@'
        cls.lines = [
            "0 {} FAM".format(cls.fam_id),
            "1 _UID D87E88660DD8564B9820B9A149F0E2A39AD9",
            "1 HUSB @I6862@",
            "1 WIFE @I6856@",
            "1 CHIL @I16809@",
            "1 MARR",
            "2 DATE 17 Feb 1833",
            "2 PLAC Graaff - Reinet"
        ]

    def test_family(self):
        obj = elements.Family(self.lines)
        local_dict = obj.parser()
        self.assertEqual({"_id": "{}".format(self.fam_id),
                          "_uid": "D87E88660DD8564B9820B9A149F0E2A39AD9",
                          "husb": "@I6862@",
                          "wife": "@I6856@",
                          "chil": ["@I16809@"],
                          "marr": {"date": datetime(1833, 2, 17, 0, 0, 0),
                                   "plac": "Graaff - Reinet"}
                          }, local_dict)

    # def test_children(self):
    #     lines = ['1 CHIL @I1@', '1 CHIL @I2@']  # todo harden with regex
    #     res_list = family.Family(lines)._children()
    #     print(res_list)
    #     self.assertEqual(['@I1@', '@I2@'], res_list)

#
# def _children(lines, i):
#     children_list = []
#     while i < len(lines) and '1 CHIL' in lines[i]:
#         children_list.append(lines[i].split(' ')[2:])
#         i += 1
#     return children_list
