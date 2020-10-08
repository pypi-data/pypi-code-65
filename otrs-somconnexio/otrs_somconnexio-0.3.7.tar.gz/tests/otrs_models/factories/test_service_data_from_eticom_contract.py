import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.factories.service_data_from_eticom_contract \
    import ServiceDataFromEticomContract


class ServiceDataFromEticomContractTestCase(unittest.TestCase):

    def setUp(self):
        self.eticom_contract = Mock(spec=['id', 'service', 'internet_contract'])

    @patch('otrs_somconnexio.otrs_models.factories.service_data_from_eticom_contract.MobileDataFromEticomContract')
    def test_mobile_service(self, MockMobileDataFromEticomContract):
        expected_mobile_data = object()

        self.eticom_contract.service = 'mobile'

        MockMobileDataFromEticomContract.return_value = Mock(spec=['build'])
        MockMobileDataFromEticomContract.return_value.build.return_value = expected_mobile_data

        mobile_data = ServiceDataFromEticomContract(self.eticom_contract).build()

        MockMobileDataFromEticomContract.assert_called_once_with(self.eticom_contract)
        self.assertEqual(mobile_data, expected_mobile_data)

    @patch('otrs_somconnexio.otrs_models.factories.service_data_from_eticom_contract.ADSLDataFromEticomContract')
    def test_adsl_service(self, MockADSLDataFromEticomContract):
        expected_adsl_data = object()

        self.eticom_contract.service = 'adsl'
        self.eticom_contract.internet_contract = 'adsl'

        MockADSLDataFromEticomContract.return_value = Mock(spec=['build'])
        MockADSLDataFromEticomContract.return_value.build.return_value = expected_adsl_data

        adsl_data = ServiceDataFromEticomContract(self.eticom_contract).build()

        MockADSLDataFromEticomContract.assert_called_once_with(self.eticom_contract)
        self.assertEqual(adsl_data, expected_adsl_data)

    @patch('otrs_somconnexio.otrs_models.factories.service_data_from_eticom_contract.FiberDataFromEticomContract')
    def test_fiber_service(self, MockFiberDataFromEticomContract):
        expected_fiber_data = object()

        self.eticom_contract.service = 'adsl'
        self.eticom_contract.internet_contract = 'fibre'

        MockFiberDataFromEticomContract.return_value = Mock(spec=['build'])
        MockFiberDataFromEticomContract.return_value.build.return_value = expected_fiber_data

        fiber_data = ServiceDataFromEticomContract(self.eticom_contract).build()

        MockFiberDataFromEticomContract.assert_called_once_with(self.eticom_contract)
        self.assertEqual(fiber_data, expected_fiber_data)
