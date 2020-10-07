from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BaseISPInfo(models.AbstractModel):
    _name = 'base.isp.info'
    phone_number = fields.Char(string='Phone Number')
    delivery_address = fields.Many2one('res.partner',
                                       required=True,
                                       string='Delivery Address')
    type = fields.Selection([('portability', 'Portability'), ('new', 'New')],
                            default='new',
                            string='Type')
    previous_provider = fields.Many2one('previous.provider',
                                        string='Previous Provider')
    previous_owner_vat_number = fields.Char(string='Previous Owner VatNumber')
    previous_owner_first_name = fields.Char(string='Previous Owner First Name')
    previous_owner_name = fields.Char(string='Previous Owner Name')

    def name_get(self):
        res = []
        for item in self:
            if item.type == 'new':
                res.append((item.id, 'New'))
            else:
                res.append((item.id, item.phone_number))
        return res

    @api.one
    @api.constrains(
        'type', 'previous_provider', 'previous_owner_vat_number',
        'previous_owner_name', 'previous_owner_first_name', 'phone_number')
    def _check_protability_info(self):
        if self.type == 'new':
            return True
        if not self.previous_provider:
            raise ValidationError(
                'Previous provider is required in a portability'
            )
        if not self.phone_number:
            raise ValidationError(
                'Phone number is required in a portability'
            )
        if (not self.previous_owner_vat_number or not self.previous_owner_first_name or
                not self.previous_owner_name):
            raise ValidationError(
                'Previous owner info is required in a portability'
            )
