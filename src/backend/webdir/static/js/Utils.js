/*
    ## webRotas Utils ##      
    - *.*
      ├── syncLocalStorage
      ├── consoleLog
      ├── uuid
      ├── hash
      ├── getTimeStamp
      ├── saveToFile
      ├── GeoLocation (class)
      │   ├── startLocationTracking
      │   ├── stopLocationTracking
      │   ├── stopLocationTracking
      │   └── routeMidPoint
      └── Image (class)
          ├── parulaColormap
          ├── customPinIcon
          ├── colorbar
          └── pinColor
*/
(function () {
    /*---------------------------------------------------------------------------------*/
    function syncLocalStorage(type) {
        switch (type) {
            case 'startup':
                /*
                    Fluxo de inicialização:
                    - Tenta recupera informação de localStorage (url, sessionId e rotas);
                    - Cria sessionId, caso necessário; e
                    - Atualiza url, caso o protocolo de comunicação seja "http" ou "https".
                */
                if (window.localStorage.getItem('appName')) {                    
                    window.app.server.url       = window.localStorage.getItem('url');
                    window.app.server.sessionId = window.localStorage.getItem('sessionId');
                    window.app.routingContext   = JSON.parse(window.localStorage.getItem('routing'));
                }

                if (!window.app.server.sessionId) {
                    window.app.server.sessionId = uuid();
                }

                if (['http:', 'https:'].includes(window.location.protocol)) {
                    window.app.server.url = window.location.origin;
                }
                break;

            case 'update':
                window.localStorage.setItem('appName',   window.app.name);
                window.localStorage.setItem('url',       window.app.server.url);
                window.localStorage.setItem('sessionId', window.app.server.sessionId);
                window.localStorage.setItem('routing',   JSON.stringify(window.app.routingContext));
                break;
        }
    }

    /*---------------------------------------------------------------------------------*/
    function consoleLog(msg, type = 'log') {
        const msgToPrint = `${getTimeStamp('HH:MM:SS.mmm')} [${window.app.name}] ${msg}`;

        switch (type) {
            case 'error':
                console.error(msgToPrint);
                break;
            case 'warn':
                console.warn(msgToPrint);
                break;
            default:
                console.log(msgToPrint);
                break;
        }
    }

    /*---------------------------------------------------------------------------------*/
    function uuid() {
        return (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') 
            ? crypto.randomUUID()
            : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
                const r = Math.random() * 16 | 0;
                const v = c === 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
    }

    /*---------------------------------------------------------------------------------*/
    async function hash(src) {
        const srcBytes   = new TextEncoder().encode(JSON.stringify(src));
        const hashBuffer = await crypto.subtle.digest('SHA-256', srcBytes);
        const hashArray  = Array.from(new Uint8Array(hashBuffer));
        const hashHex    = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

        return hashHex;
    }

    /*---------------------------------------------------------------------------------*/
    const getTimeStamp = (format = 'dd/mm/yyyy HH:MM:SS') => {
        const pad   = (value, numChars=2) => String(value).padStart(numChars, '0');
        const now   = new Date();
    
        const year  = now.getFullYear();
        const month = pad(now.getMonth() + 1);
        const day   = pad(now.getDate());
        const hour  = pad(now.getHours());
        const min   = pad(now.getMinutes());
        const sec   = pad(now.getSeconds());
        const msec  = pad(now.getMilliseconds(), 3);
    
        switch (format) {
            case 'dd/mm/yyyy HH:MM:SS':
                return `${day}/${month}/${year} ${hour}:${min}:${sec}`;
            case 'yyyy.mm.dd_THH.MM.SS':
                return `${year}.${month}.${day}_T${hour}.${min}.${sec}`;
            case 'HH:MM:SS.mmm':
                return `${hour}:${min}:${sec}.${msec}`;
            default:
                throw new Error('Unexpected date format');
        }
    }

    /*---------------------------------------------------------------------------------*/
    async function exportAsZip() {
        const zip = new window.JSZip();

        // HTML
        const html = window.top.document.documentElement.outerHTML;
        zip.file("index.html", html);

        // Arquivos auxiliares: CSS, JS e imagens
        const assets = [
            "css/DialogBox.css",
            "css/Tooltip.css",
            "css/webRotas.css",
            "images/ArrowLeft_32.png",
            "images/ArrowRight_32.png",
            "images/Edit_32.png",
            "images/Trash_32.png",
            "images/addFiles_32.png",
            "images/colorbar.svg",
            "images/error.svg",
            "images/export.png",
            "images/gps-off.png",
            "images/gps-on.png",
            "images/import.png",
            "images/info.svg",
            "images/layers.png",
            "images/north.png",
            "images/pin_18.png",
            "images/route.svg",
            "images/warning.svg",
            "js/webRotas.js",
            "js/Callbacks.js",
            "js/Communication.js",
            "js/Components.js",
            "js/DialogBox.js",
            "js/Layout.js",
            "js/Plot.js",
            "js/Tooltip.js",
            "js/Utils.js"
        ];

        for (const path of assets) {
            try {
                const response = await fetch(path);
                const blob = await response.blob();
                zip.file(path, blob);
            } catch (ME) {
                this.consoleLog(`Failed to fetch ${path}: ${ME.message}`, 'error');
            }
        }

        const content = await zip.generateAsync({ type: "blob" });
        
        const link = window.document.createElement("a");
        link.href = URL.createObjectURL(content);
        link.download = "webRotas.zip";
        link.target = "_blank";

        window.document.body.appendChild(link);
        link.click();
        window.document.body.removeChild(link);

        setTimeout(() => URL.revokeObjectURL(link.href), 1000);
    }

    /*---------------------------------------------------------------------------------*/
    const saveToFile = (fileType, filename, data, ...args) => {
        const link = window.document.createElement('a');
        link.download = filename;

        let revokeNeeded = false;
    
        switch (fileType) {
            case 'image': {
                let { format, quality, width, height } = args[0] || { format: 'image/png', quality: 1, width: 1024, height: 768 };

                const scale = Math.min(width / data.width, height / data.height);
                width  = data.width * scale;
                height = data.height * scale;

                const canvas  = window.document.createElement('canvas');
                canvas.width  = width;
                canvas.height = height;
                
                const context = canvas.getContext('2d');
                context.drawImage(data, 0, 0, width, height);

                link.href = canvas.toDataURL(format, quality);
                break;
            }
            case 'kml': {
                const blob = new Blob([data], { type: 'application/vnd.google-earth.kml+xml' });
                link.href = URL.createObjectURL(blob);
                revokeNeeded = true;
                break;
            }
            case 'json': {
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                link.href = URL.createObjectURL(blob);
                revokeNeeded = true;
                break;
            }
            case 'binary': {
                const blob = new Blob([data], { type: 'application/octet-stream' });
                link.href = URL.createObjectURL(blob);
                revokeNeeded = true;
                break;
            }
            default:
                throw new Error(`Unexpected filetype: ${fileType}`);
        }
    
        window.document.body.appendChild(link);
        link.click();
        window.document.body.removeChild(link);
    
        if (revokeNeeded) {
            setTimeout(() => URL.revokeObjectURL(link.href), 1000);
        }
    }

    /*---------------------------------------------------------------------------------*/
    function resolvePushType(returnedData) {
        const routing = window.app.routingContext;
        const pushContext = {
            routing: Array(returnedData.length).fill(true),
            routes:  Array(returnedData.length).fill(false)
        };

        if (routing.length !== 0) {
            for (let ii = 0; ii < returnedData.length; ii++) {
                for (let jj = 0; jj < routing.length; jj++) {
                    if (returnedData[ii].response.cacheId === routing[jj].response.cacheId) {
                        pushContext.routing[ii] = false;

                        if (JSON.stringify(returnedData[ii].response.routes) !== JSON.stringify(routing[jj].response.routes)) {
                            pushContext.routes[ii] = true;
                        }
                        break;
                    }
                }
            }
        }

        let renderUpdate = false;
        for (let kk = 0; kk < returnedData.length; kk++) {
            if (pushContext.routing[kk]) {
                routing.push(returnedData[kk]);

                if (!renderUpdate) {
                    renderUpdate = true;
                    
                    const lastIndex = routing.length-1;
                    window.app.modules.Layout.controller('routeLoaded', lastIndex, 0);
                    window.app.modules.Plot.controller('draw', lastIndex, 0);
                }

            } else if (pushContext.routes[kk]) {
                routing[kk].response.routes.push(...returnedData[kk].response.routes);

                if (!renderUpdate) {
                    renderUpdate = true;

                    const lastIndex = routing[kk].response.routes.length-1;
                    window.app.modules.Layout.controller('routeLoaded', kk, lastIndex);
                    window.app.modules.Plot.controller('draw', kk, lastIndex);
                }
            }
        }

        const hasTrueInRouting = pushContext.routing.some(Boolean);
        const hasTrueInRoutes  = pushContext.routes.some(Boolean);

        if (hasTrueInRouting || hasTrueInRoutes) {
            return true;
        } else {
            new DialogBox('Route is already in the list');
            return false;
        }
    }

    class GeoLocation {
        /*---------------------------------------------------------------------------------*/
        static startLocationTracking(updateFcn) {
            if (!window.app.mapContext.geolocation.status || window.app.mapContext.geolocation.navWatch !== null) {
                return;
            }
        
            window.app.mapContext.geolocation.navWatch = navigator.geolocation.watchPosition(
                position => updateFcn(position),
                ME => console.error(ME),
                {
                    enableHighAccuracy: true,
                    timeout: 30000,
                    maximumAge: 0
                }
            );
        }

        /*---------------------------------------------------------------------------------*/
        static stopLocationTracking() {
            try {
                if (window.app.mapContext.geolocation.navWatch != null) {
                    navigator.geolocation.clearWatch(window.app.mapContext.geolocation.navWatch);
                }                
            } catch (ME) {
                console.error(ME);
            }
        }

        /*---------------------------------------------------------------------------------*/
        static routeMidPoint(routeIndex) {
            const routeList   = window.app.analysisContext.routeList[routeIndex];
            const accumulator = routeList.waypoints.reduce((acc, curr) => {
                acc.lat += curr.lat;
                acc.lng += curr.lng;

                return acc;
            }, { lat: 0, lng: 0 });

            const midPoint = {
                lat: accumulator.lat / routeList.waypoints.length,
                lng: accumulator.lng / routeList.waypoints.length,
            }
            
            return midPoint;
        }
    }


    class Elevation {
        /*---------------------------------------------------------------------------------*/
        static range(routeInfo) {
            const elevationLimits = [routeInfo.origin, ...routeInfo.waypoints].reduce((acc, curr) => {
                if (curr.elevation < acc.min) {
                  acc.min = curr.elevation;
                }

                if (curr.elevation > acc.max) {
                  acc.max = curr.elevation;
                }

                return acc;
              }, { min: Infinity, max: -Infinity });

              return elevationLimits;
        }
    }
    

    class Image {
        static parulaColormap = [[ 53,  42, 135], [ 45,  53, 140], [ 38,  63, 146], [ 30,  73, 151], [ 23,  84, 157], [ 16,  94, 162],
                                 [ 11, 103, 167], [  8, 110, 170], [  6, 118, 173], [  5, 125, 176], [  5, 131, 178], [  6, 138, 180],
                                 [  8, 144, 182], [ 11, 150, 183], [ 14, 156, 185], [ 18, 161, 186], [ 23, 165, 187], [ 30, 170, 186],
                                 [ 37, 174, 186], [ 46, 177, 185], [ 54, 180, 184], [ 64, 183, 183], [ 74, 185, 181], [ 85, 188, 179],
                                 [ 96, 190, 176], [106, 192, 174], [116, 194, 171], [127, 197, 167], [138, 199, 164], [149, 202, 160],
                                 [159, 204, 156], [170, 204, 152], [181, 206, 147], [192, 208, 142], [202, 210, 137], [213, 212, 131],
                                 [223, 214, 126], [233, 216, 120], [242, 217, 114], [250, 218, 109], [255, 219, 103], [255, 217,  96],
                                 [255, 215,  90], [255, 211,  77], [255, 206,  63], [255, 204,  57], [255, 200,  51]];


        /*---------------------------------------------------------------------------------*/
        static customPinIcon(text, color) {
            let htmlContent = `<svg id="iconSvg" width="25" height="41" viewBox="0 0 25 41" xmlns="http://www.w3.org/2000/svg">
            \t<path d="M12.5 0 C19.4 0 25 5.6 25 12.5 C25 19.4 12.5 41 12.5 41 C12.5 41 0 19.4 0 12.5 C0 5.6 5.6 0 12.5 0Z" fill="${color.pin}"/>
            \t<text x="50%" y="35%" alignment-baseline="middle" text-anchor="middle" font-size="12" fill="${color.label}">${text}</text>
            </svg>`;

            return window.L.divIcon({
                html: htmlContent,
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                className: 'pin'
            });
        }


        /*---------------------------------------------------------------------------------*/
        static colorbar() {
            let minValue, maxValue, step;

            minValue = window.app.mapContext.colormap.range.min;
            maxValue = window.app.mapContext.colormap.range.max;
            if (maxValue === minValue) {
                maxValue++;
            }

            step = (maxValue - minValue) / 15;
            
            // Criando o elemento SVG diretamente via JavaScript
            const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svg.setAttribute("viewBox", "0 0 100 1000");
            svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
            svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
            svg.style.width = "100%"; // Garante que ele ocupa todo o espaço do container
            svg.style.height = "100%";
        
            // Criando o gradiente
            const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
            const linearGradient = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient");
            linearGradient.setAttribute("id", "grad");
            linearGradient.setAttribute("x1", "0");
            linearGradient.setAttribute("y1", "1");
            linearGradient.setAttribute("x2", "0");
            linearGradient.setAttribute("y2", "0");
        
            // Cores do gradiente
            let colors = [];
            this.parulaColormap.forEach(element => {
                let color = `rgb(${element[0]}, ${element[1]}, ${element[2]}, 1)`;
                colors.push(color);
            })

            // Criando os "stops" no gradiente
            colors.forEach((color, index) => {
                const stop = document.createElementNS("http://www.w3.org/2000/svg", "stop");
                stop.setAttribute("offset", `${index * (100 / (colors.length - 1))}%`); // Percentual de cada cor no gradiente
                stop.setAttribute("style", `stop-color:${color}; stop-opacity:1`);
                linearGradient.appendChild(stop);
            });
        
        
            defs.appendChild(linearGradient);
            svg.appendChild(defs);
        
            // Criando o fundo branco
            const background = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            background.setAttribute("x", "0");
            background.setAttribute("y", "0");
            background.setAttribute("width", "120");
            background.setAttribute("height", "1000");
            background.setAttribute("rx", "10");
            background.setAttribute("ry", "10");
            background.setAttribute("fill", "white");
            background.setAttribute("fill-opacity", "0.8");
            svg.appendChild(background);
        
            // Criando o retângulo de escala com gradiente
            const scaleRect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            scaleRect.setAttribute("x", "5");
            scaleRect.setAttribute("y", "5");
            scaleRect.setAttribute("width", "45");
            scaleRect.setAttribute("height", "990");
            scaleRect.setAttribute("rx", "10");
            scaleRect.setAttribute("ry", "10");
            scaleRect.setAttribute("fill", "url(#grad)");
            svg.appendChild(scaleRect);
        
            // Criando as marcações e os textos da escala
            for (let ii = 0; ii < 16; ii++) {
                const y = 985 - (ii * 969) / 15;
                const value = (minValue + ii * step).toFixed(1);
        
                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", "5");
                line.setAttribute("x2", "50");
                line.setAttribute("y1", y);
                line.setAttribute("y2", y);
                line.setAttribute("stroke", "white");
                line.setAttribute("stroke-opacity", "0.3");
                line.setAttribute("stroke-width", "2");
                svg.appendChild(line);
        
                const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
                text.setAttribute("x", "114");
                text.setAttribute("y", y + 7);
                text.setAttribute("font-family", "sans-serif");
                text.setAttribute("font-size", "19");
                text.setAttribute("fill", "black");
                text.setAttribute("text-anchor", "end");
                text.textContent = `${Math.round(value)}m`;
                svg.appendChild(text);
            }
        
            return svg;
        }


        /*---------------------------------------------------------------------------------*/
        static pinColor(elevation, colormap = 'parula') {
            let refColorArray, minElevation, maxElevation;

            switch (colormap) {
                case 'parula':
                    refColorArray = this.parulaColormap;
                    break;
                default:
                    throw new Error('Unexpected colomap');
            }

            minElevation = window.app.mapContext.settings.colormap.range.min;
            maxElevation = window.app.mapContext.settings.colormap.range.max;
            if (maxElevation === minElevation) {
                maxElevation++;
            }
        
            elevation = Math.max(minElevation, Math.min(maxElevation, elevation));
            const normalized = (elevation - minElevation) / (maxElevation - minElevation);
        
            // Índice interpolado
            const scaledIndex = normalized * (refColorArray.length - 1);
            const index = Math.floor(scaledIndex);
            const t = scaledIndex - index; // Posição relativa entre os dois pontos
        
            // Obtém as cores para interpolação
            const [r1, g1, b1] = refColorArray[index];
            const [r2, g2, b2] = refColorArray[Math.min(index + 1, refColorArray.length - 1)];
        
            // Interpolação linear entre os dois pontos
            const red   = Math.round(r1 + t * (r2 - r1));
            const green = Math.round(g1 + t * (g2 - g1));
            const blue  = Math.round(b1 + t * (b2 - b1));

            const brightness = 0.2126 * red + 0.7152 * green + 0.0722 * blue;
            const ratio = 1 - (brightness / 255);

            let r = Math.round(255 * ratio);
            let g = Math.round(255 * ratio);
            let b = Math.round(255 * ratio);

            return { 
                pin:   `rgb(${red}, ${green}, ${blue})`,
                label: `rgb(${r}, ${g}, ${b})`
            }
        }
    }

    window.app.modules.Utils = {
        syncLocalStorage,
        consoleLog,
        uuid,
        hash,
        getTimeStamp,
        exportAsZip,
        saveToFile,
        resolvePushType,
        GeoLocation,
        Elevation,
        Image
    };
})()