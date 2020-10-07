from odoo.tests.common import TransactionCase

from odoo.addons.somconnexio.factories.adsl_data_from_crm_lead_line \
    import ADSLDataFromCRMLeadLine


class ADSLDataFromCRMLeadLineTest(TransactionCase):
    "ADSLDataFromCRMLeadLineTest"

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.crm_lead_line_args = {
            'name': 'New CRMLeadLine',
            'product_id': self.ref('somconnexio.ADSL20MB100MinFixMobile'),
            'mobile_isp_info': None,
            'broadband_isp_info': None,
        }

    def test_build(self):
        broadband_isp_info = self.env['broadband.isp.info'].create({
            'delivery_address': self.ref(
                'easy_my_coop.res_partner_cooperator_2_demo'
            ),
            'type': 'new',
            'service_address': self.ref(
                'easy_my_coop.res_partner_cooperator_2_demo'
            ),
        })
        self.crm_lead_line_args['broadband_isp_info'] = broadband_isp_info.id
        crm_lead_line = self.env['crm.lead.line'].create(
            self.crm_lead_line_args)

        adsl_data = ADSLDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(adsl_data.order_id, crm_lead_line.id)
        self.assertFalse(adsl_data.phone_number)
        self.assertEqual(
            adsl_data.service_address,
            broadband_isp_info.service_address.street)
        self.assertEqual(
            adsl_data.service_city,
            broadband_isp_info.service_address.city)
        self.assertEqual(
            adsl_data.service_zip,
            broadband_isp_info.service_address.zip)
        self.assertEqual(
            adsl_data.service_subdivision,
            broadband_isp_info.service_address.state_id.name)
        self.assertEqual(
            adsl_data.shipment_address,
            broadband_isp_info.delivery_address.street)
        self.assertEqual(
            adsl_data.shipment_city,
            broadband_isp_info.delivery_address.city)
        self.assertEqual(
            adsl_data.shipment_zip,
            broadband_isp_info.delivery_address.zip)
        self.assertEqual(
            adsl_data.shipment_subdivision,
            broadband_isp_info.delivery_address.state_id.name)
        self.assertEqual(adsl_data.notes, crm_lead_line.lead_id.description)
        self.assertEqual(adsl_data.iban, crm_lead_line.lead_id.iban)
        self.assertEqual(adsl_data.landline_phone_number, 'new_number')
        self.assertEqual(adsl_data.product, crm_lead_line.product_id.default_code)

    def test_portability_build(self):
        broadband_isp_info = self.env['broadband.isp.info'].create({
            'phone_number': '666666666',
            'delivery_address': self.ref(
                'easy_my_coop.res_partner_cooperator_2_demo'
            ),
            'type': 'portability',
            'service_address': self.ref(
                'easy_my_coop.res_partner_cooperator_2_demo'
            ),
            'keep_phone_number': True,
            'previous_owner_name': 'Mora',
            'previous_owner_first_name': 'Josep',
            'previous_owner_vat_number': '61518707D',
            'previous_provider': 1,
            'previous_service': 'adsl',
        })
        self.crm_lead_line_args['broadband_isp_info'] = broadband_isp_info.id
        crm_lead_line = self.env['crm.lead.line'].create(
            self.crm_lead_line_args)

        adsl_data = ADSLDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(adsl_data.phone_number, broadband_isp_info.phone_number)
        self.assertEqual(adsl_data.landline_phone_number, 'current_number')
        self.assertEqual(
            adsl_data.previous_owner_vat,
            broadband_isp_info.previous_owner_vat_number)
        self.assertEqual(
            adsl_data.previous_owner_name,
            broadband_isp_info.previous_owner_first_name)
        self.assertEqual(
            adsl_data.previous_owner_surname,
            broadband_isp_info.previous_owner_name)
        self.assertEqual(
            adsl_data.previous_provider,
            broadband_isp_info.previous_provider.name)
        self.assertEqual(
            adsl_data.previous_service,
            broadband_isp_info.previous_service)
