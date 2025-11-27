/*
    ## webRotas Model ##
    - *.*
      ├── syncLocalStorage
      ├── openDB
      ├── loadRoutingFromIndexedDB
      ├── updateRoutingInIndexedDB
      ├── loadRouteFromFileOrServer
      ├── loadCustomRouteFromServer
      └── isRequestAlreadyHandled

    ToDo:
    Inserir aqui a exclusão de rotas, a inclusão de rotas, a análise sobre a rota customizada etc.
    Tentar manter arquivos com tamanhos e funcionalidades segregadas.
*/
(function () {
    /*---------------------------------------------------------------------------------*/
    async function syncLocalStorage(type, ...args) {
        if (!window.app.routingDB) {
            window.app.routingDB = await openDB();
        }

        switch (type) {
            case 'startup': {
                /*
                    Fluxo de inicialização:
                    - Tenta recupera informação de localStorage e indexedDB;
                    - Cria sessionId, caso necessário; e
                    - Atualiza url, caso o protocolo de comunicação seja "http" ou "https".
                */
                switch (window.location.protocol) {
                    case 'http:':
                    case 'https:': {
                        window.app.server.url = window.location.origin;
                        break;
                    }

                    case 'file:': {
                        try {
                            await loadScript('data/session.js');
                        } catch (ME) {
                            (window.app.modules.Utils) ? window.app.modules.Utils.consoleLog(ME, 'error') : console.error(ME);
                        }
                        break;
                    }
                }

                const sessionId = window.localStorage.getItem('sessionId');
                window.app.server.sessionId = sessionId ? sessionId : window.app.modules.Utils.uuid();
                
                loadRoutingFromIndexedDB()
                    .then(routingContext => {
                        routingContext = routingContext || [];

                        if (routingContext.length) {
                            const [index1 = 0, index2 = 0] = args;
                            
                            window.app.routingContext = routingContext;
                            window.app.modules.Layout.startup(index1, index2);
                        } else {
                            window.app.modules.Layout.startup();
                        }
                    })
                    .catch(ME => console.error(ME) /*new DialogBox(ME.message, "error")*/);
                break;
            }

            case 'update':                
                updateRoutingInIndexedDB(window.app.routingContext)
                    .then(() => {
                        if (window.app.routingContext.length) {
                            const [index1 = 0, index2 = 0] = args;
                            window.app.modules.Layout.startup(index1, index2);
                        } else {
                            window.app.modules.Layout.startup();
                        }

                        window.localStorage.setItem('appName',   window.app.name);
                        window.localStorage.setItem('sessionId', window.app.server.sessionId);
                        window.localStorage.setItem("timestamp", window.app.modules.Utils.getTimeStamp());
                    })
                    .catch(ME => console.error(ME) /*new DialogBox(ME.message, "error")*/);
                break;
        }
    }

    /*---------------------------------------------------------------------------------*/
    function openDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open("RoutingDB", 1);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains("routing")) {
                    db.createObjectStore("routing");
                }
            };

            request.onsuccess = (event) => resolve(event.target.result);
            request.onerror   = (event) => reject(event.target.error);
        });
    }

    /*---------------------------------------------------------------------------------*/
    async function loadRoutingFromIndexedDB(key = "latest") {
        if (!window.app.routingDB) {
            window.app.routingDB = await openDB();
        }

        return new Promise((resolve, reject) => {
            const tx = window.app.routingDB.transaction("routing", "readonly");
            const store = tx.objectStore("routing");
            const request = store.get(key);

            request.onsuccess = () => resolve(request.result);
            request.onerror   = () => reject(request.error);
        });
    }

    /*---------------------------------------------------------------------------------*/
    async function updateRoutingInIndexedDB(data, key = "latest") {
        if (!window.app.routingDB) {
            window.app.routingDB = await openDB();
        }

        return new Promise((resolve, reject) => {
            const tx = window.app.routingDB.transaction("routing", "readwrite");
            const store = tx.objectStore("routing");
            store.put(data, key);

            tx.oncomplete = () => resolve(true);
            tx.onerror    = () => reject(tx.error);
        });
    }

    /*---------------------------------------------------------------------------------*/
    function loadRouteFromFileOrServer(initialRoute) {
        let isRenderUpdateNeed = Array(initialRoute.length).fill(true);
        const routingContext   = window.app.routingContext;        
        
        if (routingContext.length === 0) {
            routingContext.push(...initialRoute);
        } else {
            for (let ii = 0; ii < initialRoute.length; ii++) {                
                for (let jj = 0; jj < routingContext.length; jj++) {
                    const currentRequest = routingContext[jj].request;
                    const firstRoute     = routingContext[jj].response.routes[0];

                    if (currentRequest.requestId === initialRoute[ii].request.requestId && firstRoute.automatic) {
                        isRenderUpdateNeed[ii] = false;
                        break;
                    }
                }

                if (isRenderUpdateNeed[ii]) {
                    routingContext.push(initialRoute[ii]);
                }
            }
        }

        if (isRenderUpdateNeed.some(Boolean)) {
            window.app.modules.Layout.controller('routeLoaded', 0, 0);
            window.app.modules.Plot.controller('draw', 0, 0);
            return true;
        } else {
            new DialogBox('Route is already in the list');
            return false;
        }
    }

    /*---------------------------------------------------------------------------------*/
    function loadCustomRouteFromServer(customRoute) {
        const routingContext = window.app.routingContext;
        
        for (let ii = 0; ii < routingContext.length; ii++) {
            const routes = routingContext[ii].response.routes;
            
            for (let jj = 0; jj < routes.length; jj++) {
                if (routes[jj].routeId === customRoute.routeId) {
                    Object.assign(routes[jj], customRoute);
                    
                    window.app.modules.Layout.controller('routeLoaded', ii, jj);
                    window.app.modules.Plot.controller('draw', ii, jj);
                    return true;
                }
            }
        }

        return false;
    }

    /*---------------------------------------------------------------------------------*/
    function isRequestAlreadyHandled(newRequestId) {
        let isAlreadyHandled = false;
        let index1, index2;
        const routingContext = window.app.routingContext;
        
        for (let ii = 0; ii < routingContext.length; ii++) {
            const currentRequest = routingContext[ii].request;
            const firstRoute     = routingContext[ii].response.routes[0];

            if (currentRequest.requestId === newRequestId && firstRoute.automatic) {
                isAlreadyHandled = true;
                index1 = ii;
                index2 = 0;
                break;
            }
        }

        return [isAlreadyHandled, index1, index2];
    }

    window.app.modules.Model = {
        syncLocalStorage,
        loadRoutingFromIndexedDB,
        updateRoutingInIndexedDB,
        loadRouteFromFileOrServer,
        loadCustomRouteFromServer,
        isRequestAlreadyHandled
    };
})()