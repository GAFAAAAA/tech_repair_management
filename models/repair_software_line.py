from odoo import models, fields, api

class RepairSoftwareLine(models.Model):
    _name = 'tech.repair.software.line'
    _description = 'Software Line for repair job'

    repair_order_id = fields.Many2one(
        'tech.repair.order', 
        string="Repair Job", 
        required=True, 
        ondelete='cascade'
    )
    software_id = fields.Many2one(
        'tech.repair.software', 
        string="Software", 
        required=True
    )
    add_to_sum = fields.Boolean(
        string="Add to total", 
        default=True
    )


    # Related fields to display software information
    software_price = fields.Float(
        related='software_id.price', 
        string="Price", 
        readonly=True
    )
    software_renewal_required = fields.Boolean(
        related='software_id.renewal_required', 
        string="Renewal Required", 
        readonly=True
    )
    software_duration = fields.Selection(
        related='software_id.duration', 
        string="Duration", 
        readonly=True
    )
