from otrs_somconnexio.otrs_models.fiber_data import FiberData


class FiberDataFromCRMLeadLine:

    def __init__(self, crm_lead_line):
        self.crm_lead_line = crm_lead_line

    def build(self):
        isp_info = self.crm_lead_line.broadband_isp_info
        service_address = isp_info.service_address

        return FiberData(
            order_id=self.crm_lead_line.id,
            phone_number=isp_info.phone_number,
            service_address=service_address.street,
            service_city=service_address.city,
            service_zip=service_address.zip,
            service_subdivision=service_address.state_id.name,
            shipment_address=isp_info.delivery_address.street,
            shipment_city=isp_info.delivery_address.city,
            shipment_zip=isp_info.delivery_address.zip,
            shipment_subdivision=isp_info.delivery_address.state_id.name,
            previous_provider=isp_info.previous_provider.name or 'None',
            previous_owner_vat=isp_info.previous_owner_vat_number or '',
            previous_owner_name=isp_info.previous_owner_first_name or '',
            previous_owner_surname=isp_info.previous_owner_name or '',
            previous_service=isp_info.previous_service,
            notes=self.crm_lead_line.lead_id.description,
            iban=self.crm_lead_line.lead_id.iban,
            product=self.crm_lead_line.product_id.default_code,

            # TODO: We need to define the ChangeAddress wizard to fill this fields.
            adsl_coverage='',
            mm_fiber_coverage='',
            vdf_fiber_coverage='',
            change_address='no',
            previous_internal_provider='',

            # TODO: To be removed when we will unsupport Tryton
            internet_speed='',
        )
