/*
    ## webRotas ##
    No contexto global do "window", o webRotas cria os objetos:
    - L (Leaflet)
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
      │   ├── url             ('http://127.0.0.1:5000')
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
      │           └── estimatedDistance
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
              └── tooltip

    window.app organiza informações geradas pelo servidor, referências para classes 
    declaradas em arquivos auxiliares ("js/Communication.js", "js/Components.js" 
    etc) e estados de elementos do front-end.
    
    window.localStorage é usado para sincronizar informações essenciais do app, como
    a url do servidor, a sessionId e os detalhes das rotas.

    ToDo:
    (01) Editar elemento "menu-context" que suporta o mapa, de forma que ele possa ser
         dragado por meio do ponto de ancoragem.
    (02) Criar possibilidade de abrir o streeview no próprio webRotas, encapsulando-o em
         um iframe, ou abrindo uma nova aba controlável (evitando bloqueio do navegador).
    (03) Implementar "ping" a cada 10s, de forma que o servidor possa registrar as sessões
         ativas no seu controle de sessões.
    (04) Implementar leitura múltipla de arquivos (tanto de "request" quando de "routing").
    (05) Ajustar estrutura de "request.json". Ao invés de "pontosvisita", usar "waypoints",
         ao invés de lista de listas, usar lista de objetos etc.
    (06) Ao adicionar uma routa à routingContext, validar se rota já se encontra por meio
         de análise de cacheId e routeId.
    (07) inserir dataset=index na árvore.
    (08) Criar um fallback para o caso do app não carregar os CSS/JS das bibliotecas Leaflet,
         toKML e JSZip.
    (09) Ajustar colorbar, de forma que as suas dimensões sejam ajustáveis ao tamanho do
         navegador.
    (10) Verificar se é possível passar o ícone customizado do Leaflet para o toKML, de 
         forma que o KML exportado possa ser visualizado no Google Earth.
    (11) Inserir um label no popup (basemaps e exportFile) que contextualize o usuário,
         ao invés de apenas apresentar as opções.
    ...
*/
(function () {
    window.app = {
        name: 'webRotas',

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
            status: 'offline', 
            statusMonitor: {
                intervalId: null, 
                intervalMs: 10000,
                failureCount: 0,
                failureThreshold: 3
            }
        },

        routingContext: [], // list de objetos com campos "request" e "response"

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
                        iconType: 'customPinIcon:Home',
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
                exportFile: {
                    options: (window.location.protocol === "file:") ? ["KML"] : ["KML", "HTML+JS+CSS"],
                    selected: "KML"
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
            await loadScript('js/Plot.js');
            await loadScript('js/Utils.js');

            if (window.location.protocol === "file:") {
                try {
                    await loadScript('data/session.js');
                } catch (ME) {
                    (window.app.modules.Utils) ? window.app.modules.Utils.consoleLog(ME, 'error') : console.error(ME);
                }
            }

            window.addEventListener("load",         (event) => window.app.modules.Callbacks.onWindowLoad(event));
            window.addEventListener("beforeunload", (event) => window.app.modules.Callbacks.onWindowBeforeUnload(event));
            window.addEventListener("storage",      (event) => window.app.modules.Callbacks.onLocalStorageUpdate(event));

        } catch (ME) {
            (window.app.modules.Utils) ? window.app.modules.Utils.consoleLog(ME, 'error') : console.error(ME);
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
})();