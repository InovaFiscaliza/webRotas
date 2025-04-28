/*-----------------------------------------------------------------------------------
    ## webRotas ##
    No contexto global do "window", o webRotas cria os seguintes objetos:
    - app
    - Funções assíncronas appStartup() e loadScript(filename)
    - Classes DialogBox e Tooltip.
    - L (Leaflet)

    window.app organiza informações geradas pelo servidor ("routeList", por exemplo), 
    referências para classes declaradas em arquivos auxiliares ("js/Communication.js", 
    "js/CreateComponents.js" etc) e estados de elementos do front-end.
    
    window.localStorage é usado para sincronizar informações essenciais do app, como
    a url do servidor e os detalhes das rotas ("routeList").
-----------------------------------------------------------------------------------*/
window.app = {
    modules: {
        Callback: null,
        Communication: null,
        CreateComponent: null,            
        Plot: null,
        Tooltip: new Tooltip,
        Util: null
    },

    server: { 
        url: null, // 'http://127.0.0.1:5000'
        osrmPort: null, // eliminar campo após implementar sessionId
        sessionId: '',
        status: 'offline', 
        statusMonitor: {
            intervalId: null, 
            intervalMs: 10000,
            failureCount: 0,
            failureThreshold: 3
        }
    },

    analysisContext: {
        userRequest: null,
        boundingBox: null,
        location: {
            limits: null,
            urbanAreas: null,
            urbanCommunities: null
        },
        routeList: []
    },

    map: null, // window.L.map
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
                        textResolver: ({ lat, lng, elevation, description }) => { return `${description}<br>(${lat.toFixed(6)}º, ${lng.toFixed(6)}º, ${elevation}m)` },
                        offsetResolver: 'default'
                    }
                }
            },
            routeMidpoint: {
                handle: null,
                type: 'marker',
                options: {
                    iconType: 'defaultIcon',
                    iconTooltip: {
                        status: true,
                        textResolver: ({ lat, lng }) => { return `Ponto central<br>(${lat.toFixed(6)}º, ${lng.toFixed(6)}º)` },
                        offsetResolver: () => { return [0, 0] }
                    },
                    iconSize: [25, 41]
                }
            },
            routeOrigin: {
                handle: null,
                type: 'marker',
                options: {
                    iconType: 'customPinIcon',
                    iconTooltip: {
                        status: true,
                        textResolver: ({ lat, lng, elevation, description }) => { return `Ponto inicial: ${description}<br>(${lat.toFixed(6)}º, ${lng.toFixed(6)}º, ${elevation}m)` },
                        offsetResolver: 'default'
                    }
                }
            },
            routePath: {
                handle: null,
                type: 'polyline',
                options: {
                    weight: 3,
                    color: 'rgba(0,0,255,0.75)',
                    interactive: false
                }
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
            tooltip: {
                direction: 'bottom',
                textResolver: ({ lat, lng }) => {
                    return `Latitude: ${lat.toFixed(6)}º<br>Longitude: ${lng.toFixed(6)}º`
                },
                offsetResolver: (direction) => { 
                    return (direction === "top") ? [0, -41] : [0, 0] 
                }
            }
        }
    }
}

/*---------------------------------------------------------------------------------*/
async function appStartup() {
    try {
        await loadScript('js/CustomRoute.js');

        const savedConfig = window.localStorage.getItem('webRotas');
        if (savedConfig) {
            const parsedConfig = JSON.parse(savedConfig);
            window.app.server.url = parsedConfig.serverUrl;
            window.app.analysisContext.routeList = parsedConfig.routeList;
        } else {
            const configToSave = JSON.stringify({
                serverUrl: window.app.server.url,
                routeList: window.app.analysisContext.routeList
            })
            window.localStorage.setItem('webRotas', configToSave)
        }

        /* 
            Após a importação de cada um dos módulos, uma referência do módulo será
            armazenada em window.app.modules.
        */
        await loadScript('js/Callback.js');
        await loadScript('js/Communication.js');
        await loadScript('js/CreateComponent.js');
        //await loadScript('js/Layout.js');
        await loadScript('js/Plot.js');
        await loadScript('js/Util.js');

        window.addEventListener("load", function () {
            console.log(`webRotas session started at ${window.app.modules.Util.getTimeStamp()}`);

            window.app.modules.CreateComponent.leftPanel();
            window.app.modules.CreateComponent.document();
            window.app.modules.CreateComponent.toolbar();

            //window.app.modules.Layout.controller('startup');
            window.app.modules.Plot.controller('startup')

            if (!!window.app.server.url) {
                window.app.server.statusMonitor.intervalId = setInterval(() => {
                    window.app.modules.Communication.isServerOnline();
                }, window.app.server.statusMonitor.intervalMs);
            }
        });

    } catch (ME) {
        console.error(ME);
    }
}

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
appStartup();