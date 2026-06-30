from odoo import models, fields


class QatgEmployee(models.Model):
    _inherit = 'hr.employee'

    # Adding a custom dropdown choice selection field
    employee_type_selection = fields.Selection([
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contractor', 'Contractor')
    ], string='Custom Employment Category', default='full_time')

