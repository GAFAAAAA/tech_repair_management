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
    model_variant = fields.Char(string="Variant", help="e.g. 14x4.3")
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

    @api.depends('category_id', 'brand_id', 'model_id', 'model_variant', 'serial_number')
    def _compute_name(self):
        for record in self:
            parts = []
            if record.category_id:
                parts.append(record.category_id.name)
            if record.brand_id:
                parts.append(record.brand_id.name)
            if record.model_id:
                parts.append(record.model_id.name)
            if record.model_variant:
                parts.append(record.model_variant)
            if record.serial_number:
                parts.append(f"S/N: {record.serial_number}")
            record.name = ' - '.join(parts) if parts else 'New Inventory Item'

    @api.constrains('serial_number', 'category_id', 'brand_id', 'model_id', 'model_variant')
    def _check_unique_serial(self):
        for record in self:
            domain = [
                ('serial_number', '=', record.serial_number),
                ('category_id', '=', record.category_id.id),
                ('brand_id', '=', record.brand_id.id),
                ('model_id', '=', record.model_id.id),
                ('model_variant', '=', record.model_variant),
                ('id', '!=', record.id),
                ('active', '=', True)
            ]
            if self.search_count(domain) > 0:
                raise ValidationError(
                    f"A device with serial number '{record.serial_number}' for "
                    f"{record.category_id.name} {record.brand_id.name} {record.model_id.name} "
                    f"{record.model_variant or ''} already exists in inventory."
                )

    @api.constrains('brand_id', 'model_id')
    def _check_brand_and_model_required(self):
        for rec in self:
            if not rec.brand_id:
                raise ValidationError("Brand is required.")
            if not rec.model_id:
                raise ValidationError("Model is required.")

    @api.onchange('category_id')
    def _onchange_category_id(self):
        if self.category_id:
            self.brand_id = False
            self.model_id = False

    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        self.model_id = False
        domain = {'model_id': [('brand_id', '=', self.brand_id.id)]} if self.brand_id else {'model_id': []}
        return {'domain': domain}

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.model_id:
            self.brand_id = self.model_id.brand_id
            # Show only models that match the brand
            if self.model_id.brand_id:
                return {'domain': {'model_id': [('brand_id', '=', self.model_id.brand_id.id)]}}
        return {'domain': {'model_id': []}}