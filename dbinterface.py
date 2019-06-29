import logging
log = logging.getLogger(__name__)
import pymongo
from datetime import datetime
from abc import ABC, abstractmethod


class DataConnector(ABC):  # pragma: no cover

    __instance = None

    def __new__(cls, *args, **kwargs):  # pragma: no cover
        if DataConnector.__instance is None:
            print('creating a new object')
            DataConnector.__instance = object.__new__(cls)
        else:
            print ('it is not none, it is {}'.format(DataConnector.__instance))
        return DataConnector.__instance

    @classmethod
    def destroy(cls):
        DataConnector.__instance = None

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
        try:
            if self._connection:
                pass
        except AttributeError:
            self._connection = None  # it has not been set

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
            self._connection = pymongo.MongoClient(self.host, self.port)
            return self
        except Exception as e:
            log.error('Cannot connect to {}.{}: {}'.format(self.host, self.port, e))
            raise


class DataStore(ABC, object):   # pragma: no cover

    def __init__(self, connector: DataConnector):
        self.connector = connector

    # @abstractmethod
    # def read(self, *args, **kwargs):
    #     raise NotImplementedError()
    #
    def write(self, *args, **kwargs):
        raise NotImplementedError()


class MongoDb(DataStore):

    # what other kind of connectors can the mongodb dao have? will always be mongoconnector
    # will have to rethink this:  this object should come with the connector backed in
    def __init__(self, connector: DataConnector, db, coll):
        super(MongoDb, self).__init__(connector)
        self.db = db
        # mongo already lazy loads the connection - for testing easier to move but leaving here for now
        # todo
        self.coll = self._collection(self.db, coll)

    # def _index_field(self, field_name):
    #     self.coll.ensure_index(field_name, unique=True)

    # drop connection
    # if drop:
    #     m_db.drop_collection(coll)

    def read_person(self, id):
        return self.coll.find_one({"_id": id})

    def _collection(self, db, coll):
        """
        get a  collection object, and if it already exists, raise exception or drop it
        :param db: db name
        :param coll: collection name
        :return: a collection in mongo
        """
        try:
            log.info('accessing db {} and collection {}'.format(db, coll))
            m_db = self.connector.connection[db]
            coll = m_db[coll]
        except ValueError as e:
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
        record = cursor.next()
        while record:
            yield record
            record = cursor.next()  # benefits over just returning cursor are that I can do ops on it here

    def read_parent_family_counts(self, id):
        """
        get the parent that corresponds to the id <id>, and project
        only their married status, their child list and if they have spouses
        :param id:
        :return: a dictionary of {'married_count': X, 'children_count': Y, spouses: []}
        """
        cursor = self.coll.find_one({'_id': id},
                                    {'married_count': 1,
                                     'children_count': 1,
                                     'spouses': 1})
        return cursor

    def write_update(self, id, update_dict):
        """
        :param id:
        :param update_dict:
        :return:
        """
        self.coll.find_one_and_update(
            {'_id': id},
            {"$set": update_dict}, upsert=True)

    def write(self, data_dict):
        """
        write a dictionary to mongo, adding {_insert_time: now}
        :param data_dict:
        :return:
        """
        data_dict.update({'_insert_time': datetime.now()})
        self.coll.insert_one(data_dict)

    def write_processor(self, id, processor_name):
        """
        Add the field 'processors': <processor_name>, where id=<id>
        :param processor_name:
        :return:
        """
        self.coll.find_one_and_update(
            {'_id': id}, {"$set": {'processors': [processor_name]}}, upsert=True)

    def read_parents_of_child(self, child_id):
        """
        PARENTS db (todo - logical split)
        :param id:
        :return:
        """
        cursor = self.coll.find_one({'_id': child_id, 'parents': {'$exists': True, '$ne': []}})
        # there is no benefit to having generators here --- remove
        # todo
        record = cursor.next()
        while record:
            yield record
            record = cursor.next()