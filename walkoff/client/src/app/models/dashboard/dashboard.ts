import { Type } from 'class-transformer';

import { DashboardWidget, 
         BarChartWidget, 
         PieChartWidget, 
         LineChartWidget,  
         TextWidget,
         TableWidget,
         KibanaWidget
} from "./dashboardWidget";

import { UUID } from 'angular2-uuid';

export class Dashboard {

    id: string;

    name: string;

    @Type(() => DashboardWidget, {
        discriminator: {
            property: "type",
            subTypes: [
                { value: BarChartWidget, name: "bar" },
                { value: PieChartWidget, name: "pie" },
                { value: LineChartWidget, name: "line" },
                { value: TextWidget, name: "text" },
                { value: TableWidget, name: "table" },
                { value: KibanaWidget, name: "kibana" },
            ]
        }
    })
    widgets: DashboardWidget[] = []; 

    constructor() { 
        this.id = UUID.UUID();
    }
}
