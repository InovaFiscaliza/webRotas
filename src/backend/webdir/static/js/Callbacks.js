/*
    ## webRotas Callbacks ##
    - APP
      ├── onWindowLoad
      ├── onWindowBeforeUnload
      ├── onLocalStorageUpdate
      └── onWindowMessage
    - BARRA DE NAVEGAÇÃO
      └── onNavBarButtonClicked
    - MAPA
      ├── onContextMenuCreation  
      ├── onContextMenuItemSelected
      └── updateGeoLocationPosition       (!! ToDo: PENDENTE !!)
    - PAINEL À ESQUERDA DO MAPA
      ├── onPanelButtonClicked
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

            window.app.modules.Model.syncLocalStorage('startup');
            
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
            window.app.modules.Model.syncLocalStorage('startup');
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
                    if (window.app.modules.Model.loadRouteFromFileOrServer(event.data.routing)) {
                        window.app.modules.Model.syncLocalStorage('update');
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
                            const dialogBoxText = `Esta é a versão <i>online</i> do webRotas, executada via <b>${protocol}</b>. O <i>status</i>
                                atual do servidor, contudo, é <i>offline</i>.<br><br>Quer tentar reconectar?`;

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
                    const { name, version, released, sharepoint } = window.app;
                    const { href, protocol } = window.top.location;
                    const { userAgent, vendor, deviceMemory, hardwareConcurrency } = window.navigator;
                    const platform = navigator.userAgentData?.platform || navigator.platform;
                    
                    let mobile = navigator.userAgentData?.mobile ?? window.app.modules.Utils.isMobile();
                    mobile = mobile ? '1' : '0';

                    const keyStyle = (key, value) => `<br>•&thinsp;<span style="color: gray; font-size: 10px;">${key}:</span> ${!!value ? value : 'n/a'}`;
                    const appInfo  = `
                    <p style="font-size: 12px;">O repositório das ferramentas desenvolvidas no Laboratório de inovação da SFI pode ser acessado 
                    <a href="${sharepoint}" target="_blank" rel="noopener noreferrer">aqui</a>.
                    <br><br><span style="font-size:10px;">COMPUTADOR</span>
                    ${keyStyle('platform', platform)}
                    ${keyStyle('deviceMemory', deviceMemory)}
                    ${keyStyle('hardwareConcurrency', hardwareConcurrency)}

                    <br><br><span style="font-size:10px;">NAVEGADOR</span>
                    ${keyStyle('url', href)}
                    ${keyStyle('protocol', protocol)}
                    ${keyStyle('mobile', mobile)}
                    ${keyStyle('userAgent', userAgent)}
                    ${keyStyle('vendor', vendor)}

                    <br><br><span style="font-size:10px;">APLICATIVO</span>
                    ${keyStyle('version', name)}
                    ${keyStyle('version', version)}
                    ${keyStyle('released', released)}
                    </p>
                    `;

                    new DialogBox(appInfo, 'info');
                    break;
                }
            }
        }

        /*-----------------------------------------------------------------------------------
            ## MAPA ##
        -----------------------------------------------------------------------------------*/
        static onContextMenuCreation(event) {
            /*
                ToDo: 
                Movimentar menu de contexto pela sua ancoragem. E, além disso, deixá-lo mais robusto, 
                evitando a inclusão literal dos "54px" do menu de navegação, por exemplo.
            */
            const map   = window.app.map;
            const panel = window.document.getElementById('panel');
            let context = window.document.getElementById('contextMenu');                

            if (!context) {
                context = window.app.modules.Components.createContextMenu();
            }

            const { lat, lng } = event.latlng;
            const { clientX, clientY } = event.originalEvent;
            
            context.style.left  = (panel.classList.contains('panel-on')) ? `${clientX - 5 - parseInt(getComputedStyle(panel).width)}px` : `${clientX}px`;
            context.style.top  = `${clientY - 54}px`;

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
        static onPanelButtonClicked(event, ...args) {
            // console.log(event.target.id);

            switch (event.target.id) {
                case 'routeListAddBtn': {
                    const { index1, currentRoute } = window.app.modules.Layout.findSelectedRoute();

                    const currentRouteGhost   = structuredClone(currentRoute);
                    currentRouteGhost.routeId = window.app.modules.Utils.uuid();

                    window.app.routingContext[index1].response.routes.push(currentRouteGhost);

                    window.app.modules.Model.syncLocalStorage('update', index1, window.app.routingContext[index1].response.routes.length-1);
                    break;
                }

                case 'routeListDelBtn': {
                    const { index1, index2 } = window.app.modules.Layout.findSelectedRoute();

                    if (window.app.routingContext[index1].response.routes.length <= 1) {
                        window.app.routingContext.splice(index1, 1);    
                    } else {
                        window.app.routingContext[index1].response.routes.splice(index2, 1);
                    }

                    window.app.modules.Model.syncLocalStorage('update');
                    break;
                }
                
                case 'routeListEditModeBtn':
                case 'routeListCancelBtn': {
                    /*
                        Avalia se a origem da rota foi alterada.
                    */
                    const { index1, index2, hasOriginRouteChanged } = window.app.modules.Layout.checkIfOriginChanged();
                    if (hasOriginRouteChanged) {
                        window.app.modules.Plot.controller('update', index1, index2);
                    }

                    switch (event.target.id) {
                        case 'routeListEditModeBtn': {
                            event.target.dataset.value = (event.target.dataset.value == 'on') ? 'off' : 'on';
                            window.app.modules.Layout.controller('editionMode', (event.target.dataset.value == 'on') ? true : false);
                            break;
                        }
                        case 'routeListCancelBtn': {
                            window.document.getElementById('routeListEditModeBtn').dataset.value = 'off';
                            window.app.modules.Layout.controller('editionMode', false);
                            break;
                        }
                    }                    
                    break;
                }

                case 'routeListConfirmBtn': {
                    function createCustomRoute(criterion) {
                        let origin = [];
                        if (hasOriginRouteChanged) {
                            origin     = editedOrigin;
                            origin.lat = parseFloat(origin.lat);
                            origin.lng = parseFloat(origin.lng);
                            origin.elevation = null;
                        } else {
                            origin     = {...currentRoute.origin};
                        }                    
                        
                        let waypointList = structuredClone(currentRoute.waypoints);
                        if (hasVisitOrderChanged) {
                            waypointList = visitOrderIndexes.map(index => waypointList[index]);
                        }

                        const routeId = window.app.modules.Utils.uuid();
                        const customRouteRequest = {
                            type: 'ordered',
                            origin,
                            parameters: {
                                routeId, 
                                cacheId: currentResponse.cacheId,
                                boundingBox: currentResponse.boundingBox,
                                waypoints: waypointList
                            },
                            avoidZones: currentRequest.avoidZones,
                            criterion
                        };
                        
                        const customRouteGhost = {
                            routeId,
                            automatic: criterion !== "ordered",
                            created: window.app.modules.Utils.getTimeStamp(),
                            origin,
                            waypoints: waypointList,
                            paths: [[origin.lat, origin.lng]],
                            estimatedDistance: "-1",
                            estimatedTime: "-1"
                        };

                        window.app.routingContext[index1].response.routes.push(customRouteGhost);
                        window.app.modules.Model.syncLocalStorage('update', index1, window.app.routingContext[index1].response.routes.length-1);
                        
                        window.document.getElementById('routeListEditModeBtn').dataset.value = 'off';
                        window.app.modules.Layout.controller('editionMode', false);                        
                        
                        window.app.modules.Communication.computeRoute(customRouteRequest);
                    }

                    const { index1, index2, currentRoute, editedOrigin, hasOriginRouteChanged, hasOriginDescriptionChanged } = window.app.modules.Layout.checkIfOriginChanged();
                    const currentRequest  = window.app.routingContext[index1].request;
                    const currentResponse = window.app.routingContext[index1].response;

                    const visitOrderIndexes    = Array.from(window.document.getElementById('pointsToVisit').children, child => child.value);
                    const hasVisitOrderChanged = Array.from({ length: visitOrderIndexes.length }, (_, i) => i).toString() !== visitOrderIndexes.toString();

                    if (!hasOriginRouteChanged && !hasVisitOrderChanged) {
                        if (hasOriginDescriptionChanged) {
                            currentRoute.origin.description = editedOrigin.description;
                            window.app.modules.Model.syncLocalStorage('update', index1, index2);

                            window.document.getElementById('routeListEditModeBtn').dataset.value = 'off';
                            window.app.modules.Layout.controller('editionMode', false);
                        } else {
                            new DialogBox('No changes were made to the route.', 'info');
                        }
                        return;
                    } 
                    
                    let criterion = null;
                    if (hasOriginRouteChanged && !hasVisitOrderChanged) {
                        criterion = "distance";
                    } else if (!hasOriginRouteChanged && hasVisitOrderChanged) {
                        criterion = "ordered";
                    }

                    if (criterion) {
                        createCustomRoute(criterion)
                    } else {
                        const criterionButtonGroup = window.app.modules.Components.createBasicSelector('criterion');
                        new DialogBox(criterionButtonGroup, 'question', [{ text: 'OK', callback: () => {
                            const popup = window.document.querySelector('.selector-popup');
                            const selected = popup.querySelector('input[type="radio"]:checked').value;
                            createCustomRoute(selected)
                        }, focus: true }]);
                    }
                    break;
                }

                case 'initialPointBtn': {
                    /*
                        Cria-se um marcador fantasma da origem, possibilitando alteração do seu 
                        local, com ajuste automáticos dos campos lat, lng e description, além 
                        da informação que suporta a geração dos tooltips.
                    */
                    const originMarker = window.app.mapContext.layers.routeOrigin.handle[0];
                                        
                    const originGhost  = window.L.marker(originMarker.getLatLng(), {
                        draggable: true, 
                        icon: window.app.modules.Utils.Image.customPinIcon('🏠', originMarker.options.color),
                        opacity: 0.25
                    }).addTo(window.app.map);

                    const originLat = window.document.getElementById("initialPointLatitude");
                    const originLng = window.document.getElementById("initialPointLongitude");
                    const originElevation = window.document.getElementById("initialPointElevation");
                    const originDescription = window.document.getElementById("initialPointDescription");

                    originGhost.on('drag', (event) => {
                        originLat.value = event.latlng.lat.toFixed(6);
                        originLng.value = event.latlng.lng.toFixed(6);
                    });

                    originGhost.on('dragend', (event) => {
                        originElevation.value = '-1';
                        
                        let { lat, lng } = event.target.getLatLng();
                        lat = Number(lat.toFixed(6));
                        lng = Number(lng.toFixed(6));
                        originMarker.setLatLng({ lat, lng });

                        const tooltipDescription = window.app.mapContext.layers.routeOrigin.options.iconTooltip.textResolver( {
                            lat,
                            lng,
                            elevation: -1,
                            description: originDescription.value.trim()
                        })
                        
                        window.app.mapContext.layers.routeOrigin.handle[0]._tooltip.setContent(tooltipDescription);
                        window.app.mapContext.layers.routeOrigin.handle[0]._tooltipContext.config.coords = [lat, lng];
                        window.app.mapContext.layers.routeOrigin.handle[0]._tooltipContext.config.text = tooltipDescription;
                        
                        if (window.app.mapContext.layers.routeOrigin.handle[0]._tooltipContext.handle.sticky) {
                            window.app.mapContext.layers.routeOrigin.handle[0]._tooltipContext.handle.sticky.setContent(tooltipDescription);
                            window.app.mapContext.layers.routeOrigin.handle[0]._tooltipContext.handle.sticky.setLatLng({ lat, lng });
                        }

                        originGhost.remove();
                    })
                    break;
                }

                case 'initialPointLatitude':
                case 'initialPointLongitude': {
                    const range = args[0];
                    this.onNumericFieldValidation(event, range);
                    
                    const htmlEl = window.app.modules.Layout.getDOMElements([
                        'initialPointLatitude',
                        'initialPointLongitude',
                        'initialPointDescription'
                    ]);

                    const lat = parseFloat(htmlEl.initialPointLatitude.value);
                    const lng = parseFloat(htmlEl.initialPointLongitude.value);

                    /*
                        Atualização plot
                    */
                    const originMarker = window.app.mapContext.layers.routeOrigin.handle[0];
                    originMarker.setLatLng({ lat, lng });

                    const tooltipDescription = window.app.mapContext.layers.routeOrigin.options.iconTooltip.textResolver( {
                        lat,
                        lng,
                        elevation: -1,
                        description: htmlEl.initialPointDescription.value.trim()
                    })
                    
                    window.app.mapContext.layers.routeOrigin.handle[0]._tooltip.setContent(tooltipDescription);
                    window.app.mapContext.layers.routeOrigin.handle[0]._tooltipContext.config.coords = [lat, lng];
                    window.app.mapContext.layers.routeOrigin.handle[0]._tooltipContext.config.text = tooltipDescription;
                    
                    if (window.app.mapContext.layers.routeOrigin.handle[0]._tooltipContext.handle.sticky) {
                        window.app.mapContext.layers.routeOrigin.handle[0]._tooltipContext.handle.sticky.setContent(tooltipDescription);
                        window.app.mapContext.layers.routeOrigin.handle[0]._tooltipContext.handle.sticky.setLatLng({ lat, lng });
                    }
                    break;
                }

                case 'routeListMoveUpBtn':
                case 'routeListMoveDownBtn': {
                    const htmlContainer = window.document.getElementById('pointsToVisit');
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
                    throw new Error('Unexpected element Id')
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
            let value = Number(parseFloat(event.target.value).toFixed(6));

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
                    /*
                        São dois os tipos de .json aceitos pelo webRotas. O "request", que 
                        é enviado ao servidor p/ geração de uma nova rota, e "routing", que 
                        é um arquivo salvo em sessão prévia do webRotas.

                        A estrutura desses arquivos devem possuir as seguintes chaves:
                        - "request": ["type", "origin", "avoidZones", "parameters" ]
                        - "routing": ["routing"]
                    */

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
                                if (!returnedData || typeof returnedData !== "object" || Array.isArray(returnedData)) {
                                    throw new Error("Invalid JSON structure");
                                }

                                const expectedKeys = window.app.mapContext.settings.importFile.expectedKeys;

                                if (expectedKeys.request.every(key => key in returnedData)) {
                                    const protocol = window.location.protocol;
                                    if (protocol === "file:") {
                                        throw new Error(`Esta é a versão <i>offline</i> do webRotas, executada via <b>${protocol}</b>.<br><br>
                                                        Recursos que dependem de comunicação com o servidor foram removidos ou desativados.`);
                                    }
                                    window.app.modules.Communication.computeRoute(returnedData);

                                } else if (expectedKeys.routing.every(key => key in returnedData)) {
                                    if (window.app.modules.Model.loadRouteFromFileOrServer(returnedData.routing)) {
                                        window.app.modules.Model.syncLocalStorage('update');
                                    }

                                } else {
                                    throw new Error('Unexpected file content');
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
                    const exportButtonGroup = window.app.modules.Components.createBasicSelector('exportFile');
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

                case 'toolbarPositionSlider': {
                    const min = Number(event.target.min);
                    const max = Number(event.target.max);
                    const val = Number(event.target.value);
                    const percent = 100*(val - min) / (max - min);

                    const fillColor = getComputedStyle(window.document.documentElement).getPropertyValue('--backgroundColor-slider-value').trim() || '#4caf50';
                    const trackBg   = getComputedStyle(window.document.documentElement).getPropertyValue('--backgroundColor-slider').trim()       || 'rgb(180, 180, 180)';
                    event.target.style.background = `linear-gradient(to right, ${fillColor} 0%, ${fillColor} ${percent}%, ${trackBg} ${percent}%, ${trackBg} 100%)`;

                    window.document.getElementById("toolbarPositionSliderValue").textContent = `${val}%`;

                    if (window.app.routingContext.length) {
                        const { currentRoute } = window.app.modules.Layout.findSelectedRoute();
                        
                        const index  = Math.floor(currentRoute.paths.length * val / 100);
                        const coords = currentRoute.paths.slice(0, index);
                        window.app.modules.Plot.update('toolbarPositionSlider', coords)
                    }
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
                    currentRoute 
                    ? window.app.modules.Plot.setView('zoom', [...currentRoute.waypoints, currentRoute.origin])
                    : window.app.modules.Plot.setView('center', window.app.mapContext.settings.position.default.center, window.app.mapContext.settings.position.default.zoom);
                    break;
                }

                default:
                    throw new Error('Unexpected element Id')
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