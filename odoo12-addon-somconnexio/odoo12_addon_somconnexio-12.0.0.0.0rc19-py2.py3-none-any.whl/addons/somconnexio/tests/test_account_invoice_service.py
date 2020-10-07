import json
from .common_service import BaseEMCRestCaseAdmin
import odoo
from datetime import date


class InvoiceServiceRestCase(BaseEMCRestCaseAdmin):

    def setUp(self):
        super().setUp()
        self.date_invoice = date(2021, 1, 31)
        self.partner = self.browse_ref('easy_my_coop.res_partner_cooperator_1_demo')
        self.product = self.browse_ref('somconnexio.Fibra100Mb')
        self.price_unit = 41
        self.quantity = 1
        self.account = self.env['account.account'].search([('code', '=', '430000')])
        self.account_taxes = self.env['account.account'].search(
            [('code', '=', '477000')]
        )
        self.oc_number = "12345"
        self.oc_amount_untaxed = 10.0
        self.oc_amount_taxes = 2.1
        if not self.account:
            self.account = self.env['account.account'].create({
                'code': '430000',
                'internal_type': 'receivable',
                'name': 'Clientes (euros)',
                'reconcile': True,
                'user_type_id': 1
            })

        if not self.account_taxes:
            self.account_taxes = self.env['account.account'].create({
                'code': '477000',
                'internal_group': 'liability',
                'name': 'Hacienda Pública. IVA repercutido',
                'reconcile': False,
                'user_type_id': 9
            })
        self.tax = self.env['account.tax'].search([
            ('name', '=', 'IVA 21% (Servicios)')
        ])
        self.account_tax_group = self.env['account.tax.group'].search(
            [('name', '=', 'IVA 21%')]
        )
        if not self.account_tax_group:
            self.account_tax_group = self.env['account.tax.group'].create({
                'name': 'IVA 21%'
            })
        if not self.tax:
            self.tax = self.env['account.tax'].create({
                'name': 'IVA 21% (Servicios)',
                'description': 'S_IVA21S',
                'type_tax_use': 'sale',
                'amount_type': 'percent',
                'amount': 21.0,
                'account_id': self.account_taxes.id,
                'refund_account_id': self.account_taxes.id,
                'tax_group_id': self.account_tax_group.id,
            })

    def test_route_right_create(self):
        url = "/api/invoice"
        data = {
            'partner_id': self.partner.id,
            'date_invoice': self.date_invoice.strftime("%Y-%m-%d"),
            'oc_number': self.oc_number,
        }

        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)
        invoice = self.env['account.invoice'].browse(content['id'])
        self.assertEquals(invoice.partner_id, self.partner)
        self.assertEquals(invoice.date_invoice, self.date_invoice)
        self.assertEquals(invoice.oc_number, self.oc_number)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_wrong_create_missing_partner_id(self):
        url = "/api/invoice"
        data = {
            'date_invoice': self.date_invoice.strftime("%Y-%m-%d"),
            'oc_number': self.oc_number,
        }
        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 400)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_wrong_create_bad_partner_id(self):
        url = "/api/invoice"
        data = {
            'partner_id': 0,
            'date_invoice': self.date_invoice.strftime("%Y-%m-%d"),
            'oc_number': self.oc_number,
        }
        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 400)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_wrong_create_missing_date_invoice(self):
        url = "/api/invoice"
        data = {
            'partner_id': self.partner.id,
            'oc_number': self.oc_number,
        }
        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 400)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_wrong_create_bad_format_date_invoice(self):
        url = "/api/invoice"
        data = {
            'partner_id': self.partner.id,
            'date_invoice': '6666-66-66',
            'oc_number': self.oc_number,
        }
        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 400)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_wrong_create_missing_oc_number(self):
        url = "/api/invoice"
        data = {
            'partner_id': self.partner.id,
            'date_invoice': self.date_invoice.strftime("%Y-%m-%d"),
        }
        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 400)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_wrong_create_bad_format_date_invoice(self):
        url = "/api/invoice"
        data = {
            'partner_id': self.partner.id,
            'date_invoice': self.date_invoice.strftime("%Y-%m-%d"),
            'oc_number': 1234,
        }
        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 400)

    def test_route_right_invoice_line(self):
        url = "/api/invoice"
        data = {
            'partner_id': self.partner.id,
            'date_invoice': self.date_invoice.strftime("%Y-%m-%d"),
            'oc_number': self.oc_number,
            'invoice_lines': [
                {
                    'product_code': self.product.default_code,
                    'oc_amount_untaxed': self.oc_amount_untaxed,
                    'oc_amount_taxes': self.oc_amount_taxes,
                }
            ]
        }
        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)
        invoice = self.env['account.invoice'].browse(content['id'])
        self.assertEquals(self.product, invoice.invoice_line_ids[0].product_id)
        self.assertEquals(
            self.oc_amount_untaxed,
            invoice.invoice_line_ids[0].price_subtotal
        )
        self.assertEquals(
            self.oc_amount_untaxed + self.oc_amount_taxes,
            invoice.invoice_line_ids[0].price_total)
        self.assertEquals(self.account, invoice.invoice_line_ids[0].account_id)
        self.assertEquals(invoice.amount_tax, self.oc_amount_taxes)
        self.assertEquals(invoice.amount_untaxed, self.oc_amount_untaxed)

    def test_create_right_regular_invoice(self):
        tax_id = self.env['account.tax'].search([
            ('name', '=', 'IVA 21% (Servicios)')
        ]).id
        invoice_line_params = {
            'name': self.product.name,
            'product_id': self.product.id,
            'quantity': self.quantity,
            'price_unit': self.price_unit,
            "account_id": self.env['account.account'].search(
                [('code', '=', '430000')]
            ).id,
            "invoice_line_tax_ids": [(4, tax_id, 0)]
        }
        invoice_line = self.env['account.invoice.line'].create(
            invoice_line_params
        )
        invoice_params = {
            'partner_id': self.partner.id,
            'date_invoice': self.date_invoice.strftime("%Y-%m-%d"),
            'invoice_line_ids': [(6, 0, [invoice_line.id])]
        }
        invoice = self.env['account.invoice'].create(invoice_params)
        self.env['account.invoice.line'].create(invoice_line_params)
        self.assertEquals(self.product, invoice.invoice_line_ids[0].product_id)
        self.assertEquals(
            self.quantity*self.price_unit,
            invoice.invoice_line_ids[0].price_subtotal
        )
        self.assertEquals(
            (self.quantity*self.price_unit)*1.21,
            invoice.invoice_line_ids[0].price_total
        )
        self.assertEquals(self.account, invoice.invoice_line_ids[0].account_id)
        self.assertEquals(invoice.amount_untaxed, self.quantity*self.price_unit)
        self.assertEquals(invoice.amount_total, (self.quantity*self.price_unit)*1.21)
