from odoo import models, fields, api

class RepairOrderDevice(models.Model):
    """Device line items for repair orders - supports multiple devices per order"""
    _name = 'tech.repair.order.device'
    _description = 'Repair Order Device Line'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    repair_order_id = fields.Many2one('tech.repair.order', string='Repair Order', required=True, ondelete='cascade')
    
    # Device configuration
    category_id = fields.Many2one('tech.repair.device.category', string='Category', required=True)
    brand_id = fields.Many2one('tech.repair.device.brand', string='Brand', required=True)
    model_id = fields.Many2one('tech.repair.device.model', string='Model', required=True, domain="[('brand_id', '=', brand_id)]")
    variant_id =  fields.Many2one('tech.repair.device.variant', string='Variant', required=False)
    
    # Serial number from inventory
    inventory_id = fields.Many2one(
        'tech.repair.inventory',
        string='Serial Number',
        required=True,
        domain="[('category_id', '=', category_id), ('brand_id', '=', brand_id), ('model_id', '=', model_id), ('variant_id', '=', variant_id), ('status', '=', 'available')]",
        help="Select from available inventory items"
    )
    
    serial_number = fields.Char(related='inventory_id.serial_number', string='S/N', readonly=True, store=True)
    
    # Display name
    name = fields.Char(string='Device', compute='_compute_name', store=True)
    
    # Device details (optional, for additional info)
    aesthetic_condition = fields.Selection([
        ('new', 'New'),
        ('good', 'Good'),
        ('used', 'Used'),
        ('damaged', 'Damaged')
    ], string='Aesthetic Condition', default='good')
    aesthetic_state = fields.Char(string='Visual Defects', help="If there are visible damages/scratches, write them here")

    @api.depends('category_id', 'brand_id', 'model_id', 'variant_id', 'serial_number')
    def _compute_name(self):
        """Generate a display name for the device line"""
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
                parts.append(f"(S/N: {record.serial_number})")
            record.name = ' '.join(parts) if parts else 'Device'

    @api.onchange('category_id')
    def _onchange_category_id(self):
        """Clear dependent fields when category changes"""
        if self.category_id:
            self.brand_id = False
            self.model_id = False
            self.variant_id = False
            self.inventory_id = False

    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        """Clear dependent fields when brand changes"""
        if self.brand_id:
            self.model_id = False
            self.variant_id = False
            self.inventory_id = False

    @api.onchange('model_id')
    def _onchange_model_id(self):
        """Clear dependent fields when model changes"""
        if self.model_id:
            self.variant_id = False
            self.inventory_id = False

    @api.onchange('variant_id')
    def _onchange_variant_id(self):
        """Clear inventory when variant changes"""
        if self.variant_id:
            self.inventory_id = False

    @api.model_create_multi
    def create(self, vals_list):
        """Update inventory status when device line is created"""
        lines = super().create(vals_list)
        for line in lines:
            if line.inventory_id:
                line.inventory_id.write({
                    'status': 'in_repair',
                    'repair_order_id': line.repair_order_id.id
                })
        return lines

    def write(self, vals):
        """Update inventory status when device line is modified"""
        # Handle inventory changes
        if 'inventory_id' in vals:
            # Release old inventory
            for line in self:
                if line.inventory_id and line.inventory_id.id != vals.get('inventory_id'):
                    line.inventory_id.write({
                        'status': 'available',
                        'repair_order_id': False
                    })
            
        result = super().write(vals)
        
        # Assign new inventory
        if 'inventory_id' in vals:
            for line in self:
                if line.inventory_id:
                    line.inventory_id.write({
                        'status': 'in_repair',
                        'repair_order_id': line.repair_order_id.id
                    })
        
        return result

    def unlink(self):
        """Release inventory when device line is deleted"""
        for line in self:
            if line.inventory_id:
                line.inventory_id.write({
                    'status': 'available',
                    'repair_order_id': False
                })
        return super().unlink()
