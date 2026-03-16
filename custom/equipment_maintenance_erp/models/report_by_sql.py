from odoo import models, fields, tools
from odoo.tools import SQL
from odoo.exceptions import UserError

class ReportBySql(models.Model):
    _name = "report.bysql"
    _description = "Report By Sql"
    _auto = False 

    category_id = fields.Many2one('equipment.category', string="Equipment Category", readonly=True)
    total_equipment = fields.Integer(string="Total Equipment", readonly=True)
    total_requests = fields.Integer(string="Total Requests", readonly=True)
    done_requests = fields.Integer(string="Done Requests", readonly=True)
    overdue_requests = fields.Integer(string="Overdue Requests", readonly=True)
    avg_duration = fields.Float(string="Average Duration (Hrs)", readonly=True, aggregator="avg")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER () AS id,
                    cat.id AS category_id,
                    cat.equipment_count AS total_equipment,
                    count(req.id) AS total_requests,
                    count(req.id) FILTER (WHERE req.state = 'done') AS done_requests,
                    count(req.id) FILTER (WHERE req.state != 'done' AND req.end_date < now()) AS overdue_requests,
                    avg(req.duration) AS avg_duration
                FROM equipment_category cat
                LEFT JOIN equipment_equipment equip ON equip.category_id = cat.id
                LEFT JOIN maintenance_request req ON req.equipment_id = equip.id
                GROUP BY cat.id, cat.equipment_count
            )
        """ % self._table)