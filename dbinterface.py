import logging
log = logging.getLogger(__name__)
from pymongo import MongoClient
from abc import ABCMeta


class DataStore(metaclass=ABCMeta):

    __instance = None

    def __new__(cls, *args, **kwargs):
        if DataStore.__instance is None:
            DataStore.__instance = object.__new__(cls)
        return DataStore.__instance

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.__connection = None


class MongoDb(DataStore):

    def __init__(self, host='localhost', port=27017):
        super(MongoDb, self).__init__(host, port)
        try:
            log.info('opening mongo client connection to {}:{}'.format(host, port))
            self.__connection = MongoClient(host, port)
        except Exception as e:
            log.error('Cannot connect to {}.{}: {}'.format(host, port, e))
            raise

    @property
    def connection(self):
        if not self.__connection:
            raise ValueError('connection not initialised')
        else:
            return self

    def collection(self, db, coll, index_field=None, drop=False):
        """
        get a  collection object, and if it already exists, raise exception or drop it
        :param db: db name
        :param coll: collection name
        :return: a collection in mongo
        """
        try:
            log.info('accessing db {} and collection {}'.format(db, coll))
            m_db = self.__connection[db]
            if drop:
                m_db.drop_collection(coll)
            coll = self.__connection[db][coll]
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

