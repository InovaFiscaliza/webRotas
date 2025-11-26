/*
    ## webRotas Layout ##      
    - Layout
      ├── startup
      ├── controller
      ├── updateControlState
      ├── getDOMElements
      ├── findSelectedRoute
      ├── checkIfOriginChanged
      ├── routeListSelectionChanged
      ├── updateEditableField
      ├── toggleEnabled
      └── toggleVisibility
*/

(function() {
    class Layout {
        /*---------------------------------------------------------------------------------*/
        static startup(...args) {
            const routingContext = window.app.routingContext;

            if (routingContext.length == 0) {
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
            const routingContext = window.app.routingContext;

            if (routingContext.length === 0) {
                type = 'idle';
            }

            switch (type) {
                case 'idle': {
                    this.updateControlState(type);
                    break;
                }

                case 'routeLoaded': {
                    const index1 = args[0];
                    const index2 = args[1];
                    const htmlRouteEl = window.document.getElementById('routeList');

                    this.updateControlState(type);

                    window.app.modules.Components.createRouteList(
                        htmlRouteEl,
                        routingContext,
                        (route, index1, index2) => {
                            /*
                                isComplete registra a qualidade dos dados. Posteriormente, criar uma chamada p/
                                que servidor possa sanar as pendências (elevação, ou paths).
                            */
                            let isComplete = true;
                            if ([null, -9999].includes(route.origin.elevation)) {
                                isComplete = false;
                            }

                            for (let ii = 0; ii < route.waypoints.length; ii++) {
                                if ([null, -9999].includes(route.waypoints[ii].elevation)) {
                                    isComplete = false;
                                    break;
                                }
                            }

                            if (route.paths.length <= 1) {
                                isComplete = false;
                            }

                            const automaticMark = route.automatic 
                                ? '<span style="color: #4caf50; font-size: 8px;">AUTO</span>' 
                                : '<span style="color: rgb(180, 180, 180); font-size: 8px;">MANUAL</span>';

                            // ⌛📐

                            return `<div style="display:flex;">
                                        <div style="min-width:16px;">[${index1},${index2}]:</div>
                                        <div style="padding-left:5px;">${route.routeId} ${automaticMark} ${isComplete ? '' : ' 🔴'}<br>(${route.estimatedTime || 'unknown'}, ${route.estimatedDistance || 'unknown'})</div>
                                    </div>`
                        },
                        {
                            click: (event) => window.app.modules.Callbacks.onRouteListSelectionChanged(event),
                            keydown: (event) => {
                                if (!["ArrowUp", "ArrowDown", " ", "Enter"].includes(event.key)) return;

                                const current = event.target.closest("li");
                                if (!current) return;

                                let nextItem;

                                switch (event.key) {
                                    case " ":
                                    case "Enter":
                                        nextItem = current;
                                        break;
                                    case "ArrowUp":
                                        nextItem = current.previousElementSibling;
                                        break;
                                    case "ArrowDown":
                                        nextItem = current.nextElementSibling;
                                        break;
                                }

                                if (nextItem) {
                                    nextItem.focus();
                                    nextItem.click();
                                }
                            },
                            mouseover: (event) => window.app.modules.Callbacks.onHighlightTextListItem(event),
                            mouseleave: (event) => window.app.modules.Callbacks.onHighlightTextListItem(event)
                        },
                        [index1, index2]
                    );

                    this.controller('routeSelected', index1, index2);
                    break;
                }

                case 'routeSelected': {
                    const index1 = args[0];
                    const index2 = args[1];

                    const routing = routingContext[index1].response;
                    const route = routing.routes[index2];
                    const htmlPointsEl = window.document.getElementById('pointsToVisit');

                    this.updateControlState(type, routing, route);
                    
                    window.app.modules.Components.createTextList(
                        htmlPointsEl,
                        route.waypoints,
                        (waypoint, index) => {
                            const descriptionText = waypoint.description.length ? `${waypoint.description}<br>` : '';
                            const elevationText   = [null, -9999].includes(waypoint.elevation) ? '' : `, ${waypoint.elevation.toFixed(1)}m`;
                            
                            return `<div style="display:flex;">
                                        <div style="min-width:16px;">${index}:</div>
                                        <div style="padding-left:5px;">${descriptionText}(${waypoint.lat.toFixed(6)}, ${waypoint.lng.toFixed(6)}${elevationText})</div>
                                    </div>`;
                        },
                        {
                            click:      (event) => window.app.modules.Callbacks.onPointListSelectionChanged(event, htmlPointsEl),
                            mouseover:  (event) => window.app.modules.Callbacks.onHighlightTextListItem(event),
                            mouseleave: (event) => window.app.modules.Callbacks.onHighlightTextListItem(event)
                        }
                    );                    
                    break;
                }

                case 'editionMode': {
                    const editionMode = args[0]; // true | false
                    const { index1, index2 } = this.findSelectedRoute();
                    this.updateControlState(type, editionMode);

                    if (!editionMode) {
                        this.controller('routeSelected', index1, index2);
                    }
                    break;
                }

                default: 
                    throw Error('Unexpected type')
            }
        }

        /*---------------------------------------------------------------------------------*/
        static updateControlState(type, ...args) {
            switch (type) {
                case 'idle': {
                    const htmlEl = this.getDOMElements([
                        'routeListAddBtn',
                        'routeListDelBtn',
                        'routeListEditModeBtn',
                        'routeListConfirmBtn',
                        'routeListCancelBtn',
                        'initialPointBtn',
                        'initialPointLatitude',
                        'initialPointLongitude',
                        'initialPointElevation',
                        'initialPointDescription',
                        'routeListMoveUpBtn',
                        'routeListMoveDownBtn',
                        'routeIds',
                        'toolbarExportBtn',
                        'toolbarPositionSlider',
                        'toolbarLocationBtn',
                        'toolbarOrientationBtn'
                    ]);
                    const htmlElArray = Object.values(htmlEl);
                    this.toggleEnabled(htmlElArray, false);

                    window.document.getElementById('routeList').innerHTML = '';
                    this.updateEditableField(htmlEl.initialPointLatitude,    '');
                    this.updateEditableField(htmlEl.initialPointLongitude,   '');
                    this.updateEditableField(htmlEl.initialPointElevation,   '');
                    this.updateEditableField(htmlEl.initialPointDescription, '');
                    window.document.getElementById('pointsToVisit').innerHTML = '';
                    htmlEl.routeIds.textContent = '';

                    htmlEl.toolbarPositionSlider.value = 0;
                    window.app.modules.Callbacks.onToolbarButtonClicked({ target: htmlEl.toolbarPositionSlider });

                    window.app.mapContext.settings.colormap.range.current = structuredClone(window.app.mapContext.settings.colormap.range.default);
                    window.app.modules.Components.updateColorbar();

                    window.app.modules.Plot.setView('center', window.app.mapContext.settings.position.default.center, window.app.mapContext.settings.position.default.zoom);
                    break;
                }

                case 'routeLoaded': {
                    const htmlEl = this.getDOMElements([
                        'routeListAddBtn',
                        'routeListDelBtn',
                        'toolbarExportBtn',
                        'toolbarPositionSlider',
                        'toolbarLocationBtn',
                        'toolbarOrientationBtn'
                    ]);
                    const htmlElArray = Object.values(htmlEl);                    
                    this.toggleEnabled(htmlElArray, true);

                    const htmlEditModeBtnElArray = [window.document.getElementById('routeListEditModeBtn')];
                    this.toggleEnabled(htmlEditModeBtnElArray, (window.location.protocol === "file:") ? false : true);

                    const htmlRouteEl = window.document.getElementById('routeList');
                    htmlRouteEl.innerHTML = '';
                    break;
                }

                case 'routeSelected': {
                    const routing = args[0];
                    const route   = args[1];

                    const htmlEl = this.getDOMElements([
                        'initialPointLatitude',
                        'initialPointLongitude',
                        'initialPointElevation',
                        'initialPointDescription',
                        'routeIds'
                    ]);

                    this.updateEditableField(htmlEl.initialPointLatitude,    route.origin.lat.toFixed(6));
                    this.updateEditableField(htmlEl.initialPointLongitude,   route.origin.lng.toFixed(6));
                    this.updateEditableField(htmlEl.initialPointElevation,   route.origin.elevation ? route.origin.elevation.toFixed(1) : -9999);
                    this.updateEditableField(htmlEl.initialPointDescription, route.origin.description);

                    let ids = {
                        created: route.created,
                        routeId: route.routeId || "n/a"
                    };
                    htmlEl.routeIds.textContent = JSON.stringify(ids, null, 1);
                    break;
                }

                case 'editionMode': {
                    const editionMode = args[0]

                    const htmlEl = this.getDOMElements([
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
                    if (!editionMode) {
                        htmlEl.routeList.querySelectorAll('li').forEach(li => li.tabIndex = 0);
                    } else {
                        htmlEl.routeList.querySelectorAll('li').forEach(li => li.tabIndex = -1);
                    }

                    this.toggleEnabled([htmlEl.initialPointBtn, htmlEl.routeListMoveUpBtn, htmlEl.routeListMoveDownBtn], editionMode);
                    [htmlEl.initialPointLatitude, htmlEl.initialPointLongitude, htmlEl.initialPointDescription].forEach(item => { 
                        item.disabled = !editionMode; 
                    });
                }
            }
        }

        /*---------------------------------------------------------------------------------*/
        static getDOMElements(ids) {
            /*
                Retorna-sa um objeto cujas chaves correspondem aos ids dos elementos HTML.
            */
            const elements = {};
            ids.forEach(id => {
                elements[id] = window.document.getElementById(id);
            });

            return elements;
        }

        /*---------------------------------------------------------------------------------*/
        static findSelectedRoute() {
            const htmlRouteEl = window.document.getElementById('routeList');
            const htmlRouteElChildren = Array.from(htmlRouteEl.children);

            let currentSelection = null;
            let [index1, index2] = [-1, -1];
            let currentRoute = null;

            currentSelection = htmlRouteElChildren.find(item => item.classList.contains('selected'));
            if (currentSelection) {
                [index1, index2] = JSON.parse(currentSelection.dataset.index);            
                currentRoute = window.app.routingContext[index1].response.routes[index2];
            }

            return { htmlRouteEl, htmlRouteElChildren, currentSelection, index1, index2, currentRoute };
        }

        /*---------------------------------------------------------------------------------*/
        static checkIfOriginChanged() {
            const { index1, index2, currentRoute } = this.findSelectedRoute();

            const initialPointHtmlElements = this.getDOMElements([
                'initialPointLatitude',
                'initialPointLongitude',
                'initialPointElevation',
                'initialPointDescription'
            ]);

            /*
                ⚠️ Cuidado no uso de initialOrigin e editedOrigin fora desta função porque
                as informações de "lat" e "lng" originalmente são numéricas. Aqui, pra fins
                de comparação do seu conteúdo, trunca-se e converte-se em string.
            */

            const initialOrigin = {...currentRoute.origin};
            initialOrigin.lat = initialOrigin.lat.toFixed(6);
            initialOrigin.lng = initialOrigin.lng.toFixed(6);
            initialOrigin.description = initialOrigin.description.trim();

            const editedOrigin = {
                lat: parseFloat(initialPointHtmlElements.initialPointLatitude.value).toFixed(6),
                lng: parseFloat(initialPointHtmlElements.initialPointLongitude.value).toFixed(6),
                elevation: parseFloat(initialPointHtmlElements.initialPointElevation.value),
                description: initialPointHtmlElements.initialPointDescription.value.trim()
            };

            const hasOriginRouteChanged = initialOrigin.lat !== editedOrigin.lat || initialOrigin.lng !== editedOrigin.lng;
            const hasOriginDescriptionChanged = initialOrigin.description !== editedOrigin.description;

            return { index1, index2, currentRoute, initialPointHtmlElements, initialOrigin, editedOrigin, hasOriginRouteChanged, hasOriginDescriptionChanged }
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