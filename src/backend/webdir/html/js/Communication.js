/*
    ToDo:
    - Substituir termo em português "porta" por "port" para manter consistência.
      Demanda refatoração do servidor, no parseamento da URL.
    - Se o servidor estiver fora do ar, criar uma linha apontando da posição corrente
      para o próximo waypoint.
*/

(function () {
    class Communication {
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
              console.warn(`Server unreachable after ${window.app.server.statusMonitor.failureThreshold} retries. Stopping checks.`);
            }            
        }


        /*---------------------------------------------------------------------------------*/
        static checkIfUpdateLayoutNeeded(initialStatus) {
            if (initialStatus !== window.app.server.status) {
                window.app.modules.Callback.updateLayout('server-status-changed');
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
                    console.error(ME);
                });
        }
    }

    window.app.modules.Communication = Communication;
})()