from typing import List
from enum import Enum
from datetime import datetime, timedelta

from my_feed.modules.post import PostModel
from my_feed.platforms.reddit import Reddit
from my_feed.platforms.instagram import Instagram
# from my_feed.platforms.twitter import Twitter


# To ad a new social add a new entry on the enum
# they will be automatically handled
class Platforms(Enum):
    REDDIT = Reddit
    INSTAGRAM = Instagram
    # TWITTER = Twitter


class Channel:

    def __init__(self, platform: Platforms, target: str):

        # in case of a non existing channel set as disabled, so it will not update
        self.is_enabled = True

        # The platform update type (reddit, instagram, etc)
        self.platform = platform
        self.updater = platform.value  # the updater Class

        # initialize last update with an old time
        self.last_update: datetime = datetime.now() - timedelta(hours=5)
        # the exact time when the update start, to save it later
        self.__temp_last_update = None

        # update the data every minutes interval
        self.update_interval: int = 1

        # how to identify the last update, to not send again the same data
        # this value can be a string, slug, int or tuple based on the platform that you are using
        self.last_update_id = None
        # temporally save the last update id
        self.__temp_last_update_id = None

        # the channel specification, this must match che update requirements in the platform api
        self.target: str = target

    @property
    def is_time_to_update(self) -> bool:
        if datetime.now() - self.last_update > timedelta(minutes=self.update_interval) and self.is_enabled:
            return True
        return False

    def update(self) -> List[PostModel]:
        updater = self.updater()  # create the class
        out = updater.update(self.target, self.last_update_id)
        self.__temp_last_update = datetime.now()

        # temporally save the last update id
        # after all the operations on the data are done call set_last_update_now()
        self.__temp_last_update_id = updater.last_post_id

        # if is the first time the last_update_id is none, so dont show any post
        if self.last_update_id:
            return out
        else:
            return []

    def set_last_update_now(self) -> None:
        # update the last id, after all the operation on the data is done
        self.last_update_id = self.__temp_last_update_id
        self.last_update = self.__temp_last_update
