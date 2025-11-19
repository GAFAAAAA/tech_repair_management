from odoo import models, fields

class RepairDeviceCategory(models.Model):
    _name = 'tech.repair.device.category'
    _description = 'Repair Device Category'

    name = fields.Char(string='Category', required=True)


class RepairDeviceBrand(models.Model):
    _name = 'tech.repair.device.brand'
    _description = 'Repair Device Brand'

    name = fields.Char(string='Brand', required=True)


class RepairDeviceModel(models.Model):
    _name = 'tech.repair.device.model'
    _description = 'Repair Device Model'

    name = fields.Char(string='Model', required=True)
    brand_id = fields.Many2one('tech.repair.device.brand', string='Brand', required=True)
