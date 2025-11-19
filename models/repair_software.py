from odoo import models, fields, api
from datetime import timedelta

class RepairSoftware(models.Model):
    _name = 'tech.repair.software'
    _description = 'Installed Software'

    name = fields.Char(string='Software', required=True, index=True)
    price = fields.Float(string='Price', required=True, default=0.0)
    renewal_required = fields.Boolean(string='Renewal Required', default=False)
    
    duration = fields.Selection([
        ('1', '1 Month'),
        ('3', '3 Months'),
        ('6', '6 Months'),
        ('12', '12 Months'),
        ('24', '24 Months')
    ], string="Software Duration", required=True, default='12')

    tech_repair_order_ids = fields.Many2many('tech.repair.order', string="Associated Jobs")
