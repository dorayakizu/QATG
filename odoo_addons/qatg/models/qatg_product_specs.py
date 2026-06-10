from odoo import models, fields


class QatgProductSpecs(models.Model):
    _name = 'qatg.product.specs'
    _description = 'Product Specification'

    name = fields.Char(
        string='Thông số',
        required=True
    )

    unit = fields.Char(
        string='Đơn vị'
    )

    value_type = fields.Selection([
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
    ], string ='Loại', default='text')

    specs_value_ids = fields.One2many(
        'qatg.product.specs.value',
        'specs_id',
        string='Giá trị'
    )



