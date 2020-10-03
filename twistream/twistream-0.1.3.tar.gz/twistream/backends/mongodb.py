from typing import Dict

import pymongo
from tweepy.models import Status

from twistream.backends.base import BaseStorageBackend
from twistream.log import log

LOG = log.get_logger()


class MongoDBStorageBackend(BaseStorageBackend):

    db: pymongo.MongoClient = None

    def __init__(self, params: Dict[str, str]):
        db_string = params.get("db_string")
        LOG.debug(f"DB connection string: {db_string}")
        self.client = pymongo.MongoClient(db_string)
        self.init_backend()

    def init_backend(self):
        self.db = self.client.twistream

    def persist_status(self, status: Status) -> None:
        self.db.tweets.insert_one(status._json)
