(function () { 
    class Callback {
        static updateLayout(operationType) {
            switch (operationType) {
                case 'server-status-changed':
                    console.log(operationType);
                    break;
                default:
                    // Pendente
            }
        }


        /* ## HTML LISTENERS ## */
        static addEventListener(component, eventName, ...args) {
            switch (eventName) {
                case 'input:numeric:range-validation':
                    component.addEventListener('input', (event) => {                                
                        const value = component.valueAsNumber;
                        const min   = parseFloat(component.min);
                        const max   = parseFloat(component.max);
        
                        if (value < min) component.value = min;
                        if (value > max) component.value = max;
                    });
                    break;

                default:
                    // PENDENTE
                    break;
            }
        }

        /* ## PANEL ## */
        static onRouteListChange(event) {
            switch (event.sourceTarget.id) {
                case 'routeListEditionMode':
                    console.log(event.sourceTarget.id);
                    break;

                case 'routeListEditionConfirm':
                    console.log(event.sourceTarget.id);
                    break;

                case 'routeListEditionCancel':
                    console.log(event.sourceTarget.id);
                    break;

                default:
                    throw Error('Unexpected element Id')
            }
        }

        /* ## TOOLBAR ## */
        static toolbar_routeButtonClick() {
            let panelContainer = document.getElementById('left-panel');

            if (panelContainer.classList.contains('left-panel-on')) {
                panelContainer.classList.remove('left-panel-on');
                panelContainer.classList.add('left-panel-off');

                setTimeout(() => window.app.map.invalidateSize(), 300);
            } else {
                panelContainer.classList.remove('left-panel-off');
                panelContainer.classList.add('left-panel-on');
            }

            let tooltip = document.querySelector('.tooltip');
            if (tooltip) {
                tooltip.remove();
                tooltip = null;
            }
        }

        static toolbar_orientationButtonClick() {
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
        }

        static toolbar_locationButtonClick() {
            let currentStatus, iconSrc;
            currentStatus = window.app.mapContext.settings.geolocation.status;

            if (currentStatus == 'on') {
                window.app.mapContext.settings.geolocation.status = 'off'
                iconSrc = window.app.mapContext.settings.geolocation.icon.off;
            } else {
                window.app.mapContext.settings.geolocation.status = 'on'
                iconSrc = window.app.mapContext.settings.geolocation.icon.on;
            }

            window.document.getElementById('location').style.backgroundImage = `url("${src}")`;

            try {
                AtualizaGpsTimer(gpsAtivado);
            } catch (ME) {
                alert(ME.message);
            }
        }

        static toolbar_exportKmlButtonClick() {
            let msg = null;
            try {
                // CRIAR OPERAÇÃO SÍNCRONA
                GerarKML(polylineRotaDat, pontosVisitaOrdenados, pontosvisitaDados);
                msg = 'Arquivo .KML salvo para uso no MapsMe, Google Earth etc.';
            } catch (ME) {
                msg = ME.message;
            }
            alert(msg);
        }

        static toolbar_colorbarButtonClick() { 
            console.log("Colorbar Button Clicked");
        }


        /* ## PAINEL ## */
        static panel_routePanelClick() {
            console.log("Route Panel Clicked");
        }


        /* ## MAPA ## */
        static map_click() {
            console.log("Map Clicked");
        }

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
    }

    window.app.modules.Callback = Callback;
})()