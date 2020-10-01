from odoo import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    subscription_request_id = fields.Many2one(
        'subscription.request', 'Subscription Request'
    )
    iban = fields.Char(string="IBAN")

    def write(self, values):
        crm_lead = super(CrmLead, self).write(values)
        if values.get('stage_id', 0) == self.env.ref('crm.stage_lead4').id:
            self.call_otrs()
        return crm_lead

    def call_otrs(self):
        for line in self.lead_line_ids:
            self.env['crm.lead.line'].with_delay().create_ticket(line.id)
