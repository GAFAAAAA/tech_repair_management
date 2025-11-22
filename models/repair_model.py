from odoo import models, fields

# repair device management
class RepairModel(models.Model):
    _name = 'tech.repair.model'
    _description = 'Device Model'

    name = fields.Char(string='Model', required=True)
    brand_id = fields.Many2one('tech.repair.brand', string='Brand')

    category_id = fields.Many2one('tech.repair.category', string='Category')
    variants = fields.one2many('tech.repair.variant', 'model_id', string='Variants')
    