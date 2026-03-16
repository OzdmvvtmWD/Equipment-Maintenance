/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, useState } = owl;

export class MaintenanceDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            stats: {
                total_equipment: 0,
                open_requests: 0,
                overdue_requests: 0
            }
        });

        onWillStart(async () => {
            await this.fetchData();
        });
    }

    async fetchData() {
        const data = await this.orm.call(
            "equipment.equipment",
            "get_maintenance_dashboard_data",
            []
        );
        this.state.stats = data;
    }
}

MaintenanceDashboard.template = "equipment_maintenance_erp.MaintenanceDashboard";
registry.category("actions").add("maintenance_dashboard_action", MaintenanceDashboard);