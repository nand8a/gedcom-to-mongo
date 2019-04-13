import logging
log = logging.getLogger(__name__)
from pymongo import MongoClient
from abc import ABC, abstractmethod
# from typing import *


class DataConnector(ABC):

    __instance = None

    def __new__(cls, *args, **kwargs):
        if DataConnector.__instance is None:
            DataConnector.__instance = object.__new__(cls)
        return DataConnector.__instance

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def connect(self, host, port):
        """
        create connection
        :param host: hostname
        :param port: port number
        :return: this object
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def connection(self):
        raise NotImplementedError()


class MongoConnector(DataConnector):

    def __init__(self):
        super(MongoConnector, self).__init__()

    @property
    def connection(self):
        if not self._connection:
            raise ValueError('connection not initialised')
        else:
            return self._connection

    def connect(self, host, port):
        self.host = host
        self.port = port
        try:
            log.info('opening mongo client connection to {}:{}'.format(self.host, self.port))
            self._connection = MongoClient(self.host, self.port)
            return self
        except Exception as e:
            log.error('Cannot connect to {}.{}: {}'.format(self.host, self.port, e))
            raise


class DataStore(ABC):

    def __init__(self, connector: DataConnector):
        self.connector = connector

    @abstractmethod
    def read(self, *args, **kwargs):
        raise NotImplementedError()

    def write(self, *args, **kwargs):
        raise NotImplementedError()


class MongoDb(DataStore):

    def __init__(self, connector: DataConnector, db, coll):
        super(MongoDb).__init__(connector)
        self.db = db
        self.coll = self._collection(self.db, coll)

    def _collection(self, db, coll, index_field=None, drop=False):
        """
        get a  collection object, and if it already exists, raise exception or drop it
        :param db: db name
        :param coll: collection name
        :return: a collection in mongo
        """
        try:
            log.info('accessing db {} and collection {}'.format(db, coll))
            m_db = self.connector.connection()[db]
            if drop:
                m_db.drop_collection(coll)
            coll = m_db[db][coll]
            index_field = index_field
            if index_field:
                log.info('ensure index on {}'.format(index_field))
                coll.ensure_index(index_field, unique=True)
            else:
                log.info('not creating an index on the collection')
        except Exception as e:
            log.error('Unable to access db {} and collection {}: {}'.format(db, coll, e))
            raise
        return coll

    # todo - see where all the reads are and put them in here, then clean up
    #
    def read_unprocessed(self, processor_name):
        """
        :param processor_name:
        :return: yield result from cursor
        """
        cursor = self.coll.find(
            {'processors': {'$not': {'$elemMatch': {'$regex': processor_name}}}}
        )
        while cursor.hasNext():
            yield cursor.next()











