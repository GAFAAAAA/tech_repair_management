from odoo import models, fields

class RepairStatePublic(models.Model):
    _name = 'tech.repair.state.public'
    _description = 'Customer Visible States'
    _order = 'sequence asc'

    name = fields.Char(string="Customer State Name", required=True)
    description = fields.Text(string="State Description")
    sequence = fields.Integer(string="Order", default=10)
