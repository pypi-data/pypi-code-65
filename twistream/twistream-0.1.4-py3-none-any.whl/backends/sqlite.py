from typing import Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tweepy.models import Status

from twistream.backends.base import BaseStorageBackend
from twistream.log import log
from twistream.twitter.models import Base, TwistreamStatus

LOG = log.get_logger()


class SqliteStorageBackend(BaseStorageBackend):
    def __init__(self, params: Dict[str, str]):
        LOG.debug(f'DB path: {params.get("db_path")}')
        self.engine = create_engine(f'sqlite:///{params.get("db_path")}?check_same_thread=False')
        self.session = sessionmaker(bind=self.engine)()
        self.init_backend()

    def init_backend(self):
        Base.metadata.create_all(self.engine)

    def persist_status(self, status: Status) -> None:
        s = TwistreamStatus(
            status.id,
            status.text,
            status.created_at,
            status.user.screen_name,
            status.user.id,
            status.user.followers_count,
        )
        self.session.add(s)
        self.session.commit()
