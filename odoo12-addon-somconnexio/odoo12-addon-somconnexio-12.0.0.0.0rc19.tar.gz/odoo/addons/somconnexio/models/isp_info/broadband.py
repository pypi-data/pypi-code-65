from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BroadbandISPInfo(models.Model):
    _inherit = 'base.isp.info'

    _name = 'broadband.isp.info'
    _description = "Broadband ISP Info"
    service_address = fields.Many2one(
        'res.partner',
        required=True,
        string='Service Address')

    previous_service = fields.Selection(
        selection=[
            ('fiber', 'Fiber'),
            ('adsl', 'ADSL')
        ],
        string='Previous Service')

    keep_phone_number = fields.Boolean(string='Keep Phone Number')

    change_address = fields.Boolean(string='Change Address')

    @api.one
    @api.constrains('type', 'previous_service')
    def _check_broadband_protability_info(self):
        if self.type == 'new':
            return True
        if not self.previous_service:
            raise ValidationError(
                'Previous service is required in a portability'
            )
