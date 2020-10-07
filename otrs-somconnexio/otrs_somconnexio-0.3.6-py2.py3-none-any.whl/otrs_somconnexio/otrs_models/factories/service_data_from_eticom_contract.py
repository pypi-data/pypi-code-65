from otrs_somconnexio.otrs_models.factories.mobile_data_from_eticom_contract \
    import MobileDataFromEticomContract
from otrs_somconnexio.otrs_models.factories.fiber_data_from_eticom_contract \
    import FiberDataFromEticomContract
from otrs_somconnexio.otrs_models.factories.adsl_data_from_eticom_contract \
    import ADSLDataFromEticomContract


# TODO: This library is not the place for this factory class.
# This class must live in the project that uses this library.
# That project knows the structure of its data model and can create directly a CustomerData object and use it.
# This factory is for Tryton. In Tryton we can't test this functionality and by this reason it's here.

class ServiceDataFromEticomContract:
    def __init__(self, eticom_contract):
        self.eticom_contract = eticom_contract

    def build(self):
        if self.eticom_contract.service == 'mobile':
            return MobileDataFromEticomContract(self.eticom_contract).build()
        elif self.eticom_contract.service == 'adsl':
            return self._internet_type()

    def _internet_type(self):
        """ This method is called when the service is `adsl` (really is `internet`)"""
        if self.eticom_contract.internet_contract == 'adsl':
            return ADSLDataFromEticomContract(self.eticom_contract).build()
        # I need change this typo. Fibre not exist, is fiber!
        if self.eticom_contract.internet_contract == 'fibre':
            return FiberDataFromEticomContract(self.eticom_contract).build()
