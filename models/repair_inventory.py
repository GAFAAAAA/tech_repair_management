from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RepairInventory(models.Model):
    _name = 'tech.repair.inventory'
    _description = 'Device Inventory'
    _order = 'create_date desc'

    name = fields.Char(string='Inventory Reference', compute='_compute_name', store=True)

    # Device information
    category_id = fields.Many2one(
        'tech.repair.device.category',
        string='Category',
        required=True,
    )
    brand_id = fields.Many2one('tech.repair.device.brand', string='Brand', required=True)
    model_id = fields.Many2one('tech.repair.device.model', string='Model', required=True)
    variant_id = fields.Many2one('tech.repair.device.variant', string='Variant')
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

    @api.onchange('category_id')
    def _onchange_category_id(self):
        """Clear brand, model, and variant when category changes"""
        if self.category_id:
            self.brand_id = False
            self.model_id = False
            self.variant_id = False
            # Return domain to filter brands that have models in this category
            model_ids = self.env['tech.repair.device.model'].search([
                ('category_id', '=', self.category_id.id)
            ])
            brand_ids = model_ids.mapped('brand_id').ids
            return {
                'domain': {
                    'brand_id': [('id', 'in', brand_ids)],
                    'model_id': [('id', '=', False)],
                    'variant_id': [('id', '=', False)],
                }
            }
        return {
            'domain': {
                'brand_id': [],
                'model_id': [('id', '=', False)],
                'variant_id': [('id', '=', False)],
            }
        }

    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        """Clear model and variant when brand changes"""
        if self.brand_id:
            self.model_id = False
            self.variant_id = False
            # Return domain to filter models by category and brand
            return {
                'domain': {
                    'model_id': [
                        ('category_id', '=', self.category_id.id),
                        ('brand_id', '=', self.brand_id.id)
                    ],
                    'variant_id': [('id', '=', False)],
                }
            }
        return {
            'domain': {
                'model_id': [('id', '=', False)],
                'variant_id': [('id', '=', False)],
            }
        }

    @api.onchange('model_id')
    def _onchange_model_id(self):
        """Clear variant when model changes and validate model matches category and brand"""
        if self.model_id:
            # Validate that the selected model matches the category and brand
            if self.model_id.category_id != self.category_id:
                self.model_id = False
                return {
                    'warning': {
                        'title': 'Invalid Model',
                        'message': 'The selected model does not belong to the chosen category.'
                    }
                }
            if self.model_id.brand_id != self.brand_id:
                self.model_id = False
                return {
                    'warning': {
                        'title': 'Invalid Model',
                        'message': 'The selected model does not belong to the chosen brand.'
                    }
                }
            self.variant_id = False
            # Return domain to filter variants by model
            return {
                'domain': {
                    'variant_id': [('model_id', '=', self.model_id.id)]
                }
            }
        return {
            'domain': {
                'variant_id': [('id', '=', False)]
            }
        }

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
                parts.append(record.variant_id.name)
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
                ('variant_id', '=', record.variant_id.id if record.variant_id else False),
                ('id', '!=', record.id),
                ('active', '=', True)
            ]
            if self.search_count(domain) > 0:
                variant_name = record.variant_id.name if record.variant_id else ''
                raise ValidationError(
                    f"A device with serial number '{record.serial_number}' for "
                    f"{record.category_id.name} {record.brand_id.name} {record.model_id.name} "
                    f"{variant_name} already exists in inventory."
                )
