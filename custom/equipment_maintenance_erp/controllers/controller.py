from odoo import http

#controller to show all user's maintenance requests with oportunity to go for details
class Home(http.Controller):
    @http.route('/my/requests', auth='user', website=True)
    def maintenance_users_requests(self):
        user = http.request.env.user
        is_manager = user.has_group('equipment_maintenance_erp.group_managers')
        
        if is_manager:
            domain = [] 
        else:
            domain = [('user_id', '=', user.id)]
        maintenance_requests = http.request.env['maintenance.request'].search(domain)
        
        return http.request.render('equipment_maintenance_erp.portal_my_requests_template', {
            'maintenance_requests': maintenance_requests
        })

#go to the user's requests by req_id
class Details(http.Controller):
    @http.route('/my/requests/request/<int:req_id>', auth='user', website=True)
    def detail_users_request(self, req_id, **kw):
        maintenance_request = http.request.env['maintenance.request'].browse(req_id)
        
        if not maintenance_request.exists() or maintenance_request.user_id.id != http.request.env.user.id:
            return http.request.render('website.404')

        return http.request.render('equipment_maintenance_erp.portal_request_details_template', {
            'req': maintenance_request
        })


class MaintenancePortalCreate(http.Controller):

    @http.route('/my/requests/new', type='http', auth='user', website=True)
    def maintenance_request_form(self, **kw):
        user = http.request.env.user
        equipments = http.request.env['equipment.equipment'].search([])
        
        if user.has_group('equipment_maintenance_erp.group_managers'):
            users = http.request.env['res.users'].search([
                ('groups_id', 'in', http.request.env.ref('equipment_maintenance_erp.group_employers').id)
            ])
        else:
            users = user

        return http.request.render('equipment_maintenance_erp.portal_create_request_template', {
            'equipments': equipments,
            'users': users,
            'priority_selection': [('0', 'Low'), ('1', 'Medium'), ('2', 'High')],
        })

    @http.route('/my/requests/submit', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def maintenance_request_submit(self, **post):
        user = http.request.env.user
        
        assigned_user_id = int(post.get('user_id')) if post.get('user_id') else user.id
        if not user.has_group('equipment_maintenance_erp.group_managers'):
            assigned_user_id = user.id

        http.request.env['maintenance.request'].create({
            'equipment_id': int(post.get('equipment_id')),
            'user_id': assigned_user_id,
            'description': post.get('description'),
            'priority': post.get('priority', '1'),
        })
        return http.request.redirect('/my/requests')