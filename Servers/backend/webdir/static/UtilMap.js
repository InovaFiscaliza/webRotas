//////////////////////////////////////////////////////////////////////////////////////////////////////
/*
 const redMarker = L.AwesomeMarkers.icon({
 icon: 'info-sign',
 markerColor: 'red', // Cor do marcador
 prefix: 'glyphicon' // Biblioteca de icones (use 'fa' para FontAwesome)
 });
 */

var  gpsMarker = null;
gpsMarker = L.marker([0, 0], { icon: gpsIcon }).addTo(map);


document.addEventListener("DOMContentLoaded", function () {
    // Sua função aqui
    
    console.log("A página foi carregada (DOM completamente construído).");
});

window.addEventListener("load", function () {
    // Sua função aqui
    CreateControls();
    console.log("Todos os recursos da página foram carregados.");
});
 
const clickedIcon = L.icon({
    iconUrl: 'data:image/png;base64,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gAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJElcmvXAAABLxJREFUAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQBAUZnGMvFnAMgkAgAorscz8mcAyCACACgq17ZM/BkAMokAAAoqcX1Bks/qz0hLm6s0B0DGEABAQX3xs3c+bNLfzPSfd9M9X/zc7z1UzU0AsoMAAAosSfQ2zex1/MdrTG+v9h4A2UEAAAX2hb+886A8uU2uQ1P+h1yH5MltX/jLOw/O4TQAgREAQMFt/sy7O0umdknfmsL//FslU/vmz7y7c653AQjLQg8AMH9e/pr3vtATf7WkH5fUdPb/PCDp3yy1u+/57Hu+HW4dgPn0/wF4jPYZF7VEIQAAAABJRU5ErkJggg==', // Icone clicado
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    className: 'clicked-marker' // Adiciona uma classe para diferenciar visualmente
});

const clickedIconHalf = L.icon({
    iconUrl: 'data:image/png;base64,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gAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJElcmvXAAABLxJREFUAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQAAAESIAAAAIEIEAAAAESIAAACIEAEAAECECAAAACJEAAAAECECAACACBEAAABEiAAAACBCBAAAABEiAAAAiBABAABAhAgAAAAiRAAAABAhAgAAgAgRAAAARIgAAAAgQgQAAAARIgAAAIgQAQAAQIQIAAAAIkQAAAAQIQIAAIAIEQBAUZnGMvFnAMgkAgAorscz8mcAyCACACgq17ZM/BkAMokAAAoqcX1Bks/qz0hLm6s0B0DGEABAQX3xs3c+bNLfzPSfd9M9X/zc7z1UzU0AsoMAAAosSfQ2zex1/MdrTG+v9h4A2UEAAAX2hb+886A8uU2uQ1P+h1yH5MltX/jLOw/O4TQAgREAQMFt/sy7O0umdknfmsL//FslU/vmz7y7c653AQjLQg8AMH9e/pr3vtATf7WkH5fUdPb/PCDp3yy1u+/57Hu+HW4dgPn0/wF4jPYZF7VEIQAAAABJRU5ErkJggg==', // Icone clicado
    iconSize: [18, 18],
    iconAnchor: [9, 18],
    className: 'clicked-marker' // Adiciona uma classe para diferenciar visualmente
});

/*
var iMarquerVerde = L.icon({
    iconUrl: '/static/MarkerVerde.png', // Icone clicado
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    className: 'marker' // Adiciona uma classe para diferenciar visualmente
});
*/
var iMarquerVerde = createCustomSvgIcon("o",[25, 41],[12, 41],"#007b22");

var iMarquerAzul = L.icon({
    iconUrl: '/static/MarkerAzul.png', // Icone clicado
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    className: 'marker' // Adiciona uma classe para diferenciar visualmente
});

var iMarquerVerdeHalf = L.icon({
    iconUrl: '/static/MarkerVerde.png', // Icone clicado
    iconSize: [12, 20],
    iconAnchor: [6, 20],
    className: 'marker' // Adiciona uma classe para diferenciar visualmente
});

var iMarquerAzulHalf  = L.icon({
    iconUrl: '/static/MarkerAzul.png', // Icone clicado
    iconSize: [12, 20],
    iconAnchor: [6, 20],
    className: 'marker' // Adiciona uma classe para diferenciar visualmente
});
//////////////////////////////////////////////////////////////////////////////////////////////////////
/*
var newIcon=null; // Não funciona
function ChangeMarquerIconSize(marker,div, newSize,newAnchor) 
{
    // Chamar a função para alterar o tamanho do ícone para metade do original
    // changeIconSize(marker, [25, 41]);
    // Criar um novo ícone com o novo tamanho
    newIcon = L.icon({
        iconUrl: marker.options.icon.options.iconUrl,
        iconSize: [newSize[0]/2 , newSize[1]/2 ],
        iconAnchor: [newAnchor[0]/2 , newAnchor[1]/2 ],
        className: 'changed'
    });

    // Atualizar o ícone do marcador
    marker.setIcon(newIcon);
} */

//////////////////////////////////////////////////////////////////////////////////////////////////////
// Função para criar um icone svg numerado
function createSvgIcon(number) {  

    return createCustomSvgIcon(number,[25, 41],[12, 41],"#007bff");
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function createSvgIconAzul(number) {  

    return createCustomSvgIcon(number,[25, 41],[12, 41],"#007bff");
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function createSvgIconAzulHalf(number) {  

    return createCustomSvgIcon(number,[12, 20],[6, 20],"#007bff");
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function ElevationColor(elevation) {
    // Limita a elevação ao intervalo 0-8900
    max_elevation = globalMaxElevation;
    elevation = Math.max(0, Math.min(max_elevation, elevation));

    // Normaliza a elevação para o intervalo 0-1
    const normalized = elevation / max_elevation;

    // Converte a normalização em cores do arco-íris
    const hue = (1 - normalized) * 240; // 240° (azul) a 0° (vermelho)
    return hslToHex(hue, 100, 50); // Saturação 100%, Luminosidade 50%
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
// Função auxiliar: converte HSL para HEX
function hslToHex(h, s, l) {
    s /= 100;
    l /= 100;

    const k = n => (n + h / 30) % 12;
    const a = s * Math.min(l, 1 - l);
    const f = n =>
        l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));

    const r = Math.round(255 * f(0));
    const g = Math.round(255 * f(8));
    const b = Math.round(255 * f(4));

    return `#${r.toString(16).padStart(2, "0")}${g
        .toString(16)
        .padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function getElevationSync(latitude, longitude){
    getElevation(latitude, longitude)
    .then(elevation => {
        if (elevation !== null) {
            console.log(`Elevation - ${elevation}`)
            return elevation;
        } else {
            return 0;
        }
    });
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
async function getElevation(latitude, longitude) {
    const apiUrl = `https://api.open-elevation.com/api/v1/lookup?locations=${latitude},${longitude}`;
    
    try {
        const response = await fetch(apiUrl); // Faz a requisição à API
        if (!response.ok) {
            throw new Error(`Erro ao buscar elevação: ${response.statusText}`);
        }

        const data = await response.json(); // Converte a resposta para JSON
        if (data.results && data.results.length > 0) {
            return data.results[0].elevation; // Retorna a elevação
        } else {
            throw new Error("Nenhum dado de elevação encontrado.");
        }
    } catch (error) {
        console.error("Erro ao obter elevação:", error.message);
        return null; // Retorna `null` em caso de erro
    }
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function createSvgIconColorAltitude(number,altitude) {  
    color = ElevationColor(altitude);
    return createCustomSvgIcon(number,[25, 41],[12, 41],color);
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function createSvgIconColorAltitudeHalf(number,altitude) {  
    color = ElevationColor(altitude);
    return createCustomSvgIcon(number,[12, 20],[6, 20],color);
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function createSvgIconVerde(number) {  

    return createCustomSvgIcon(number,[25, 41],[12, 41],"#007b22");
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function createSvgIconVerdeHalf(number) {  

    return createCustomSvgIcon(number,[12, 20],[6, 20],"#007b22");
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function createSvg(iconSz, iconColor, text) {
    const width = iconSz[0];
    const height = iconSz[1];

    // Tamanhos base do SVG original
    const baseWidth = 25;
    const baseHeight = 41;

    // Calcula fatores de escala
    const scaleX = width / baseWidth;
    const scaleY = height / baseHeight;

    // Recalcula o path com base no fator de escala
    const dynamicPath = `
        M${12.5 * scaleX} 0
        C${19.4 * scaleX} 0 ${25 * scaleX} ${5.6 * scaleY} ${25 * scaleX} ${12.5 * scaleY}
        C${25 * scaleX} ${19.4 * scaleY} ${12.5 * scaleX} ${41 * scaleY} ${12.5 * scaleX} ${41 * scaleY}
        C${12.5 * scaleX} ${41 * scaleY} 0 ${19.4 * scaleY} 0 ${12.5 * scaleY}
        C0 ${5.6 * scaleY} ${5.6 * scaleX} 0 ${12.5 * scaleX} 0Z
    `.trim();

    // Retorna o SVG ajustado
    return `
        <svg id="iconSvg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" 
             xmlns="http://www.w3.org/2000/svg">
            <path d="${dynamicPath}" fill="${iconColor}"/> 
            <text x="50%" y="50%" alignment-baseline="middle" text-anchor="middle" font-size="${Math.min(width, height) * 0.55}" 
                  fill="white" font-weight="bold">${text}</text>
        </svg>`;
}

//////////////////////////////////////////////////////////////////////////////////////////////////////
function createCustomSvgIcon(text,iconSz,iconAnc,iconColor) {  
    /*
    datHtml = `<svg id="iconSvg" width="${iconSz[0]}" height="${iconSz[1]}" viewBox="0 0 ${iconSz[0]} ${iconSz[1]}" 
               xmlns="http://www.w3.org/2000/svg">
               <path d="M12.5 0C19.4 0 25 5.6 25 12.5C25 19.4 12.5 41 12.5 41C12.5 41 0 19.4 0 12.5C0 5.6 5.6 0 12.5 0Z" 
               fill="${iconColor}"/> <text x="50%" y="50%" alignment-baseline="middle" text-anchor="middle" font-size="12" 
               fill="white" font-weight="bold">${text}</text>
               </svg>`; 
    */
    datHtml = createSvg(iconSz, iconColor, text)           
    return L.divIcon({
        className: '', // Sem classe adicional
        html: datHtml,
        iconSize: iconSz, // Tamanho do ícone
        iconAnchor: iconAnc // Ponto de ancoragem (centro)
    });
}
//////////////////////////////////////////////////////////////////////////////////////////////////////        
function onMarkerClick(e) {
    const currentMarker = e.target;
    const markerId = currentMarker._icon.getAttribute('data-id');
    const clicado = currentMarker._icon.getAttribute('clicado');
    const altitude = currentMarker._icon.getAttribute('altitude');
    console.log(`Marquer clicado - ID - ${markerId} - Clicado - ${clicado}`)
    // Verifica o ícone atual e troca para o outro
    if (HeadingNorte==0)
    {    
        console.log(`aqui`)
        if (clicado === "0") {
            currentMarker.setIcon(clickedIcon);
            currentMarker._icon.setAttribute('clicado', "1");
        } else {
            // aaaaaaaaaaaaaaaa createSvgIconColorAltitude
            // currentMarker.setIcon(createSvgIconAzul(String(markerId)));   
            currentMarker.setIcon(createSvgIconColorAltitude(String(markerId),String(altitude))); 
            currentMarker._icon.setAttribute('clicado', "0");
        }      
        currentMarker._icon.setAttribute('tamanho', "full");
    }
    else
    {
        if (clicado === "0") {
            currentMarker.setIcon(clickedIconHalf);
            currentMarker._icon.setAttribute('clicado', "1");
        } else {
            // currentMarker.setIcon(createSvgIconAzulHalf(String(markerId)));
            currentMarker.setIcon(createSvgIconColorAltitudeHalf(String(markerId),String(altitude))); 
            currentMarker._icon.setAttribute('clicado', "0");
        }
        currentMarker._icon.setAttribute('tamanho', "half");
    }
    currentMarker._icon.setAttribute('data-id', String(markerId));
    currentMarker._icon.setAttribute('altitude', String(altitude));
    AtualizaGps();
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
// Fução que rotaciona um icone no Leaflet
(function () {
    // save these original methods before they are overwritten
    var proto_initIcon = L.Marker.prototype._initIcon;
    var proto_setPos = L.Marker.prototype._setPos;

    var oldIE = (L.DomUtil.TRANSFORM === 'msTransform');

    L.Marker.addInitHook(function () {
        var iconOptions = this.options.icon && this.options.icon.options;
        var iconAnchor = iconOptions && this.options.icon.options.iconAnchor;
        if (iconAnchor) {
            iconAnchor = (iconAnchor[0] + 'px ' + iconAnchor[1] + 'px');
        }
        this.options.rotationOrigin = this.options.rotationOrigin || iconAnchor || 'center bottom';
        this.options.rotationAngle = this.options.rotationAngle || 0;

        // Ensure marker keeps rotated during dragging
        this.on('drag', function (e) {
            e.target._applyRotation();
        });
    });

    L.Marker.include({
        _initIcon: function () {
            proto_initIcon.call(this);
        },

        _setPos: function (pos) {
            proto_setPos.call(this, pos);
            this._applyRotation();
        },

        _applyRotation: function () {
            if (this.options.rotationAngle) {
                this._icon.style[L.DomUtil.TRANSFORM + 'Origin'] = this.options.rotationOrigin;

                if (oldIE) {
                    // for IE 9, use the 2D rotation
                    this._icon.style[L.DomUtil.TRANSFORM] = 'rotate(' + this.options.rotationAngle + 'deg)';
                } else {
                    // for modern browsers, prefer the 3D accelerated version
                    this._icon.style[L.DomUtil.TRANSFORM] += ' rotateZ(' + this.options.rotationAngle + 'deg)';
                }
            }
        },

        setRotationAngle: function (angle) {
            this.options.rotationAngle = angle;
            this.update();
            return this;
        },

        setRotationOrigin: function (origin) {
            this.options.rotationOrigin = origin;
            this.update();
            return this;
        }
    });
})();

//////////////////////////////////////////////////////////////////////////////////////////////////////
function decodePolyline(encoded) {
    let index = 0;
    const coordinates = [];
    let lat = 0;
    let lng = 0;

    while (index < encoded.length) {
        let shift = 0;
        let result = 0;
        let byte;

        do {
            byte = encoded.charCodeAt(index++) - 63;
            result |= (byte & 0x1f) << shift;
            shift += 5;
        } while (byte >= 0x20);

        const deltaLat = (result & 1) ? ~(result >> 1) : (result >> 1);
        lat += deltaLat;

        shift = 0;
        result = 0;

        do {
            byte = encoded.charCodeAt(index++) - 63;
            result |= (byte & 0x1f) << shift;
            shift += 5;
        } while (byte >= 0x20);

        const deltaLng = (result & 1) ? ~(result >> 1) : (result >> 1);
        lng += deltaLng;

        coordinates.push([lat / 1e5, lng / 1e5]);
    }

    return coordinates;
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
// Função para calcular a distância Haversine entre duas coordenadas
function haversineDistance(coord1, coord2) {
    const toRad = angle => (angle * Math.PI) / 180;
    const R = 6371; // Raio da Terra em km
    const dLat = toRad(coord2.lat - coord1.lat);
    const dLon = toRad(coord2.lng - coord1.lng);
    const lat1 = toRad(coord1.lat);
    const lat2 = toRad(coord2.lat);

    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.sin(dLon / 2) * Math.sin(dLon / 2) * Math.cos(lat1) * Math.cos(lat2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
// Função para encontrar o marcador mais próximo
var DistMakerMaisProximo = null
var markerVet = null;
function GetNearestPoint(lat, lon) {
    const userLocation = {lat: lat, lng: lon};

    // Lista de marcadores já adicionados ao mapa
    // const markers = [marker1, marker2, marker3, marker4, marker5, marker6, marker7, marker8];

    let closestMarkerCoords = null;
    let minDistance = Infinity;
    if (markerVet==null)
        return(null);
    markerVet.forEach(marker => {
        const markerCoords = marker.getLatLng(); // Obtém as coordenadas do marcador
        const distance = haversineDistance(userLocation, markerCoords);
        if ((distance < minDistance) && ((marker.options.icon != clickedIcon) && (marker.options.icon != clickedIconHalf))) 
        {
            minDistance = distance;
            closestMarkerCoords = markerCoords;   
        }
    });
    DistMakerMaisProximo = minDistance.toFixed(2);
    return closestMarkerCoords; // Retorna as coordenadas do marcador mais próximo
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
// Exemplo de uso
// const nearestPoint = GetNearestPoint(-22.9000, -43.0500);
// console.log("Marcador mais próximo está em:", nearestPoint.lat, nearestPoint.lng);
//////////////////////////////////////////////////////////////////////////////////////////////////////
function calcularMediaUltimasNCoordenadas(coordinates, n) {
    // Verifica se há coordenadas suficientes
    if (coordinates.length < n) {
        console.error("Não há coordenadas suficientes para calcular a média");
        return null;
    }

    // Seleciona as últimas n coordenadas
    const primeirasNCoordenadas = coordinates.slice(0,n);

    // Calcula a média de latitude e longitude
    let somaLat = 0;
    let somaLng = 0;
    primeirasNCoordenadas.forEach(coord => {
        somaLat += coord[0];
        somaLng += coord[1];
    });

    const mediaLat = somaLat / n;
    const mediaLng = somaLng / n;

    return [mediaLat, mediaLng];  // Retorna a média como uma nova coordenada [latitude, longitude]
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
var polyRotaAux = null;
var inicioRota = null;
function DesenhaRota(coordinates)
{
    // Crie a polyline com as coordenadas e adicione ao mapa
    if (polyRotaAux) {
        polyRotaAux.remove();
        polyRotaAux = null; // Opcional: redefinir a variável para null
    }
    console.log("Plotando nova rota auxiliar")
    polyRotaAux = L.polyline(coordinates, {color: 'red', "opacity": 0.7}).addTo(map);
    
    // armazena o inicio da rota para a simulação de movimento buscar a rota ok
    if (coordinates.length > 0) {
        inicioRota = calcularMediaUltimasNCoordenadas(coordinates,20);
    }  
    else 
       inicioRota = null;  
    // Ajuste a visualização do mapa para mostrar a polyline inteira
    // map.fitBounds(poly_line.getBounds());
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function ServerUrl()
{
    // Pega o protocolo (http ou https)
    const protocol = window.location.protocol;
    // Pega o hostname (domínio ou IP)
    const host = window.location.hostname;
    // Pega a porta (se estiver definida, por exemplo, 5000 para Flask)
    const port = window.location.port;
    // Constrói a URL base
    const serverUrl = `${protocol}//${host}${port ? `:${port}` : ''}`;
    return serverUrl
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
async function getRoute(startCoords, endCoords){
    if(ServerTec == "OSMR")
    {
        return getRouteOSMR(startCoords, endCoords);
    } 
    if(ServerTec == "GHopper")
    {
        return getRouteGHopper(startCoords, endCoords);
    } 
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
// Função para obter a rota do OSRM por roteamento do mesmo site externo
async function getRouteGHopper(startCoords, endCoords) {
    serverUrl = "http://localhost:8989"

    // "http://localhost:8989/route?point=-22.87248975925445,-43.08681365669065&point=-22.885656291854495,-43.05230110610495"
    
    const url = `${serverUrl}/route?point=${startCoords[0]},${startCoords[1]}&point=${endCoords[0]},${endCoords[1]}`;
    console.log("\n\n" + url + "\n");

    try {
        // Fazer a solicitação usando fetch
        const response = await fetch(url);
        const data = await response.json();

        // Verificar se a solicitação foi bem-sucedida
        if (response.ok && data.paths) {
            const route = data.paths[0];
            const geometry = route.points;

            // Decodificar a geometria usando uma biblioteca como @mapbox/polyline
            coordinates = decodePolyline(geometry); // polyline precisa estar disponível/importada
            console.log("Coordinates:", coordinates);
            DesenhaRota(coordinates);
            return coordinates;
        } else {
            console.error("Erro ao obter a rota:", data.message || "Resposta inválida");
            return null;
        }
    } catch (error) {
        console.error("Erro de rede:", error);
        return null;
    }
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
// Função para obter a rota do OSRM por roteamento do mesmo site externo
async function getRouteOSMR(startCoords, endCoords) {
    // URL da solicitação ao servidor OSRM
    // const baseUrl = "{{ url_for('proxy') }}"
    
    // serverUrl = ServerUrl()  // Falhou no ngrock a resposta em json
    // console.log("URL do servidor:", serverUrl);
    // const url = `${serverUrl}/osmr/route/v1/driving/${startCoords[1]},${startCoords[0]};${endCoords[1]},${endCoords[0]}?overview=full&geometries=polyline&steps=true`; 
    
    // ngrok http 5001  
    if ( window.location.hostname=="127.0.0.1") 
    {
       //  sem ngrock 
       serverUrl = `${window.location.protocol}//${window.location.hostname}`;
       url = `${serverUrl}:5001/route?porta=${OSRMPort}&start=${startCoords[1]},${startCoords[0]}&end=${endCoords[1]},${endCoords[0]}`
    }    
    else
    {
       //  no ngrock
       serverUrl = `${window.location.protocol}//${window.location.hostname}`;
       url = `${serverUrl}/route?porta=${OSRMPort}&start=${startCoords[1]},${startCoords[0]}&end=${endCoords[1]},${endCoords[0]}`
    }
    console.log("\n\n" + url + "\n");

    try {
        // Fazer a solicitação usando fetch
        const response = await fetch(url);
        const data = await response.json();

        // Verificar se a solicitação foi bem-sucedida
        if (response.ok && data.routes) {
            const route = data.routes[0];
            const geometry = route.geometry;

            // Decodificar a geometria usando uma biblioteca como @mapbox/polyline
            coordinates = decodePolyline(geometry); // polyline precisa estar disponível/importada
            console.log("Coordinates:", coordinates);
            DesenhaRota(coordinates);
            return coordinates;
        } else {
            console.error("Erro ao obter a rota:", data.message || "Resposta inválida");
            return null;
        }
    } catch (error) {
        console.error("Erro de rede:", error);
        return null;
    }
}
////////////////////////////////////////////////////////////////////////////////////////////////////// 

var headingError=0
function AtualizaMapaHeading(heading)
{
    // alert("atualizando gps - ",HeadingNorte);
    if (HeadingNorte==0)
    { 
       // Mapa fixo direção sul e carro rotacionando
       RodaMapaPorCss(0);
       gpsMarker.setRotationAngle(heading-90);

       
    }
    else
    {
        // Mapa girando em direção ao heading
        RodaMapaPorCss(heading -(2*heading));
        headingError=heading -(2*heading)
        gpsMarker.setRotationAngle(-90-headingError);     
    }

}
//////////////////////////////////////////////////////////////////////////////////////////////////////
let latitude = -22.91745583955038;  // Latitude inicial
let longitude = -43.08681365669065; // Longitude inicial
let heading = 0;
let velocidade = 180/3.6;  // Velocidade em km/h ---> m/s
let raio = 1000; // Raio de movimentação (em metros)
//////////////////////////////////////////////////////////////////////////////////////////////////////
function adjustHeading(heading) {
    if (heading >= 360) {
        heading -= 360;
    }
    return heading;
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
// Calcula heading em direção a um ponto
function calculateHeading(lat1, lon1, lat2, lon2) {
    // Converte latitude e longitude de graus para radianos
    let radLat1 = lat1 * Math.PI / 180;
    let radLon1 = lon1 * Math.PI / 180;
    let radLat2 = lat2 * Math.PI / 180;
    let radLon2 = lon2 * Math.PI / 180;

    // Diferença entre as longitudes
    let dLon = radLon2 - radLon1;

    // Fórmula para o cálculo do heading
    let y = Math.sin(dLon) * Math.cos(radLat2);
    let x = Math.cos(radLat1) * Math.sin(radLat2) -
            Math.sin(radLat1) * Math.cos(radLat2) * Math.cos(dLon);

    // Calcula o ângulo e converte para graus
    let heading = Math.atan2(y, x) * 180 / Math.PI;

    // Ajusta o ângulo para estar entre 0 e 360 graus
    return (heading + 360) % 360;
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
var incHead = 1;
function simularMovimento() {
    // Calcula a distância percorrida por atualização (300ms ou 0.3 segundos)
    const distancia = velocidade * 0.3;  // Em metros

    /* 
    if (heading==80)
        incHead = -1;
    if (heading==0)
        incHead = 1;    
    heading = heading+incHead;
    heading = adjustHeading(heading);
    */
    
    if (inicioRota!=null)
        heading = calculateHeading(latitude, longitude, inicioRota[0], inicioRota[1]);   // Aponta para o inicio da rota
    // Convertendo a direção (heading) para radianos
    const radianos = heading * (Math.PI / 180);

    // Calcula as novas coordenadas simulando movimento em linha reta
    latitude += (distancia * Math.cos(radianos)) / 111320; // Convertendo metros para graus de latitude (aproximadamente)
    longitude += (distancia * Math.sin(radianos)) / (111320 * Math.cos(latitude * (Math.PI / 180))); // Convertendo metros para graus de longitude


    // Atualiza o GPS a cada 300ms
    updateGPSPosition({ coords: { latitude, longitude, heading, speed: velocidade } });
}
// Simular movimento
// setInterval(simularMovimento, 800); // Atualiza a cada 300ms (aproximadamente)
//////////////////////////////////////////////////////////////////////////////////////////////////////
async function obterHeadingOsrm(lat, lon) {
    serverUrl = `http://localhost:${OSRMPort}`
    const url = `${serverUrl}/nearest/v1/driving/${lon},${lat}?number=1`;

    try {
        // Faz a requisição para o OSRM
        const response = await fetch(url);

        if (response.ok) {
            const data = await response.json();

            // Verifica se há waypoints na resposta
            if (data.waypoints && data.waypoints.length > 0) {
                // Captura o bearing (heading)
                const heading = data.waypoints[0].bearing;
                console.log(`Heading encontrado: ${heading} graus`);
                return heading;
            } else {
                console.error("Nenhum waypoint encontrado.");
                return null;
            }
        } else {
            console.error(`Erro na requisição: ${response.status} - ${response.statusText}`);
            return null;
        }
    } catch (error) {
        console.error(`Erro ao conectar ao OSRM: ${error.message}`);
        return null;
    }
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
// Adiciona o evento de clique no mapa 
// Simula posição do carro em clique para debugar

map.on('click', function(e) {
    // Obtém as coordenadas do clique
    var lat = e.latlng.lat;
    var lon = e.latlng.lng;

    gpsMarker.setLatLng([lat, lon]);
    // Centraliza o mapa na nova posição do marcador
    map.setView([lat, lon]);
    latitude =lat;
    longitude = lon;
    heading = 0;
    velocidade = 0;
    GetRouteCarFromHere(latitude,longitude); 
});
//////////////////////////////////////////////////////////////////////////////////////////////////////
var LastHeading = 0;  
var maxHistorySize = 5;
var positionHistory = [];    
//////////////////////////////////////////////////////////////////////////////////////////////////////   
var gpsAtivado = false; // Defina como false para desabilitar a geolocalização  
////////////////////////////////////////////////////////////////////////////////////////////////////// 
function updateGPSPosition(position) {
    if(gpsAtivado==false)
        return
    if (position === undefined) {
        console.log("A posição é undefined.");
        return;
    }
    latitude = position.coords.latitude;
    longitude = position.coords.longitude;
    heading = position.coords.heading;
    speed = position.coords.speed;

    // Armazena a nova posição
    positionHistory.push({ latitude, longitude, heading });
    if (positionHistory.length > maxHistorySize) {
        positionHistory.shift(); // Remove a posição mais antiga
    }



    // degub lat e lon RETIRAR EM PRODUÇÃO
    // latitude = -22.87714906709627;    
    // longitude = -42.98235891833397;

    if (heading !== null || !isNaN(heading)) 
    {
        // heading = Math.round(heading);
        LastHeading = heading;
    } else
    {
        heading = 'N/A';
        LastHeading = 0;
    }

    if (speed !== null) {
        speed = Math.round(speed * 3.6)
    } else
    {
        speed = 'N/A';
    }

    // Calcula a média das posições
    latitude = positionHistory.reduce((sum, pos) => sum + pos.latitude, 0) / positionHistory.length;
    longitude = positionHistory.reduce((sum, pos) => sum + pos.longitude, 0) / positionHistory.length;
    if (heading !== 'N/A')
       heading = positionHistory.reduce((sum, pos) => sum + pos.heading, 0) / positionHistory.length;
    // Move o marcador para a nova posição
    gpsMarker.setLatLng([latitude, longitude]);
    // Centraliza o mapa na nova posição do marcador
    map.setView([latitude, longitude]);
    // Rotaciona o marcador com base no heading
    gpsMarker.setRotationAngle(heading);
    document.getElementById("gpsInfo").innerText = `Velocidade: ${speed} Km/h\nHeading: ${heading} graus\nDistancia: ${DistMakerMaisProximo} Km`;
    
    AtualizaMapaHeading(LastHeading);
    GetRouteCarFromHere(latitude,longitude); 
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function GetRouteCarFromHere(latitude,longitude)
{
   console.log("Tentando pegar rota")
   startCoords = [];
   endCoords = [];
   nearestPoint = GetNearestPoint(latitude, longitude);
   if (nearestPoint==null) // Apaga rota auxiliar 
   {
       if (polyRotaAux) {
           polyRotaAux.remove();
           polyRotaAux = null; // Opcional: redefinir a variável para null
       }
       return;
   }    
   startCoords[0] = latitude;
   startCoords[1] = longitude;
   endCoords[0] = nearestPoint.lat;
   endCoords[1] = nearestPoint.lng;
   getRoute(startCoords, endCoords); 
}  
//////////////////////////////////////////////////////////////////////////////////////////////////////
// Monitora a posição do usuário e chama updateGPSPosition a cada atualização
if (navigator.geolocation)
{
        navigator.geolocation.getCurrentPosition(updateGPSPosition,
            error => console.error(error),
            {enableHighAccuracy: true, maximumAge: 0, timeout: 30000 });  
} else
{
    alert("Geolocalização não é suportada pelo seu navegador.");
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
 function AtualizaGps() {
    navigator.geolocation.getCurrentPosition(updateGPSPosition,
        error => console.error(error),
        {enableHighAccuracy: true, maximumAge: 0, timeout: 30000 });
 }

// Definindo o intervalo de 300ms
// let timer = setInterval(AtualizaGps, 1000);
//////////////////////////////////////////////////////////////////////////////////////////////////////  
function SelIconHalf(marker,flagHeadingNorte)
{
    markerOld = marker;
    size = markerOld._icon.getAttribute('tamanho');
    clicado = markerOld._icon.getAttribute('clicado');
    markerId = markerOld._icon.getAttribute('data-id');
    altitude = markerOld._icon.getAttribute('altitude');
    if (clicado=="1")
        if (flagHeadingNorte==0)
        {    
           marker.setIcon(clickedIcon);
           marker._icon.setAttribute('tamanho',"full");
        }   
        else 
        { 
           marker.setIcon(clickedIconHalf);
           marker._icon.setAttribute('tamanho',"half");
        }   
    else
       if (flagHeadingNorte==0)
       { 
           // aaaaaaaaaaaaaa createSvgIconColorAltitude
           // marker.setIcon(createSvgIconAzul(String(markerId)));
           marker.setIcon(createSvgIconColorAltitude(String(markerId),String(altitude)));
           marker._icon.setAttribute('tamanho',"full");
       }   
       else 
       { 
           // marker.setIcon(createSvgIconAzulHalf(String(markerId))); 
           marker.setIcon(createSvgIconColorAltitudeHalf(String(markerId),String(altitude)));
           marker._icon.setAttribute('tamanho',"half");
       }    
    CopyMarkerAttribs(markerOld,marker);    
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function CopyMarkerAttribs(MarkerOrigin,MarkerDest)
{
    MarkerDest._icon.setAttribute('data-id',MarkerOrigin._icon.getAttribute('data-id'));
    MarkerDest._icon.setAttribute('clicado',MarkerOrigin._icon.getAttribute('clicado'));
    // MarkerDest._icon.setAttribute('tamanho',MarkerOrigin._icon.getAttribute('tamanho'));
    MarkerDest._icon.setAttribute('altitude',MarkerOrigin._icon.getAttribute('altitude'));
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function AjustaTamanhoMarquers(div)
{
    if(markerVet==null)
        return null;
    if (div===0)
    {
        if (TipoRoute == 'DriveTest')
            markerCentral.setIcon(createSvgIconVerde("x")); 
        markerVet.forEach(marker => {
               SelIconHalf(marker,div);
            });
        mrkPtInicial.setIcon(createSvgIconColorAltitude('i',10000))    
    }    
    else
    {
        if (TipoRoute == 'DriveTest')
            markerCentral.setIcon(createSvgIconVerdeHalf("x"));
        markerVet.forEach(marker => {
            SelIconHalf(marker,div);
        });
        mrkPtInicial.setIcon(createSvgIconColorAltitudeHalf('i',10000))  
    }

}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function RodaMapaPorCss(angle) // Não funciona bem
{
   const mapElement = document.getElementById('map');
   // Aplica a rotação e define o ponto de origem
   // var markerPosition = map.latLngToContainerPoint(gpsMarker.getLatLng());

   if(HeadingNorte==0)
   { 
      mapElement.style.transform = `rotate(${0}deg) scale(1.0) `; // Define o ângulo de rotação
      mapElement.style.transformOrigin = 'center';  // Define o ponto de rotação
      gpsMarker.setIcon(gpsIcon);
      AjustaTamanhoMarquers(HeadingNorte);
   }
   else
   { 
      mapElement.style.transform = `rotate(${angle}deg) scale(2.5) `; // Define o ângulo de rotação
      mapElement.style.transformOrigin = 'center';  // Define o ponto de rotação
      gpsMarker.setLatLng([latitude, longitude]);
      gpsMarker.setIcon(gpsIconHalf);
      AjustaTamanhoMarquers(HeadingNorte);
   }
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
// Define se o mapa é rotacionado se HeadingNorte=1
HeadingNorte=0
function createCompassIcon() {
    // Cria a div para a bússola
    const compassDiv = document.createElement('div');
    compassDiv.id = 'compassIconDirecaoMapa';
    
    // Define os estilos inline da bússola
    compassDiv.style.position = 'absolute';
    compassDiv.style.top = '10px';
    compassDiv.style.right = '10px';
    compassDiv.style.width = '45px';              // Largura da bússola
    compassDiv.style.height = '45px';             // Altura da bússola
    // compassDiv.style.backgroundImage = 'url("/static/PointerNorte.png")'; // URL da imagem da bússola
    compassDiv.style.backgroundImage = imgPointerNorte; 
    compassDiv.style.backgroundSize = '35px 35px';    // Redimensiona a imagem para cobrir a div
    compassDiv.style.backgroundPosition = 'center'; // Centraliza o background
    compassDiv.style.backgroundRepeat = 'no-repeat'; // Evita repetição da imagem
    compassDiv.style.backgroundColor = 'white'; 
    compassDiv.style.display = 'flex';
    compassDiv.style.alignItems = 'center';
    compassDiv.style.justifyContent = 'center';
    compassDiv.style.borderRadius = '50%';        // Bordas arredondadas
    compassDiv.style.cursor = 'pointer';          // Mostra o cursor de clique
    compassDiv.style.zIndex = 1000;
    
    // Cria o ícone da bússola (seta para o norte)
    const icon = document.createElement('i');
    
    // Estilos inline do ícone
    // icon.style.fontSize = '20px';
    // icon.style.color = '#fff';
    //icon.style.transform = 'rotate(0deg)';        // Alinhado ao norte

    // Adiciona um evento de clique à bússola
    compassDiv.addEventListener('click', function() {
        // alert('Você clicou na bússola!');         // Alerta ou função quando clicado
        if (HeadingNorte==0) 
        {    
            // alert('Clicou para PointerNorte.png',HeadingNorte)
            // compassDiv.style.backgroundImage = 'url("/static/Pointer.png")';
            compassDiv.style.backgroundImage = imgPointer;
            HeadingNorte=1;
            AtualizaMapaHeading(LastHeading);
        }
        else    
        {
            // alert('Clicou para Pointer.png',HeadingNorte)
            // compassDiv.style.backgroundImage = 'url("/static/PointerNorte.png")';
            compassDiv.style.backgroundImage = imgPointerNorte;
            HeadingNorte=0
            AtualizaMapaHeading(LastHeading);
        }    
    });

    // Adiciona o ícone dentro da bússola
    // compassDiv.appendChild(icon);

    // Adiciona a bússola ao corpo da página
    document.body.appendChild(compassDiv);
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function SetHeadingNorte_SemRodarMapa()
{
   compassDiv = document.getElementById('compassIconDirecaoMapa'); 
   compassDiv.style.backgroundImage = imgPointerNorte;
   HeadingNorte=0;
   AtualizaMapaHeading(LastHeading);
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function createAtivaGps() {
    // Cria a div para a bússola
    const compassDiv = document.createElement('div');
    
    // Define os estilos inline da bússola
    compassDiv.style.position = 'absolute';
    compassDiv.style.top = '60px';
    compassDiv.style.right = '10px';
    compassDiv.style.width = '45px';              // Largura da bússola
    compassDiv.style.height = '45px';             // Altura da bússola
    // compassDiv.style.backgroundImage = 'url("/static/GpsAtivo.png")'; // URL da imagem da bússola
    if(gpsAtivado)
        compassDiv.style.backgroundImage = imgGpsAtivo;
    else
        compassDiv.style.backgroundImage = imgGpsInativo;    
    compassDiv.style.backgroundSize = '35px 35px';    // Redimensiona a imagem para cobrir a div
    compassDiv.style.backgroundPosition = 'center'; // Centraliza o background
    compassDiv.style.backgroundRepeat = 'no-repeat'; // Evita repetição da imagem
    compassDiv.style.backgroundColor = 'white'; 
    compassDiv.style.display = 'flex';
    compassDiv.style.alignItems = 'center';
    compassDiv.style.justifyContent = 'center';
    compassDiv.style.borderRadius = '50%';        // Bordas arredondadas
    compassDiv.style.cursor = 'pointer';          // Mostra o cursor de clique
    compassDiv.style.zIndex = 1000;
    
    // Cria o ícone da bússola (seta para o norte)
    const icon = document.createElement('i');
    
    // Estilos inline do ícone
    // icon.style.fontSize = '20px';
    // icon.style.color = '#fff';
    //icon.style.transform = 'rotate(0deg)';        // Alinhado ao norte

    // Adiciona um evento de clique à bússola
    compassDiv.addEventListener('click', function() {
        // alert('Você clicou na bússola!');         // Alerta ou função quando clicado
        if (gpsAtivado) 
        {    
            // alert('Clicou para PointerNorte.png',HeadingNorte)
            // compassDiv.style.backgroundImage = 'url("/static/GpsInativo.png")';
            compassDiv.style.backgroundImage = imgGpsInativo;
            gpsAtivado=false;
        }
        else    
        {
            // alert('Clicou para Pointer.png',HeadingNorte)
            // compassDiv.style.backgroundImage = 'url("/static/GpsAtivo.png")';
            compassDiv.style.backgroundImage = imgGpsAtivo;
            gpsAtivado=true;
        }    
    });

    // Adiciona o ícone dentro da bússola
    // compassDiv.appendChild(icon);

    // Adiciona a bússola ao corpo da página
    document.body.appendChild(compassDiv);
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
ElevationTableOpen = false;
function createColorTable() {
    // Cria a div para a bússola
    const compassDiv = document.createElement('div');
    
    // Define os estilos inline da bússola
    compassDiv.style.position = 'absolute';
    compassDiv.style.top = '80px';
    compassDiv.style.left = '10px';
    compassDiv.style.width = '45px';             
    compassDiv.style.height = '45px'; 
    compassDiv.style.borderRadius = '50%';        // Bordas arredondadas    
    compassDiv.style.backgroundSize = '45px 45px';    
    // compassDiv.style.backgroundImage = 'url("/static/OpenElevTable.png")';  
    compassDiv.style.backgroundImage = imgOpenElevTable;
    compassDiv.style.backgroundPosition = 'center'; // Centraliza o background
    compassDiv.style.backgroundRepeat = 'no-repeat'; // Evita repetição da imagem
    compassDiv.style.backgroundColor = 'white'; 
    compassDiv.style.display = 'flex';
    compassDiv.style.alignItems = 'center';
    compassDiv.style.justifyContent = 'center';
    compassDiv.style.cursor = 'pointer';          // Mostra o cursor de clique
    compassDiv.style.zIndex = 1000;
    
  
    const icon = document.createElement('i');
    
    // Estilos inline do ícone
    // icon.style.fontSize = '20px';
    // icon.style.color = '#fff';
    //icon.style.transform = 'rotate(0deg)';        // Alinhado ao norte

    // Adiciona um evento de clique à bússola
    compassDiv.addEventListener('click', function() {
        // Alerta ou função quando clicado
        if (ElevationTableOpen == false) 
        {
            // compassDiv.style.backgroundImage = 'url("/static/elevation_table.png")';  
            compassDiv.style.backgroundImage = imgElevationTable ;  
            
            ElevationTableOpen=true;
            compassDiv.style.width = '150px';            
            compassDiv.style.height = '500px';   
            compassDiv.style.backgroundSize = '150px 500px';   
            compassDiv.style.borderRadius = '2%';           
        }   
        else
        {
            compassDiv.style.backgroundImage = imgOpenElevTable;  
            ElevationTableOpen=false;
            compassDiv.style.width = '45px';             
            compassDiv.style.height = '45px'; 
            compassDiv.style.backgroundSize = '45px 45px';
            compassDiv.style.borderRadius = '50%';
        } 
    });
    document.body.appendChild(compassDiv);
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
// https://base64.guru/converter/encode/file
//////////////////////////////////////////////////////////////////////////////////////////////////////
function createDivOrdemPontos() {
    // Cria a div para a bússola
    // Desabilita modo mapa girar com o veículopara evitar bugs

    const compassDiv = document.createElement('div');
    
    // Define os estilos inline da bússola
    compassDiv.style.position = 'absolute';
    compassDiv.style.top = '130px';
    compassDiv.style.left = '10px';
    compassDiv.style.width = '45px';             
    compassDiv.style.height = '45px'; 
    compassDiv.style.borderRadius = '50%';        // Bordas arredondadas    
    compassDiv.style.backgroundSize = '45px 45px';    
    // compassDiv.style.backgroundImage = 'url("/static/OrdemPontos.png")';  
    compassDiv.style.backgroundImage = imgOrdemPontos;
    compassDiv.style.backgroundPosition = 'center'; // Centraliza o background
    compassDiv.style.backgroundRepeat = 'no-repeat'; // Evita repetição da imagem
    compassDiv.style.backgroundColor = 'white'; 
    compassDiv.style.display = 'flex';
    compassDiv.style.alignItems = 'center';
    compassDiv.style.justifyContent = 'center';
    compassDiv.style.cursor = 'pointer';          // Mostra o cursor de clique
    compassDiv.style.zIndex = 999;
    
  
    const icon = document.createElement('i');
    
    // Estilos inline do ícone
    // icon.style.fontSize = '20px';
    // icon.style.color = '#fff';
    //icon.style.transform = 'rotate(0deg)';        // Alinhado ao norte

    // Adiciona um evento de clique à bússola
    compassDiv.addEventListener('click', function() {
        // Alerta ou função quando clicado
        createDivOrdenaPontos();
    });
    // Adiciona o ícone dentro da bússola
    // compassDiv.appendChild(icon);

    // Adiciona a bússola ao corpo da página
    document.body.appendChild(compassDiv);
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function EncontrarDado(pontosvisitaDados, lat, lon,iDado) {
    // Procura o ponto com a mesma latitude e longitude
    const ponto = pontosvisitaDados.find(p => p[0] === lat && p[1] === lon);

    // Retorna o endereço se o ponto for encontrado, ou uma mensagem padrão
    return ponto ? ponto[iDado] : "Idado não encontrado";
}

//////////////////////////////////////////////////////////////////////////////////////////////////////
function EncontrarDadoPn(pontosvisitaDados, Pn,iDado) {
    // Procura o ponto com a mesma latitude e longitude
    ponto = pontosvisitaDados.find(p => p[2] === Pn);
    // Retorna o endereço se o ponto for encontrado, ou uma mensagem padrão
    return ponto ? ponto[iDado] : "Idado não encontrado";
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function limparMarcadores(markerVet) {
    // Verifica se o array tem marcadores
    if (!markerVet || markerVet.length === 0) {
        console.log("Nenhum marcador para remover.");
        return;
    }

    // Itera sobre os marcadores e remove cada um do mapa
    markerVet.forEach(marker => {
        if (marker.remove) {
            marker.remove(); // Remove o marcador do mapa
        }
    });

    // Esvazia o array
    markerVet.length = 0;

}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function AtualizaPontosvisitaDados(pontosvisitaDados,lat, lon,iPn,iPnDados)
{
    console.log(`lat ${lat}, lon ${lat}, iPn - ${iPn}, iPnDados -  ${iPnDados}`);
    i_posicaoiPnDados = pontosvisitaDados.findIndex(ponto => ponto[2] === iPnDados );
    i_posicaolatlon = pontosvisitaDados.findIndex(ponto => ponto[0] === lat && ponto[1] === lon );
    
    pontosvisitaDados[i_posicaoiPnDados][2]=iPnDados;
    pontosvisitaDados[i_posicaolatlon][2]=iPn;
    return pontosvisitaDados; 
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function ReordenaPontosTela(pontosVisita){
    limparMarcadores(markerVet)
    
    markerVet = [];
    i=0;
    pontosVisita.forEach(point => {
        lat = point[0];
        lon = point[1];

        iPn = `P${i}`;
        iPnDados=EncontrarDado(pontosvisitaDados, lat, lon,2);
        tooltip = EncontrarDado(pontosvisitaDados, lat, lon,4);
        alt = EncontrarDado(pontosvisitaDados, lat, lon,5);
        console.log(`---->>> lat ${lat}, lon ${lat}`);
        console.log(`---->>> iPn - ${iPn}, iPnDados -  ${iPnDados}`);
        if(iPn!=iPnDados)
        {
            pontosvisitaDados=AtualizaPontosvisitaDados(pontosvisitaDados,lat, lon,iPn,iPnDados);
        }

        markerbufTemp = L.marker([lat, lon]).addTo(map).on('click', onMarkerClick).setIcon(createSvgIconColorAltitude(i,alt));
        markerbufTemp._icon.setAttribute('data-id', `${i}`); 
        markerbufTemp._icon.setAttribute('clicado', '0'); 
        markerbufTemp._icon.setAttribute('tamanho', 'full'); 
        markerbufTemp._icon.setAttribute('altitude', '`${alt}`');
        markerbufTemp.bindTooltip(tooltip, {permanent: false,direction: 'top',offset: [0, -60],className:'custom-tooltip'});
        markerVet.push(markerbufTemp);
        i=i+1;
    });

}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function createDivOrdenaPontos() {
    // Cria a div principal

    if (document.getElementById('divOrdenaPontos')) {
        console.log('A div já está aberta.');
        return; // Sai da função se a div já existir
    }
    SetHeadingNorte_SemRodarMapa();
    const compassDiv = document.createElement('div');
    compassDiv.id = 'divOrdenaPontos';
    // Define os estilos da div principal
    compassDiv.style.position = 'absolute';
    compassDiv.style.top = '50%';
    compassDiv.style.left = '50%';
    compassDiv.style.transform = 'translate(-50%, -50%)';
    compassDiv.style.width = '400px'; // Tamanho inicial
    compassDiv.style.height = '300px';
    compassDiv.style.backgroundColor = '#f9f9f9';
    compassDiv.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
    compassDiv.style.display = 'flex';
    compassDiv.style.flexDirection = 'column';
    compassDiv.style.alignItems = 'flex-start';
    compassDiv.style.padding = '10px';
    compassDiv.style.border = '2px solid #ccc';
    compassDiv.style.borderRadius = '8px';
    compassDiv.style.resize = 'both';
    compassDiv.style.overflow = 'auto';
    compassDiv.style.cursor = 'move'; // Cursor de movimento para o arrasto
    compassDiv.style.zIndex = 1000;

    document.body.appendChild(compassDiv);

    // Função para arrastar a div
    let offsetX, offsetY, isDragging = false;

    compassDiv.addEventListener('mousedown', function (e) {
        isDragging = true;
        offsetX = e.clientX - compassDiv.offsetLeft;
        offsetY = e.clientY - compassDiv.offsetTop;
        compassDiv.style.cursor = 'grabbing'; // Muda o cursor ao arrastar
    });

    document.addEventListener('mousemove', function (e) {
        if (isDragging) {
            compassDiv.style.left = `${e.clientX - offsetX}px`;
            compassDiv.style.top = `${e.clientY - offsetY}px`;
        }
    });

    document.addEventListener('mouseup', function () {
        isDragging = false;
        compassDiv.style.cursor = 'move'; // Retorna ao cursor padrão
    });

    // Adiciona o rótulo
    const label = document.createElement('label');
    label.htmlFor = 'lista3';
    label.textContent = 'Ordem dos pontos:';
    label.style.marginBottom = '10px';
    label.style.fontFamily = 'Arial, sans-serif';
    label.style.fontSize = '14px';
    label.style.color = '#333';
    compassDiv.appendChild(label);

    // Cria o controle de seleção múltipla
    const select = document.createElement('select');
    select.id = 'listaPontos';
    // select.multiple = true;
    select.size = 10000; // Define o número de itens visíveis
    select.style.width = '100%';
    select.style.height = 'calc(100% - 70px)'; // Ocupa o espaço restante
    select.style.fontSize = '16px';
    compassDiv.appendChild(select);

    // Adiciona opções ao select
    /*
    ['P1', 'P2', 'P3', 'P4', 'P5'].forEach((text, index) => {
        const option = document.createElement('option');
        option.value = index + 1;
        option.textContent = text;
        select.appendChild(option);
    });
    */
    // Adiciona opções ao select
    function LoadSelect()
    {
        pontosVisita.forEach((ponto, index) => {
            const [latitude, longitude] = ponto;
            const option = document.createElement('option');
            option.value = index + 1;
            option.textContent = EncontrarDado(pontosvisitaDados, latitude, longitude,2);
            select.appendChild(option);
        });
    
    }
    LoadSelect();
    // Cria os botões
    const buttonsContainer = document.createElement('div');
    buttonsContainer.style.position = 'absolute';
    buttonsContainer.style.bottom = '10px';
    buttonsContainer.style.left = '10px';
    buttonsContainer.style.right = '10px';
    buttonsContainer.style.display = 'flex'; // Flex para alinhar os botões horizontalmente
    buttonsContainer.style.gap = '10px'; // Espaçamento entre os botões

    const sobeBtn = createButton('Sobe', () => moveOption(-1));
    const desceBtn = createButton('Desce', () => moveOption(1));
    const reordenaBtn = createButton('Reordena', () => reordenaOption());
    const fechaBtn = createButton('Fecha', () => document.body.removeChild(compassDiv));
    fechaBtn.style.backgroundColor = '#0039FF';
    fechaBtn.style.color = '#fff';

    buttonsContainer.appendChild(sobeBtn);
    buttonsContainer.appendChild(desceBtn);
    buttonsContainer.appendChild(reordenaBtn);
    buttonsContainer.appendChild(fechaBtn);
    compassDiv.appendChild(buttonsContainer);

    // Função auxiliar para criar botões
    function createButton(text, onClick) {
        const button = document.createElement('button');
        button.textContent = text;
        button.style.padding = '8px 12px';
        button.style.cursor = 'pointer';
        button.addEventListener('click', onClick);
        return button;
    }
    ////////////////////////////////
    function reordenaOption(){
        const selectElement = document.getElementById('listaPontos');
        // Pega a lista de itens (opções)
        const options = Array.from(selectElement.options); // Converte para array para facilitar manipulação
        
        // Exibe os valores e textos no console
        pontosVisitaNew = []
        options.forEach(option => {
            // console.log(`Value: ${option.value}, Text: ${option.textContent}`);
            // alert(`Value: ${option.value}, Text: ${option.textContent}`);
            lat = EncontrarDadoPn(pontosvisitaDados, option.textContent,0)
            lon = EncontrarDadoPn(pontosvisitaDados, option.textContent,1)
            pontosVisitaNew.push([lat, lon]); 
        });
        pontosVisita = pontosVisitaNew;
        ReordenaPontosTela(pontosVisita);
        select.innerHTML = '';
        LoadSelect();
    }
    ////////////////////////////////
    // Função para mover opções na lista
    function moveOption(direction) {
        const selectedIndex = select.selectedIndex;
        if (selectedIndex === -1) return; // Nenhuma opção selecionada
    
        const selectedOption = select.options[selectedIndex];
        const newIndex = selectedIndex + direction;
    
        // Verificar limites
        if (newIndex < 0 || newIndex >= select.options.length) return;
    
        // Mover a opção
        select.removeChild(selectedOption);
        select.insertBefore(selectedOption, select.options[newIndex]);
    
        // Atualizar o índice selecionado
        select.selectedIndex = newIndex;
    }
    
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function CreateControls()
{
    HeadingNorte=0;
    createCompassIcon();
    createAtivaGps();
    createColorTable();
    createDivOrdemPontos(); 
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
