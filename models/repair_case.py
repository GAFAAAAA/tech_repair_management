from odoo import models, fields, api

class RepairCase(models.Model):
    _name = 'tech.repair.case'
    _description = 'Flight Case for Devices'
    _order = 'create_date desc'

    name = fields.Char(string='Case Number', required=True, copy=False, readonly=True, default=lambda self: 'New')
    
    # Mandatory colour field
    colour = fields.Selection([
        ('aluminium', 'Aluminium'),
        ('black', 'Black'),
        ('custom', 'Custom')
    ], string='Colour', required=True, default='aluminium')
    
    colour_custom = fields.Char(string='Custom Colour', help="Specify custom colour if selected")
    
    # Optional corner colour field
    corner_colour = fields.Selection([
        ('yellow', 'Yellow'),
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('black', 'Black'),
        ('custom', 'Custom')
    ], string='Corner Colour')
    
    corner_colour_custom = fields.Char(string='Custom Corner Colour', help="Specify custom corner colour if selected")
    
    # Company field (customer/contact)
    company_id = fields.Many2one('res.partner', string='Company', help="Company the case came from")
    
    # Audit fields
    check_in_date = fields.Datetime(string='Check-in Date', default=lambda self: fields.Datetime.now(), readonly=True)
    checked_in_by = fields.Many2one('res.users', string='Checked In By', default=lambda self: self.env.user, readonly=True)
    
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True, string="Active")

    @api.model_create_multi
    def create(self, vals_list):
        """Generate case number on creation"""
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('tech.repair.case') or 'New'
        return super().create(vals_list)
