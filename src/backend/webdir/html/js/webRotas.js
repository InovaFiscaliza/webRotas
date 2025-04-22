/*  
    No contexto global do "window", o webRotas cria três objetos:
    - app: organiza as informações do webRotas no front-end, como o endereço do servidor, 
      a requisição do usuário, os detalhes das rotas, referências  para todos os objetos 
      plotados no mapa Leaflet etc.
    - Função assíncrona appStartup(): inicializa o app, importando todos os arquivos .JS
      necessários para sua execução.
    - Função assíncrona loadScript(filename): permite a importação de arquivos .JS.

    Algumas dessas informações são atualizadas quando o script "js/CustomRoute.js" é 
    executado, o qual é gerado pelo servidor com detalhes sobre a rota requisitada. 
    Outras rotas, eventualmente requisitadas pelo usuário em decorrência de edições no 
    front-end, são armazenadas no "localStorage" dentro do contexto do "window", e recuperadas 
    quando o arquivo .HTML é reiniciado.

    Atualmente, o projeto JavaScript não está organizado como módulos, pois isso exigiria uma 
    conexão com o servidor, o que impede a abertura do arquivo .HTML em ambiente offline. Esse 
    bloqueio ocorre devido à política de CORS (Cross-Origin Resource Sharing).
*/
window.app = {
    /*
        Propriedades relacionadas ao servidor, à requisição do usuário e à rota gerada automaticamente
        pelo servidor. Todos os objetos inicialmente definidos como null serão preenchidos durante a 
        execução do script "js/CustomRoute.js".

        Além disso, as propriedades window.app.server.url e window.app.routeList serão sincronizadas 
        com os valores armazenados no "localStorage", caso existam.
    */
    server: { 
        status: 'offline', 
        url: null, // 'http://127.0.0.1:5000'
        osrmPort: null,
        updateIntervalId: null, 
        updateIntervalMs: 10000,
        failureCount: 0,
        failureThreshold: 3
    },
    
    userRequest: null,
    boundingBox: null,
    location: {
        limits: null,
        urbanAreas: null,
        urbanCommunities: null
    },
    routeList: [],
    
    /*
        Propriedades relacionadas ao plot (eixo geográfico, além de referências para os objetos
        plotados neste eixo).
    */
    map: null,
    plot: {
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
                iconTooltip: true
            }
        },
        routeMidpoint: { // apenas na rota do tipo "DriveTest"
            handle: null,
            type: 'marker',
            options: {
                iconType: 'defaultIcon',
                iconTooltip: true
            }
        },
        routeOrigin: {
            handle: null,
            type: 'marker',
            options: {
                iconType: 'customPinIcon',
                iconTooltip: true
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
                iconTooltip: false,
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

    /*
        Outras propriedades, incluindo referências  para as classes declaradas nos scripts 
        "js/Callback.js", "js/Communication.js", "js/CreateComponents.js", "js/Plot.js" e 
        "js/Util.js", além de controles de estados de elementos do front-end.
    */
    module: {
        Callback: null,
        Communication: null,
        CreateComponent: null,            
        Plot: null,
        Util: null,        
    },

    mapView:     { center: { lat: -10.3, lng: -53.2 }, zoom: 4, basemap: 'street-light', colormap: 'parula' },
    geolocation: { status: false, icon: { on: 'images/gps-on.png', off: 'images/gps-off.png'     }, navWatch: null, lastPosition: null },
    orientation: { status: true,  icon: { on: 'images/north.png',  off: 'images/car-heading.png' }, lastHeading: 0 },
    colorbar:    { status: false, cLim: { min: 0, max: 100 } },
}

async function appStartup() {
    try {
        await loadScript('js/CustomRoute.js');

        const savedConfig = window.localStorage.getItem('webRotas');
        if (savedConfig !== null) {
            const parsedConfig    = JSON.parse(savedConfig);
            window.app.server.url = parsedConfig.serverUrl;
            window.app.routeList  = parsedConfig.routeList;
        } else {
            const configToSave    = JSON.stringify({
                serverUrl: window.app.server.url,
                routeList: window.app.routeList
            })
            window.localStorage.setItem('webRotas', configToSave)
        }

        /* 
            Após a importação de cada um dos módulos, uma referência do módulo será
            armazenada em window.app.module. A referência para as classes definidas em 
            cada módulo não existe em contexto global.
        */
        await loadScript('js/Callback.js');
        await loadScript('js/Communication.js');
        await loadScript('js/CreateComponent.js');
        await loadScript('js/Plot.js');
        await loadScript('js/Util.js');

        window.addEventListener("load", function () {
         // window.app.module.CreateComponent.navbar();
            window.app.module.CreateComponent.leftPanel();
         // window.app.module.CreateComponent.rightPanel();
            window.app.module.CreateComponent.document();
            window.app.module.CreateComponent.toolbar();

            window.app.module.Plot.controller('initialPlot', 0)

            if (window.app.server.url !== null) {
                window.app.server.updateIntervalId = setInterval(() => window.app.module.Communication.isServerOnline(), window.app.server.updateIntervalMs);
            }
        });

        console.log('webRotas');

    } catch (ME) {
        console.error(ME);
    }
}

async function loadScript(filename) {
    return new Promise((resolve, reject) => {
        const script = window.document.createElement('script');
        script.src = filename;
        script.onload = resolve;
        script.onerror = () => reject(new Error(`Failed to load script: ${filename}`));
        window.document.head.appendChild(script);
    });
}

appStartup();