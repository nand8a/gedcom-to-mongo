import logging
log = logging.getLogger(__name__)
from pymongo import MongoClient

class Db(object):

    def __init__(self, ip_addr, port):
        self.mc = None
        try:
            log.info('opening mongo client connection to {}:{}'.format(ip_addr, port))
            self.mc = MongoClient(ip_addr, port)
        except Exception as e:
            log.error('Cannot connect to {}.{}: {}'.format(ip_addr, port, e))
            raise
        self.coll = None
        self.index_field = None

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
            self.coll = self.mc[db][coll]
            self.index_field = index_field
            if index_field:
                log.info('ensure index on {}'.format(index_field))
                self.coll.ensure_index(index_field, unique=True)
            else:
                log.info('not creating an index on the collection')
        except Exception as e:
            log.error('Unable to access db {} and collection {}: {}'.format(db, coll, e))
            raise
        return self.coll

    def has(self, key):
        if not self.coll:
            log.error('please attach a collection first')
            raise ValueError('no collection active')
        if len(list(self.coll.find({self.index_field: key}))) > 0:
            return True
        else:
            return False

    def get(self, key):
        """
        get entire record in db
        :param key:
        :return:
        """
        ans = list(self.coll.find({self.index_field: key}))
        if len(ans) != 1:
            return None
        else:
            return ans[0]

    def update(self, index_field, update_dict):
        """
        insert/upsert a single record
        :param record:
        :return:
        """
        if not self.coll:
            log.error('please attach to a collection first')
            raise ValueError('no collection active')
        log.info('upserting {}'.format(index_field))
        log.debug('inserting/overwriting {}'.format(update_dict))
        self.coll.find_one_and_update(
            {self.index_field: index_field},
            {"$set": update_dict},
            upsert=True
        )
