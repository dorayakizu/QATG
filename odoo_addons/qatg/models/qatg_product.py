from odoo import models, fields


class QatgProduct(models.Model):
    _inherit = "product.template"



    product_type_selection = fields.Selection([
        ('camera', 'Camera'),
        ('display', 'Display'),
        ('battery', 'Battery')
    ], string="Product Category")

    specs_value_ids = fields.One2many(
        'qatg.product.specs.value',
        'product_id',
        string='Thông số'
    )

    product_manufacturer = fields.Char(
        string="Hãng"
    )

    product_warranty = fields.Char(
        string="Bảo hành"
    )

    product_serial = fields.Char(
        string="Model Sản phẩm",
    )
