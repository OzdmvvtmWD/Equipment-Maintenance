from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError

class MaintenanceHistory(models.Model):
    _name = "maintenance.history"
    _description = "History"

    equipment_id = fields.Many2one("equipment.equipment")
    request_id = fields.Many2one("maintenance.request")
    description = fields.Text()
    user_id = fields.Many2one("res.users")
    start_date = fields.Datetime()
    end_date = fields.Datetime()
    duration = fields.Float(string="Duration (hours)", readonly=True)


    @api.model
    def write(self, vals):
        raise UserError("History can't be modified")
