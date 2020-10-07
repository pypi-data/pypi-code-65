from otrs_somconnexio.otrs_models.mobile_data import MobileData
from otrs_somconnexio.otrs_models.telecom_company import TelecomCompany


# TODO: This library is not the place for this factory class.
# This class must live in the project that uses this library.
# That project knows the structure of its data model and can create directly a MobileData object and use it.
# This factory is for Tryton. In Tryton we can't test this functionality and by this reason it's here.

class MobileDataFromEticomContract:

    def __init__(self, eticom_contract):
        self.eticom_contract = eticom_contract

    def build(self):
        return MobileData(
            order_id=self.eticom_contract.id,
            phone_number=self.eticom_contract.mobile_phone_number,
            iban=self.eticom_contract.bank_iban_service,
            sc_icc=self.eticom_contract.mobile_sc_icc,
            icc=self.eticom_contract.mobile_icc_number,
            service_minutes=self._service_minutes(),
            service_internet=self._service_internet(),
            portability=self._portability(),
            previous_provider=self._previous_provider(),
            previous_owner_vat=(self.eticom_contract.mobile_vat_number
                                or self.eticom_contract.party.get_identifier().code),
            previous_owner_name=self.eticom_contract.mobile_name or self.eticom_contract.party.first_name,
            previous_owner_surname=self.eticom_contract.mobile_surname or self.eticom_contract.party.name,

            product=None
        )

    def _portability(self):
        if self.eticom_contract.mobile_option == 'portability':
            return True
        return False

    def _previous_provider(self):
        return str(TelecomCompany('mobile', self.eticom_contract.mobile_telecom_company))

    def _service_minutes(self):
        minutes = {
            "0": "0min",
            "100": "100min",
            "200": "200min",
            "unlimited": "unlim",
        }
        return minutes[self.eticom_contract.mobile_min]

    def _service_internet(self):
        data = self.eticom_contract.mobile_internet
        if not data:
            data = self.eticom_contract.mobile_internet_unlimited
        return data
