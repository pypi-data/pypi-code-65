from otrs_somconnexio.otrs_models.customer_data import CustomerData


# TODO: This library is not the place for this factory class.
# This class must live in the project that uses this library.
# That project knows the structure of its data model and can create directly a CustomerData object and use it.
# This factory is for Tryton. In Tryton we can't test this functionality and by this reason it's here.

class CustomerDataFromParty:

    def __init__(self, party):
        self.party = party

    def build(self):
        contact_address = self.party.get_contact_address()
        return CustomerData(
            id=self.party.id,
            vat_number=self.party.get_identifier().code,
            email=self.party.get_contact_email().value,
            phone=self.party.get_contact_phone().value,
            name=self.party.name,
            first_name=self.party.first_name,
            street=contact_address.street,
            city=contact_address.city,
            zip=contact_address.zip,
            subdivision=contact_address.subdivision.code,
        )
