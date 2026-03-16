from odoo import models, fields, api
from odoo.exceptions import UserError

class Equipment(models.Model):
    _name = "equipment.equipment"
    _description = "Equipment"

    name = fields.Char(required=True)
    serial_number = fields.Char()
    category_id = fields.Many2one("equipment.category")
    responsible_id = fields.Many2one("res.users")
    start_date = fields.Datetime(string="Start Date", default=fields.Datetime.now)
    active_requests = fields.Integer(compute="_compute_active_requests", store=True)
    state = fields.Selection([
        ("active", "In Use"),
        ("maintenance", "Maintenance"),
        ("retired", "Retired")
    ], default="active")

    def action_active(self):
        for eq in self:
            eq.state = "active"
            eq.start_date = fields.Datetime.now()

    def action_maintenance(self):
        for rec in self:
            rec.state = "maintenance"

    def action_retired(self):
        for rec in self:
            rec.state = "retired"

    def _compute_active_requests(self):
        for rec in self:
            rec.active_requests = self.env["maintenance.request"].search_count([
                ("equipment_id", "=", rec.id),
                ("state", "not in", ["done", "cancel"])
            ])

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.category_id:
                rec.category_id._compute_equipment_count()
        return records

    def write(self, vals):
        old_categories = self.mapped('category_id')
        res = super().write(vals)
        if 'category_id' in vals:
            new_categories = self.mapped('category_id')
            (old_categories | new_categories)._compute_equipment_count()
        return res

    def unlink(self):
        categories = self.mapped('category_id')
        res = super().unlink()
        categories._compute_equipment_count()
        return res

    @api.ondelete(at_uninstall=False)
    def _check_related_requests_and_history(self):
        for eq in self:
            requests_count = self.env['maintenance.request'].search_count([('equipment_id', '=', eq.id)])
            history_count = self.env['maintenance.history'].search_count([('equipment_id', '=', eq.id)])
            if requests_count or history_count:
                raise UserError(
                    "Cannot delete equipment because it has related maintenance requests or history!"
                )
            
    @api.model 
    def get_maintenance_dashboard_data(self):
        return {
            'total_equipment': self.search_count([]),
            'open_requests': self.env['maintenance.request'].search_count([
                ('state', 'in', ['draft', 'progress'])
            ]),
            'overdue_requests': self.env['maintenance.request'].search_count([
                ('state', 'in', ['draft', 'progress']),
                ('start_date', '<', fields.Datetime.now()) 
            ]),
        }