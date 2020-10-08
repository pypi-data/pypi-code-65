import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.factories.customer_data_from_party \
    import CustomerDataFromParty


class CustomerDataFromPartyTestCase(unittest.TestCase):

    def setUp(self):
        self.party = Mock(spec=[
            'id',
            'name'
            'first_name',
            'get_identifier',
            'get_contact_email',
            'get_contact_phone',
            'get_contact_address',
        ])
        self.party.name = 'Name'
        self.party.first_name = 'Name'

        self.expected_vat_num = '123456789G'
        identifier = Mock(spec=['code'])
        identifier.code = self.expected_vat_num
        self.party.get_identifier.return_value = identifier

        self.expected_email = 'contact@email.coop'
        email = Mock(spec=['value'])
        email.value = self.expected_email
        self.party.get_contact_email.return_value = email

        self.expected_phone = '666666666'
        phone = Mock(spec=['value'])
        phone.value = self.expected_phone
        self.party.get_contact_phone.return_value = phone

        self.expected_street = 'Norte'
        self.expected_city = 'Alacant'
        self.expected_zip = '03140'
        self.expected_subdivision = 'Alacant'
        subdivision = Mock(spec=['code'])
        subdivision.code = self.expected_subdivision
        contact_address = Mock(spec=[
            'street',
            'city',
            'zip',
            'subdivision',
        ])
        contact_address.street = self.expected_street
        contact_address.city = self.expected_city
        contact_address.zip = self.expected_zip
        contact_address.subdivision = subdivision

        self.party.get_contact_address.return_value = contact_address

    def test_build(self):
        customer_data = CustomerDataFromParty(self.party).build()

        self.assertEqual(customer_data.id, self.party.id)
        self.assertEqual(customer_data.vat_number, self.expected_vat_num)
        self.assertEqual(customer_data.email, self.expected_email)
        self.assertEqual(customer_data.phone, self.expected_phone)
        self.assertEqual(customer_data.name, self.party.name)
        self.assertEqual(customer_data.first_name, self.party.first_name)
        self.assertEqual(customer_data.street, self.expected_street)
        self.assertEqual(customer_data.city, self.expected_city)
        self.assertEqual(customer_data.zip, self.expected_zip)
        self.assertEqual(customer_data.subdivision, self.expected_subdivision)
