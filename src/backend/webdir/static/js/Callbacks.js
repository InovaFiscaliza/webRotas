/*
    ## webRotas Callbacks ##
    - APP
      ├── onWindowLoad
      ├── onWindowBeforeUnload
      └── onLocalStorageUpdate
    - BARRA DE NAVEGAÇÃO
      └── onNavBarButtonClicked
    - MAPA
      ├── onContextMenuCreation  
      ├── onContextMenuItemSelected
      └── updateGeoLocationPosition       (!! ToDo: PENDENTE !!)
    - PAINEL À ESQUERDA DO MAPA
      ├── onPanelButtonClicked            (!! ToDo: PENDENTE "initialPointBtn" !!)
      ├── onRouteListSelectionChanged
      ├── onPointListSelectionChanged
      ├── onHighlightTextListItem
      └── onNumericFieldValidation
    - TOOLBAR
      └── onToolbarButtonClicked          (!! ToDo: PENDENTE "toolbarLocationBtn" & toolbarOrientationBtn" !!)
    - *.*
      └── onServerConnectionStatusChanged

    Alguns dos layers do mapa proveem interações, mas os seus callbacks estão descritos
    na sua criação.
*/
(function () { 
    class Callbacks {
        /*-----------------------------------------------------------------------------------
            ## APP ##
        -----------------------------------------------------------------------------------*/
        static onWindowLoad(event) {
            window.app.modules.Components.createNavBar();
            window.app.modules.Components.createPanel();
            window.app.modules.Components.createMap();
            window.app.modules.Components.createToolbar();

            window.app.modules.Utils.syncLocalStorage('startup');
            window.app.modules.Layout.startup();

            window.app.modules.Communication.isServerOnlineController();
            window.app.modules.Utils.Image.loadImagesForCache();
            window.app.modules.Utils.consoleLog('Session started');
        }

        /*---------------------------------------------------------------------------------*/
        static onWindowBeforeUnload(event) {
            event.preventDefault();
            event.returnValue = '';
        }

        /*---------------------------------------------------------------------------------*/
        static onLocalStorageUpdate(event) {
            /*
                Operação disparada quando ocorre alteração no localStorage em outra aba,
                mesma url, mantendo consistência na lista de rotas sob análise.
            */
            if (event.storageArea !== window.localStorage) {
                return;
            }

            //new DialogBox('Changes detected in another tab. Reloading...', 'info');
            window.app.modules.Utils.consoleLog('Changes detected in another tab. Reloading...')
            window.app.modules.Utils.syncLocalStorage('startup');
            window.app.modules.Layout.startup();
        }

        static onWindowMessage(event) {
            /*
                Operação disparada quando a versão online do webRotas é iniciada
                a partir da sua versão offline.
            */
            if (event.origin === "null" || event.origin === "file://") {
                const urlParameters = new URLSearchParams(window.location.search);
                const expectedToken = urlParameters.get("token");

                if (event.data.type === "handshake" && event.data.token === expectedToken && !!event.data.routing.length) {
                    if (window.app.modules.Utils.resolvePushType(event.data.routing)) {
                        window.app.modules.Utils.syncLocalStorage('update');
                    }
                }
            }
        }


        /*-----------------------------------------------------------------------------------
            ## BARRA DE NAVEGAÇÃO ##
        -----------------------------------------------------------------------------------*/
        static onNavBarButtonClicked(event) {
            switch (event.target.id) {
                case 'serverStatusBtn': {
                    const protocol = window.location.protocol;

                    switch (protocol) {
                        case  "file:": {
                            const dialogBoxText = `Esta é a versão <i>offline</i> do webRotas, executada via <b>${protocol}</b>.<br><br>
                                Recursos que dependem de comunicação com o servidor, como a criação de rotas customizadas, foram 
                                removidos ou desativados.<br><br>Se o servidor estiver disponível, é possível abrir a versão 
                                <i>online</i> do webRotas. Deseja continuar?`;

                            new DialogBox(dialogBoxText, '', [{ 
                                text: 'Sim', 
                                callback: () => {
                                    try {
                                        const token  = window.app.modules.Utils.uuid();
                                        const url    = `${app.server.url}/webRotas/index.html?token=${token}`;
                                        const newWin = window.open(url, '_blank');
                                        setTimeout(() => newWin.postMessage({ 
                                            type: "handshake", 
                                            token, 
                                            routing: window.app.routingContext 
                                        }, url), 1000);
                                    } catch (ME) {
                                        new DialogBox(`${ME.message}`, 'error');
                                    }
                                },
                                focus: true 
                            }, { 
                                text: 'Não', 
                                callback: () => {},
                                focus: false 
                            }]);
                            break;
                        }

                        default: {
                            const dialogBoxText = `Esta é a versão <i>online</i> do webRotas, executada via <b>${protocol}</b>. Entretanto, o <i>status</i>
                                atual do servidor é <i>offline</i>.<br><br>Quer tentar reconectar?`;

                            new DialogBox(dialogBoxText, '', [{ 
                                text: 'Sim', 
                                callback: () => window.app.modules.Communication.isServerOnlineController(),
                                focus: true 
                            }, { 
                                text: 'Não', 
                                callback: () => {},
                                focus: false 
                            }]);
                        }
                    }
                    break;
                }

                case 'appInfoBtn': {
                    new DialogBox('Informações gerais sobre o app... sobre o navegador etc...', 'info');
                    break;
                }
            }
        }

        /*-----------------------------------------------------------------------------------
            ## MAPA ##
        -----------------------------------------------------------------------------------*/
        static onContextMenuCreation(event) {
            const map   = window.app.map;
            const panel = window.document.getElementById('panel');
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
            // console.log(event.target.id);

            switch (event.target.id) {
                case 'routeListAddBtn': {
                    const { currentSelection } = window.app.modules.Layout.findSelectedRoute();
                    const [index1, index2] = JSON.parse(currentSelection.dataset.index);
                    
                  //let refRoute = JSON.parse(JSON.stringify(window.app.routingContext[index1].response.routes[index2]));
                    let refRoute = structuredClone(window.app.routingContext[index1].response.routes[index2]);
                    refRoute.automatic = false;
                    window.app.routingContext[index1].response.routes.splice(index2+1, 0, refRoute);

                    window.app.modules.Utils.syncLocalStorage('update');
                    window.app.modules.Layout.startup(index1, index2+1);
                    break;
                }

                case 'routeListDelBtn': {
                    const { currentSelection } = window.app.modules.Layout.findSelectedRoute();
                    const [index1, index2] = JSON.parse(currentSelection.dataset.index);

                    if (window.app.routingContext[index1].response.routes.length <= 1) {
                        window.app.routingContext.splice(index1, 1);    
                    } else {
                        window.app.routingContext[index1].response.routes.splice(index2, 1);
                    }

                    window.app.modules.Utils.syncLocalStorage('update');
                    window.app.modules.Layout.startup();
                    break;
                }
                
                case 'routeListEditModeBtn': {
                    event.target.dataset.value = (event.target.dataset.value == 'on') ? 'off' : 'on';
                    window.app.modules.Layout.controller('editionMode', (event.target.dataset.value == 'on') ? true : false);
                    break;
                }

                case 'routeListConfirmBtn': {
                    const { index1, index2 } = window.app.modules.Layout.findSelectedRoute();                    
                    const currentRequest = window.app.routingContext[index1].request;
                    const currentRoute   = window.app.routingContext[index1].response.routes[index2];

                    const htmlEl = window.app.modules.Layout.getDOMElements([
                        'initialPointLatitude',
                        'initialPointLongitude',
                        'initialPointDescription',
                        'pointsToVisit'
                    ]);

                    const initialOrigin = [
                        currentRoute.origin.lat.toFixed(6),
                        currentRoute.origin.lng.toFixed(6),
                        currentRoute.origin.description.trim()
                    ];

                    const editedOrigin = [
                        parseFloat(htmlEl.initialPointLatitude.value).toFixed(6),
                        parseFloat(htmlEl.initialPointLongitude.value).toFixed(6),
                        htmlEl.initialPointDescription.value.trim()
                    ];

                    const hasOriginChanged     = (initialOrigin.slice(0,2).toString() !== editedOrigin.slice(0,2).toString()) ? true : false;
                    const visitOrderIndexes    = Array.from(htmlEl.pointsToVisit.children, child => child.value);
                    const hasVisitOrderChanged = Array.from({ length: visitOrderIndexes.length }, (_, i) => i).toString() !== visitOrderIndexes.toString();

                    if (!hasOriginChanged && !hasVisitOrderChanged) {
                        new DialogBox('No changes were made to the route.', 'info');
                        return;
                    }

                    /*
                        O servidor precisa evoluir p/ identificar a porta do container
                        e a identificação do usuário a partir do sessionId, e não do 
                        "PortaOSRMServer" e "UserName".

                        Eliminar duplicidade de chaves: "PontoInicial" e "pontoinicial",
                        "User" e "UserName".

                        Usar nomes em inglês: "requestType", "origin", "waypoints" etc.
                    */

                    const request = structuredClone(currentRequest);
                    // "routeId", "origin", "waypoints", "avoidZones", "boundingBox"
                    request.requestType     = "customRoute";
                    request.OSRMServerPort  = 50001;
                    request.origin          = hasOriginChanged ? editedOrigin : initialOrigin;
                    request.origin[0]       = parseFloat(request.PontoInicial[0]);
                    request.origin[1]       = parseFloat(request.PontoInicial[1]);

                    if (hasVisitOrderChanged) {
                        const editedWaypointsList = visitOrderIndexes.map(index => currentRoute.waypoints[index]);
                        request.waypoints   = editedWaypointsList.map(item => [item.lat, item.lng, item.description.trim()]);
                    } else {
                        request.waypoints   = currentRoute.waypoints.map(item => [item.lat, item.lng, item.description.trim()]);
                    }

                    request.avoidZones      = currentRequest.regioes;
                    request.boundingBox     = currentRoute.boundingBox;

                    /*
                        Enquanto não se refatora o backend...
                    */

                    const keysToRemove = ['pontoinicial', 'PontoInicial', 'pontosvisita', 'regioes', 'UserName', 'User'];
                    for (const key of keysToRemove) {
                        if (key in request) delete request[key];
                    }

                    window.app.modules.Communication.computeRoute(request);
                    console.log(request);

                    /*
                        Criar um novo elemento à routingContext, mas bloqueado... esse novo elemento
                        será desbloqueado quando retornar a resposta.

                        Essa sistemática tem que valer p/ novas requisições também!
                    */

                    window.document.getElementById('routeListEditModeBtn').dataset.value = 'off';
                    window.app.modules.Layout.controller('editionMode', false);
                    break;
                }

                case 'routeListCancelBtn': {
                    window.document.getElementById('routeListEditModeBtn').dataset.value = 'off';
                    window.app.modules.Layout.controller('editionMode', false);
                    break;
                }

                case 'initialPointBtn': {
                    // ...
                    break;
                }

                case 'routeListMoveUpBtn':
                case 'routeListMoveDownBtn': {
                    const htmlContainer = window.app.modules.Layout.getDOMElements(['pointsToVisit']).pointsToVisit;
                    const selectedItems = Array.from(htmlContainer.children).filter(item => item.classList.contains('selected'));

                    if (selectedItems.length === 0) {
                        return;
                    }

                    function moveItems(items, direction) {
                        const isUp = direction === 'up';
                        const ordered = isUp ? items : [...items].reverse();

                        for (const item of ordered) {
                            const sibling = isUp ? item.previousElementSibling : item.nextElementSibling;
                            if (!sibling || selectedItems.includes(sibling)) continue;

                            htmlContainer.insertBefore(item, isUp ? sibling : sibling.nextSibling);
                        }
                    }

                    switch (event.target.id) {
                        case 'routeListMoveUpBtn':
                            moveItems(selectedItems, 'up');
                            break;
                        case 'routeListMoveDownBtn':
                            moveItems(selectedItems, 'down');
                            break;
                    }
                    break;
                }

                default:
                    throw Error('Unexpected element Id')
            }
        }

        /*---------------------------------------------------------------------------------*/
        static onRouteListSelectionChanged(event) {
            const { htmlRouteElChildren, currentSelection, index1 } = window.app.modules.Layout.findSelectedRoute();
            const currentRouting = window.app.routingContext[index1];

            if (currentSelection !== event.target) {
                const [index1, index2] = JSON.parse(event.target.dataset.index);
                const routing = window.app.routingContext[index1];
                const isSameCacheId = currentRouting.response.cacheId === routing.response.cacheId;
                
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
            // console.log(event.target.id);

            switch (event.target.id) {
                case 'toolbarPanelVisibilityBtn': {
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
                }

                case 'toolbarImportInput': {
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
                }

                case 'toolbarExportBtn': {
                    const exportButtonGroup = window.app.modules.Components.createExportSelector();
                    new DialogBox(exportButtonGroup, 'question', [{ text: 'OK', callback: () => {
                        const popup = window.document.querySelector('.selector-popup');
                        const selected = popup.querySelector('input[type="radio"]:checked').value;

                        switch (selected) {
                            case 'JSON': {
                                const fileName = window.app.modules.Utils.defaultFileName('webRotas', 'json');
                                window.app.modules.Utils.exportAsJSON(fileName);
                                break;
                            }

                            case 'KML': {
                                const fileName = window.app.modules.Utils.defaultFileName('webRotas', 'kml');
                                window.app.modules.Utils.exportAsKML(fileName);
                                break;
                            }

                            case 'HTML+JS+CSS': {
                                const fileName = window.app.modules.Utils.defaultFileName('webRotas', 'zip');
                                window.app.modules.Utils.exportAsZip(fileName);
                                break;
                            }
                        }
                    }, focus: true }]);
                    break;
                }

                case 'toolbarLocationBtn': {
                    // ...

                    /*
                    const currentGeolocationStatus = window.app.mapContext.settings.geolocation.status;

                    if (currentGeolocationStatus === 'on') {
                        window.app.mapContext.settings.geolocation.status = 'off';
                        event.target.src = window.app.mapContext.settings.geolocation.icon.off;
                    } else {
                        window.app.mapContext.settings.geolocation.status = 'on';
                        event.target.src = window.app.mapContext.settings.geolocation.icon.on;
                    }
    
                    new DialogBox('<h1>Título</h1><p>Parágrafo</p>', 'warning'); 
                    */

                    /*
                    try {
                        AtualizaGpsTimer(gpsAtivado);
                    } catch (ME) {
                        alert(ME.message);
                    }
                    */
                    break;
                }

                case 'toolbarOrientationBtn': {
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
                }

                case 'toolbarColorbarBtn': {
                    window.app.modules.Components.createColorbar();
                    break;
                }

                case 'toolbarBasemapsBtn': {
                    const radioButtonGroup = window.app.modules.Components.createBasemapSelector();
                    new DialogBox(radioButtonGroup, 'question', []);
                    break;
                }

                case 'toolbarInitialZoomBtn': {
                    const { currentRoute } = window.app.modules.Layout.findSelectedRoute();
                    if (currentRoute) {
                        window.app.modules.Plot.setView('zoom', [...currentRoute.waypoints, currentRoute.origin])
                    }
                    break;
                }

                default:
                    throw Error('Unexpected element Id')
            }
        }


        /*-----------------------------------------------------------------------------------
            ## *.* ##
        -----------------------------------------------------------------------------------*/
        static onServerConnectionStatusChanged() {
            const serverStatusBtn = window.document.getElementById('serverStatusBtn');
            
            Object.assign(serverStatusBtn.style, { 
                display: window.app.server.status === 'online' ? 'none' : 'block'
            });
        }
    }

    window.app.modules.Callbacks = Callbacks;
})()