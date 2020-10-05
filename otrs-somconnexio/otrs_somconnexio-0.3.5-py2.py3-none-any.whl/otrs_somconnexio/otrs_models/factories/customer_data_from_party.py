from otrs_somconnexio.otrs_models.customer_data import CustomerData


# TODO: This library is not the place for this factory class.
# This class must live in the project that uses this library.
# That project knows the structure of its data model and can create directly a CustomerData object and use it.
# This factory is for Tryton. In Tryton we can't test this functionality and by this reason it's here.

class CustomerDataFromParty:

    def __init__(self, party):
        self.party = party

    def build(self):
        return CustomerData(
            id=self.party.id,
            vat_number=self._vat_number(),
            email=self._email(),
            phone=self._phone(),
            name=self.party.name,
            first_name=self.party.first_name
        )

    def _vat_number(self):
        return self.party.get_identifier().code

    def _email(self):
        return self.party.get_contact_email().value

    def _phone(self):
        return self.party.get_contact_phone().value
