from odoo import models, fields, api

class RepairChatMessage(models.Model):
    _name = 'tech.repair.chat.message'
    _description = 'Repair Chat Messages'
    _order = 'create_date asc'

    tech_repair_order_id = fields.Many2one(
        'tech.repair.order', 
        string="Repair", 
        required=True, 
        ondelete='cascade'
    )

    sender = fields.Selection([
        ('customer', 'Customer'),
        ('technician', 'Technician')
    ], string="Sender", required=True, default='technician')

    message = fields.Text(string="Message", required=True)
    create_date = fields.Datetime(string="Date", default=fields.Datetime.now, readonly=True)