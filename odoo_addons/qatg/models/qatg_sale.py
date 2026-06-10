from odoo import models, fields


class QatgQuotation(models.Model):
    _inherit = "sale.order"

    new_field = fields.Char(
        string="Customer Reference"
    )