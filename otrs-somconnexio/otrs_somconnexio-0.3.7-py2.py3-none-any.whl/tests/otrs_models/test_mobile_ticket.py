# coding: utf-8
import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.mobile_ticket import MobileTicket
from otrs_somconnexio.otrs_models.configurations.mobile_ticket import MobileTicketConfiguration
from otrs_somconnexio.exceptions import CustomerMailMissing


class MobileTicketTestCase(unittest.TestCase):

    @patch('otrs_somconnexio.otrs_models.provision_ticket.Ticket')
    def test_build_ticket(self, MockTicket):
        mobile_data = Mock(spec=[
            'order_id'
        ])
        mobile_data.order_id = 123

        customer_data = Mock(spec=[
            'id',
            'email',
        ])
        customer_data.email = 'contact@mail.com'

        expected_ticket_arguments = {
            "Title": "Sol·licitud mobile {}".format(mobile_data.order_id),
            "Type": MobileTicketConfiguration.type,
            "Queue": MobileTicketConfiguration.queue,
            "State": MobileTicketConfiguration.state,
            "Priority": MobileTicketConfiguration.priority,
            "CustomerUser": 'contact@mail.com',
            "CustomerID": 'contact@mail.com'
        }

        MobileTicket(mobile_data, customer_data)._build_ticket()

        MockTicket.assert_called_with(expected_ticket_arguments)

    @patch('otrs_somconnexio.otrs_models.provision_ticket.ProvisionArticle')
    def test_build_article(self, MockProvisionArticle):
        mobile_data = Mock(spec=['order_id'])
        mobile_data.order_id = 123

        customer_data = Mock(spec=['order_id'])

        mock_mobile_article = MockProvisionArticle.return_value

        MobileTicket(mobile_data, customer_data)._build_article()

        MockProvisionArticle.assert_called_with('mobile', 123)
        mock_mobile_article.call.assert_called_once()

    @patch('otrs_somconnexio.otrs_models.mobile_ticket.MobileDynamicFields')
    def test_build_dynamic_fields(self, MockMobileDynamicFields):
        mobile_data = Mock(spec=[])
        customer_data = Mock(spec=[])

        mock_mobile_dynamic_fields = MockMobileDynamicFields.return_value

        MobileTicket(mobile_data, customer_data)._build_dynamic_fields()

        MockMobileDynamicFields.assert_called_with(
            mobile_data,
            customer_data,
            MobileTicketConfiguration.process_id,
            MobileTicketConfiguration.activity_id,
        )
        mock_mobile_dynamic_fields.all.assert_called_once()

    @patch('otrs_somconnexio.otrs_models.provision_ticket.OTRSClient')
    def test_create(self, MockOTRSClient):
        mobile_data = Mock(spec=[
            'order_id',
            'iban',
            'phone_number',
            'sc_icc',
            'icc',
            'service_minutes',
            'service_internet',
            'portability',
            'previous_provider',
            'previous_owner_vat',
            'previous_owner_name',
            'previous_owner_surname',
            'product',
        ])
        mobile_data.order_id = 4321
        mobile_data.service_minutes = '0'
        mobile_data.portability = False

        customer_data = Mock(spec=[
            'id',
            'email',
            'phone',
            'first_name',
            'name',
            'vat_number',
            'street',
            'city',
            'zip',
            'subdivision',
        ])
        customer_data.id = 1234
        customer_data.email = 'contact@mail.coop'

        mock_otrs_client = Mock(spec=['create_otrs_process_ticket'])
        mock_otrs_client.create_otrs_process_ticket.return_value = Mock(MobileTicket, autospec=True)
        mock_otrs_client.create_otrs_process_ticket.return_value.id = 123
        mock_otrs_client.create_otrs_process_ticket.return_value.number = '#123'
        MockOTRSClient.return_value = mock_otrs_client

        ticket = MobileTicket(mobile_data, customer_data)
        ticket.create()

        mock_otrs_client.create_otrs_process_ticket.assert_called_once()

        self.assertEqual(ticket.id, 123)
        self.assertEqual(ticket.number, '#123')

    @patch('otrs_somconnexio.otrs_models.provision_ticket.OTRSClient')
    def test_create_raise_customer_email_missing_exeception(self, MockOTRSClient):
        mobile_data = Mock(spec=[
            'order_id',
            'iban',
            'phone_number',
            'sc_icc',
            'icc',
            'service_minutes',
            'service_internet',
            'portability',
            'previous_provider',
            'previous_owner_vat',
            'previous_owner_name',
            'previous_owner_surname',
            'product',
        ])
        mobile_data.order_id = 4321

        customer_data = Mock(spec=[
            'id',
            'email',
            'phone',
            'first_name',
            'name',
            'vat_number',
            'street',
            'city',
            'zip',
            'subdivision',
        ])
        customer_data.id = 1234
        customer_data.email = None

        ticket = MobileTicket(mobile_data, customer_data)
        self.assertRaisesRegexp(
            CustomerMailMissing,
            "Customer without mail in order ID {}".format(mobile_data.order_id),
            ticket.create
        )
