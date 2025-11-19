from odoo import models, fields, api

class RepairInformativa(models.Model):
    _name = 'tech.repair.term'
    _description = "Repair Terms"

    name = fields.Char(string="Title", required=True)
    contenuto = fields.Html(string="Terms Text", required=True)
    predefinita = fields.Boolean(string="Use as Default", default=False)

    @api.constrains('predefinita')
    def _check_unique_default(self):
        # Allows only one default term to be active at a time
        for record in self:
            if record.predefinita:
                other_defaults = self.search([('predefinita', '=', True), ('id', '!=', record.id)])
                if other_defaults:
                    raise models.ValidationError("Only one default term can exist at a time!")