from odoo import models, fields

class RepairDeviceVariant(models.Model):
    _name = 'tech.repair.device.variant'
    _description = 'Device Variant'

    name = fields.Char(string="Variant", required=True)
    model_id = fields.Many2one('tech.repair.device.model', string='Device Model', required=True)
