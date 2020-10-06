from crawliexpress.exceptions import CrawliexpressException

import re
from bs4 import BeautifulSoup


RATING_RE = re.compile(r"width:(\d+)%")


class Feedback:

    """
    A user feedback
    """

    user = None
    """Name"""
    profile = None
    """Profile link"""
    country = None
    """Country code"""
    rating = None
    """Rating out of 100"""
    datetime = None
    """Raw datetime from DOM"""
    comment = None
    """Review"""
    images = None
    """List of image links"""

    def from_node(self, node):

        # user name
        node_user = node.find("", class_="user-name")
        if node_user is None:
            raise CrawliexpressException("could not find feedback user node")
        self.user = node_user.text.strip()

        # profile
        node_profile = node_user.find("a")
        # profile can be hidden
        if node_profile is not None:
            self.profile = node_profile["href"]

        # country
        node_country = node.find("", class_="user-country")
        if node_country is None:
            raise CrawliexpressException("could not find feedback country node")
        self.country = node_country.text

        # rating
        node_rating = node.find("", class_="star-view")
        if node_rating is None:
            raise CrawliexpressException("could not find feedback rating node")
        for node_rating_stars in node_rating.children:
            rating_matches = RATING_RE.search(node_rating_stars["style"])
            if rating_matches is not None:
                self.rating = int(rating_matches.group(1))

        # review part
        node_review = node.find("", class_="buyer-review")
        if node_review is None:
            raise CrawliexpressException("could not find feedback review node")

        node_comment = node_review.find("", class_="buyer-feedback")
        if node_comment is None:
            raise CrawliexpressException("could not find feedback comment node")

        # datetime
        node_datetime = node_comment.find("", class_="r-time-new")
        if node_datetime is None:
            raise CrawliexpressException("could not find feedback datetime")
        self.datetime = node_datetime.text

        # comment
        node_comment_span = node_comment.find("span")
        if node_comment_span is None:
            raise CrawliexpressException("could not find feedback comment")
        self.comment = node_comment_span.text

        # images
        images = self.images = list()
        node_images = node.find("", class_="r-photo-list")
        if node_images is not None:
            for node_image in node_images.find_all("img"):
                images.append(node_image["src"])

    def __iter__(self):
        yield "user", self.user
        yield "profile", self.profile
        yield "country", self.country
        yield "rating", self.rating
        yield "datetime", self.datetime
        yield "comment", self.comment
        yield "images", self.images
