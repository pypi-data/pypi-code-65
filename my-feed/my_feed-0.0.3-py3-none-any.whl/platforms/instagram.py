import hashlib
import string
import random

from instagram_web_api import (
    Client,
)

from my_feed.platforms import PlatformInterface, PlatformsId
from my_feed.modules.post import PostModel
from my_feed.modules.types import PostType


class MyClient(Client):
    """
    cause of a lib bug in the web_api i have to redefine the _extract_rhx_gis
    """

    @staticmethod
    def _extract_rhx_gis(html):
        options = string.ascii_lowercase + string.digits
        text = ''.join([random.choice(options) for _ in range(8)])
        return hashlib.md5(text.encode()).hexdigest()


class Instagram(PlatformInterface):

    def __init__(self):
        super().__init__()

        self.api = MyClient(auto_patch=True, drop_incompat_keys=False)

    def __repr__(self):
        return PlatformsId.INSTAGRAM.value

    @staticmethod
    def get_media_url(data):
        media = data.get('standard_resolution', {})
        return media.get('url')

    def story(self, user_id, last_update_id):
        """
        story can be get only if you are logged in
        Load all the stories from the user loaded
        :return: InstagramStory list
        """
        pass
        # story = self.api._story_feed(user_id)
        # return story

    def post(self, user_id, last_update_id):
        """
        Get all the post from the user loaded
        Store them as a list of InstagramPost obj
        :return: PostModel list
        """
        out = []

        items = self.api.user_feed(user_id)

        for item in items:
            node = item.get('node')

            post_id = node.get('shortcode')
            if post_id == last_update_id:
                break

            caption = node.get('caption', {})
            text = ''
            if caption:
                text = caption.get('text', '')

            post = PostModel(
                post_id=post_id,
                title=text,
                created_at=node.get('created_time'),
                url=node.get("link")
            )

            post.type = PostType.IMAGE
            if node.get('is_video'):
                post.type = PostType.VIDEO

            """
            Check if is a post with multible elements
                - multi element post has media list inside carousel_media
                - if not the object media is no encapsulated
            """
            carousel = node.get('carousel_media')
            if carousel:
                for c in carousel:
                    media = c.get('videos' if post.type == PostType.VIDEO else 'images')
                    post.add_media(
                        media_id=None,
                        media_url=self.get_media_url(media)
                    )

            else:
                media = node.get('videos' if post.type == PostType.VIDEO else 'images')
                post.add_media(
                    media_id=None,
                    media_url=self.get_media_url(media)
                )

            out.append(post)

        return out

    def update(self, target, last_update_id):

        # decouple the last update id
        # this cause instagram have 2 feed sources, stories and posts
        last_update_id_story = None
        last_update_id_post = None
        if last_update_id:
            last_update_id_story, last_update_id_post = last_update_id

        # get the data from the api
        post_feed = self.post(target, last_update_id_post)

        # get the post id from the feed
        # last_update_id_story = self._get_last_post_id(story_feed, last_update_id_story)
        last_update_id_post = self._get_last_post_id(post_feed, last_update_id_post)

        # the set feed will also revert it
        self._set_feed(post_feed)

        # update the post id
        self._last_post_id = (last_update_id_story, last_update_id_post)
        return self._feed
