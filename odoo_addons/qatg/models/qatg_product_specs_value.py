from odoo import models, fields


class QatgProductSpecsValue(models.Model):
    _name = 'qatg.product.specs.value'
    _description = 'Product Specification Value'

    product_id = fields.Many2one(
        'product.template',
        required=True,
        ondelete='cascade',
        index=True
    )

    specs_id = fields.Many2one(
        'qatg.product.specs',
        required=True,
        index=True
    )

    unit = fields.Char(
        related='specs_id.unit',
        string='Đơn vị',
        store=True,
        readonly=True
    )

    value = fields.Char(
        string='Giá trị',
        required=True
    )

    _sql_constraints = [
        (
            'product_spec_unique',
            'unique(product_id, specs_id)',
            'This specification already exists for this product!'
        )
    ]