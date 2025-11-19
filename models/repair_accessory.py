from odoo import models, fields

class RepairAccessory(models.Model):
    _name = 'tech.repair.accessory'
    _description = 'Accessories Left by Customer'
    _order = 'name asc'

    tech_repair_order_id = fields.Many2one(
        'tech.repair.order', 
        string="Repair", 
        ondelete='cascade'
    )

    aesthetic_condition = fields.Selection([
        ('new', 'New'),
        ('good', 'Good'),
        ('used', 'Used'),
        ('damaged', 'Damaged')
    ], string='Aesthetic Condition', default='good')

    name = fields.Selection([
        ('alimentatore', 'Power Adapter'),
        ('cover', 'Cover'),
        ('borsa', 'Bag'),
        ('sim', 'SIM'),
        ('altro', 'Other')
    ], string="Accessory Name", required=True, default='alimentatore')

    custom_name = fields.Char(string="Other", help="Specify the name if 'Other' is selected")
