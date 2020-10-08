# coding: utf-8
from pyotrs.lib import Article


class AbstractArticle:

    subject = ""
    body = ""

    def call(self):
        article_params = {
            "Subject": self.subject,
            "Body": self.body,
            "ContentType": "text/plain; charset=utf8",
        }

        return Article(article_params)
