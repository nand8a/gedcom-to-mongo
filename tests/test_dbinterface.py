from unittest.mock import Mock
from unittest.mock import MagicMock
import unittest
from unittest import mock
from dbinterface import *
import pymongo


class test(unittest.TestCase):

    def tearDown(self) -> None:
        MongoConnector().destroy()

    @mock.patch('pymongo.MongoClient')
    def test_connect(self, mock_mongo):
        # todo, we can use mongo directly
        obj = MongoConnector().connect('localhost', 27027)
        self.assertIsInstance(obj, MongoConnector)

        mock_mongo.side_effect = Exception()
        with self.assertRaises(Exception):
            MongoConnector().connect('meh', 1)

        # print(obj._connection)

    def test_connection(self):
        obj = MongoConnector()
        with self.assertRaises(ValueError):
            obj.connection()

        obj._connection = object
        obj.connection()
