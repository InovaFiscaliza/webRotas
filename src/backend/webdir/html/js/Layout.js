(function() {
    class Layout {
        static controller(operationType, ...args) {
            let routeIndex, routeListContainer;

            const routeList  = window.app.analysisContext.routeList;
            const updateTree = window.app.modules.CreateComponent.createTextList;

            switch (operationType) {
                case 'startup':
                    routeIndex = 0;

                    updateTree(window.document.getElementById('routeList'),
                        (element, index) => {
                            return `#${index}: ${element.estimatedDistance} km ${ (element.automaticRoute == 1) ? '(AUTOMÁTICA)' : ''}`
                        },
                        {
                            click: (event) => window.app.modules.Callback.onRouteList(event, 'change'),
                            mouseover: (event) => window.app.modules.Callback.onRouteList(event, 'hover')
                        },
                        window.document.getElementById('routeList')
                    );

                    this.controller('updatePanel', routeList[routeIndex]);
                    break;

                case 'updatePanel':
                    routeIndex = args[0];
                    
                    window.document.getElementById('initialPointLatitude').value    = routeList[routeIndex].origin.lat;
                    window.document.getElementById('initialPointLongitude').value   = routeList[routeIndex].origin.lng;
                    window.document.getElementById('initialPointDescription').value = routeList[routeIndex].origin.description;

                    updateTree(window.document.getElementById('pointsToVisit'),
                        (element, index) => {
                            const elDescription = element.description.length
                                ? element.description
                                : `(${element.lat}, ${element.lng}, ${element.elevation}m)`;

                            return `${index}: ${elDescription}`;
                        },
                        {},
                        window.document.getElementById('routeList')
                    );
                    
                    break;

                default: 
                    throw Error('Unexpected operation type')
            }
    }

    window.app.modules.Layout = Layout;
})