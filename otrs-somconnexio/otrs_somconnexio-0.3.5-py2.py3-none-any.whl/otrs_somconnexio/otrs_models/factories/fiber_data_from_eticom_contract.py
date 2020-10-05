from future.utils import bytes_to_native_str as n

from otrs_somconnexio.otrs_models.fiber_data import FiberData
from otrs_somconnexio.otrs_models.telecom_company import TelecomCompany


# TODO: This library is not the place for this factory class.
# This class must live in the project that uses this library.
# That project knows the structure of its data model and can create directly a FiberDSLData object and use it.
# This factory is for Tryton. In Tryton we can't test this functionality and by this reason it's here.

class FiberDataFromEticomContract:

    def __init__(self, eticom_contract):
        self.eticom_contract = eticom_contract

    def build(self):
        return FiberData(
            order_id=self.eticom_contract.id,
            phone_number=self.eticom_contract.internet_phone_now,
            iban=self.eticom_contract.bank_iban_service,
            previous_provider=self._previous_provider(),
            previous_internal_provider=self.eticom_contract.provider_change_address,
            previous_owner_vat=self.eticom_contract.internet_vat_number,
            previous_owner_name=self._previous_owner_name(),
            previous_owner_surname=self._previous_owner_surname(),

            service_address=self.eticom_contract.internet_street,
            service_city=self.eticom_contract.internet_city,
            service_zip=self.eticom_contract.internet_zip,
            service_subdivision=self.eticom_contract.internet_subdivision.name,
            shipment_address=self.eticom_contract.internet_delivery_street or self.eticom_contract.internet_street,
            shipment_city=self.eticom_contract.internet_delivery_city or self.eticom_contract.internet_city,
            shipment_zip=self.eticom_contract.internet_delivery_zip or self.eticom_contract.internet_zip,
            shipment_subdivision=self._shipment_subdivision(),
            previous_service=self._previous_service(),
            notes=n(u"{}".format(self.eticom_contract.notes or '').encode('utf8')),
            adsl_coverage=self._adsl_coverage() or 'NoRevisat',
            mm_fiber_coverage=self._mm_fiber_coverage() or 'NoRevisat',
            vdf_fiber_coverage=self._vdf_fiber_coverage() or 'NoRevisat',
            change_address='yes' if self.eticom_contract.change_address else 'no',

            internet_speed=self.eticom_contract.internet_speed,

            product=None
        )

    def _adsl_coverage(self):
        try:
            return self.eticom_contract.coverage_availability.adsl
        except AttributeError:
            return None

    def _mm_fiber_coverage(self):
        try:
            return self.eticom_contract.coverage_availability.mm_fiber
        except AttributeError:
            return None

    def _vdf_fiber_coverage(self):
        try:
            return self.eticom_contract.coverage_availability.vdf_fiber
        except AttributeError:
            return None

    def _shipment_subdivision(self):
        try:
            return self.eticom_contract.internet_delivery_subdivision.name
        except AttributeError:
            return self.eticom_contract.internet_subdivision.name

    def _previous_owner_name(self):
        """ Concatenate name, surname and lastname. """
        name = self.eticom_contract.internet_name
        surname = self.eticom_contract.internet_surname
        lastname = self.eticom_contract.internet_lastname
        return n(u"{} {} {}".format(name, surname, lastname).encode("utf8"))

    def _previous_owner_surname(self):
        """ Concatenate surname and lastname. """
        surname = self.eticom_contract.internet_surname
        lastname = self.eticom_contract.internet_lastname
        return n(u"{} {}".format(surname, lastname).encode("utf8"))

    def _previous_provider(self):
        return str(TelecomCompany('internet', self.eticom_contract.internet_telecom_company))

    def _previous_service(self):
        if self.eticom_contract.internet_now == 'adsl':
            value = 'ADSL'
        elif self.eticom_contract.internet_now == 'fibre':
            value = 'Fibra'
        else:
            value = 'None'
        return value
