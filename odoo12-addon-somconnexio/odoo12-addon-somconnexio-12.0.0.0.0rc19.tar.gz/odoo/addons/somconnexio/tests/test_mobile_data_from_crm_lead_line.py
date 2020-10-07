from odoo.tests.common import TransactionCase

from odoo.addons.somconnexio.factories.mobile_data_from_crm_lead_line \
    import MobileDataFromCRMLeadLine


class MobileDataFromCRMLeadLineTest(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.crm_lead_line_args = {
            'name': 'New CRMLeadLine',
            'product_id': self.ref('somconnexio.100Min1GB'),
            'mobile_isp_info': None,
            'broadband_isp_info': None,
        }

    def test_build(self):
        mobile_isp_info = self.env['mobile.isp.info'].create({
            'delivery_address': self.ref(
                'easy_my_coop.res_partner_cooperator_2_demo'
            ),
            'type': 'new',
        })
        self.crm_lead_line_args['mobile_isp_info'] = mobile_isp_info.id
        crm_lead_line = self.env['crm.lead.line'].create(
            self.crm_lead_line_args)

        mobile_data = MobileDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(mobile_data.order_id, crm_lead_line.id)
        self.assertFalse(mobile_data.portability)
        self.assertEqual(mobile_data.iban, crm_lead_line.lead_id.iban)
        self.assertEqual(mobile_data.product, crm_lead_line.product_id.default_code)

    def test_portability_build(self):
        mobile_isp_info = self.env['mobile.isp.info'].create({
            'phone_number': '666666666',
            'delivery_address': self.ref(
                'easy_my_coop.res_partner_cooperator_2_demo'
            ),
            'type': 'portability',
            'previous_owner_name': 'Mora',
            'previous_owner_first_name': 'Josep',
            'previous_owner_vat_number': '61518707D',
            'previous_provider': 1,
            'previous_contract_type': 'contract',
            'icc_donor': '4343434',
            'icc': '123123421',
        })
        self.crm_lead_line_args['mobile_isp_info'] = mobile_isp_info.id
        crm_lead_line = self.env['crm.lead.line'].create(
            self.crm_lead_line_args)

        mobile_data = MobileDataFromCRMLeadLine(crm_lead_line).build()

        self.assertTrue(mobile_data.portability)
        self.assertEqual(mobile_data.phone_number, mobile_isp_info.phone_number)
        self.assertEqual(
            mobile_data.previous_owner_vat,
            mobile_isp_info.previous_owner_vat_number)
        self.assertEqual(
            mobile_data.previous_owner_name,
            mobile_isp_info.previous_owner_first_name)
        self.assertEqual(
            mobile_data.previous_owner_surname,
            mobile_isp_info.previous_owner_name)
        self.assertEqual(
            mobile_data.previous_provider,
            mobile_isp_info.previous_provider.name)
        self.assertEqual(mobile_data.sc_icc, mobile_isp_info.icc)
        self.assertEqual(mobile_data.icc, mobile_isp_info.icc_donor)
