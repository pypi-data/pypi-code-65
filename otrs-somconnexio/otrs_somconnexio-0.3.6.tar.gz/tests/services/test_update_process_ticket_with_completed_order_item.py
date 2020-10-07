# coding: utf-8
import unittest
from mock import Mock, patch
from pyotrs.lib import DynamicField
from otrs_somconnexio.services.update_process_ticket_with_completed_order_item import \
    UpdateProcessTicketWithCompletedOrderItem


class UpdateProcessTicketWithMMSuccessTestCase(unittest.TestCase):


    def setUp(self):
        self.ticket_id = '1111'
        self.phone_num = '666666666'
        self.expected_body = {
            'phone': self.phone_num
        }
        self.article = object()

        self.df_contracteMobilActivat = DynamicField(name="contracteMobilActivat", value=1)
        self.df_phone_number = DynamicField(name="msisdn", value=self.phone_num)

    def _mock_df_side_effect(self, name, value):
            if name == "contracteMobilActivat" and value == 1:
                return self.df_contracteMobilActivat
            if name == "msisdn" and value == self.phone_num:
                return self.df_phone_number

    @patch('otrs_somconnexio.services.update_process_ticket_with_completed_order_item.OTRSClient',
           return_value=Mock(spec=['update_ticket']))
    @patch('otrs_somconnexio.services.update_process_ticket_with_completed_order_item.'
           + 'MMCompletedOrderItemArticle', return_value=Mock(spec=['call']))
    @patch('otrs_somconnexio.services.update_process_ticket_with_completed_order_item.'
           + 'DynamicField')
    def test_run_new_registration(self, MockDF, MockMMCompletedOrderItemArticle, MockOTRSClient):

        MockMMCompletedOrderItemArticle.return_value.call.return_value = self.article

        MockDF.side_effect = self._mock_df_side_effect

        UpdateProcessTicketWithCompletedOrderItem(self.ticket_id, self.expected_body, True).run()

        MockMMCompletedOrderItemArticle.assert_called_once_with(self.expected_body)

        MockOTRSClient.return_value.update_ticket.assert_called_once_with(
            self.ticket_id,
            self.article,
            dynamic_fields=[self.df_contracteMobilActivat, self.df_phone_number]
        )

    @patch('otrs_somconnexio.services.update_process_ticket_with_completed_order_item.OTRSClient',
           return_value=Mock(spec=['update_ticket']))
    @patch('otrs_somconnexio.services.update_process_ticket_with_completed_order_item.'
           + 'MMCompletedOrderItemArticle', return_value=Mock(spec=['call']))
    @patch('otrs_somconnexio.services.update_process_ticket_with_completed_order_item.'
           + 'DynamicField')
    def test_run_portability(self, MockDF, MockMMCompletedOrderItemArticle, MockOTRSClient):

        MockMMCompletedOrderItemArticle.return_value.call.return_value = self.article

        MockDF.side_effect = self._mock_df_side_effect

        UpdateProcessTicketWithCompletedOrderItem(self.ticket_id, self.expected_body).run()

        MockMMCompletedOrderItemArticle.assert_called_once_with(self.expected_body)

        MockOTRSClient.return_value.update_ticket.assert_called_once_with(
            self.ticket_id,
            self.article,
            dynamic_fields=[self.df_contracteMobilActivat]
        )
