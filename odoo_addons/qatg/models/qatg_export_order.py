from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class QatgExportOrder(models.Model):
    _name = 'qatg_export_order'
    _description = 'Đơn xuất'

    name = fields.Char(string='Tên')
    status = fields.Selection([('draft', 'Nháp'), ('quotation', 'Báo giá'), ('sale_order', 'Đơn bán'),
                               ('delivering', 'Vận chuyển'), ('invoice', 'Hóa đơn')],
                              string='Trạng thái', default='draft')
    created_date = fields.Datetime(string='Ngày tạo đơn', readonly=True)
    completed_date = fields.Datetime(string='Ngày hoàn thành', readonly=True)
    quotation_status = fields.Selection([('draft', 'Nháp'), ('sent', 'Đã gửi')],
                                        string='Tình trạng báo giá', default='draft')
    sale_order_status = fields.Selection([('created', 'Đã tạo'), ('canceled', 'Đã hủy')],
                                         string='Tình trạng đơn bán')
    delivery_status = fields.Selection([('stored', 'Kho'), ('ontheway', 'Trên đường'), ('delivered', 'Đến nơi')],
                                       string='Tình trạng vận chuyển', default='stored')
    payment_status = fields.Selection([('none', 'Chưa thanh toán'), ('partial', 'Đã thanh toán một phần'),
                                       ('paid', 'Đã thanh toán toàn bộ')],
                                      string='Tình trạng thanh toán', default='none')
    paid_amount = fields.Float(string='Số tiền đã thanh toán', default='0')

    # amount = fields.Float(string='Số lượng')
    # max_amount = fields.Float(string='Tồn kho', related='inventory_id.amount')
    # price = fields.Float(string='Giá', related='inventory_id.price')
    # total = fields.Float(compute='_compute_total', string='Tổng giá trị')


    # @api.constrains('amount', 'max_amount')
    # def _check_amount(self):
    #     for rec in self:
    #         if rec.amount > rec.max_amount:
    #             raise ValidationError('Không đủ để xuất!')

    # @api.depends('amount', 'inventory_id.price')
    # def _compute_total(self):
    #      for item in self:
    #          item.total = item.amount * item.price
    #
    # def action_to_draft(self):
    #     self.status = 'draft'
    #     self.inventory_id.amount = self.max_amount + self.amount
    #
    # def action_to_completed(self):
    #     self.status = 'completed'
    #     self.completed_date = fields.Datetime.now()
    #     self.inventory_id.amount = self.max_amount - self.amount




