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
                case 'initialPlot':
                    routeIndex = args[0];
                    routeInfo  = window.app.routeList[routeIndex];

                    this.create('boundingBox', window.app.boundingBox);
                    this.create('locationLimits', window.app.location.limits);
                    this.create('locationUrbanAreas', window.app.location.urbanAreas);
                    this.create('locationUrbanCommunities', window.app.location.urbanCommunities);
                    this.create('routePath',     routeInfo.routePath);
                    this.create('routeMidpoint', routeInfo.routeMidPoint);
                    this.create('routeOrigin',   routeInfo.routeOrigin);
                    this.create('waypoints',     routeInfo.waypoints);
                    this.setView('zoom',         routeInfo.waypoints)
                    break;

                case 'customRoutePlot':
                    routeIndex = args[0];
                    routeInfo  = window.app.routeList[routeIndex];

                    this.remove('routeMidpoint');
                    this.remove('routeOrigin');
                    this.remove('waypoints');

                    this.update('routePath',     routeInfo.routePath);
                    this.create('routeMidpoint', routeInfo.routeMidPoint);
                    this.create('routeOrigin',   routeInfo.routeOrigin);
                    this.create('waypoints',     routeInfo.waypoints);
                    this.setView('zoom',         routeInfo.waypoints)
                    break;

                case 'updateCurrentLeg':
                    returnedData = args[0];

                    this.update('currentLeg',      returnedData);
                    this.update('currentPosition', returnedData);
                    this.setView('center',         returnedData)
                    break;
            }
        }


        /*---------------------------------------------------------------------------------*/
        static create(plotTag, geoData) {
            if (!geoData) {
                console.warn(`Unknown data encountered while creating layer: ${plotTag}`);
                return;
            }

            if (!Array.isArray(geoData)) {
                geoData = [geoData];
            }

            let plotHandle, plotType, plotOptions, coords;
            
            plotType    = window.app.plot[plotTag].type;
            plotOptions = window.app.plot[plotTag].options;

            switch (plotType) {
                case 'marker':
                    plotHandle = [];

                    geoData.forEach((element, index) => {
                        let id, description, lat, lng, elevation;
                        let icon, iconColor, iconTooltip;                        

                        ( { id, description, lat, lng, elevation } = element);
                        coords = [lat, lng];

                        switch (plotOptions.iconType) {
                            case 'file':
                                icon = window.L.icon({
                                    iconUrl: plotOptions.iconUrl,
                                    iconSize: plotOptions.iconSize,
                                    iconAnchor: plotOptions.iconAnchor
                                });
                                
                                plotHandle.push(window.L.marker(coords, { icon: icon }).addTo(window.app.map));
                                break;

                            case 'customPinIcon':
                                iconColor = window.app.module.Util.Image.pinColor(elevation, window.app.mapView.colormap);
                                icon = window.app.module.Util.Image.customPinIcon(id, iconColor);
                                plotHandle.push(window.L.marker(coords, { icon: icon }).addTo(window.app.map));
                                break;

                            default:
                                plotHandle.push(window.L.marker(coords).addTo(window.app.map));
                                break;
                        }

                        if (plotOptions.iconTooltip) {
                            try {
                                iconTooltip = `${description}<br>(${lat.toFixed(6)}º, ${lng.toFixed(6)}º, ${elevation}m)`;
                                window.app.module.Util.Tooltip.add(plotHandle[index]._icon, iconTooltip);                                
                            } catch (ME) {
                                console.error(ME);
                            }
                        }    
                    })
                    break;

                case 'polyline':
                    coords = geoData;
                    plotHandle = window.L.polyline(coords, plotOptions).addTo(window.app.map);
                    break;

                case 'polygon':
                    coords = geoData;
                    plotHandle = window.L.polygon(coords,  plotOptions).addTo(window.app.map);
                    break;

                default:
                    console.warn('Unexpected Leaflet object type');
                    return;
            }

            window.app.plot[plotTag].handle = plotHandle;
        }
        
        
        /*---------------------------------------------------------------------------------*/
        static update(plotTag, coords) {
            let plotHandle, plotType;
            
            plotHandle = window.app.plot[plotTag].handle;
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
            
            plotHandle = window.app.plot[plotTag].handle;
            if (!plotHandle){ 
                console.warn(`Unexpected Leaflet layer ${plotTag}`);
                return;
            }

            plotHandle.forEach(element => element.remove());
        }


        /*---------------------------------------------------------------------------------*/
        static setView(operationType, geoData) {
            switch (operationType) {
                case 'zoom':
                    if (!Array.isArray(geoData)) {
                        geoData = [geoData];
                    }

                    let coords = [];
                    geoData.forEach(element => coords.push([element.lat, element.lng]));

                    window.app.map.fitBounds(coords);
                    window.app.mapView.center = window.app.map.getCenter();
                    window.app.mapView.zoom   = window.app.map.getZoom();
                    break;

                case 'center':
                    window.app.map.setView(geoData);
                    break;
            }
        }

        
        /*---------------------------------------------------------------------------------*/
        static changeVisibility(plotTag) {
            let plotHandle, plotType, isVisible;            
            
            plotHandle = window.app.plot[plotTag].handle;
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
    }

    window.app.module.Plot = Plot;
})()