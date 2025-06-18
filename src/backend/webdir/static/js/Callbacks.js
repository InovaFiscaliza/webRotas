/*
    ## webRotas Callbacks ##
    - APP
      ├── onWindowLoad
      └── onWindowBeforeUnload
    - MAPA
      ├── onContextMenuItemSelected
      └── updateGeoLocationPosition
    - PAINEL À ESQUERDA DO MAPA
      └── onPanelButtonClicked
    - TOOLBAR
      └── onToolbarButtonClicked
    - *.*
      └── onServerConnectionStatusChanged (PENDENTE)

    Alguns dos layers do mapa proveem interações, mas os seus callbacks estão descritos
    na sua criação.
*/
(function () { 
    class Callbacks {
        /*-----------------------------------------------------------------------------------
            ## APP ##
        -----------------------------------------------------------------------------------*/
        static onWindowLoad(event) {
            const routing = window.app.routingContext;

            window.app.modules.Components.createMap();
            window.app.modules.Components.createPanel();
            window.app.modules.Components.createToolbar();

            window.app.modules.Utils.syncLocalStorage('startup');
            window.app.modules.Layout.startup();

            window.app.modules.Utils.consoleLog('Session started');
        }

        /*---------------------------------------------------------------------------------*/
        static onWindowBeforeUnload(event) {
            event.preventDefault();
            event.returnValue = '';
        }

        /*---------------------------------------------------------------------------------*/
        static onLocalStorageUpdate(event) {
            if (event.storageArea !== localStorage) {
                return;
            }

            new DialogBox('Changes detected in another tab. Reloading...', 'info');
            window.app.modules.Utils.syncLocalStorage('startup');
            window.app.modules.Layout.startup();
        }


        /*-----------------------------------------------------------------------------------
            ## MAPA ##
        -----------------------------------------------------------------------------------*/
        static onContextMenuCreation(event) {
            const map   = window.app.map;
            const panel = document.getElementById('panel');
            let context = window.document.getElementById('contextMenu');                

            if (!context) {
                context = window.app.modules.Components.createContextMenu();
            }

            const { lat, lng } = event.latlng;
            const { clientX, clientY } = event.originalEvent;
            
            context.style.left  = (panel.classList.contains('panel-on')) ? `${clientX - 5 - parseInt(getComputedStyle(panel).width)}px` : `${clientX}px`;
            context.style.top  = `${clientY}px`;

            window.document.getElementById('contextMenuCoords').textContent = `Coordenadas: ${lat.toFixed(6)}, ${lng.toFixed(6)}`;

            map.on('mousedown', removeContextMenu);
            map.on('zoomstart', removeContextMenu);
            map.on('resize',    removeContextMenu);
            window.L.DomEvent.disableClickPropagation(context);

            function removeContextMenu() {
                context.remove();
                map.off('mousedown', removeContextMenu);
                map.off('zoomstart', removeContextMenu);
                map.off('resize',    removeContextMenu);
            }
        }

        /*---------------------------------------------------------------------------------*/
        static onContextMenuItemSelected(event) {
            event.preventDefault();
            event.stopPropagation();

            const coords = window.document.getElementById('contextMenuCoords').textContent.match(/-?\d+\.\d+/g);
            const [ lat, lng ] = coords;

            if (!coords || coords.length !== 2) {
                return;
            }
        
            switch (event.target.id) {
                case 'contextMenuCoords':
                    const coordsToCopy = `${lat}, ${lng}`;

                    navigator.clipboard.writeText(coordsToCopy)
                        .then(() => {
                            new DialogBox(`Coordenadas copiadas para a área de transferência: ${coordsToCopy}`, 'info');
                        })
                        .catch((ME) => {
                            new DialogBox(`${ME.message}`, 'error');
                        });
                    break;

                case 'contextMenuStreetView':
                    let streeviewWindow = window.app.mapContext.settings.streetview.handle;

                    if (streeviewWindow && !streeviewWindow.window && !streeviewWindow.closed) {
                        streeviewWindow.focus();
                        streeviewWindow.location.href = window.app.mapContext.settings.streetview.url(lat, lng);
                    } else {
                        const width  = window.innerWidth  * 0.7;
                        const height = window.innerHeight * 0.7;

                        const left   = (window.innerWidth  - width)  / 2 + window.screenX;
                        const top    = (window.innerHeight - height) / 2 + window.screenY;

                        const windowFeatures = `
                            width=${width},
                            height=${height},
                            left=${left},
                            top=${top},
                            zoom=0.5,
                            menubar=no,
                            toolbar=no,
                            location=no,
                            status=no,
                            resizable=yes,
                            scrollbars=yes
                        `;

                        window.app.mapContext.settings.streetview.handle = window.open(window.app.mapContext.settings.streetview.url(lat, lng), '_blank', windowFeatures);

                        if (!window.app.mapContext.settings.streetview.handle) {
                            new DialogBox('O navegador bloqueou a abertura da janela.', 'error');
                            return;
                        }
                    }
                    break;

                case 'contextMenuUpdateVehicle':
                    console.log('contextMenuUpdateVehicle');
                    /*
                    const vehicleCoords = contextMenu.querySelector('#coords').textContent.match(/-?\d+\.\d+/g);
                    const [vehicleLat, vehicleLng] = vehicleCoords;
                    window.app.modules.Plot.updateVehiclePosition(vehicleLat, vehicleLng);
                    */
                    break;
            }
        }

        /*---------------------------------------------------------------------------------*/
        static updateGeoLocationPosition(position) {
            /*
                O estado inicial do webRotas é não requisitar a localização ao
                navegador. Consequentemente, não existe o objeto "L.Marker".

                Posteriormente à criação, ou atualização, do marcador, avalia-se
                se heading retornado é válido, girando o marcado (caso mapa orientado
                ao norte) ou o próprio mapa (caso mapa orientado ao heading).

                Por fim, atualiza rota para o próximo ponto, além de trocar o ícone
                dos waypoints a até 200 metros da atual posição.
            */
            if (!position || !position.coords) {
                console.warn('Undefined position')
                return;
            }

            window.app.mapContext.settings.geolocation.lastPosition = position;
            const { latitude, longitude, heading } = position.coords;
            
            if (window.app.plotHandle.geolocation === null) {
                window.app.model.plot.createMarker('geolocation', latitude, longitude)
            } else {
                window.app.plotHandle.geolocation.setLatLng([latitude, longitude]);
            }

            window.app.modules.Plot.setView('center', [latitude, longitude]);

            if (heading !== null) {
                window.app.mapContext.settings.orientation.lastHeading = heading;

                if (window.app.mapContext.settings.orientation.status) {
                    window.app.mapContext.settings.geolocation.setRotationAngle(heading);
                } else {
                    let mapContainer = document.getElementById('document');
                    mapContainer.style.transform = `rotate(${heading}deg) scale(1.0) `;
                    mapContainer.style.transformOrigin = 'center'; 
                }            
            }

            calculateRouteToNextWayPoint(latitude, longitude); // GetRouteCarFromHere
            checkIfNearSomeWayPoint(latitude, longitude); // DesabilitaMarquerNoGPSRaioDaEstacao
        }


        /*-----------------------------------------------------------------------------------
            ## PAINEL À ESQUERDA DO MAPA ##
        -----------------------------------------------------------------------------------*/
        static onPanelButtonClicked(event) {
            let currentSelection, index1, index2;
            console.log(event.target.id);

            switch (event.target.id) {
                case 'routeListAddBtn':
                    ({ currentSelection } = window.app.modules.Layout.findSelectedRoute());
                    ([index1, index2] = JSON.parse(currentSelection.dataset.index));
                    
                    let refRoute = JSON.parse(JSON.stringify(window.app.routingContext[index1].response.routes[index2]));
                    refRoute.automatic = false;
                    window.app.routingContext[index1].response.routes.splice(index2+1, 0, refRoute);

                    window.app.modules.Utils.syncLocalStorage('update');
                    window.app.modules.Layout.startup(index1, index2+1);
                    break;

                case 'routeListDelBtn':
                    ({ currentSelection } = window.app.modules.Layout.findSelectedRoute());
                    ([index1, index2] = JSON.parse(currentSelection.dataset.index));

                    if (window.app.routingContext[index1].response.routes.length <= 1) {
                        window.app.routingContext.splice(index1, 1);    
                    } else {
                        window.app.routingContext[index1].response.routes.splice(index2, 1);
                    }

                    window.app.modules.Utils.syncLocalStorage('update');
                    window.app.modules.Layout.startup();
                    break;
                
                case 'routeListEditModeBtn':
                    event.target.dataset.value = (event.target.dataset.value == 'on') ? 'off' : 'on';
                    window.app.modules.Layout.controller('editionMode', (event.target.dataset.value == 'on') ? true : false);
                    break;

                case 'routeListConfirmBtn':
                    // ...
                    window.document.getElementById('routeListEditModeBtn').dataset.value = 'off';
                    window.app.modules.Layout.controller('editionMode', false);
                    break;

                case 'routeListCancelBtn':
                    window.document.getElementById('routeListEditModeBtn').dataset.value = 'off';
                    window.app.modules.Layout.controller('editionMode', false);
                    break;

                case 'initialPointBtn':
                    // ...
                    break;

                case 'routeListMoveUpBtn':
                    // ...
                    break;

                case 'routeListMoveDownBtn':
                    // ...
                    break;

                default:
                    throw Error('Unexpected element Id')
            }
        }

        /*---------------------------------------------------------------------------------*/
        static onRouteListSelectionChanged(event) {
            const { htmlRouteElChildren, currentSelection, currentRoute } = window.app.modules.Layout.findSelectedRoute();

            if (currentSelection !== event.target) {
                const [index1, index2] = JSON.parse(event.target.dataset.index);
                const routing = window.app.routingContext[index1];
                const isSameCacheId = currentRoute.cacheId === routing.cacheId;
                
                htmlRouteElChildren.forEach(item => item.classList.toggle('selected', item === event.target));
                
                window.app.modules.Layout.controller('routeSelected', index1, index2);
                window.app.modules.Plot.controller(isSameCacheId ? 'update' : 'draw', index1, index2);
            }
        }

        /*---------------------------------------------------------------------------------*/
        static onPointListSelectionChanged(event, htmlPointsEl) {
            if (event.ctrlKey) {
                event.target.classList.toggle('selected');
            } else {
                const htmlPointsElChildren = Array.from(htmlPointsEl.children);
                const currentSelection = htmlPointsElChildren.indexOf(event.target);                                
                let previousSelection  = htmlPointsElChildren.findIndex(item => item.classList.contains('selected'));
            
                if (previousSelection === -1) {
                    previousSelection = currentSelection;
                }
            
                const start = Math.min(previousSelection, currentSelection);
                const end   = Math.max(previousSelection, currentSelection);
            
                for (let ii = 0; ii < htmlPointsElChildren.length; ii++) {
                    if (ii == currentSelection) {
                        htmlPointsElChildren[ii].classList.add('selected');
                    } else {
                        if (event.shiftKey && ii >= start && ii <= end) {
                            htmlPointsElChildren[ii].classList.add('selected');
                        } else {
                            htmlPointsElChildren[ii].classList.remove('selected');
                        }
                    }
                }
            }
        }

        /*---------------------------------------------------------------------------------*/
        static onHighlightTextListItem(event) {
            event.target.classList.toggle('hover', event.type === 'mouseover');
        }

        /*---------------------------------------------------------------------------------*/
        static onNumericFieldValidation(event, range) {
            let value = parseFloat(event.target.value);

            if (Number.isNaN(value) || value < range.min || value > range.max) {
                event.target.value = event.target.dataset.value; // previousValue
                return;
            }

            event.target.value = value;
            event.target.dataset.value = value;
        }


        /*-----------------------------------------------------------------------------------
            ## TOOLBAR ##
        -----------------------------------------------------------------------------------*/
        static onToolbarButtonClicked(event) {
            console.log(event.target.id);

            switch (event.target.id) {
                case 'toolbarPanelVisibilityBtn':
                    const map   = window.app.map;
                    const panel = window.document.getElementById('panel');
                    const btn   = window.document.getElementById('toolbarPanelVisibilityBtn') ;
                    let tooltip = window.document.querySelector('.tooltip');

                    panel.classList.toggle('panel-on');
                    panel.classList.toggle('panel-off');
                    setTimeout(() => map.invalidateSize(), 300);

                    btn.classList.toggle('btn-panel-on');
                    btn.classList.toggle('btn-panel-off');
                    
                    if (tooltip) {
                        tooltip.remove();
                        tooltip = null;
                    }
                    break;

                case 'toolbarImportInput':
                    if (event.target.files.length === 0) {
                        return;
                    }

                    const filename = event.target.files[0].name.toLowerCase();
                    if (!filename.endsWith('.json')) {
                        new DialogBox('Only ".json" files are allowed.', 'error');
                        return;
                    }

                    const readFile = (file) => {
                        return new Promise((resolve, reject) => {
                            const reader   = new FileReader();
                            reader.onload  = () => {
                                try {
                                    const data = JSON.parse(reader.result);
                                    resolve(data);
                                } catch (ME) {
                                    reject(`Failed to deserialize the content of the file "${file.name}": ${ME.message}`);
                                }
                            }
                            reader.onerror = (ME) => {
                                reject(`Failed to read the file "${file.name}": ${ME?.message || 'Unknown error'}`);
                            }
                            reader.readAsText(file);
                        });
                    };

                    readFile(event.target.files[0])
                        .then(returnedData => {
                            try {
                                /*
                                    Tipos de .json:
                                    - "routing": arquivo salvo em sessão prévia do webRotas;
                                    - "request": arquivo de requisição, que será enviado ao servidor.
                                */
                                if (Object.keys(returnedData).includes('routing')) {
                                    if (window.app.modules.Utils.resolvePushType(returnedData.routing)) {
                                        window.app.modules.Utils.syncLocalStorage('update');
                                    }

                                } else if (Object.keys(returnedData).includes('TipoRequisicao')) {
                                    window.app.modules.Communication.computeRoute(returnedData);

                                } else {
                                    throw Error('Unexpected file content');
                                }
                            } catch (ME) {
                                new DialogBox(ME.message, 'error');
                            }                            
                        })
                        .catch(ME => {
                            new DialogBox(ME.message, 'error');
                        });
                    break;

                case 'toolbarExportBtn':
                    window.app.modules.Utils.exportAsZip()
                        .then(()  => new DialogBox('Arquivo .zip salvo para uso em ambiente offline.', 'info'))
                        .catch(ME => new DialogBox(`Failed to export data: ${ME.message}`, 'error'))

                    /*
                    let msg = null;
                    try {
                        // CRIAR OPERAÇÃO SÍNCRONA
                        GerarKML(polylineRotaDat, pontosVisitaOrdenados, pontosvisitaDados);
                        msg = 'Arquivo .KML salvo para uso no MapsMe, Google Earth etc.';
                    } catch (ME) {
                        msg = ME.message;
                    }
                    alert(msg);
                    */
                    break;

                case 'toolbarLocationBtn':
                    // ...
                    const currentGeolocationStatus = window.app.mapContext.settings.geolocation.status;

                    if (currentGeolocationStatus === 'on') {
                        window.app.mapContext.settings.geolocation.status = 'off';
                        event.target.src = window.app.mapContext.settings.geolocation.icon.off;
                    } else {
                        window.app.mapContext.settings.geolocation.status = 'on';
                        event.target.src = window.app.mapContext.settings.geolocation.icon.on;
                    }
    
                    new DialogBox('<h1>Título</h1><p>Parágrafo</p>', 'warning'); 

                    /*
                    try {
                        AtualizaGpsTimer(gpsAtivado);
                    } catch (ME) {
                        alert(ME.message);
                    }
                    */
                    break;

                case 'toolbarOrientationBtn':
                    // ...
                    const currentOrientationStatus = window.app.mapContext.settings.orientation.status;

                    if (currentOrientationStatus === 'north') {
                        window.app.mapContext.settings.orientation.status = 'car-heading';
                        event.target.src = window.app.mapContext.settings.orientation.icon.off;
                    } else {
                        window.app.mapContext.settings.orientation.status = 'north';
                        event.target.src = window.app.mapContext.settings.orientation.icon.on;
                    }
    
                    new DialogBox('<h1>Título</h1><p>Parágrafo</p>', 'error', [], 800); 
                    new DialogBox('Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer...  Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer...', '', [{ text: 'OK', callback: () => console.log('OK'), focus: true }, { text: 'Cancel', callback: () => console.error('Cancel'), focus: false }]);

                    /*
                    window.app.mapContext.settings.orientation.status = !window.app.mapContext.settings.orientation.status;

                    let btn = document.getElementById('orientation');
                    let src = window.app.mapContext.settings.orientation.status ? window.app.mapContext.settings.orientation.icon.on : window.app.mapContext.settings.orientation.icon.off;
                    btn.style.backgroundImage = `url("${src}")`;

                    try {
                        if (window.app.mapContext.settings.orientation.status) {
                            RodaMapaPorCss(0);
                            window.app.plotHandle.geolocation.setRotationAngle(heading);
                        } else {
                            RodaMapaPorCss(-heading);
                            gpsMarker.setRotationAngle(0);
                        }
                    } catch (ME) {
                        alert(ME.message);
                    }
                    */
                    break;

                case 'toolbarColorbarBtn':
                    window.app.modules.Components.createColorbar();
                    break;

                case 'toolbarBasemapsBtn':
                    const radioButtonGroup = window.app.modules.Components.createBasemapSelector();
                    new DialogBox(radioButtonGroup, 'question', []);
                    break;

                default:
                    throw Error('Unexpected element Id')
            }
        }


        /*-----------------------------------------------------------------------------------
            ## *.* ##
        -----------------------------------------------------------------------------------*/
        static onServerConnectionStatusChanged() {
            console.log('onServerConnectionStatusChanged');
            // ...
        }
    }

    window.app.modules.Callbacks = Callbacks;
})()