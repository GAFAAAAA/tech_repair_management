from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    repair_order_id = fields.Many2one(
        'tech.repair.order',
        string="Repair Job",
        help="Repair Job associated with the Lead"
    )
