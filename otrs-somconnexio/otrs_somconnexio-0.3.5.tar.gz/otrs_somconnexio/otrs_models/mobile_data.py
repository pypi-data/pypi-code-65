class MobileData:
    type = 'mobile'

    def __init__(
        self, order_id, phone_number, iban, sc_icc, icc,
        service_minutes, service_internet, portability, previous_owner_vat,
            previous_owner_name, previous_owner_surname, previous_provider, product):
        self.order_id = order_id
        self.phone_number = phone_number
        self.iban = iban
        self.sc_icc = sc_icc
        self.icc = icc
        self.service_minutes = service_minutes
        self.service_internet = service_internet
        self.portability = portability
        self.previous_provider = previous_provider
        self.previous_owner_vat = previous_owner_vat
        self.previous_owner_name = previous_owner_name
        self.previous_owner_surname = previous_owner_surname

        self.product = product
