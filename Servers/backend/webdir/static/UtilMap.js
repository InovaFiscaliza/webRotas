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
    iconUrl: '/static/RedPin.png', // Icone clicado
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    className: 'clicked-marker' // Adiciona uma classe para diferenciar visualmente
});

const clickedIconHalf = L.icon({
    iconUrl: '/static/RedPin.png', // Icone clicado
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
    console.log(`Marquer clicado - ID - ${markerId} - Clicado - ${clicado}`)
    // Verifica o ícone atual e troca para o outro
    if (HeadingNorte==0)
    {    
        console.log(`aqui`)
        if (clicado === "0") {
            currentMarker.setIcon(clickedIcon);
            currentMarker._icon.setAttribute('clicado', "1");
        } else {
            currentMarker.setIcon(createSvgIconAzul(String(markerId)));   
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
            currentMarker.setIcon(createSvgIconAzulHalf(String(markerId)));
            currentMarker._icon.setAttribute('clicado', "0");
        }
        currentMarker._icon.setAttribute('tamanho', "half");
    }
    currentMarker._icon.setAttribute('data-id', String(markerId));
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
var gpsAtivado = true; // Defina como false para desabilitar a geolocalização  
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
let timer = setInterval(AtualizaGps, 1000);
//////////////////////////////////////////////////////////////////////////////////////////////////////  
function SelIconHalf(marker)
{
    markerOld = marker;
    size = markerOld._icon.getAttribute('tamanho');
    clicado = markerOld._icon.getAttribute('clicado');
    markerId = markerOld._icon.getAttribute('data-id');
    if (clicado=="1")
        if (size=="full")
           marker.setIcon(clickedIcon);
        else 
           marker.setIcon(clickedIconHalf);
    else
       if (size=="full")
           marker.setIcon(createSvgIconAzul(String(markerId)));
       else 
           marker.setIcon(createSvgIconAzulHalf(String(markerId))); 
    CopyMarkerAttribs(markerOld,marker);    
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function CopyMarkerAttribs(MarkerOrigin,MarkerDest)
{
    MarkerDest._icon.setAttribute('data-id',MarkerOrigin._icon.getAttribute('data-id'));
    MarkerDest._icon.setAttribute('clicado',MarkerOrigin._icon.getAttribute('clicado'));
    MarkerDest._icon.setAttribute('tamanho',MarkerOrigin._icon.getAttribute('tamanho'));
    MarkerDest._icon.setAttribute('altitude',MarkerOrigin._icon.getAttribute('altitude'));
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
function AjustaTamanhoMarquers(div)
{
    /*
    var iMarquerVerde = L.icon({
        iconUrl: '/static/MarkerVerde.png', // Icone clicado
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        className: 'clicked-marker' // Adiciona uma classe para diferenciar visualmente
    });
    */
    if(markerVet==null)
        return null;
    if (div==0)
    {
        if (TipoRoute == 'DriveTest')
            markerCentral.setIcon(createSvgIconVerde("x")); 
        markerVet.forEach(marker => {
            SelIconHalf(marker)
        });
    }    
    else
    {
        if (TipoRoute == 'DriveTest')
            markerCentral.setIcon(createSvgIconVerdeHalf("x"));
        markerVet.forEach(marker => {
            SelIconHalf(marker)
        });
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
      /*       Testando outras formas de rotacionar mapa 
      mapElement.style.width = '100vw';
      mapElement.style.height = '100vh';      
      mapElement.style.transformOrigin = `${markerPosition.x}px ${markerPosition.y}px`;
      mapElement.style.transform = `rotate(${0}deg) `; 
      */
   }
   else
   { 
      mapElement.style.transform = `rotate(${angle}deg) scale(2.5) `; // Define o ângulo de rotação
      mapElement.style.transformOrigin = 'center';  // Define o ponto de rotação
      gpsMarker.setLatLng([latitude, longitude]);
      gpsMarker.setIcon(gpsIconHalf);
      AjustaTamanhoMarquers(HeadingNorte);
      /*  Testando outras formas de rotacionar mapa      
      mapElement.style.width = '4000px';
      mapElement.style.height = '4000px';      
      mapElement.style.overflow= 'visible';
      mapElement.style.transformOrigin = `${markerPosition.x}px ${markerPosition.y}px`;
      mapElement.style.transform = `rotate(${angle}deg) `;  
      */
   }
}
//////////////////////////////////////////////////////////////////////////////////////////////////////
// Define se o mapa é rotacionado se HeadingNorte=1
HeadingNorte=0
function createCompassIcon() {
    // Cria a div para a bússola
    const compassDiv = document.createElement('div');
    
    // Define os estilos inline da bússola
    compassDiv.style.position = 'absolute';
    compassDiv.style.top = '10px';
    compassDiv.style.right = '10px';
    compassDiv.style.width = '45px';              // Largura da bússola
    compassDiv.style.height = '45px';             // Altura da bússola
    compassDiv.style.backgroundImage = 'url("/static/PointerNorte.png")'; // URL da imagem da bússola
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
            compassDiv.style.backgroundImage = 'url("/static/Pointer.png")';
            HeadingNorte=1;
            AtualizaMapaHeading(LastHeading);
        }
        else    
        {
            // alert('Clicou para Pointer.png',HeadingNorte)
            compassDiv.style.backgroundImage = 'url("/static/PointerNorte.png")';
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
function createAtivaGps() {
    // Cria a div para a bússola
    const compassDiv = document.createElement('div');
    
    // Define os estilos inline da bússola
    compassDiv.style.position = 'absolute';
    compassDiv.style.top = '60px';
    compassDiv.style.right = '10px';
    compassDiv.style.width = '45px';              // Largura da bússola
    compassDiv.style.height = '45px';             // Altura da bússola
    compassDiv.style.backgroundImage = 'url("/static/GpsAtivo.png")'; // URL da imagem da bússola
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
            compassDiv.style.backgroundImage = 'url("/static/GpsInativo.png")';
            gpsAtivado=false;
        }
        else    
        {
            // alert('Clicou para Pointer.png',HeadingNorte)
            compassDiv.style.backgroundImage = 'url("/static/GpsAtivo.png")';
            gpsAtivado=true;
        }    
    });

    // Adiciona o ícone dentro da bússola
    // compassDiv.appendChild(icon);

    // Adiciona a bússola ao corpo da página
    document.body.appendChild(compassDiv);
}

//////////////////////////////////////////////////////////////////////////////////////////////////////
function CreateControls()
{
    HeadingNorte=0;
    createCompassIcon();
    createAtivaGps();

}
//////////////////////////////////////////////////////////////////////////////////////////////////////
