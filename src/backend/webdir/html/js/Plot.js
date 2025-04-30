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
        static controller(operationType, ...args) {
            let routeInfo, routeIndex, returnedData;

            switch (operationType) {
                case 'startup':
                    routeInfo  = window.app.analysisContext.routeList[0];                    
            
                    window.app.mapContext.settings.colormap.range = window.app.modules.Util.Elevation.range(routeInfo);
                    //window.app.modules.Util.GeoLocation.routeMidPoint(routeIndex);

                    this.create('boundingBox', window.app.analysisContext.boundingBox);
                    this.create('locationLimits', window.app.analysisContext.location.limits);
                    this.create('locationUrbanAreas', window.app.analysisContext.location.urbanAreas);
                    this.create('locationUrbanCommunities', window.app.analysisContext.location.urbanCommunities);
                    this.create('routePath', routeInfo.paths);
                    this.create('routeMidpoint', routeInfo.midpoint);
                    this.create('routeOrigin', routeInfo.origin);
                    this.create('waypoints', routeInfo.waypoints);
                    this.setView('zoom', routeInfo.waypoints)
                    break;

                case 'update':
                    routeInfo = args[0];

                    this.remove('routeMidpoint');
                    this.remove('routeOrigin');
                    this.remove('waypoints');

                    this.update('routePath', routeInfo.paths);
                    this.create('routeMidpoint', routeInfo.midpoint);
                    this.create('routeOrigin', routeInfo.origin);
                    this.create('waypoints', routeInfo.waypoints);
                    this.setView('zoom', routeInfo.waypoints)
                    break;

                case 'updateCurrentLeg':
                    returnedData = args[0];

                    this.update('currentLeg', returnedData);
                    this.update('currentPosition', returnedData);
                    this.setView('center', returnedData)
                    break;
            }
        }

        /*---------------------------------------------------------------------------------*/
        static create(plotTag, geoData) {
            const map = window.app.map;

            if (!geoData) {
                console.warn(`Unknown data encountered while creating layer: ${plotTag}`);
                return;
            }

            if (!Array.isArray(geoData)) {
                geoData = [geoData];
            }

            let handle, type, options, coords;
            
            type    = window.app.mapContext.layers[plotTag].type;
            options = window.app.mapContext.layers[plotTag].options;

            switch (type) {
                case 'marker':
                    handle = [];

                    geoData.forEach(element => {
                        let marker;
                        let id, lat, lng, elevation;
                        let icon, color;

                        ( { id, lat, lng, elevation } = element);
                        coords = [lat, lng];

                        switch (options.iconType) {
                            case 'file':
                                icon = window.L.icon({
                                    iconUrl: options.iconUrl,
                                    iconSize: options.iconSize,
                                    iconAnchor: options.iconAnchor
                                });
                                
                                marker = window.L.marker(coords, { icon }).addTo(map);
                                break;

                            case 'customPinIcon':
                                color  = window.app.modules.Util.Image.pinColor(elevation, window.app.mapContext.settings.colormap.scale);
                                icon   = window.app.modules.Util.Image.customPinIcon(id, color);
                                marker = window.L.marker(coords, { icon }).addTo(map);
                                break;

                            default:
                                icon = new L.Icon.Default({
                                    iconSize: options.iconSize,
                                    tooltipAnchor: [0, 0]
                                });

                                marker = window.L.marker(coords, { icon }).addTo(map);
                                break;
                        }

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
                    console.warn('Unexpected Leaflet object type');
                    return;
            }

            window.app.mapContext.layers[plotTag].handle = handle;
        }        
        
        /*---------------------------------------------------------------------------------*/
        static update(plotTag, coords) {
            let plotHandle, plotType;
            
            plotHandle = window.app.mapContext.layers[plotTag].handle;
            if (!plotHandle){ 
                this.create(plotTag, coords)
                return;
            }

            plotType = this.checkPlotType(plotHandle);
            switch (plotType) {
                case 'marker':
                    plotHandle.setLatLng(coords);
                    break;

                case 'polyline':
                case 'polygon':
                    plotHandle.setLatLngs(coords);
                    break;

                default:
                    console.warn('Unexpected Leaflet object type');
                    return
            }
        }

        /*---------------------------------------------------------------------------------*/
        static remove(plotTag) {
            let plotHandle;
            
            plotHandle = window.app.mapContext.layers[plotTag].handle;
            if (!plotHandle){ 
                console.warn(`Unexpected Leaflet layer ${plotTag}`);
                return;
            }

            plotHandle.forEach(element => element.remove());
        }
        
        /*---------------------------------------------------------------------------------*/
        static changeVisibility(plotTag) {
            let plotHandle, plotType, isVisible;            
            
            plotHandle = window.app.mapContext.layers[plotTag].handle;
            if (!plotHandle){ 
                console.warn(`Unexpected Leaflet layer ${plotTag}`);
                return;
            }

            plotType = this.checkPlotType(plotHandle);
            switch (plotType) {
                case 'marker':    
                    isVisible = plotHandle._icon.checkVisibility();
                    plotHandle._icon.style.display = isVisible ? 'none' : 'block';
                    break;

                case 'polyline':
                case 'polygon':
                    isVisible = plotHandle._path.checkVisibility();
                    plotHandle._path.style.display = isVisible ? 'none' : 'block';
                    break;

                default:
                    console.warn('Unexpected Leaflet object type');
                    return;
            }
        }

        /*---------------------------------------------------------------------------------*/
        static checkPlotType(plotHandle) {
            if (plotHandle instanceof window.L.Marker) {
                return 'marker';
            } else if (plotHandle instanceof window.L.Polyline) {
                return 'polyline';
            } else if (plotHandle instanceof window.L.Polygon) {
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