from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class MaintenanceRequest(models.Model):
    _name = "maintenance.request"
    _description = "Maintenance Request"

    serial_number = fields.Char(string="Request Number", required=True, copy=False, readonly=True, default=lambda self: _('New'))
    equipment_id = fields.Many2one("equipment.equipment", string="Equipment", required=True)
    
    user_id = fields.Many2one(
        "res.users", 
        string="Responsible", 
        default=lambda self: self.env.user
    )
    
    description = fields.Text(string="Problem Description")
    priority = fields.Selection([
        ("0","Low"),
        ("1","Medium"),
        ("2","High")
    ], default="1")
    
    state = fields.Selection([
        ("draft","Draft"),
        ("progress","In Progress"),
        ("done","Done"),
        ("cancel","Cancelled")
    ], default="draft")
    
    start_date = fields.Datetime(string="Start Date", readonly=True) 
    end_date = fields.Datetime(string="End Date", readonly=True)
    duration = fields.Float(string="Duration (hours)", compute="_compute_duration", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        is_manager = self.env.user.has_group('equipment_maintenance_erp.group_managers')

        for vals in vals_list:
            if not is_manager:
                vals['user_id'] = self.env.user.id
                vals['start_date'] = False 

            if vals.get('serial_number', _('New')) == _('New'):
                vals['serial_number'] = self.env['ir.sequence'].next_by_code('maintenance.request') or _('New')

        requests = super().create(vals_list)
        
        for rec in requests:
            if rec.equipment_id:
                rec.equipment_id._compute_active_requests()
        
        return requests

    def write(self, vals):
        if 'user_id' in vals and not self.env.user.has_group('equipment_maintenance_erp.group_managers'):
            if vals['user_id'] != self.env.user.id:
                raise UserError(_("Вы можете назначать заявки только на себя!"))
        
        res = super().write(vals)
        
        if 'state' in vals or 'equipment_id' in vals:
            for rec in self:
                if rec.equipment_id:
                    rec.equipment_id._compute_active_requests()
        return res

    def action_start(self):
        for rec in self:
            rec.state = "progress"
            rec.start_date = datetime.now()
            rec.equipment_id._compute_active_requests()

    def action_done(self):
        for rec in self:
            rec.state = "done"
            rec.end_date = datetime.now()
            rec._create_history()
            rec.equipment_id._compute_active_requests()

    def action_cancel(self):
        for rec in self:
            rec.state = "cancel"
            rec.equipment_id._compute_active_requests()

    @api.depends('start_date','end_date')
    def _compute_duration(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                delta = rec.end_date - rec.start_date
                rec.duration = delta.total_seconds() / 3600  
            else:
                rec.duration = 0

    def _create_history(self):
        history_obj = self.env['maintenance.history']
        for rec in self:
            history_obj.create({
                'equipment_id': rec.equipment_id.id,
                'description': rec.description,
                'user_id': rec.user_id.id,
                'start_date': rec.start_date,
                'end_date': rec.end_date,
                'duration': rec.duration,
            })