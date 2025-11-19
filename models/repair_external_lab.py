from odoo import models, fields

class RepairExternalLab(models.Model):
    _name = 'tech.repair.external.lab'
    _description = 'External Laboratory Interventions'
    _order = 'send_date desc, lab_id asc'

    tech_repair_order_id = fields.Many2one(
        'tech.repair.order', string='Repair', ondelete='cascade'
    )  # Connection to the repair

    lab_id = fields.Many2one(
        'res.partner', string='Laboratory',
        domain=[('is_company', '=', True)], required=True
    )  # Selection of external laboratory

    operation_description = fields.Text(string='Operation Description')
    external_cost = fields.Float(string='Cost to Us', default=0.0)
    customer_cost = fields.Float(string='Cost to Customer', default=0.0)

     # Goods shipment date
    send_date = fields.Datetime(string='Date Left from TECH', readonly=False)

    # Goods return date
    out_date = fields.Datetime(
        string='Date Returned',
        readonly=False,
    )

    add_to_sum = fields.Boolean(
        string="Add to total", 
        default=True
    )
