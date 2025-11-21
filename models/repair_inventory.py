from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RepairInventory(models.Model):
    _name = 'tech.repair.inventory'
    _description = 'Device Inventory'
    _order = 'create_date desc'

    name = fields.Char(string='Inventory Reference', compute='_compute_name', store=True)

    # Device information
    category_id = fields.Many2one(
        related='model_id.category_id',
        comodel_name='tech.repair.device.category',
        string='Category',
        store=True,
        readonly=True,
    )
    brand_id = fields.Many2one('tech.repair.device.brand', string='Brand')  # No required=True here!
    model_id = fields.Many2one('tech.repair.device.model', string='Model', domain=[],)  # No required=True, no domain in field!
    variant_id = fields.Many2one('tech.repair.device.variant', string='Variant', domain=[],)
    serial_number = fields.Char(string='Serial Number', required=True)
    
    # Status tracking
    status = fields.Selection([
        ('available', 'Available'),
        ('in_repair', 'In Repair'),
        ('returned', 'Returned to Customer')
    ], string='Status', default='available', required=True)
    
    # Link to repair order if in use
    repair_order_id = fields.Many2one('tech.repair.order', string='Current Repair Order', readonly=True)
    
    # Audit fields
    check_in_date = fields.Datetime(string='Check-in Date', default=lambda self: fields.Datetime.now(), readonly=True)
    checked_in_by = fields.Many2one('res.users', string='Checked In By', default=lambda self: self.env.user, readonly=True)
    
    notes = fields.Text(string='Notes')

    active = fields.Boolean(default=True, string="Active")

    @api.depends('category_id', 'brand_id', 'model_id', 'variant_id', 'serial_number')
    def _compute_name(self):
        for record in self:
            parts = []
            if record.category_id:
                parts.append(record.category_id.name)
            if record.brand_id:
                parts.append(record.brand_id.name)
            if record.model_id:
                parts.append(record.model_id.name)
            if record.variant_id:
                parts.append(record.variant_id)
            if record.serial_number:
                parts.append(f"S/N: {record.serial_number}")
            record.name = ' - '.join(parts) if parts else 'New Inventory Item'

    @api.constrains('serial_number', 'category_id', 'brand_id', 'model_id', 'variant_id')
    def _check_unique_serial(self):
        for record in self:
            domain = [
                ('serial_number', '=', record.serial_number),
                ('category_id', '=', record.category_id.id),
                ('brand_id', '=', record.brand_id.id),
                ('model_id', '=', record.model_id.id),
                ('variant_id', '=', record.variant_id),
                ('id', '!=', record.id),
                ('active', '=', True)
            ]
            if self.search_count(domain) > 0:
                raise ValidationError(
                    f"A device with serial number '{record.serial_number}' for "
                    f"{record.category_id.name} {record.brand_id.name} {record.model_id.name} "
                    f"{record.variant_id or ''} already exists in inventory."
                )
