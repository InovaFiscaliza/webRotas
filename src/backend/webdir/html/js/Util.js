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
        static add(targetElement, tooltipText) {
            let tooltip, tooltipArrow;
    
            targetElement.addEventListener('mouseenter', () => {
                tooltip = window.document.createElement('div');
                tooltip.className = 'tooltip-panel';
                tooltip.innerHTML = tooltipText;
    
                tooltipArrow = window.document.createElement('div');
                tooltipArrow.className = 'tooltip-arrow';
    
                tooltip.appendChild(tooltipArrow);
                window.document.body.appendChild(tooltip);
    
                const rect = targetElement.getBoundingClientRect();
                const scrollX  = window.scrollX;
                const scrollY  = window.scrollY;
                const centerX  = rect.left + scrollX + rect.width / 2;
                const maxRight = scrollX + window.innerWidth - 4;
    
                const tooltipWidth  = tooltip.offsetWidth;
                const tooltipHeight = tooltip.offsetHeight;    
                
                let left = centerX - tooltipWidth / 2;
                if (left < 4) { left = 4; }
                if (left + tooltipWidth > maxRight) { left = maxRight - tooltipWidth; }
    
                let top = rect.top + scrollY - tooltipHeight - 8;
                let showAbove = true;
                if (top < scrollY + 4) {
                    top = rect.bottom + scrollY + 8;
                    showAbove = false;
                }
    
                const arrowOffset = centerX - left - 6;
    
                Object.assign(tooltip.style, {
                    left: `${left}px`,
                    top: `${top}px`
                });
    
                Object.assign(tooltipArrow.style, {
                    left: `${arrowOffset}px`,
                    top: showAbove ? 'unset' : '-6px',
                    bottom: showAbove ? '-6px' : 'unset',
                    borderTop: showAbove ? '6px solid #333' : 'none',
                    borderBottom: showAbove ? 'none' : '6px solid #333'
                });
            });    
    
            targetElement.addEventListener('mouseleave', () => {
                if (tooltip) {
                    tooltip.remove();
                    tooltip = null;
                }
            });
        }
    }


    const Util = {
        "GeoLocation": GeoLocation,
        "Image": Image,
        "Tooltip": Tooltip,
    }

    window.app.module.Util = Util;
})()