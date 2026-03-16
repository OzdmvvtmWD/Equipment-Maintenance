from odoo import models, fields, api, _
from datetime import datetime

class EquipmentCategory(models.Model):
    _name = "equipment.category"
    _description = "Equipment Category"

    name = fields.Char(required=True)
    description = fields.Text()
    parent_id = fields.Many2one("equipment.category")
    child_ids = fields.One2many('equipment.category', 'parent_id', string='Subcategories')

    equipment_count = fields.Integer(
        compute="_compute_equipment_count",
        store=True
    )


    def _compute_equipment_count(self):
        for eq in self:
            eq.equipment_count = self.env["equipment.equipment"].search_count([("category_id", "=", eq.id)])

    @api.model_create_multi
    def create(self, vals_list):
        is_manager = self.env.user.has_group('equipment_maintenance_erp.group_managers')

        for vals in vals_list:
            if not is_manager:
                vals['user_id'] = self.env.user.id
                vals['start_date'] = False 

            if vals.get('serial_number', _('New')) == _('New'):
                vals['serial_number'] = self.env['ir.sequence'].next_by_code('maintenance.request') or _('New')

        return super().create(vals_list)