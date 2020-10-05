import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.factories.fiber_data_from_eticom_contract \
    import FiberDataFromEticomContract


class FiberDataFromEticomContractTestCase(unittest.TestCase):

    def setUp(self):
        self.eticom_contract = Mock(spec=[
            'id',
            'party'
            'bank_iban_service',
            'internet_phone_now',
            'internet_telecom_company',
            'internet_vat_number',
            'internet_name',
            'internet_surname',
            'internet_lastname',
            'internet_street',
            'internet_city',
            'internet_zip',
            'internet_subdivision',
            'internet_delivery_street',
            'internet_delivery_city',
            'internet_delivery_zip',
            'internet_delivery_subdivision',
            'internet_now',
            'notes',
            'coverage_availability',
            'change_address',
            'internet_speed',
            'provider_change_address',
        ])
        self.eticom_contract.id = 123
        self.eticom_contract.bank_iban_service = "ES6621000418401234567891"
        self.eticom_contract.internet_name = 'Josep'
        self.eticom_contract.internet_surname = 'Perez'
        self.eticom_contract.internet_lastname = 'Ford'
        self.eticom_contract.change_address = False
        self.eticom_contract.coverage_availability = Mock(spec=['adsl', 'mm_fiber', 'vdf_fiber'])
        self.eticom_contract.coverage_availability.adsl = '20'
        self.eticom_contract.coverage_availability.mm_fiber = 'CoberturaMM'
        self.eticom_contract.coverage_availability.vdf_fiber = 'FibraCoaxial'

    @patch('otrs_somconnexio.otrs_models.factories.fiber_data_from_eticom_contract.TelecomCompany')
    def test_build(self, MockTelecomCompany):

        MockTelecomCompany.return_value = "SomConnexio"

        fiber_data = FiberDataFromEticomContract(self.eticom_contract).build()

        self.assertEqual(fiber_data.order_id, self.eticom_contract.id)
        self.assertEqual(fiber_data.phone_number, self.eticom_contract.internet_phone_now)
        self.assertEqual(fiber_data.iban, self.eticom_contract.bank_iban_service)
        self.assertEqual(fiber_data.previous_provider, 'SomConnexio')
        self.assertEqual(fiber_data.previous_owner_vat, self.eticom_contract.internet_vat_number)
        self.assertEqual(fiber_data.previous_owner_name, 'Josep Perez Ford')
        self.assertEqual(fiber_data.previous_owner_surname, 'Perez Ford')

        self.assertEqual(fiber_data.service_address, self.eticom_contract.internet_street)
        self.assertEqual(fiber_data.service_city, self.eticom_contract.internet_city)
        self.assertEqual(fiber_data.service_zip, self.eticom_contract.internet_zip)
        self.assertEqual(fiber_data.service_subdivision, self.eticom_contract.internet_subdivision.name)
        self.assertEqual(fiber_data.shipment_address, self.eticom_contract.internet_delivery_street)
        self.assertEqual(fiber_data.shipment_city, self.eticom_contract.internet_delivery_city)
        self.assertEqual(fiber_data.shipment_zip, self.eticom_contract.internet_delivery_zip)
        self.assertEqual(fiber_data.shipment_subdivision, self.eticom_contract.internet_delivery_subdivision.name)
        self.assertEqual(fiber_data.previous_service, 'None')
        self.assertEqual(fiber_data.notes, u"{}".format(self.eticom_contract.notes))
        self.assertEqual(fiber_data.adsl_coverage, self.eticom_contract.coverage_availability.adsl)
        self.assertEqual(fiber_data.mm_fiber_coverage, self.eticom_contract.coverage_availability.mm_fiber)
        self.assertEqual(fiber_data.vdf_fiber_coverage, self.eticom_contract.coverage_availability.vdf_fiber)
        self.assertEqual(fiber_data.change_address, 'no')
        self.assertEqual(fiber_data.previous_internal_provider, self.eticom_contract.provider_change_address)

        self.assertEqual(fiber_data.internet_speed, self.eticom_contract.internet_speed)

    @patch('otrs_somconnexio.otrs_models.factories.fiber_data_from_eticom_contract.TelecomCompany')
    def test_build_adsl_as_previous_service(self, MockTelecomCompany):
        self.eticom_contract.internet_now = 'adsl'

        MockTelecomCompany.return_value = "SomConnexio"

        fiber_data = FiberDataFromEticomContract(self.eticom_contract).build()

        self.assertEqual(fiber_data.previous_service, 'ADSL')

    @patch('otrs_somconnexio.otrs_models.factories.fiber_data_from_eticom_contract.TelecomCompany')
    def test_build_fiber_as_previous_service(self, MockTelecomCompany):
        self.eticom_contract.internet_now = 'fibre'

        MockTelecomCompany.return_value = "SomConnexio"

        fiber_data = FiberDataFromEticomContract(self.eticom_contract).build()

        self.assertEqual(fiber_data.previous_service, 'Fibra')

    @patch('otrs_somconnexio.otrs_models.factories.fiber_data_from_eticom_contract.TelecomCompany')
    def test_build_change_address(self, MockTelecomCompany):
        self.eticom_contract.change_address = True

        MockTelecomCompany.return_value = "SomConnexio"

        fiber_data = FiberDataFromEticomContract(self.eticom_contract).build()

        self.assertEqual(fiber_data.change_address, 'yes')

    @patch('otrs_somconnexio.otrs_models.factories.fiber_data_from_eticom_contract.TelecomCompany')
    def test_build_without_shipment_data(self, MockTelecomCompany):
        self.eticom_contract.internet_delivery_street = None
        self.eticom_contract.internet_delivery_city = None
        self.eticom_contract.internet_delivery_zip = None
        self.eticom_contract.internet_delivery_subdivision = None

        MockTelecomCompany.return_value = "SomConnexio"

        fiber_data = FiberDataFromEticomContract(self.eticom_contract).build()

        self.assertEqual(fiber_data.shipment_address, self.eticom_contract.internet_street)
        self.assertEqual(fiber_data.shipment_city, self.eticom_contract.internet_city)
        self.assertEqual(fiber_data.shipment_zip, self.eticom_contract.internet_zip)
        self.assertEqual(fiber_data.shipment_subdivision, self.eticom_contract.internet_subdivision.name)
