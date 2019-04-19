from unittest.mock import Mock
from unittest.mock import MagicMock
import unittest
from unittest import mock
from dbinterface import *


class TestConnector(unittest.TestCase):

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


class TestMongoDb(unittest.TestCase):

    def test_constructor_failure(self):
        # test if either db connection of collection connection exception
        # is handled by checking the latter only
        dconnector = MagicMock()
        coll = MagicMock()
        coll.__getitem__.side_effect = ValueError()
        dconnector.connection.__getitem__.return_value = coll

        with self.assertRaises(ValueError):
            MongoDb(dconnector, 'db_name', 'db_coll')

    # todo replace with integration test
    def test_constructor_success(self):
        MongoDb(MagicMock(), 'db_name', 'db_coll')

