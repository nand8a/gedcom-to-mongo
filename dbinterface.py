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

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.__connection = None

    @abstractmethod
    def connection(self):
        raise NotImplementedError()


class MongoConnector(DataConnector):

    def __init__(self, host, port):
        super(MongoConnector, self).__init__(host, port)
        if host and port:
            self.host = host
            self.port = port
            try:
                log.info('opening mongo client connection to {}:{}'.format(host, port))
                self.__connection = MongoClient(host, port)
            except Exception as e:
                log.error('Cannot connect to {}.{}: {}'.format(host, port, e))
                raise
        else:
            # already instantiated - we think
            pass

    @property
    def connection(self):
        if not self.__connection:
            raise ValueError('connection not initialised')
        else:
            return self



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


    def collection(self, db, coll, index_field=None, drop=False):
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


    def read_many(self, query=, projection={}):
        """
        This could return many or one
        :param query:
        :param projection:
        :return:
        """
        cursor = .find(
            {'processors': {'$not': {'$elemMatch': {'$regex': __proc_name__}}}}
        )
        record = cursor.next()
        yield








