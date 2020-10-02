import logging
import os

from bson.objectid import ObjectId
from pymongo import MongoClient


logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MongoDB:
    """
    Mongo DB Utility to help put data to database via
    different python applications
    """
    def __init__(self, force_db_name=False, collection_name=None):
        """
        :usage: Creates connection to db, creates DB and collection (DEFAULT/TESTING)
        """
        self._create_connection(force_db_name=force_db_name)
        if collection_name:
            self._create_collection(collection_name)

    def __repr__(self):
        return str(self.db)

    def _create_connection(self, test=False, force_db_name=False):
        """ create a database connection to the Mongo database specified by conf file
            :param test: to create a test db or default db
            :return: mongoclient object
            """
        try:
            host = os.environ.get("DATABASE_HOST")
            port = os.environ.get("DATABASE_PORT")
            db_name =  os.environ.get("DATABASE_NAME")
            username = os.environ.get('MONGO_INITDB_ROOT_USERNAME')
            password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD')
            logger.info(">>> Connecting to {} DB <<<".format(db_name))
            self.client = MongoClient(
                host, int(port),
                username=username, password=password
            )
            if force_db_name:
                self._create_db(force_db_name)
            else:
                self._create_db(db_name)
            return self.client
        except Exception as e:
            print(e)

    def _create_db(self, db_name):
        """
        Creates a database
        :param db_name: Database name picked from config
        :return: mongo db instance
        """
        self._db_name = db_name
        self.db = self.client.get_database(db_name)
        return self.db

    def _create_collection(self, collection_name):
        """
        Creates a collection and adds the collection as an
        attribute to the class for easier access. 
        :param collection_name: name of the collection
        :return: mongodb collection instance
        """
        collection = self.db.get_collection(collection_name)
        setattr(self, collection_name, collection)
        return collection

    def fetch_by_id(self, _id, collection_name):
        """
        Fetches a record by the provided _id
        :param _id: PK for the record on which the search to be done
        :param collection_name: collection name  on which the search is to be done.
        :return: Identified record
        """
        try:
            collection = getattr(self, collection_name)
        except:
            collection = self._create_collection(collection_name)
        document = collection.find_one({'_id': ObjectId(_id)})
        return document

    def fetch_many(self, collection_name, filter_dict):
        """
        Fetches multiple records based on the filter
        :param collection_name: name of the collection on which the filter is to be done
        :param filter_dict: filter condition dictionary, leave empty for all
        :return: list of identified records
        """
        try:
            collection = getattr(self, collection_name)
        except:
            collection = self._create_collection(collection_name)
        document = collection.find(filter_dict)
        return list(document)

    def insert(self, key, value, collection_name):
        """
        Inserts a new record to mentioned collection
        :param key: key of the record
        :param value:  value of the record
        :param collection_name: name of the collection
        :return: id of the inserted object
        """
        try:
            collection = getattr(self, collection_name)
        except:
            collection = self._create_collection(collection_name)

        obj = collection.insert_one({key: value})
        return obj.inserted_id

    def insert_record(self, data, collection_name):
        """
        Inserts a new record to mentioned collection
        :param data: dictionary of key value pairs
        :param collection_name: name of the collection
        :return: id of the inserted object
        """
        try:
            collection = getattr(self, collection_name)
        except:
            collection = self._create_collection(collection_name)

        obj = collection.insert_one(data)
        return obj.inserted_id

    def update(self, _id, key, value, collection_name):
        """
        Updates an existing record
        :param _id: id of the intended record
        :param key: key to update
        :param value: value to update
        :param collection_name: name of the collection
        """
        try:
            collection = getattr(self, collection_name)
        except:
            collection = self._create_collection(collection_name)

        myquery = {"_id": ObjectId(_id)}
        newvalues = {"$set": {key: value}}

        collection.update_one(myquery, newvalues)

    def create_or_update(self, key, value, collection_name, _id=None):
        """
        Insert new or update if existing record
        :param key: key for the operation
        :param value: value for the operation
        :param collection_name: name of the collection
        :param _id: _id to find the record if already existing
        :return: id of the object
        """
        doc = self.fetch_by_id(_id, collection_name)
        if doc:
            self.update(_id, key, value, collection_name)
            return _id
        else:
            obj_id = self.insert(key, value, collection_name)
            return obj_id

    def bulk_insert(self, value_list, collection_name):
        """
        Bulk insert for a collection
        :param value_list: list of all records
        :param collection_name: name of the collection
        """
        try:
            collection = getattr(self, collection_name)
        except:
            collection = self._create_collection(collection_name)

        try:
            collection.insert_many(value_list)
        except Exception as e:
            print(e)
            raise Exception("Bulk Insert Failed")

    def delete(self, _id, collection_name):
        """
        Deletes a selected record
        :param _id: id of a selected record
        :param collection_name: name of the collection
        """
        try:
            collection = getattr(self, collection_name)
        except:
            collection = self._create_collection(collection_name)

        try:
            collection.remove(ObjectId(_id))
        except:
            raise Exception("Unable to delete record: {}".format(_id))

    def truncate_collection(self, collection_name):
        """
        Truncates a collection by removing all records
        :param collection_name: name of the collection
        """
        try:
            collection = getattr(self, collection_name)
        except:
            collection = self._create_collection(collection_name)

        collection.remove()