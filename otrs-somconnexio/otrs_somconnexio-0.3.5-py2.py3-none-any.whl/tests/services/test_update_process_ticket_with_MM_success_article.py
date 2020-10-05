# coding: utf-8
import unittest
from mock import Mock, patch
from pyotrs.lib import DynamicField
from otrs_somconnexio.services.update_process_ticket_with_MM_success_answer import \
    UpdateProcessTicketWithMMSuccessAnswer


class UpdateProcessTicketWithMMSuccessTestCase(unittest.TestCase):

    @patch('otrs_somconnexio.services.update_process_ticket_with_MM_success_answer.OTRSClient',
           return_value=Mock(spec=['update_ticket']))
    @patch('otrs_somconnexio.services.update_process_ticket_with_MM_success_answer.'
           + 'MMSuccessArticle')
    @patch('otrs_somconnexio.services.update_process_ticket_with_MM_success_answer.'
           + 'DynamicField')
    def test_run(self, MockDF, MockMMSuccessArticle, MockOTRSClient):

        ticket_id = '1111'
        expected_body = 'body'
        order_item_id = '12345'
        df_introPlataforma = DynamicField(name="introPlataforma", value=1)
        df_MMOrderItemId = DynamicField(name="MMOrderItemId", value=order_item_id)
        df_enviarProxy = DynamicField(name="enviarProxy", value=0)

        mock_MM_success_article = Mock(spec=['call'])
        MM_success_article = object()

        def mock_MM_success_article_side_effect(body):
            if body == expected_body:
                mock_MM_success_article.call.return_value = MM_success_article
                return mock_MM_success_article

        MockMMSuccessArticle.side_effect = mock_MM_success_article_side_effect

        def mock_df_side_effect(name, value):
            if name == "introPlataforma" and value == 1:
                return df_introPlataforma
            elif name == "MMOrderItemId" and value == order_item_id:
                return df_MMOrderItemId
            elif name == "enviarProxy" and value == 0:
                return df_enviarProxy

        MockDF.side_effect = mock_df_side_effect

        UpdateProcessTicketWithMMSuccessAnswer(ticket_id, expected_body,
                                               order_item_id).run()

        MockOTRSClient.return_value.update_ticket.assert_called_once_with(
            ticket_id,
            MM_success_article,
            dynamic_fields=[df_introPlataforma, df_enviarProxy, df_MMOrderItemId],
        )
