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
            window.app.orientation.status = !window.app.orientation.status;

            let btn = document.getElementById('orientation');
            let src = window.app.orientation.status ? window.app.orientation.icon.on : window.app.orientation.icon.off;
            btn.style.backgroundImage = `url("${src}")`;

            try {
                if (window.app.orientation.status) {
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
            window.app.location.status = !window.app.location.status;

            let btn = document.getElementById('location');
            let src = window.app.location.status ? window.app.location.icon.on : window.app.location.icon.off;
            btn.style.backgroundImage = `url("${src}")`;
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

            window.app.geolocation.lastPosition = position;
            const { latitude, longitude, heading } = position.coords;
            
            if (window.app.plotHandle.geolocation === null) {
                window.app.model.plot.createMarker('geolocation', latitude, longitude)
            } else {
                window.app.plotHandle.geolocation.setLatLng([latitude, longitude]);
            }

            window.app.plotHandle.map.setView([latitude, longitude]);

            if (heading !== null) {
                window.app.orientation.lastHeading = heading;

                if (window.app.orientation.status) {
                    window.app.plotHandle.geolocation.setRotationAngle(heading);
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

    window.app.module.Callback = Callback;
})()