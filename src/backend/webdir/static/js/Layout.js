(function() {
    class Layout {
        /*---------------------------------------------------------------------------------*/
        static startup(...args) {
            const routing = window.app.routingContext;

            if (routing.length == 0) {
                this.controller('idle');
                window.app.modules.Plot.controller('clearAll');
            } else {
                const [index1 = 0, index2 = 0] = args;

                this.controller('routeLoaded', index1, index2);
                window.app.modules.Plot.controller('draw', index1, index2);
            }
        }

        /*---------------------------------------------------------------------------------*/
        static controller(type, ...args) {
            const routing = window.app.routingContext;
            let index1, index2;

            if (routing.length === 0) {
                type = 'idle';
            }

            switch (type) {
                case 'idle':
                    this.updateControlState(type);
                    break;

                case 'routeLoaded':
                    index1 = args[0];
                    index2 = args[1];
                    const htmlRouteEl = this.getDOMElements(['routeList']).routeList;

                    this.updateControlState(type);

                    window.app.modules.Components.createRouteList(
                        htmlRouteEl,
                        routing,
                        (routeEl, index1, index2) => {
                            return `[${index1},${index2}]: ${routeEl.estimatedDistance.toFixed(1)} km${routeEl.automatic ? ' (AUTOMÁTICA)' : ''}`
                        },
                        {
                            click:      (event) => window.app.modules.Callbacks.onRouteListSelectionChanged(event),
                            mouseover:  (event) => window.app.modules.Callbacks.onHighlightTextListItem(event),
                            mouseleave: (event) => window.app.modules.Callbacks.onHighlightTextListItem(event)
                        },
                        [index1, index2]
                    );

                    this.controller('routeSelected', index1, index2);
                    break;

                case 'routeSelected':
                    index1 = args[0];
                    index2 = args[1];                    
                    const route = routing[index1].response.routes[index2];
                    const htmlPointsEl = this.getDOMElements(['pointsToVisit']).pointsToVisit;

                    this.updateControlState(type, routing[index1], route);
                    
                    window.app.modules.Components.createTextList(
                        htmlPointsEl,
                        route.waypoints,
                        (routeEl, index) => {
                            const routeElDescription = routeEl.description.length ? ` ${routeEl.description}` : '';
                            return `${index}: (${routeEl.lat.toFixed(6)}, ${routeEl.lng.toFixed(6)}, ${routeEl.elevation.toFixed(0)}m)${routeElDescription}`;
                        },
                        {
                            click:      (event) => window.app.modules.Callbacks.onPointListSelectionChanged(event, htmlPointsEl),
                            mouseover:  (event) => window.app.modules.Callbacks.onHighlightTextListItem(event),
                            mouseleave: (event) => window.app.modules.Callbacks.onHighlightTextListItem(event)
                        }
                    );                    
                    break;

                case 'editionMode':
                    const editionMode = args[0]; // true | false
                    ({ index1, index2 } = this.findSelectedRoute());
                    this.updateControlState(type, editionMode);

                    if (!editionMode) {
                        this.controller('routeSelected', index1, index2);
                    }
                    break;

                default: 
                    throw Error('Unexpected type')
            }
        }

        /*---------------------------------------------------------------------------------*/
        static updateControlState(type, ...args) {
            let htmlEl, htmlElArray, htmlRouteEl, htmlPointsEl;

            switch (type) {
                case 'idle':
                    htmlEl = this.getDOMElements([
                        'routeListAddBtn',
                        'routeListDelBtn',
                        'routeListEditModeBtn',
                        'routeListConfirmBtn',
                        'routeListCancelBtn',
                        'initialPointBtn',
                        'initialPointLatitude',
                        'initialPointLongitude',
                        'initialPointDescription',
                        'routeListMoveUpBtn',
                        'routeListMoveDownBtn',
                        'routeIds',
                        'toolbarExportBtn',
                        'toolbarLocationBtn',
                        'toolbarOrientationBtn',
                        'toolbarColorbarBtn',
                        'toolbarInitialZoomBtn'
                    ]);
                    htmlElArray = Object.values(htmlEl);
                    this.toggleEnabled(htmlElArray, false);

                    htmlRouteEl = this.getDOMElements(['routeList']).routeList;
                    htmlRouteEl.innerHTML = '';

                    this.updateEditableField(htmlEl.initialPointLatitude,    '');
                    this.updateEditableField(htmlEl.initialPointLongitude,   '');
                    this.updateEditableField(htmlEl.initialPointDescription, '');

                    htmlPointsEl = this.getDOMElements(['pointsToVisit']).pointsToVisit;
                    htmlPointsEl.innerHTML = '';

                    htmlEl.routeIds.textContent = '';
                    break;

                case 'routeLoaded':
                    htmlEl = this.getDOMElements([
                        'routeListAddBtn',
                        'routeListDelBtn',
                        'routeListEditModeBtn',
                        'toolbarExportBtn',
                        'toolbarLocationBtn',
                        'toolbarOrientationBtn',
                        'toolbarColorbarBtn',
                        'toolbarInitialZoomBtn'
                    ]);
                    htmlElArray = Object.values(htmlEl);                    
                    this.toggleEnabled(htmlElArray, true);

                    htmlRouteEl = this.getDOMElements(['routeList']).routeList;
                    htmlRouteEl.innerHTML = '';
                    break;

                case 'routeSelected':
                    const routing = args[0];
                    const route   = args[1];

                    htmlEl = this.getDOMElements([
                        'initialPointLatitude',
                        'initialPointLongitude',
                        'initialPointDescription',
                        'routeIds'
                    ]);

                    this.updateEditableField(htmlEl.initialPointLatitude,    route.origin.lat.toFixed(6));
                    this.updateEditableField(htmlEl.initialPointLongitude,   route.origin.lng.toFixed(6));
                    this.updateEditableField(htmlEl.initialPointDescription, route.origin.description);

                    let ids = {
                        created: route.created,
                        cacheId: routing.response.cacheId,
                        routeId: route.routeId
                    };
                    htmlEl.routeIds.textContent = JSON.stringify(ids, null, 1);
                    break;

                case 'editionMode':
                    const editionMode = args[0]

                    htmlEl = this.getDOMElements([
                        'routeListAddBtn',
                        'routeListDelBtn',
                        'routeListEditModeBtn',
                        'routeListConfirmBtn',
                        'routeListCancelBtn',
                        'routeList',
                        'initialPointBtn',
                        'initialPointLatitude',
                        'initialPointLongitude',
                        'initialPointDescription',
                        'routeListMoveUpBtn',
                        'routeListMoveDownBtn'
                    ]);

                    htmlEl.routeListEditModeBtn.parentElement.style.gridTemplateColumns = editionMode ? 'minmax(0px, 1fr) 18px 18px 18px 18px 18px' : 'minmax(0px, 1fr) 18px 18px 18px';
                    htmlEl.routeListEditModeBtn.style.backgroundImage = editionMode ? 'url(images/Edit_32Filled.png)'     : 'url(images/Edit_32.png)';
                    htmlEl.routeListEditModeBtn.dataset.tooltipText   = editionMode ? 'Desabilita modo de edição da rota' : 'Habilita modo de edição da rota';

                    this.toggleVisibility([htmlEl.routeListConfirmBtn, htmlEl.routeListCancelBtn], editionMode);
                    this.toggleEnabled([htmlEl.routeListConfirmBtn, htmlEl.routeListCancelBtn], editionMode);

                    this.toggleEnabled([htmlEl.routeListAddBtn, htmlEl.routeListDelBtn, htmlEl.routeList], !editionMode);
                    this.toggleEnabled([htmlEl.initialPointBtn, htmlEl.routeListMoveUpBtn, htmlEl.routeListMoveDownBtn], editionMode);
                    [htmlEl.initialPointLatitude, htmlEl.initialPointLongitude, htmlEl.initialPointDescription].forEach(item => { 
                        item.disabled = !editionMode; 
                    });
            }
        }

        /*---------------------------------------------------------------------------------*/
        static getDOMElements(ids) {
            const elements = {};
            ids.forEach(id => {
                elements[id] = window.document.getElementById(id);
            });

            return elements;
        }

        /*---------------------------------------------------------------------------------*/
        static findSelectedRoute() {
            const htmlRouteEl = this.getDOMElements(['routeList']).routeList;
            const htmlRouteElChildren = Array.from(htmlRouteEl.children);

            const currentSelection = htmlRouteElChildren.find(item => item.classList.contains('selected'));
            const [index1, index2] = JSON.parse(currentSelection.dataset.index);            
            const currentRoute     = window.app.routingContext[index1].response.routes[index2];

            return { htmlRouteEl, htmlRouteElChildren, currentSelection, index1, index2, currentRoute };
        }

        /*---------------------------------------------------------------------------------*/
        static routeListSelectionChanged(event) {
            const { htmlRouteElChildren, currentSelection } = this.findSelectedRoute();

            if (currentSelection !== event.target) {
                const [index1, index2] = JSON.parse(event.target.dataset.index);
                const route = window.app.routingContext[index1].response.routes[index2];
                
                htmlRouteElChildren.forEach(item => item.classList.toggle('selected', item === event.target));    
                
                this.controller('routeSelected', route);
                window.app.modules.Plot.controller('update', route);   
            }
        }

        /*---------------------------------------------------------------------------------*/
        static updateEditableField(element, value) {
            /*
                Armazena o valor do elemento no campo dataset, possibilitando validar a nova
                entrada quando disparado o evento "change", eventualmente revertendo para o 
                valor anterior se não for válido.
            */
            element.value = value;
            element.dataset.value = value;
        }

        /*---------------------------------------------------------------------------------*/
        static toggleEnabled(elements, enabled) {
            elements.forEach(item => {
                item.disabled = !enabled;
                item.classList.toggle('disabled', !enabled);
            });
        }

        /*---------------------------------------------------------------------------------*/        
        static toggleVisibility(elements, visible) {
            const display = visible ? 'block' : 'none';

            elements.forEach(item => {
                item.style.display = display;
            });
        }
    }

    window.app.modules.Layout = Layout;
})()