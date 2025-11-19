from odoo import models, fields

# work type management
class RepairWorktype(models.Model):

    _name = 'tech.repair.worktype'
    _description = 'Work to be Done'

    name = fields.Char(string='Work Type', required=True)
    description = fields.Html(
        string="Description",
        translate=True,
        sanitize=False,  # Allows HTML without restrictions (can be useful if you want buttons or special formatting)
        sanitize_attributes=False,
        help="Enter a complete description for printing and use '/' for commands."
        )
    price = fields.Float(string='Price €', required=True, default=0.0)
    stimated_time = fields.Integer(string='Duration (days)', default=1)
    extra_workflow = fields.Boolean(string='Has Additional Work', default=False)
    extra_workflow_name = fields.Char(string='Work')
    extra_workflow_time = fields.Integer(string='Extra Duration(days)', default=0)
    extra_workflow_price = fields.Float(string='Extra Price €', default=0.0)
