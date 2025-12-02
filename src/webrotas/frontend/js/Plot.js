/*
    ## webRotas Plot ##      
    - Plot
      ├── controller
      ├── create
      ├── update
      ├── remove
      ├── removeTooltip
      ├── changeVisibility
      ├── checkPlotType
      └── setView
*/

(function () {
    class Plot {
        /*---------------------------------------------------------------------------------*/
        static controller(type, ...args) {
            switch (type) {
                case 'clearAll': {
                    this.remove('allLayers');
                    this.setView('zoom');
                    break;
                }

                case 'clearForUpdate': {
                    this.remove('specificLayers', 'routeMidpoint', 'routeOrigin', 'waypoints');
                    break;
                }

                case 'draw': 
                case 'update': {
                    const index1 = args[0];
                    const index2 = args[1];

                    const routing = window.app.routingContext[index1];
                    const route = routing.response.routes[index2];
            
                    window.app.mapContext.settings.colormap.range.current = window.app.modules.Utils.Elevation.range(route);
                    window.app.modules.Components.updateColorbar();
                  //window.app.modules.Utils.GeoLocation.routeMidPoint(route);

                    switch (type) {
                        case 'draw': {
                            this.controller('clearAll');

                            const avoidZonesRaw = routing.request.avoidZones;
                            let avoidZones = [];
                            if (avoidZonesRaw) {
                                avoidZones = avoidZonesRaw.map(el => el.coord);
                                this.create('avoidZones',           avoidZones);
                            }

                            this.create('locationLimits',           routing.response.location.limits);
                            this.create('locationUrbanAreas',       routing.response.location.urbanAreas);
                            this.create('locationUrbanCommunities', routing.response.location.urbanCommunities);
                            this.create('routePath',                route.paths);
                            this.create('toolbarPositionSlider',   [route.paths[0]]);
                            break;
                        }

                        case 'update': {
                            this.controller('clearForUpdate');

                            this.update('routePath',                route.paths);
                            break;
                        }
                    }

                    const routePositionSlider = window.document.getElementById("toolbarPositionSlider");
                    routePositionSlider.value = 0;
                    window.app.modules.Callbacks.onToolbarButtonClicked({ target: routePositionSlider })

                  //this.create('routeMidpoint',            route.midpoint);
                    this.create('routeOrigin',              route.origin);
                    this.create('waypoints',                route.waypoints);
                    
                    const lastPosition = window.app.mapContext.settings.geolocation.lastPosition
                    if (lastPosition) {
                        const { latitude, longitude } = window.app.mapContext.settings.geolocation.lastPosition.coords;
                        window.app.modules.Plot.create('currentPosition', { lat: latitude, lng: longitude })
                    }

                    this.setView('zoom');
                    break;
                }

                case 'updateCurrentLeg': {
                    const returnedData = args[0];

                    this.update('currentLeg',      returnedData);
                    this.update('currentPosition', returnedData);
                    this.setView('center',         returnedData)
                    break;
                }
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

            if (!geoData.length) {
                return;
            }

            const type    = window.app.mapContext.layers[tag].type;
            const options = window.app.mapContext.layers[tag].options;
            let handle, coords;

            switch (type) {
                case 'marker':
                    handle = [];

                    geoData.forEach((element, index) => {
                        let marker;
                        let lat, lng, elevation, interactive;
                        let icon, color, radius;

                        if (Array.isArray(element)) {
                            ( [ lat, lng, elevation ] = element);
                        } else {
                            ( { lat, lng, elevation } = element)
                        }
                        coords = [lat, lng];
                        elevation = ![null, -9999].includes(elevation) ? elevation : -9999;

                        ( { interactive } = options );
                        if (interactive === null || interactive === undefined) {
                            interactive = true;
                        }

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

                            case 'customPinIcon:Circle':
                                color  = options.iconOptions.color;
                                radius = options.iconOptions.radius;
                                icon   = window.app.modules.Utils.Image.customCircleIcon(color, radius);
                                break;

                            default:
                                icon = new L.Icon.Default({
                                    iconSize: options.iconSize,
                                    tooltipAnchor: [0, 0]
                                });
                        }

                        marker = window.L.marker(coords, { icon, interactive }).addTo(map);
                        if (color) {
                            marker.options.color = color.pin;
                        }

                        /*
                            Caso tooltip esteja habilitado, o marker estará relacionado a três 
                            eventos: mouseover e click (ambos definidos em "Tooltip.js"), além
                            de dblclick, definido aqui.
                        */
                       if (interactive) {
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
                        }
                        
                        handle.push(marker);
                    })
                    break;

                case 'polyline':
                    coords = geoData.filter(el => el.length > 0);
                    handle = window.L.polyline(coords, options).addTo(map);
                    break;

                case 'polygon':
                    coords = geoData;
                    handle = window.L.polygon(coords, options).addTo(map);
                    break;

                default:
                    window.app.modules.Utils.consoleLog(`Unexpected Leaflet object type "${type}"`, 'warn');
                    return;
            }

            window.app.mapContext.layers[tag].handle = handle;
            
            const handles = Array.isArray(handle) ? handle : [handle];
            handles.forEach((h, index) => {
                if (tag === "waypoints") {
                    h._tag = `${index}`;
                } else {
                    h._tag = tag;
                }
            });
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
                        let handle = window.app.mapContext.layers[tag].handle;
                        if (!handle) return;

                        if (!Array.isArray(handle)) {
                            handle = [handle];
                        }

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
        static setView(operationType, ...args) {
            const map = window.app.map;

            switch (operationType) {
                case 'zoom': {
                    const { currentRoute } = window.app.modules.Layout.findSelectedRoute();

                    if (currentRoute) {
                        const lastPosition = window.app.mapContext.settings.geolocation.lastPosition;
                        const geoData = [...currentRoute.waypoints, currentRoute.origin, ...(lastPosition ? [{ lat: lastPosition.coords.latitude, lng: lastPosition.coords.longitude }] : [])];

                        if (!Array.isArray(geoData)) {
                            geoData = [geoData];
                        }

                        let coords = [];
                        geoData.forEach(element => coords.push([element.lat, element.lng]));

                        map.fitBounds(coords);
                        window.app.mapContext.settings.position.current.center = map.getCenter();
                        window.app.mapContext.settings.position.current.zoom   = map.getZoom();
                    } else {
                        const { center, zoom } = window.app.mapContext.settings.position.default;
                        map.setView(center, zoom);
                    }

                    if (window.app.map.getBearing() !== 0) {
                        map.setBearing(0);
                    }
                    break;
                }

                case 'center': {
                    const lastPosition = window.app.mapContext.settings.geolocation.lastPosition;
                    const heading = window.app.mapContext.settings.orientation.lastHeading;

                    if (lastPosition) {
                        const { latitude, longitude, heading } = window.app.mapContext.settings.geolocation.lastPosition.coords;
                        const { zoomLevel } = window.app.mapContext.settings.orientation;
                        map.setView( { lat: latitude, lng: longitude }, zoomLevel);
                    }

                    if (heading !== null) {
                        map.setBearing(heading);
                    }
                    break;
                }
            }
        }
    }

    window.app.modules.Plot = Plot;
})()