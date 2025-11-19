from odoo import models, fields

class RepairDeviceColor(models.Model):
    _name = 'tech.repair.device.color'
    _description = 'Device Colors'

    name = fields.Char(string="Color", required=True)
