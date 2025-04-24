(function () {
    class GeoLocation {
        /*---------------------------------------------------------------------------------*/
        static startLocationTracking(updateFcn) {
            if (!window.app.geolocation.status || window.app.geolocation.navWatch !== null) {
                return;
            }
        
            window.app.geolocation.navWatch = navigator.geolocation.watchPosition(
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
                if (window.app.geolocation.navWatch != null) {
                    navigator.geolocation.clearWatch(window.app.geolocation.navWatch);
                }                
            } catch (ME) {
                console.error(ME);
            }
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

            minValue = window.app.colorbar.cLim.min;
            maxValue = window.app.colorbar.cLim.max;
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

            minElevation = window.app.colorbar.cLim.min;
            maxElevation = window.app.colorbar.cLim.max;
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


    class Tooltip {
        /*-----------------------------------------------------------------------------------
            Customizações de estilo em "css/webRotas.scss"
            Classes: "tooltip-panel" e "tooltip-arrow"
        -----------------------------------------------------------------------------------*/
        static controller(targetElement, operationtype, tooltipText, tooltipRole) {
            let tooltip, tooltipId;

            if (!targetElement.dataset.tooltipId) {
                targetElement.dataset.tooltipId    = `${window.app.module.CreateComponent.uuid()}`;
                targetElement.dataset.tooltipState = 'hidden';
            }

            tooltipId = targetElement.dataset.tooltipId;

            switch (operationtype) {
                case 'add-hover-listener':
                    targetElement.addEventListener('mouseenter', () => tooltip = this.mouseEnterCallback(tooltip, targetElement, tooltipId, tooltipText, tooltipRole));
                    targetElement.addEventListener('mouseleave', () => this.mouseLeaveCallback(tooltip, targetElement));
                    break;

                case 'add-leaflet-tooltip':
                    tooltip = window.document.getElementById(tooltipId);

                    if (!tooltip) {
                        tooltip = window.app.module.CreateComponent.tooltip(targetElement, tooltipId, tooltipText, tooltipRole);
                        targetElement.dataset.tooltipState = 'click';

                    } else {
                        switch (targetElement.dataset.tooltipState) {
                            case 'click':
                                tooltip.remove();
                                tooltip = null;

                                targetElement.dataset.tooltipState = 'hidden';
                                break;

                            default:
                                targetElement.dataset.tooltipState = 'click';
                        }
                    }
                break;
            }
        }


        /*---------------------------------------------------------------------------------*/
        static mouseEnterCallback(tooltip, targetElement, tooltipId, tooltipText, tooltipRole) {
            if (!tooltip || targetElement.dataset.tooltipState === 'hidden') {
                tooltip = window.app.module.CreateComponent.tooltip(targetElement, tooltipId, tooltipText, tooltipRole);
                targetElement.dataset.tooltipState = 'hover';
            }

            return tooltip;
        }


        /*---------------------------------------------------------------------------------*/
        static mouseLeaveCallback(tooltip, targetElement) {
            if (tooltip && targetElement.dataset.tooltipState === 'hover') {
                tooltip.remove();
                tooltip = null;

                targetElement.dataset.tooltipState = 'hidden';
            }
        }


        /*---------------------------------------------------------------------------------*/
        static createLeafletTooltip(type, target, direction, text, ...args) {
            const offset = (direction === 'top') ? [0, -41] : [0, 0];

            switch (type) {
                case 'hover':
                    target.bindTooltip(text, { 
                        className: 'tooltip-panel', 
                        direction: direction,
                        offset: offset
                    });

                    return;

                case 'sticky':
                    const coords  = args[0];
                    const tooltip = window.L.tooltip({
                        className: 'tooltip-panel',
                        direction: direction,
                        offset: offset,
                        permanent: true,
                        interactive: true
                    })
                    .setContent(text)
                    .setLatLng(coords)
                    .addTo(window.app.map);

                    tooltip._CustomTooltip = { 
                        target: target,
                        direction: direction,
                        text: text,
                        coords: coords
                    };
        
                    tooltip.on('mousedown', (event) => {
                        window.app.map.dragging.disable();
    
                        if (window.app.plot.tooltip.mouseDownTarget.handle !== event.sourceTarget) {
                            const { screenX, screenY } = event.originalEvent;

                            window.app.plot.tooltip.mouseDownTarget.handle = event.sourceTarget;
                            window.app.plot.tooltip.mouseDownTarget.position = [screenX, screenY];
                        }                        
                    })
    
                    tooltip.on('mouseup', () => {
                        window.app.module.Plot.checkDragging();
                    });

                    window.L.DomEvent.on(tooltip, 'mousedown', window.L.DomEvent.stopPropagation);
                    window.L.DomEvent.on(tooltip, 'mouseup',   window.L.DomEvent.stopPropagation);

                    return tooltip;
            }            
        }


        /*---------------------------------------------------------------------------------*/
        static recreateLeafletTooltip(tooltip, newDirection) {
            const { target, text, coords } = tooltip._CustomTooltip;    
            
            target._tooltip.remove();
            window.app.module.Util.Tooltip.createLeafletTooltip('hover', target, newDirection, text);
            
            tooltip.remove();            
            target._CustomTooltip.handle    = this.createLeafletTooltip('sticky', target, newDirection, text, coords)
            target._CustomTooltip.mode      = 'sticky';
            target._CustomTooltip.direction = newDirection
        }


        /*---------------------------------------------------------------------------------*/
        static detectMouseDirection(initPosition, finalPosition) {          
            const hor  = finalPosition[0] > initPosition[0] ? "E" : "W";
            const vert = finalPosition[1] > initPosition[1] ? "S" : "N";
          
            return vert + hor;
        }                  


        /*---------------------------------------------------------------------------------*/
        static suggestNewTooltipDirection(tooltipDirection, mouseDirection) {
            switch (tooltipDirection) {
              case "bottom":
                if (mouseDirection === "NE") return "right";
                if (mouseDirection === "NW") return "left";
                if (mouseDirection === "N")  return "top";
                break;
          
              case "left":
                if (mouseDirection === "E")  return "right";
                if (mouseDirection === "NE") return "top";
                if (mouseDirection === "SE") return "bottom";
                break;
          
              case "right":
                if (mouseDirection === "W")  return "left";
                if (mouseDirection === "NW") return "top";
                if (mouseDirection === "SW") return "bottom";
                break;
          
              case "top":
                if (mouseDirection === "SE") return "right";
                if (mouseDirection === "SW") return "left";
                if (mouseDirection === "S")  return "bottom";
                break;
            }
            return null;
        }                       
    }


    const Util = {
        "GeoLocation": GeoLocation,
        "Image": Image,
        "Tooltip": Tooltip,
    }

    window.app.module.Util = Util;
})()