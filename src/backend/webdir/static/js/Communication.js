/*
    ## webRotas Communication ##
    - COMMUNICATION
      ├── computeRoute
      ├── isServerOnlineController
      ├── isServerOnline
      ├── handleFailure
      ├── checkIfUpdateLayoutNeeded
      ├── updateMissingInfo                   (!! ToDo: PENDENTE !!)
      └── updateCurrentLeg                    (!! ToDo: PENDENTE !!)
*/

(function () {
    class Communication {
        /*---------------------------------------------------------------------------------*/
        static computeRoute(request) {
            if (window.app.server.status === "offline") {
                const dialogBoxText = `O <i>status</i> atual do servidor é <i>offline</i>.`
                new DialogBox(dialogBoxText, 'info');
                return;
            }

            const { url, sessionId } = window.app.server;
            const serverRoute = `${url}/process?sessionId=${sessionId}`;

            return fetch(serverRoute, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(request) 
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`${response.status}`);
                }

                return response.json();
            })
            .then(returnedData => {
                switch (returnedData.type) {
                    case "initialRoute": {
                        if (window.app.modules.Model.loadRouteFromFileOrServer(returnedData.routing)) {
                            const index1 = window.app.routingContext.length-1;
                            const index2 = 0;

                            window.app.modules.Model.syncLocalStorage('update', index1, index2);
                        }
                        break;
                    }
                    case "customRoute": {
                        if (window.app.modules.Model.loadCustomRouteFromServer(returnedData.route)) {
                            const { index1, index2 } = window.app.modules.Layout.findSelectedRoute();
                            window.app.modules.Model.syncLocalStorage('update', index1, index2);
                        }
                        break;
                    }
                    default:
                        throw new Error(`Unexpected request type: ${returnedData.type}`);
                }
            })
            .catch(ME => {      
                new DialogBox(`Error: ${ME.message || "Unknown error"}`);
                this.handleFailure("online");                    
            });
        }

        /*---------------------------------------------------------------------------------*/
        static isServerOnlineController() {
            if (window.location.protocol === "file:") {
                return;
            }

            window.app.server.statusMonitor.intervalId = setInterval(() => {
                this.isServerOnline();
            }, window.app.server.statusMonitor.intervalMs);
        }

        /*---------------------------------------------------------------------------------*/
        static isServerOnline() {
            const { url, sessionId, status } = window.app.server;
            const serverRoute = `${url}/ok?sessionId=${sessionId}`;
            const initialStatus = status;

            return fetch(serverRoute, {
                method: 'GET'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`${response.status}`);
                }

                // console.log(response.statusText);
                window.app.server.status !== 'online' && (window.app.server.status = 'online');
                window.app.server.failureCount > 0    && (window.app.server.statusMonitor.failureCount = 0);
                this.checkIfUpdateLayoutNeeded(initialStatus)
            })
            .catch(ME => {
                this.handleFailure(initialStatus);
            });
        }

        /*---------------------------------------------------------------------------------*/
        static handleFailure(initialStatus) {
            window.app.server.status = 'offline';
            window.app.server.statusMonitor.failureCount++;
            this.checkIfUpdateLayoutNeeded(initialStatus)
        
            if (window.app.server.statusMonitor.failureCount >= window.app.server.statusMonitor.failureThreshold) {
                clearInterval(window.app.server.statusMonitor.intervalId);
                window.app.modules.Utils.consoleLog(`Server unreachable after ${window.app.server.statusMonitor.failureThreshold} retries. Stopping checks.`, 'warn');

                window.app.server.statusMonitor.intervalId   = null;
                window.app.server.statusMonitor.failureCount = 0;
            }            
        }

        /*---------------------------------------------------------------------------------*/
        static checkIfUpdateLayoutNeeded(initialStatus) {
            if (initialStatus !== window.app.server.status) {
                window.app.modules.Callbacks.onServerConnectionStatusChanged();
            }
        }

        /*---------------------------------------------------------------------------------*/
        static updateMissingInfo() {
            // PENDENTE
            if (window.app.server.status === 'offline') {
                return;
            }

            // ...            
        }

        /*---------------------------------------------------------------------------------*/
        static updateCurrentLeg(currentPosition, nextWaypointPosition) {
            // PENDENTE
            if (window.app.server.status === 'offline') {
                return;
            }

            const { url, osrmPort, sessionId } = window.app.server;
            const serverRoute = `${url}/route?porta${osrmPort}`      +
                `&start=${currentPosition[1]},${currentPosition[0]}` + 
                `&end=${nextWaypointPosition[1]},${nextWaypointPosition[0]}`;

            return fetch(serverRoute)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`${response.status}`);
                    }

                    return response.json();
                })
                .then(returnedData => {
                    window.app.modules.Plot.controller('updateCurrentLeg', returnedData);
                })
                .catch(ME => {
                    window.app.modules.Utils.consoleLog(ME, 'error');
                });
        }
    }

    window.app.modules.Communication = Communication;
})()