import logging
from odoo.addons.component.core import Component
from . import schemas
from werkzeug.exceptions import BadRequest
from odoo.addons.base_rest.http import wrapJsonException

_logger = logging.getLogger(__name__)


class AccountInvoiceService(Component):
    _inherit = "account.invoice.service"

    def create(self, **params):
        params = self._prepare_create(params)
        # tracking_disable=True in context is needed
        # to avoid to send a mail in Account Invoice creation
        invoice = self.env["account.invoice"].with_context(
            tracking_disable=True
        ).create(params)
        return self._to_dict(invoice)

    def _validator_create(self):
        return schemas.S_ACCOUNT_INVOICE_CREATE

    def _validator_return_create(self):
        return schemas.S_ACCOUNT_INVOICE_RETURN_CREATE

    def _prepare_create_line(self, line):
        product = self.env["product.product"].search(
            [('default_code', '=', line["product_code"])]
        )
        if not product:
            raise wrapJsonException(
                BadRequest(
                    'Product with code %s not found' % (
                        line['product_code'], )
                )
            )
        tax_id = self.env['account.tax'].search([
            ('name', '=', 'IVA 21% (Servicios)')
        ]).id
        response_line = {
            "name": product.name,
            "product_id": product.id,
            "oc_amount_untaxed": line['oc_amount_untaxed'],
            "oc_amount_taxes": line['oc_amount_taxes'],
            "account_id": self.env['account.account'].search(
                [('code', '=', '430000')]
            ).id,
            "invoice_line_tax_ids": [(4, tax_id, 0)]
        }
        return response_line

    def _prepare_create(self, params):
        if (
            'partner_id' in params
            and not self.env['res.partner'].search(
                [('id', '=', params['partner_id'])]
            )
        ):
            raise wrapJsonException(
                BadRequest(
                    'Partner with id %s not found' % (
                        params['partner_id'],)
                )
            )
        if 'invoice_lines' in params:
            lines = [
                self.env['account.invoice.line'].create(
                    self._prepare_create_line(line)
                ).id
                for line in params['invoice_lines']
            ]
        else:
            lines = []
        return {
            "partner_id": params.get("partner_id"),
            "date_invoice": params.get('date_invoice'),
            "oc_number": params.get('oc_number'),
            "invoice_line_ids": [(6, 0, lines)],
        }

    @staticmethod
    def _to_dict(account_invoice):
        return {
            "id": account_invoice.id
        }
