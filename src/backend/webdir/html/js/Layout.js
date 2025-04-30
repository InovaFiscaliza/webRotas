(function() {
    class Layout {
        static controller(operationType, ...args) {
            let idx, el;

            const routeList  = window.app.analysisContext.routeList;
            const updateTree = window.app.modules.CreateComponent.createTextList;

            switch (operationType) {
                case 'startup':
                    idx = 0;
                    el  = this.getDOMElements(['routeList']);

                    updateTree(routeList,
                        (item, index) => {
                            return `#${index}: ${item.estimatedDistance} km ${ (item.automaticRoute == 1) ? '(AUTOMÁTICA)' : ''}`
                        },
                        {
                            click: (event) => {
                                const list = Array.from(el.routeList.children);
                                
                                const previousSelection = list.findIndex(item => item.classList.contains('selected'));
                                const currentSelection = list.indexOf(event.target);

                                if (previousSelection !== currentSelection) {
                                    this.routeListSelectionChanged(event, list, routeList[currentSelection])
                                }
                            },
                            mouseover:  (event) => this.highlightTextListItem(event),
                            mouseleave: (event) => this.highlightTextListItem(event)
                        },
                        el.routeList,
                        idx
                    );

                    this.controller('update', routeList[idx]);
                    break;

                case 'update':
                    const routeInfo = args[0]; // routeInfo = routeList[routeIndex]
                    el = this.getDOMElements(['initialPointLatitude',
                                              'initialPointLongitude',
                                              'initialPointDescription',
                                              'pointsToVisit']);

                    this.updateEditableField(el.initialPointLatitude,    routeInfo.origin.lat);
                    this.updateEditableField(el.initialPointLongitude,   routeInfo.origin.lng);
                    this.updateEditableField(el.initialPointDescription, routeInfo.origin.description);

                    updateTree(routeInfo.waypoints,
                        (item, index) => {
                            const elDescription = item.description.length
                                ? item.description
                                : `(${item.lat}, ${item.lng}, ${item.elevation}m)`;

                            return `${index}: ${elDescription}`;
                        },
                        {
                            click: (event) => {
                                if (event.ctrlKey) {
                                    event.target.classList.toggle('selected');
                                } else {
                                    const list = Array.from(el.pointsToVisit.children);
                                    const currentSelection = list.indexOf(event.target);
                                
                                    let previousSelection = list.findIndex(item => item.classList.contains('selected'));
                                
                                    if (previousSelection === -1) {
                                        previousSelection = currentSelection;
                                    }
                                
                                    const start = Math.min(previousSelection, currentSelection);
                                    const end = Math.max(previousSelection, currentSelection);
                                
                                    for (let ii = 0; ii < list.length; ii++) {
                                        if (ii == currentSelection) {
                                            list[ii].classList.add('selected');
                                        } else {
                                            if (event.shiftKey && ii >= start && ii <= end) {
                                                list[ii].classList.add('selected');
                                            } else {
                                                list[ii].classList.remove('selected');
                                            }
                                        }
                                    }
                                }
                            },
                            mouseover: (event) => this.highlightTextListItem(event),
                            mouseleave: (event) => this.highlightTextListItem(event)
                        },
                        el.pointsToVisit,
                        -1
                    );
                    
                    break;

                case 'editionMode':
                    const mode = args[0]; // true | false
                    el = this.getDOMElements(['routeListAddBtn',
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
                                              'routeListMoveDownBtn']);

                    el.routeListEditModeBtn.parentElement.style.gridTemplateColumns = mode ? 'minmax(0px, 1fr) 18px 18px 18px 18px 18px' : 'minmax(0px, 1fr) 18px 18px 18px';

                    el.routeListEditModeBtn.style.backgroundImage = mode ? 'url(images/Edit_32Filled.png)'     : 'url(images/Edit_32.png)';
                    el.routeListEditModeBtn.dataset.tooltipText   = mode ? 'Desabilita modo de edição da rota' : 'Habilita modo de edição da rota';

                    this.toggleVisibility([el.routeListConfirmBtn, el.routeListCancelBtn], mode);
                    this.toggleEnabled([el.routeListAddBtn, el.routeList], !mode);
                    this.toggleEnabled([el.routeListDelBtn], !(mode || this.getRouteInfo().automaticRoute));
                    this.toggleEnabled([el.initialPointBtn, el.routeListMoveUpBtn, el.routeListMoveDownBtn], mode);
                    [el.initialPointLatitude, el.initialPointLongitude, el.initialPointDescription].forEach(item => { item.disabled = !mode; });                    
                    break;

                default: 
                    throw Error('Unexpected operation type')
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
        static getRouteInfo() {
            const el    = this.getDOMElements(['routeList']);
            const list  = Array.from(el.routeList.children);                                
            const index = list.findIndex(item => item.classList.contains('selected'));

            return window.app.analysisContext.routeList[index];
        }


        /*---------------------------------------------------------------------------------*/
        static routeListSelectionChanged(event, list, routeInfo) {
            list.forEach(item => {
                if (item === event.target) {
                    item.classList.add('selected');
                } else {
                    item.classList.remove('selected');
                }
            })
            window.document.getElementById('routeListDelBtn').classList.toggle('disabled', routeInfo.automaticRoute);
            
            this.controller('update', routeInfo);
            window.app.modules.Plot.controller('update', routeInfo);
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

        /*---------------------------------------------------------------------------------*/
        static highlightTextListItem(event) {
            event.target.classList.toggle('hover', event.type === 'mouseover');
        }
    }

    window.app.modules.Layout = Layout;
})()