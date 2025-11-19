from odoo import models, fields

#brand management module
class RepairBrand(models.Model):
    _name = 'tech.repair.brand'
    _description = 'Device Brand'

    name = fields.Char(string='Brand', required=True)
    
