import { Injectable } from '@angular/core';
import { plainToClass, classToPlain, serialize, deserializeArray } from 'class-transformer';
import { UtilitiesService } from '../utilities.service';
import { Dashboard } from '../models/dashboard/dashboard';
import { ExecutionService } from '../execution/execution.service';
import { DashboardWidget } from '../models/dashboard/dashboardWidget';
import { WorkflowStatus } from '../models/execution/workflowStatus';

import * as csv from 'csvtojson';

@Injectable({
    providedIn: 'root'
})
export class DashboardService {

    constructor(private utils: UtilitiesService, private executionService: ExecutionService) { }

    saveDashboard(newDashboard: Dashboard): void {
        const dashboards: Dashboard[] = this.getDashboards();
        const index = dashboards.findIndex(item => item.id == newDashboard.id);

        if (index == -1) dashboards.push(newDashboard);
        else dashboards[index] = newDashboard;

        localStorage.setItem('dashboards', serialize(dashboards));
    }

    deleteDashboard(deletedDashboard: Dashboard): void {
        const dashboards: Dashboard[] = this.getDashboards().filter(item => item.id != deletedDashboard.id);
        localStorage.setItem('dashboards', serialize(dashboards));
    }

    getDashboards() : Dashboard[] {
        return deserializeArray(Dashboard, localStorage.getItem('dashboards')) || [];
    }

    getDashboard(name: string) : Dashboard {
        return this.getDashboards().find(item => item.name == name);
    }

    async getDashboardWithMetadata(name: string) : Promise<Dashboard> {
        const theDashboard: Dashboard = this.getDashboard(name);
        await Promise.all(theDashboard.widgets.map(widget => this.getWidgetMetadata(widget)));
        return theDashboard;
    }

    async getWidgetMetadata(widget: DashboardWidget) {
        const options = widget.options;
        if (options.workflow && options.execution && options.action) {         
            const workflowStatus: WorkflowStatus = (options.execution == "latest") ?
                await this.executionService.getLatestExecution(options.workflow) :
                await this.executionService.getWorkflowStatus(options.execution)

            const actionStatus = workflowStatus.action_statuses.find(status => status.action_id == options.action);
            if (actionStatus) widget.setMetadata(await this.parseResult(actionStatus.result));
        }
    }

    async parseResult(result) {
        let headers = [];
        return csv()
            .fromString(result)
            .on('header', row => headers = row)
            .then(data => ({
                headers,
                rows: data.map(Object.values),
                data
            }), err => {
                console.log(err);
                return result
            })
    }
}
