from odoo import models, fields


class QatgProduct(models.Model):
    _inherit = "product.template"


    product_manufacturer = fields.Char(
        string="Hãng"
    )

    product_warranty = fields.Char(
        string="Bảo hành"
    )

