/*
    ToDo:
    - Substituir termo em português "porta" por "port" para manter consistência.
      Demanda refatoração do servidor, no parseamento da URL.
    - Se o servidor estiver fora do ar, criar uma linha apontando da posição corrente
      para o próximo waypoint.
*/

(function () {
    class Communication {
        static checkProtocolOrigin() {
            const isValid = ['http:', 'https:'].includes(window.location.protocol);
            return {
                isValid: isValid,
                message: (isValid) ? '' : `Unexpected protocol "${window.location.protocol}".`
            };
        }

        /*---------------------------------------------------------------------------------*/
        static computeRoute(request) {
            const { isValid, message } = this.checkProtocolOrigin();
            if (!isValid) {
                new DialogBox(message, 'error');
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
                    if (window.app.modules.Utils.resolvePushType(returnedData.routing)) {
                        window.app.modules.Utils.syncLocalStorage('update');
                    }
                })
                .catch(ME => {                    
                    new DialogBox(`Error: ${ME.message || "Unknown error"}`);
                });
        }

        /*---------------------------------------------------------------------------------*/
        static isServerOnlineController() {
            window.app.server.statusMonitor.intervalId = setInterval(() => {
                this.isServerOnline();
            }, window.app.server.statusMonitor.intervalMs);
        }

        /*---------------------------------------------------------------------------------*/
        static isServerOnline() {
            const { url, osrmPort, sessionId, status } = window.app.server;
            const serverRoute   = `${url}/health?porta=${osrmPort}`;
            //const serverRoute = `${url}/health?sessionId=${sessionId}`;
            const initialStatus = status;

            return fetch(serverRoute)
                .then(response => {
                    if (!response.ok) {
                        this.handleFailure(initialStatus);
                    }

                    window.app.server.status = 'online';
                    window.app.server.statusMonitor.failureCount = 0;
                    this.checkIfUpdateLayoutNeeded(initialStatus)
                })
                .catch(() => {
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
              window.app.server.statusMonitor.intervalId = null;
              window.app.modules.Utils.consoleLog(`Server unreachable after ${window.app.server.statusMonitor.failureThreshold} retries. Stopping checks.`, 'warn');
            }            
        }

        /*---------------------------------------------------------------------------------*/
        static checkIfUpdateLayoutNeeded(initialStatus) {
            if (initialStatus !== window.app.server.status) {
                window.app.modules.Callbacks.onServerConnectionStatusChanged();
            }
        }

        /*---------------------------------------------------------------------------------*/
        static updateCurrentLeg(currentPosition, nextWaypointPosition) {
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