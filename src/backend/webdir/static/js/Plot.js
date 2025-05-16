/*
    ToDo:
    - Organizar window.app.routeList, de forma que sejam registrados, de forma consistente, 
      os "waypoints" e o "routeMidpoint" com a mesma informação (id, descrição, coordenadas,
      altitude etc). Atualmente, ListaRotasCalculadas[0].pontoinicial é bem diferente de 
      ListaRotasCalculadas[0].pontosvisitaDados. E, por fim, ao invés de fazer um array de array,
      organizar a informação em objetos, de forma que tenhamos um array de objetos, evitando 
      coisas como "coord[5]".

    - Limitar a atualização dos waypointsA atualização dos waypoints parece algo complicado porque
      demandaria alterar não apenas as suas coordenadas, mas também
      o tooltip. Neste momento, por simplicidade, os marcadores serão
      recriados.
*/

(function () {
    class Plot {
        /*---------------------------------------------------------------------------------*/
        static controller(type, ...args) {
            let routing, route, returnedData;
            let index1, index2;

            switch (type) {
                case 'clearAll':
                    this.remove('allLayers');
                    break;

                case 'clearForUpdate':
                    this.remove('specificLayers', 'routeMidpoint', 'routeOrigin', 'waypoints');
                    break;

                case 'draw':
                    index1 = args[0];
                    index2 = args[1];

                    routing = window.app.routingContext[index1];
                    route = routing.response.routes[index2];
            
                    window.app.mapContext.settings.colormap.range = window.app.modules.Utils.Elevation.range(route);
                  //window.app.modules.Utils.GeoLocation.routeMidPoint(route);

                    this.controller('clearAll');
                    this.create('boundingBox',              routing.response.boundingBox);
                  //this.create('avoidZones',               routing.response.avoidZones);
                    this.create('locationLimits',           routing.response.location.limits);
                    this.create('locationUrbanAreas',       routing.response.location.urbanAreas);
                    this.create('locationUrbanCommunities', routing.response.location.urbanCommunities);

                    this.create('routePath',                route.paths);
                  //this.create('routeMidpoint',            route.midpoint);
                    this.create('routeOrigin',              route.origin);
                    this.create('waypoints',                route.waypoints);
                    this.setView('zoom',                    [...route.waypoints, route.origin])
                    break;

                case 'update':
                    index1 = args[0];
                    index2 = args[1];

                    routing = window.app.routingContext[index1];
                    route = routing.response.routes[index2];

                    window.app.mapContext.settings.colormap.range = window.app.modules.Utils.Elevation.range(route);
                  //window.app.modules.Utils.GeoLocation.routeMidPoint(route);

                    this.controller('clearForUpdate');
                    this.update('routePath',                route.paths);
                  //this.create('routeMidpoint',            route.midpoint);
                    this.create('routeOrigin',              route.origin);
                    this.create('waypoints',                route.waypoints);
                    this.setView('zoom',                    [...route.waypoints, route.origin])
                    break;

                case 'updateCurrentLeg':
                    returnedData = args[0];

                    this.update('currentLeg',               returnedData);
                    this.update('currentPosition',          returnedData);
                    this.setView('center',                  returnedData)
                    break;
            }
        }

        /*---------------------------------------------------------------------------------*/
        static create(tag, geoData) {
            const map = window.app.map;

            if (!geoData) {
                window.app.modules.Utils.consoleLog(`Unknown data encountered while creating layer "${tag}"`, 'warn');
                return;
            }

            if (!Array.isArray(geoData)) {
                geoData = [geoData];
            }

            const type    = window.app.mapContext.layers[tag].type;
            const options = window.app.mapContext.layers[tag].options;
            let handle, coords;

            switch (type) {
                case 'marker':
                    handle = [];

                    geoData.forEach((element, index) => {
                        let marker;
                        let lat, lng, elevation;
                        let icon, color;

                        ( { lat, lng, elevation } = element);
                        coords = [lat, lng];

                        switch (options.iconType) {
                            case 'file':
                                icon = window.L.icon({
                                    iconUrl: options.iconUrl,
                                    iconSize: options.iconSize,
                                    iconAnchor: options.iconAnchor
                                });
                                break;

                            case 'customPinIcon':
                                color  = window.app.modules.Utils.Image.pinColor(elevation, window.app.mapContext.settings.colormap.scale);
                                icon   = window.app.modules.Utils.Image.customPinIcon(index, color);
                                break;

                            case 'customPinIcon:Home':
                                color  = window.app.modules.Utils.Image.pinColor(elevation, window.app.mapContext.settings.colormap.scale);
                                icon   = window.app.modules.Utils.Image.customPinIcon('🏠', color);
                                break;

                            default:
                                icon = new L.Icon.Default({
                                    iconSize: options.iconSize,
                                    tooltipAnchor: [0, 0]
                                });
                        }

                        marker = window.L.marker(coords, { icon }).addTo(map);

                        /*
                            Caso tooltip esteja habilitado, o marker estará relacionado a três 
                            eventos: mouseover e click (ambos definidos em "Tooltip.js"), além
                            de dblclick, definido aqui.
                        */
                        marker.on('dblclick', () => {
                            marker.setOpacity((marker.options.opacity === 1) ? 0.35 : 1);
                        })
                        window.L.DomEvent.on(marker, 'dblclick', window.L.DomEvent.stopPropagation);

                        if (options.iconTooltip.status) {
                            let textResolver = options.iconTooltip.textResolver;
                            if (textResolver === 'default' || typeof textResolver !== 'function') {
                                textResolver = window.app.mapContext.settings.tooltip.textResolver;
                            }
                            const text = textResolver(element);
                            
                            let offsetResolver = options.iconTooltip.offsetResolver;
                            if (offsetResolver === 'default' || typeof offsetResolver !== 'function') {
                              offsetResolver = window.app.mapContext.settings.tooltip.offsetResolver;
                            }

                            const direction = window.app.mapContext.settings.tooltip.direction;
                            
                            window.app.modules.Tooltip.bindLeafletTooltip(map, marker, coords, text, direction, offsetResolver);
                        } 
                        
                        handle.push(marker);
                    })
                    break;

                case 'polyline':
                    coords = geoData;
                    handle = window.L.polyline(coords, options).addTo(map);
                    break;

                case 'polygon':
                    coords = geoData;
                    handle = window.L.polygon(coords,  options).addTo(map);
                    break;

                default:
                    window.app.modules.Utils.consoleLog(`Unexpected Leaflet object type "${type}"`, 'warn');
                    return;
            }

            window.app.mapContext.layers[tag].handle = handle;
        }        
        
        /*---------------------------------------------------------------------------------*/
        static update(tag, coords) {
            const handle = window.app.mapContext.layers[tag].handle;
            if (!handle){ 
                this.create(tag, coords)
                return;
            }

            const type = this.checkPlotType(handle);
            switch (type) {
                case 'marker':
                    handle.setLatLng(coords);
                    break;

                case 'polyline':
                case 'polygon':
                    handle.setLatLngs(coords);
                    break;

                default:
                    window.app.modules.Util.consoleLog(`Unexpected Leaflet object type "${type}"`, 'warn');
                    return
            }
        }

        /*---------------------------------------------------------------------------------*/
        static remove(type, ...args) {
            const map = window.app.map;

            switch (type) {
                case 'allLayers':                    
                    map.eachLayer(layer => {
                        if (!(layer instanceof window.L.TileLayer)) {
                            this.removeTooltip(map, layer);
                            map.removeLayer(layer);
                        }
                    });
                    break;

                case 'specificLayers':
                    const tags = args;
                    tags.forEach(tag => {
                        const handle = window.app.mapContext.layers[tag].handle;
                        if (!handle) return;

                        handle.forEach(el => {
                            this.removeTooltip(map, el);
                            el.remove();
                        });
                    });
                    break;
            }
        }

        /*---------------------------------------------------------------------------------*/
        static removeTooltip(map, target) {
            const tooltip = target._tooltipContext?.handle.sticky;
            if (tooltip instanceof window.L.Tooltip && map.hasLayer(tooltip)) {
                map.removeLayer(tooltip);
            }
        }

        /*---------------------------------------------------------------------------------*/
        static changeVisibility(tag) {
            const handle = window.app.mapContext.layers[tag].handle;
            if (!handle) return;

            const type = this.checkPlotType(handle);
            let isVisible;
            switch (type) {
                case 'marker':    
                    isVisible = handle._icon.checkVisibility();
                    handle._icon.style.display = isVisible ? 'none' : 'block';
                    break;

                case 'polyline':
                case 'polygon':
                    isVisible = handle._path.checkVisibility();
                    handle._path.style.display = isVisible ? 'none' : 'block';
                    break;

                default:
                    window.app.modules.Utils.consoleLog(`Unexpected Leaflet object type "${type}"`, 'warn');
                    return;
            }
        }

        /*---------------------------------------------------------------------------------*/
        static checkPlotType(handle) {
            if (handle instanceof window.L.Marker) {
                return 'marker';
            } else if (handle instanceof window.L.Polyline) {
                return 'polyline';
            } else if (handle instanceof window.L.Polygon) {
                return 'polygon';
            } else {
                return 'unknown';
            }
        }

        /*---------------------------------------------------------------------------------*/
        static setView(operationType, geoData) {
            const map = window.app.map;

            switch (operationType) {
                case 'zoom':
                    if (!Array.isArray(geoData)) {
                        geoData = [geoData];
                    }

                    let coords = [];
                    geoData.forEach(element => coords.push([element.lat, element.lng]));

                    map.fitBounds(coords);
                    window.app.mapContext.settings.position.center = map.getCenter();
                    window.app.mapContext.settings.position.zoom   = map.getZoom();
                    break;

                case 'center':
                    map.setView(geoData);
                    break;
            }
        }
    }

    window.app.modules.Plot = Plot;
})()