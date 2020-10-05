# coding: utf-8
import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.mm_success_article import MMSuccessArticle

class MMSuccessArticleTestCase(unittest.TestCase):

    @patch('otrs_somconnexio.otrs_models.abstract_article.Article')
    def test_call(self, MockArticle):

        body = 'Whatever is the success message'
        expected_article_arguments = {
            "Subject": "Petició d'alta a MM entrada correctament",
            "Body": body,
            "ContentType": "text/plain; charset=utf8"
        }

        MMSuccessArticle(body).call()
        MockArticle.assert_called_once_with(expected_article_arguments)
