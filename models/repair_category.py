from odoo import models, fields

# category management
class RepairCategory(models.Model):

    _name = 'tech.repair.category'
    _description = 'Device Category'

    name = fields.Char(string='Category', required=True)