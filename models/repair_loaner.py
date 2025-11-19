from odoo import models, fields

class RepairLoanerDevice(models.Model):
    _name = 'tech.repair.loaner_device'
    _description = 'Loaner Devices'

    name = fields.Char(string='Device Name', required=True)
    serial_number = fields.Char(string='Serial / IMEI', required=True)
    aesthetic_condition = fields.Selection([
        ('new', 'New'),
        ('good', 'Good'),
        ('used', 'Used'),
        ('damaged', 'Damaged')
    ], string='Aesthetic Condition', default='good')
    description = fields.Text(string='Description')
    tech_repair_order_id = fields.Many2one('tech.repair.order', string='Assigned to Repair', ondelete='set null')

    status = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'In Maintenance')
    ], string='Status', default='available')

    def name_get(self):
        # Customize display in Many2one fields
        result = []
        for device in self:
            name = f"{device.name} ({device.serial_number})"
            result.append((device.id, name))
        return result
    
    def mark_as_available(self):
        # Method to release the loaner and make it available again """
        for record in self:
            record.status = 'available'
            record.tech_repair_order_id = False
    
