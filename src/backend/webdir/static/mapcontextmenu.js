// Cria o menu de contexto dinamicamente
const contextMenu = document.createElement('div');
contextMenu.id = 'contextMenu';
contextMenu.style.position = 'absolute';
contextMenu.style.background = 'white';
contextMenu.style.border = '1px solid #ccc';
contextMenu.style.boxShadow = '2px 2px 10px rgba(0, 0, 0, 0.2)';
contextMenu.style.zIndex = '1000';
contextMenu.style.padding = '5px';
contextMenu.style.display = 'none';
document.body.appendChild(contextMenu);

// Cria a lista de itens do menu
const menuList = document.createElement('ul');
menuList.style.listStyle = 'none';
menuList.style.margin = '0';
menuList.style.padding = '0';
contextMenu.appendChild(menuList);

// Função para adicionar itens ao menu
function addMenuItem(text, id, onClick) {
    const menuItem = document.createElement('li');
    menuItem.id = id;
    menuItem.textContent = text;
    menuItem.style.padding = '5px 10px';
    menuItem.style.cursor = 'pointer';
    menuItem.style.fontFamily = 'Arial, sans-serif'; // Fonte Arial
    menuItem.style.fontSize = '12px'; // Tamanho da fonte 12px
    menuItem.addEventListener('click', onClick);
    menuItem.addEventListener('mouseenter', () => {
        menuItem.style.backgroundColor = '#f0f0f0';
    });
    menuItem.addEventListener('mouseleave', () => {
        menuItem.style.backgroundColor = 'white';
    });
    menuList.appendChild(menuItem);
}

// Adiciona os itens do menu
addMenuItem('Coordenadas: lat, lon', 'coords', () => {
    // Obtém o texto das coordenadas
    const coordsText = contextMenu.querySelector('#coords').textContent;

    // Extrai apenas os valores de lat e lon usando uma expressão regular
    const coordsMatch = coordsText.match(/-?\d+\.\d+/g); // Captura números decimais (positivos ou negativos)
    if (coordsMatch && coordsMatch.length === 2) {
        const [lat, lon] = coordsMatch;
        const coordsToCopy = `${lat}, ${lon}`; // Formata como "lat, lon"

        // Copia as coordenadas para o clipboard
        navigator.clipboard.writeText(coordsToCopy)
            .then(() => {
                exibirMensagemComTimeout('Coordenadas copiadas para a área de transferência: ' + coordsToCopy,timeout = 1000);
            })
            .catch((err) => {
                console.error('Erro ao copiar coordenadas: ', err);
                exibirMensagemComTimeout('Erro ao copiar coordenadas. Tente novamente.' + coordsToCopy,timeout = 1000);
            });
    } else {
        alert('Formato de coordenadas inválido.');
    }

    closeMenu();
});

addMenuItem('Visualizar no StreetView', 'streetView', () => {
    const coords = contextMenu.querySelector('#coords').textContent.match(/-?\d+\.\d+/g);
    const [lat, lng] = coords;
    openStreetView(lat, lng); 
    closeMenu();
});

addMenuItem('Atualizar posição do veículo (offline)', 'updateVehicle', () => {
    const coords = contextMenu.querySelector('#coords').textContent.match(/-?\d+\.\d+/g);
    const [lat, lon] = coords;
    simulaVeiculoNesteLocal(lat,lon) ;
    closeMenu();
});

// Evento de clique com o botão direito no mapa
map.on('contextmenu', function(e) {
    const { lat, lng } = e.latlng;

    // Atualiza o texto das coordenadas no menu
    document.getElementById('coords').textContent = `Coordenadas: ${lat.toFixed(6)}, ${lng.toFixed(6)}`;

    // Posiciona o menu no local do clique
    contextMenu.style.left = `${e.originalEvent.clientX}px`;
    contextMenu.style.top = `${e.originalEvent.clientY}px`;
    contextMenu.style.display = 'block';

    // Fecha o menu ao clicar em qualquer lugar fora dele
    document.addEventListener('click', closeMenu);
});

// Fecha o menu
function closeMenu() {
    contextMenu.style.display = 'none';
    document.removeEventListener('click', closeMenu);
}