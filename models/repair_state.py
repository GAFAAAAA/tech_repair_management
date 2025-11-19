from odoo import models, fields

# Model for repair states
class RepairState(models.Model):
    _name = 'tech.repair.state'
    _description = 'Repair States'

    # State name (e.g. Waiting, In repair, Completed)
    name = fields.Char(string='State Name', required=True)
    # Display order of states
    sequence = fields.Integer(string='Order', default=10)
    # Flag that sets whether or not to close the job
    is_closed = fields.Boolean(string='Is this a closing state?', default=False)  # Flag to define closed states
    # Flag for external laboratories
    is_external_lab = fields.Boolean(string='External Laboratory Operation?', default=False)  

    # Connection with the customer visible state
    public_state_id = fields.Many2one(
        'tech.repair.state.public',
        string="Customer Visible Status",
        help="When this state is set, the assigned public state is automatically updated."
    )
