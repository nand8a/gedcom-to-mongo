import unittest
import utils
from datetime import datetime


class TestDate(unittest.TestCase):

    def test_date_fmt(self):
        date_in = 1999
        date_alpha = datetime(date_in, 1, 1, 0, 0)
        date_beta = utils.get_date(str(date_in))
        self.assertEqual(date_alpha, date_beta)

        date_in = '23 Jan 1700'
        date_alpha = datetime(1700, 1, 23)
        self.assertEqual(utils.get_date(date_in), date_alpha)

    def test_date_negative(self):
        self.assertEqual(None, utils.get_date('123'))


class TestDateDictionary(unittest.TestCase):

    def test_date_positive(self):
        date_in = 1999
        key = 'my_date'
        date_alpha = {key: datetime(date_in, 1, 1, 0, 0)}
        self.assertEqual(date_alpha, utils.get_date_dictionary(key, str(date_in)))

        date_in = 'Feb 2017 19:43:36'
        date_alpha = {key: datetime(2017, 2, 1, 19, 43, 36)}
        self.assertEqual(date_alpha, utils.get_date_dictionary(key, date_in))

    def test_date_negative(self):
        date_in = 'not a real date'
        key = 'my_date'
        date_alpha = {key: {'raw': date_in, 'error': True}}
        self.assertEqual(date_alpha, utils.get_date_dictionary(key, str(date_in)))
