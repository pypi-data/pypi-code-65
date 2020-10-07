# coding: utf-8
import unittest
from mock import Mock, patch
from pyotrs.lib import DynamicField

from otrs_somconnexio.services.update_process_ticket_with_MM_error import UpdateProcessTicketWithMMError


class UpdateProcessTicketWithMMErrorTestCase(unittest.TestCase):

    def setUp(self):
        self.ticket_id = '1111'
        self.expected_error = {
            "statusCode": "400",
            "message": "El documentType no contiene un valor apto: 2",
            "fields": "documentType"
        }
        self.df_errorPeticio = DynamicField(name="errorPeticio", value=1)
        self.df_errorActivacio = DynamicField(name="errorActivacio", value=1)
        self.df_enviarProxy = DynamicField(name="enviarProxy", value=0)

        self.MM_error_article = object()

    def _mock_df_side_effect(self, name, value):
        if name == "errorPeticio" and value == 1:
            return self.df_errorPeticio
        elif name == "errorActivacio" and value == 1:
            return self.df_errorActivacio
        elif name == "enviarProxy" and value == 0:
            return self.df_enviarProxy

    @patch('otrs_somconnexio.services.update_process_ticket_with_MM_error.OTRSClient',
           return_value=Mock(spec=['update_ticket']))
    @patch('otrs_somconnexio.services.update_process_ticket_with_MM_error.MMErrorArticle',
           return_value=Mock(spec=['call']))
    @patch('otrs_somconnexio.services.update_process_ticket_with_MM_error.DynamicField')
    def test_run(self, MockDF, MockMMErrorArticle, MockOTRSClient):

        object_type = "OrderItem"
        MockMMErrorArticle.return_value.call.return_value = self.MM_error_article
        MockDF.side_effect = self._mock_df_side_effect

        UpdateProcessTicketWithMMError(self.ticket_id, self.expected_error,
                                       "creació", object_type).run()

        MockMMErrorArticle.assert_called_once_with(
            self.expected_error, "creació", object_type)

        MockOTRSClient.return_value.update_ticket.assert_called_once_with(
            self.ticket_id,
            self.MM_error_article,
            dynamic_fields=[self.df_enviarProxy, self.df_errorPeticio]
        )

    @patch('otrs_somconnexio.services.update_process_ticket_with_MM_error.OTRSClient',
           return_value=Mock(spec=['update_ticket']))
    @patch('otrs_somconnexio.services.update_process_ticket_with_MM_error.MMErrorArticle',
           return_value=Mock(spec=['call']))
    @patch('otrs_somconnexio.services.update_process_ticket_with_MM_error.DynamicField')
    def test_run_cancelled_asset(self, MockDF, MockMMErrorArticle, MockOTRSClient):

        object_type = "Asset"
        MockMMErrorArticle.return_value.call.return_value = self.MM_error_article
        MockDF.side_effect = self._mock_df_side_effect

        UpdateProcessTicketWithMMError(self.ticket_id, self.expected_error,
                                       "obtenció", object_type).run()

        MockMMErrorArticle.assert_called_once_with(
            self.expected_error, "obtenció", object_type)

        MockOTRSClient.return_value.update_ticket.assert_called_once_with(
            self.ticket_id,
            self.MM_error_article,
            dynamic_fields=[self.df_enviarProxy, self.df_errorActivacio]
        )