# coding: utf-8
import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.mm_completed_order_item_article import MMCompletedOrderItemArticle

class MMCompletedOrderItemArticleTestCase(unittest.TestCase):

    @patch('otrs_somconnexio.otrs_models.abstract_article.Article')
    def test_call(self, MockArticle):

        mm_asset = {
            "id": "111",
            "status": "en progreso",
            "productName": "Tarifa Ilimitada CM Voz Total Nov19",
        }

        expected_article_arguments = {
            "Subject": "Línia de mòbil donada d'alta a MasMóvil",
            "Body": u"id: 111\nproductName: Tarifa Ilimitada CM Voz Total Nov19\nstatus: en progreso\n",
            "ContentType": "text/plain; charset=utf8"
        }

        MMCompletedOrderItemArticle(mm_asset).call()
        MockArticle.assert_called_once_with(expected_article_arguments)
