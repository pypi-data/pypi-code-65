import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.factories.mobile_data_from_eticom_contract \
    import MobileDataFromEticomContract


class MobileDataFromEticomContractTestCase(unittest.TestCase):

    def setUp(self):
        self.eticom_contract = Mock(spec=[
            'id',
            'party'
            'bank_iban_service',
            'mobile_phone_number',
            'mobile_sc_icc',
            'mobile_icc_number',
            'mobile_min',
            'mobile_internet',
            'mobile_option',
            'mobile_telecom_company',
            'mobile_vat_number',
            'mobile_name',
            'mobile_surname',
        ])
        self.eticom_contract.id = 123
        self.eticom_contract.mobile_phone_number = "666666666"
        self.eticom_contract.mobile_option = "new"
        self.eticom_contract.mobile_min = "0"
        self.eticom_contract.mobile_internet = "2GB"
        self.eticom_contract.mobile_internet_unlimited = "20GB"
        self.eticom_contract.bank_iban_service = "ES6621000418401234567891"
        self.eticom_contract.mobile_vat_number = "1234"
        self.eticom_contract.mobile_icc_number = "1234"
        self.eticom_contract.mobile_sc_icc = "1234"

    @patch('otrs_somconnexio.otrs_models.factories.mobile_data_from_eticom_contract.TelecomCompany')
    def test_build(self, MockTelecomCompany):

        MockTelecomCompany.return_value = "SomConnexio"

        mobile_data = MobileDataFromEticomContract(self.eticom_contract).build()

        self.assertEqual(mobile_data.order_id, self.eticom_contract.id)
        self.assertEqual(mobile_data.phone_number, self.eticom_contract.mobile_phone_number)
        self.assertEqual(mobile_data.iban, self.eticom_contract.bank_iban_service)
        self.assertEqual(mobile_data.sc_icc, self.eticom_contract.mobile_sc_icc)
        self.assertEqual(mobile_data.icc, self.eticom_contract.mobile_icc_number)
        self.assertEqual(mobile_data.service_minutes, "0min")
        self.assertEqual(mobile_data.service_internet, self.eticom_contract.mobile_internet)
        self.assertEqual(mobile_data.portability, False)
        self.assertEqual(mobile_data.previous_provider, "SomConnexio")
        self.assertEqual(mobile_data.previous_owner_vat, self.eticom_contract.mobile_vat_number)
        self.assertEqual(mobile_data.previous_owner_name, self.eticom_contract.mobile_name)
        self.assertEqual(mobile_data.previous_owner_surname, self.eticom_contract.mobile_surname)

    @patch('otrs_somconnexio.otrs_models.factories.mobile_data_from_eticom_contract.TelecomCompany')
    def test_build_portability(self, MockTelecomCompany):
        self.eticom_contract.mobile_option = "portability"

        MockTelecomCompany.return_value = "SomConnexio"

        mobile_data = MobileDataFromEticomContract(self.eticom_contract).build()

        self.assertTrue(mobile_data.portability)

    @patch('otrs_somconnexio.otrs_models.factories.mobile_data_from_eticom_contract.TelecomCompany')
    def test_build_100min(self, MockTelecomCompany):
        MockTelecomCompany.return_value = "SomConnexio"
        self.eticom_contract.mobile_min = '100'

        MobileDataFromEticomContract(self.eticom_contract).build()

        mobile_data = MobileDataFromEticomContract(self.eticom_contract).build()

        self.assertEqual(mobile_data.service_minutes, "100min")

    @patch('otrs_somconnexio.otrs_models.factories.mobile_data_from_eticom_contract.TelecomCompany')
    def test_build_200min(self, MockTelecomCompany):
        MockTelecomCompany.return_value = "SomConnexio"
        self.eticom_contract.mobile_min = '200'

        mobile_data = MobileDataFromEticomContract(self.eticom_contract).build()

        self.assertEqual(mobile_data.service_minutes, "200min")

    @patch('otrs_somconnexio.otrs_models.factories.mobile_data_from_eticom_contract.TelecomCompany')
    def test_build_unlim(self, MockTelecomCompany):
        MockTelecomCompany.return_value = "SomConnexio"
        self.eticom_contract.mobile_min = 'unlimited'

        mobile_data = MobileDataFromEticomContract(self.eticom_contract).build()

        self.assertEqual(mobile_data.service_minutes, "unlim")

    @patch('otrs_somconnexio.otrs_models.factories.mobile_data_from_eticom_contract.TelecomCompany')
    def test_build_unlim_internet(self, MockTelecomCompany):
        MockTelecomCompany.return_value = "SomConnexio"
        self.eticom_contract.mobile_min = 'unlimited'
        self.eticom_contract.mobile_internet = None

        mobile_data = MobileDataFromEticomContract(self.eticom_contract).build()

        self.assertEqual(mobile_data.service_minutes, "unlim")
        self.assertEqual(mobile_data.service_internet, self.eticom_contract.mobile_internet_unlimited)

    @patch('otrs_somconnexio.otrs_models.factories.mobile_data_from_eticom_contract.TelecomCompany')
    def test_build_portability_previous_owner_info(self, MockTelecomCompany):
        MockTelecomCompany.return_value = "SomConnexio"
        self.eticom_contract.mobile_vat_number = None
        self.eticom_contract.mobile_name = None
        self.eticom_contract.mobile_surname = None

        self.eticom_contract.party = Mock(spec=['name', 'first_name', 'get_identifier'])
        self.eticom_contract.party.name = 'Joan'
        self.eticom_contract.party.first_name = 'Mey'
        self.eticom_contract.party.get_identifier.return_value = Mock(spec=['code'])
        self.eticom_contract.party.get_identifier.return_value.code = '09079514B'

        mobile_data = MobileDataFromEticomContract(self.eticom_contract).build()

        self.assertEqual(mobile_data.previous_owner_vat, "09079514B")
        self.assertEqual(mobile_data.previous_owner_name, self.eticom_contract.party.first_name)
        self.assertEqual(mobile_data.previous_owner_surname, self.eticom_contract.party.name)
