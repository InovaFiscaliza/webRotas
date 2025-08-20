/*
    ## webRotas ##
    O projeto é escrito em JavaScript, sem frameworks, mas faz uso das bibliotecas 
    Leaflet, JSZip e toKML. No contexto global do "window", o webRotas cria os objetos:
    - L
    - JSZip
    - tokml
    - DialogBox
    - Tooltip
    - app
      ├── name                ('webRotas')
      ├── modules
      │   ├── Callbacks       ('js/Callbacks.js')
      │   ├── Communication   ('js/Communication.js')
      │   ├── Components      ('js/Components.js')
      │   ├── Layout          ('js/Layout.js')
      │   ├── Plot            ('js/Plot.js')
      │   ├── Tooltip         (new Tooltip)
      │   └── Utils           ('js/Utils.js')
      ├── server
      │   ├── url             ('http://127.0.0.1:5001')
      │   ├── sessionId
      │   ├── status
      │   └── statusMonitor
      │       ├── intervalId
      │       ├── intervalMs
      │       ├── failureCount
      │       └── failureThreshold
      ├── routingContext[]
      │   ├── request         (conteúdo do arquivo ".json")
      │   └── response
      │       ├── cacheId     (hash boundingBox+avoidZones)
      │       ├── boundingBox
      │       ├── location
      │       │   ├── limits
      │       │   ├── urbanAreas
      │       │   └── urbanCommunities
      │       └── routes[]
      │           ├── routeId (hash origin+waypoints)
      │           ├── automatic
      |           ├── created
      │           ├── origin
      │           ├── waypoints[]
      │           ├── paths
      │           ├── estimatedDistance
      │           └── estimatedTime
      ├── map                 (L.map)
      └── mapContext
          ├── layers
          │   ├── basemap
          │   ├── boundingBox
          │   ├── avoidZones
          │   ├── locationLimits
          │   ├── locationUrbanAreas
          │   ├── locationUrbanCommunities
          │   ├── waypoints[]
          │   ├── routeMidpoint
          │   ├── routeOrigin
          │   ├── routePath
          │   ├── currentPosition
          │   └── currentLeg
          └── settings
              ├── basemap
              ├── colorbar
              ├── colormap
              ├── geolocation
              ├── orientation
              ├── position
              ├── streetview
              ├── tooltip
              └── exportFile

    window.app organiza informações geradas pelo servidor, referências para classes 
    declaradas em arquivos auxiliares ("js/Communication.js", "js/Components.js" 
    etc) e estados de elementos do front-end.
    
    window.localStorage é usado para sincronizar informações essenciais do app, como
    a url do servidor, a sessionId e os detalhes das rotas.
*/

/*---------------------------------------------------------------------------------*/
async function loadScript(filename) {
    return new Promise((resolve, reject) => {
        const script = window.document.createElement('script');
        script.src = filename;
        script.onload = resolve;
        script.onerror = () => reject(new Error(`Failed to load script: ${filename}`));

        window.document.head.appendChild(script);
    });
}

/*---------------------------------------------------------------------------------*/
(function () {
    window.app = {
        name: 'webRotas',
        version: '0.90.0',
        released: 'R2025b (01/09/2025)',
        sharepoint: 'https://anatel365.sharepoint.com/sites/InovaFiscaliza/SitePages/webRotas.aspx',

        modules: {
            Callbacks: null,
            Communication: null,
            Components: null,
            Layout: null,
            Plot: null,
            Tooltip: new Tooltip,
            Utils: null
        },

        server: { 
            url: null,
            sessionId: '',
            status: (window.location.protocol === "file:") ? 'offline' : 'online',
            statusMonitor: {
                intervalId: null, 
                intervalMs: 10000,
                failureCount: 0,
                failureThreshold: 3
            }
        },

        routingDB: null,
        routingContext: [],

        map: null,

        mapContext: {        
            layers: {
                basemap: {
                    "street-light": window.L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
                        maxZoom: 19,
                        attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
                        subdomains: 'abcd'
                    }),
                    "street-dark": window.L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                        maxZoom: 19,
                        attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
                        subdomains: 'abcd'
                    }),
                    "open-street": window.L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        maxZoom: 19,
                        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    }),
                    "satellite": window.L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                        maxZoom: 19,
                        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
                    })
                },
                boundingBox: {
                    handle: null,
                    type: 'polygon',
                    options: {
                        weight: 1,
                        color: 'rgba(0,255,0,0.5)',
                        fillColor: 'rgba(0,255,0,0)',
                        interactive: false
                    }
                },
                avoidZones: {
                    handle: null,
                    type: 'polygon',
                    options: {
                        weight: 1,
                        color: 'rgba(255,0,0,0.5)',
                        fillColor: 'rgba(255,0,0,0.25)',
                        interactive: false
                    }
                },
                locationLimits: {
                    handle: null,
                    type: 'polygon',
                    options: {
                        weight: 1,
                        color: 'rgba(255,0,0,0.5)',
                        fillColor: 'rgba(255,0,0,0)',
                        interactive: false
                    }
                },
                locationUrbanAreas: {
                    handle: null,
                    type: 'polygon',
                    options: {
                        weight: 1,
                        color: 'rgba(0,0,255,0.5)',
                        fillColor: 'rgba(0,0,255,0)',
                        interactive: false
                    }
                },
                locationUrbanCommunities: {
                    handle: null,
                    type: 'polygon',
                    options: {
                        weight: 1,
                        color: 'rgba(102,0,204,0.85)',
                        fillColor: 'rgba(102,0,204, 0.5)',
                        interactive: false
                    }
                },
                waypoints: {
                    handle: null,
                    type: 'marker',
                    options: {
                        iconType: 'customPinIcon',
                        iconTooltip: {
                            status: true,
                            textResolver: ({ lat, lng, elevation, description }) => {
                                const descriptionText = description.length ? `${description}<br>` : '';
                                const elevationText   = ![null, -9999].includes(elevation) ? `, ${elevation.toFixed(1)}m` : '';

                                return `${descriptionText}(${lat.toFixed(6)}º, ${lng.toFixed(6)}º${elevationText})`
                            },
                            offsetResolver: 'default'
                        }
                    }
                },
                routeMidpoint: {
                    handle: null,
                    type: 'marker',
                    options: {
                        iconType: 'customPinIcon:Circle',
                        iconTooltip: {
                            status: true,
                            textResolver: ({ lat, lng }) => { 
                                return `Ponto central<br>(${lat.toFixed(6)}º, ${lng.toFixed(6)}º)` 
                            },
                            offsetResolver: () => { return [0, 0] }
                        },
                        iconSize: [25, 41],
                        iconOptions: {
                            color: 'rgb(51, 51, 51)',
                            radius: 10
                        }
                    }
                },
                routeOrigin: {
                    handle: null,
                    type: 'marker',
                    options: {
                        iconType: 'customPinIcon:Home',
                        iconTooltip: {
                            status: true,
                            textResolver: ({ lat, lng, elevation, description }) => { 
                                const descriptionText = description.length ? `: ${description}` : '';
                                const elevationText   = ![null, -9999].includes(elevation) ? `, ${elevation.toFixed(1)}m` : '';

                                return `Ponto inicial${descriptionText}<br>(${lat.toFixed(6)}º, ${lng.toFixed(6)}º${elevationText})`
                            },
                            offsetResolver: 'default'
                        }
                    }
                },
                routePath: {
                    handle: null,
                    type: 'polyline',
                    options: {
                        weight: 3,
                        color: 'rgb(180, 180, 180)',
                        interactive: false
                    }
                },
                toolbarPositionSlider: {
                    handle: null,
                    type: 'polyline',
                    options: {
                        weight: 2,
                        color: 'rgb(76, 175, 80)',
                        interactive: false
                    },
                    mergedPaths: []
                },
                currentPosition: {
                    handle: null,
                    type: 'marker',
                    options: {
                        iconType: 'file',
                        iconTooltip: {
                            status: false,
                            offsetResolver: 'default'
                        },
                        iconUrl: 'images/car.png',
                        iconSize: [48, 48],
                        iconAnchor: [12, 12]
                    }
                },
                currentLeg: {
                    handle: null,
                    type: 'polyline',
                    options: {
                        weight: 3,
                        color: 'rgba(255,0,0,0.5)',
                        interactive: false
                    }
                }
            },
            settings: { 
                basemap: 'street-light', // 'street-light' | 'street-dark' | 'open-street' | 'satellite'
                colorbar: 'hidden', // 'hidden' | 'visible'
                colormap: {
                    scale: 'parula', // 'parula'
                    range: {
                        min: 0, 
                        max: 100
                    }
                },
                geolocation: { 
                    status: 'off', // 'on' | 'off'
                    icon: { on: 'images/gps-on.png', off: 'images/gps-off.png' }, 
                    navWatch: null, 
                    lastPosition: null 
                },
                orientation: { 
                    status: 'north', // 'north' | 'car-heading'  
                    icon: { on: 'images/north.png',  off: 'images/car-heading.png' }, 
                    lastHeading: 0 
                },
                position: {
                    center: { 
                        lat: -10.3, 
                        lng: -53.2 
                    },
                    zoom: 4
                },
                streetview: {
                    handle: null,
                    url: (lat, lng) => {
                        return `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lng}&zoom=0`;
                    }
                },
                tooltip: {
                    direction: 'bottom',
                    textResolver: ({ lat, lng }) => {
                        return `Latitude: ${lat.toFixed(6)}º<br>Longitude: ${lng.toFixed(6)}º`
                    },
                    offsetResolver: (direction) => { 
                        return (direction === "top") ? [0, -41] : [0, 0] 
                    }
                },
                importFile: {
                    format: '.json',
                    expectedKeys: {
                        request: ["type", "origin", "parameters" ],
                        routing: ["routing"]
                    }
                },
                exportFile: {
                    options: (window.location.protocol === "file:") ? ["JSON", "KML"] : ["JSON", "KML", "HTML+JS+CSS"],
                    selected: "JSON",
                    parameters: {
                        kml: {
                            ignoredLayers: [
                                "basemap",
                                "toolbarPositionSlider",
                                "currentPosition",
                                "currentLeg"
                            ]
                        }
                    }
                },
                criterion: {
                    options: ["distance", "duration", "ordered"],
                    selected: "distance"
                }
            }
        }
    }

    /*---------------------------------------------------------------------------------*/
    async function appStartup() {
        /*
            Inicialmente, carregam-se os scripts auxiliares (Callbacks, Communication, 
            Components, Layout, Plot e Utils). Além disso, caso o protocolo seja "file:", 
            carrega-se o script da sessão (session.js).
        */
        try {
            await loadScript('js/Callbacks.js');
            await loadScript('js/Communication.js');
            await loadScript('js/Components.js');
            await loadScript('js/Layout.js');
            await loadScript('js/Model.js');
            await loadScript('js/Plot.js');
            await loadScript('js/Utils.js');

            window.addEventListener("load",         (event) => window.app.modules.Callbacks.onWindowLoad(event));
            window.addEventListener("beforeunload", (event) => window.app.modules.Callbacks.onWindowBeforeUnload(event));
            window.addEventListener("storage",      (event) => window.app.modules.Callbacks.onLocalStorageUpdate(event));
            window.addEventListener("message",      (event) => window.app.modules.Callbacks.onWindowMessage(event));

        } catch (ME) {
            (window.app.modules.Utils) ? window.app.modules.Utils.consoleLog(ME, 'error') : console.error(ME);
        }
    }

    /*---------------------------------------------------------------------------------*/
    appStartup();
})();