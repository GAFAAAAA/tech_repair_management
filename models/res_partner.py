from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        # Check if the context indicates the creation is from the repair module
        if self._context.get('from_tech_repair_order'):
            for vals in vals_list:
                # Ensure either phone or email is provided
                if not vals.get('phone') and not vals.get('email') :
                    raise ValidationError("To save a contact, you need either a landline phone number, or an email!")
        return super().create(vals_list)
