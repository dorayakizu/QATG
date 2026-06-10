from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class QatgExportOrder(models.Model):
    _name = 'qatg_export_order'
    _description = 'Chi tiết đơn xuất'

    amount = fields.Float(string='Số lượng')
    max_amount = fields.Float(string='Tồn kho', related='inventory_id.amount')
    price = fields.Float(string='Giá', related='inventory_id.price')
    total = fields.Float(compute='_compute_total', string='Tổng giá trị')




