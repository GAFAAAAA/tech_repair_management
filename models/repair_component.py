import logging
import json
from odoo import models, fields, api

class RepairComponent(models.Model):
    _name = 'tech.repair.component'
    _description = 'Components used in repair'
    _logger = logging.getLogger(__name__)

    # Connection to the "job" (repair order)
    repair_order_id = fields.Many2one('tech.repair.order', string='Job')

    # Actual product (product.product)
    product_id = fields.Many2one('product.product', string='Component')

    supplier_domain = fields.Char(
        compute='_compute_supplier_domain',
        store=False  # Usually a dynamic domain, so not saved to DB
    )
    # These fields are "local" to the single job
    supplier_id = fields.Many2one(
        'res.partner',
        string="Supplier",
        domain=[('is_company', '=', True)]
    )
    purchase_date = fields.Date(string="Purchase Date")
    receipt_date = fields.Date(string="Receipt Date")
    serial_number = fields.Char(string="Serial")
    pur_price = fields.Float(string='Component Cost €', default=0.0)
    lst_price = fields.Float(string='Price €', default=0.0)
    add_to_sum = fields.Boolean(string='Add to Total', default=False)


    # Calculate the valid domain for supplier_id based on the template's seller_ids and set it in the view
    @api.depends('product_id')
    def _compute_supplier_domain(self):
        
        for rec in self:
            if rec.product_id:
                partner_ids = rec.product_id.product_tmpl_id.seller_ids.mapped('partner_id').ids
                # Prepare the domain tuple
                domain = [('id', 'in', partner_ids)]
            else:
                domain = []  # No supplier allowed

            # Convert the list of tuples to JSON
            rec.supplier_domain = json.dumps(domain)