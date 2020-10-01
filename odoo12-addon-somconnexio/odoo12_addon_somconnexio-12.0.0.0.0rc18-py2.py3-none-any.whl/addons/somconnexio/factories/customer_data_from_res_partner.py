from otrs_somconnexio.otrs_models.customer_data import CustomerData


class CustomerDataFromResPartner:

    def __init__(self, partner):
        self.partner = partner

    def build(self):
        return CustomerData(
            id=self.partner.id,
            vat_number=self.partner.vat,
            email=self.partner.email,
            phone=self.partner.mobile or self.partner.phone,
            name=self.partner.name,
            first_name=self.partner.name
        )
