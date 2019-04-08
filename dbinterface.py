import logging
log = logging.getLogger(__name__)
from pymongo import MongoClient


class Db(object):

    __instance = None

    def __new__(cls, *args, **kwargs):
        if Db.__instance is None:
            Db.__instance = object.__new__(cls)
        return Db.__instance

    def connect(self, host='localhost', port=27017):
        self.host = host
        self.port = port
        try:
            log.info('opening mongo client connection to {}:{}'.format(host, port))
            self.mc = MongoClient(host, port)
        except Exception as e:
            log.error('Cannot connect to {}.{}: {}'.format(host, port, e))
            raise
        return self.get_connect()

    def get_connect(self):
        if not (self.host and self.port):
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
            m_db = self.mc[db]
            if drop:
                m_db.drop_collection(coll)
            coll = self.mc[db][coll]
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

