# coding: utf-8
import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.fiber_ticket import FiberTicket
from otrs_somconnexio.otrs_models.configurations.fiber_ticket import FiberTicketConfiguration
from otrs_somconnexio.exceptions import CustomerMailMissing


class FiberTicketTestCase(unittest.TestCase):

    @patch('otrs_somconnexio.otrs_models.provision_ticket.Ticket')
    def test_build_ticket(self, MockTicket):
        customer_data = Mock(spec=['email'])
        customer_data.email = 'contact@mail.com'
        service_data = Mock(spec=['order_id'])

        expected_ticket_arguments = {
            "Title": "Sol·licitud fiber {}".format(service_data.order_id),
            "Type": FiberTicketConfiguration.type,
            "Queue": FiberTicketConfiguration.queue,
            "State": FiberTicketConfiguration.state,
            "Priority": FiberTicketConfiguration.priority,
            "CustomerUser": 'contact@mail.com',
            "CustomerID": 'contact@mail.com'
        }

        FiberTicket(service_data, customer_data)._build_ticket()
        MockTicket.assert_called_with(expected_ticket_arguments)

    @patch('otrs_somconnexio.otrs_models.provision_ticket.ProvisionArticle')
    def test_build_article(self, MockInternetArticle):
        customer_data = Mock(spec=[])
        service_data = Mock(spec=['order_id'])

        mock_mobile_article = MockInternetArticle.return_value

        FiberTicket(service_data, customer_data)._build_article()

        MockInternetArticle.assert_called_with('fiber', service_data.order_id)
        mock_mobile_article.call.assert_called_once()

    @patch('otrs_somconnexio.otrs_models.fiber_ticket.FiberDynamicFields')
    def test_build_dynamic_fields(self, MockFiberDynamicFields):
        customer_data = Mock(spec=[])
        service_data = Mock(spec=['order_id'])

        mock_fiber_dynamic_fields = MockFiberDynamicFields.return_value

        FiberTicket(service_data, customer_data)._build_dynamic_fields()

        MockFiberDynamicFields.assert_called_with(
            service_data,
            customer_data,
            FiberTicketConfiguration.process_id,
            FiberTicketConfiguration.activity_id,
        )
        mock_fiber_dynamic_fields.all.assert_called_once()

    @patch('otrs_somconnexio.otrs_models.provision_ticket.OTRSClient')
    def test_create(self, MockOTRSClient):
        customer_data = Mock(spec=[
            'id',
            'email',
            'phone',
            'first_name',
            'name',
            'vat_number',
        ])
        service_data = Mock(spec=[
            'order_id',
            'iban',
            'previous_service',
            'phone_number',
            'previous_provider',
            'previous_owner_vat',
            'previous_owner_name',
            'previous_owner_surname',
            'service_address',
            'service_city',
            'service_zip',
            'service_subdivision',
            'shipment_address',
            'shipment_city',
            'shipment_zip',
            'shipment_subdivision',
            'notes',
            'adsl_coverage',
            'mm_fiber_coverage',
            'vdf_fiber_coverage',
            'change_address',
            'internet_speed',
            'product',
            'previous_internal_provider',
        ])

        mock_otrs_client = Mock(spec=['create_otrs_process_ticket'])
        mock_otrs_client.create_otrs_process_ticket.return_value.id = 123
        mock_otrs_client.create_otrs_process_ticket.return_value.number = '#123'
        MockOTRSClient.return_value = mock_otrs_client

        ticket = FiberTicket(service_data, customer_data)
        ticket.create()

        mock_otrs_client.create_otrs_process_ticket.assert_called_once()

        self.assertEqual(ticket.id, 123)
        self.assertEqual(ticket.number, '#123')

    @patch('otrs_somconnexio.otrs_models.provision_ticket.OTRSClient')
    def test_create_raise_customer_email_missing_exeception(self, MockOTRSClient):
        service_data = Mock(spec=['order_id'])
        service_data.order_id = 4321
        customer_data = Mock(spec=[
            'id',
            'email',
            'phone',
            'first_name',
            'name',
            'vat_number',
        ])
        customer_data.id = 1234
        customer_data.email = None

        ticket = FiberTicket(service_data, customer_data)

        self.assertRaisesRegexp(
            CustomerMailMissing,
            "Customer without mail in order ID {}".format(service_data.order_id),
            ticket.create
        )
