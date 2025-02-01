//////////////////////////////////////////////////////////////////////////////////////////////////////
// Dialogo de ordenação de pontos
fontSize = '10px';   // Tamanho da fonte
function clDivOrdenaPontos() {
    // Cria a div principal

    if (document.getElementById('divOrdenaPontos')) {
        console.log('A div já está aberta.');
        return; // Sai da função se a div já existir
    }
    SetHeadingNorte_SemRodarMapa();
    const iDlg = document.createElement('div');
    iDlg.id = 'divOrdenaPontos';
    // Define os estilos da div principal
    iDlg.style.position = 'absolute';
    // iDlg.style.top = '50%';
    // iDlg.style.left = '50%';
    // iDlg.style.transform = 'translate(-50%, -50%)';
    iDlg.style.top = '10px';
    iDlg.style.left = '10px'; 
    iDlg.style.width = '300px'; // Tamanho inicial
    iDlg.style.height = '600px';
    iDlg.style.backgroundColor = '#f9f9f9';
    iDlg.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.4)';  // sombra em torno do div para destaque na interface
    iDlg.style.display = 'flex';
    iDlg.style.flexDirection = 'column';
    iDlg.style.alignItems = 'flex-start';
    iDlg.style.padding = '10px';
    iDlg.style.border = '2px solid #ccc';
    iDlg.style.borderRadius = '8px';
    iDlg.style.resize = 'both';
    iDlg.style.overflow = 'auto';
    iDlg.style.cursor = 'move'; // Cursor de movimento para o arrasto
    iDlg.style.zIndex = 1000;
    iDlg.style.userSelect = 'none';           // Para navegadores modernos
    iDlg.style.webkitUserSelect = 'none';     // Para navegadores baseados no WebKit
    iDlg.style.mozUserSelect = 'none';        // Para Firefox
    iDlg.style.msUserSelect = 'none';


    document.body.appendChild(iDlg);

    // Função para arrastar a div
    let offsetX, offsetY, isDragging = false;

    iDlg.addEventListener('mousedown', function (e) {
        isDragging = true;
        offsetX = e.clientX - iDlg.offsetLeft;
        offsetY = e.clientY - iDlg.offsetTop;
        iDlg.style.cursor = 'grabbing'; // Muda o cursor ao arrastar
    });

    document.addEventListener('mousemove', function (e) {
        if (isDragging) {
            iDlg.style.left = `${e.clientX - offsetX}px`;
            iDlg.style.top = `${e.clientY - offsetY}px`;
        }
    });

    document.addEventListener('mouseup', function () {
        isDragging = false;
        iDlg.style.cursor = 'move'; // Retorna ao cursor padrão
    });

    
    // Adicionando o botão "X" para fechar
    const closeButton = document.createElement('button');
    closeButton.textContent = 'x';
    closeButton.style.position = 'absolute';
    closeButton.style.top = '5px';
    closeButton.style.right = '5px';
    closeButton.style.border = 'none';
    closeButton.style.borderRadius = '50%';
    closeButton.style.width = '15px';
    closeButton.style.height = '15px';
    closeButton.style.cursor = 'pointer';
    closeButton.style.display = 'flex';
    closeButton.style.alignItems = 'center';
    closeButton.style.justifyContent = 'center';
    closeButton.style.fontSize = fontSize;
    closeButton.title = 'Fechar';
    
    // Função para fechar o div
    closeButton.addEventListener('click', () => {
      iDlg.remove();
    });
    
    // Adicionando o botão ao div
    iDlg.appendChild(closeButton);

    //-----------------------------------------------------------------------------------
    // Rótulo Lista Rotas e seu controle de apagar rota
    // Cria um contêiner para acomodar os controles na horizontal
    container = document.createElement('div');
    container.style.display = 'flex';
    container.style.alignItems = 'center';
    container.style.justifyContent = 'space-between'; // Mantém um espaço entre os elementos
    container.style.width = '100%';
    container.style.paddingTop = '15px'; // Adiciona espaçamento no topo

    // Cria o rótulo
    label = document.createElement('label');
    label.htmlFor = 'listaRotas';
    label.textContent = 'Rotas:';
    label.style.marginBottom = '5px';
    label.style.fontFamily = 'Arial, sans-serif';
    label.style.fontSize = fontSize;
    label.style.color = '#333';

    // Cria o botão de lixeira
    trashButton = document.createElement('button');
    trashButton.innerHTML = '🗑️'; // Ícone de lixeira
    trashButton.style.border = 'none';
    trashButton.style.background = 'transparent';
    trashButton.style.cursor = 'pointer';
    trashButton.style.fontSize = fontSize;
    trashButton.style.marginLeft = '10px'; // Adiciona um espaçamento entre o label e a lixeira
    DisableTrashButton(); // Desabilita o botão de lixeira inicialmente
    function DisableTrashButton()
    {
        trashButton.style.cursor = 'not-allowed'; // Cursor indicando que está desabilitado
        trashButton.style.opacity = '0.5'; // Deixa o botão visualmente mais "fraco"
        trashButton.disabled = true; // Desabilita a interação do botão
    }
    function EnableTrashButton()
    {
        trashButton.disabled = false;
        trashButton.style.opacity = '1';
        trashButton.style.cursor = 'pointer';
    }

    // Adiciona um evento para limpar a lista ao clicar no botão de lixeira
    trashButton.addEventListener('click', () => {
        // document.getElementById('listaRotas').innerHTML = ''; // Limpa o select de rotas
        // LoadSelectPontos(selectRotas.value)
        if(selectRotas.value==0)
            return;

        // Obtém o ID selecionado
        const idSelecionado = parseInt(selectRotas.value, 10); // Converte para número inteiro base 10
        index = ListaRotasCalculadas.findIndex(item => item.id === idSelecionado); // Encontra o índice da rota selecionada
        // Se o item for encontrado, remove do array
        if (index !== -1) {
            ListaRotasCalculadas.splice(index, 1);
            console.log(`Item com ID ${idSelecionado} removido.`);
        } else {
            console.log(`Item com ID ${idSelecionado} não encontrado.`);
        }

        CarregaRotasCalculadas(0)
    });

    // Adiciona os elementos ao contêiner
    container.appendChild(label);
    container.appendChild(trashButton);

    // Adiciona o contêiner ao elemento pai
    iDlg.appendChild(container);


    //-----------------------------------------------------------------------------------
    // Cria a lista de rotas já calculadas 
    selectRotas = document.createElement('select');
    selectRotas.id = 'listaRotas';
    // select.multiple = true;
    selectRotas.size = 10000; // Define o número de itens visíveis
    selectRotas.style.width = '100%';
    selectRotas.style.height = '80px'; // Ocupa o espaço restante e retira os espaços para outros controles
    selectRotas.style.fontSize = fontSize;
    iDlg.appendChild(selectRotas);

    // ListaRotas Adiciona o evento 'change' ao select
    selectRotas.addEventListener('change', function () {
        console.log(`Valor selecionado: ${selectRotas.value}`);
        selectRotas.value==0 ? DisableTrashButton() : EnableTrashButton(); // Desabilita o botão de lixeira se rota selecionada for a 0
        LoadSelectPontos(selectRotas.value)
    });


    // Adicionando itens ao select
    function adicionarItemAoSelect(selectHandle,texto, valor) {
        let opcao = document.createElement('option'); // Cria o elemento <option>
        opcao.text = texto; // Define o texto visível da opção
        opcao.value = valor; // Define o valor da opção
        selectHandle.appendChild(opcao); // Adiciona a opção ao select
    }


    function CarregaRotasCalculadas(selIndex)
    {
        // Loop para varrer os itens
        // AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa
        selectRotas.innerHTML = ""; // Limpa todo o conteúdo do select
        for (let i = 0; i < ListaRotasCalculadas.length; i++) {
            let item = ListaRotasCalculadas[i];
            fmtDist = item.DistanceTotal.toFixed(2);
            adicionarItemAoSelect(selectRotas,`Rota #${item.id} - ${item.time} - ${fmtDist} km`, `${item.id}`);
            
            console.log(`Item ${i}:`);
            console.log(`ID: ${item.id}`);
            console.log(`Polyline: ${item.polylineRotaDat}`);
            console.log(`Pontos de Visita: ${item.pontosvisitaDados}`);
            console.log(`Ponto Inicial: ${item.pontoinicial}`);
            console.log(`Distância Total: ${item.DistanceTotal}`);
        }
        selectRotas.selectedIndex = selIndex;
    }

    CarregaRotasCalculadas(0);
    // rotaSel = ListaRotasCalculadas[0];
    rotaSel = structuredClone(ListaRotasCalculadas[0]); // Clona o objeto para evitar alterações indesejadas
    //-----------------------------------------------------------------------------------
    // Ponto Inicial
    label = document.createElement('label');
    label.htmlFor = 'listaRotas';
    label.textContent = 'Ponto Inicial:';
    label.style.marginTop = '5px';
    label.style.marginBottom = '5px';
    label.style.fontFamily = 'Arial, sans-serif';
    label.style.fontSize = fontSize;
    label.style.color = '#333';
    iDlg.appendChild(label);
     
    //-----------------------------------------------------------------------------------
    // Div com lat, lon e descrição 
    let divPai = document.createElement('div');
    divPai.style.width = '98%';
    divPai.style.display = 'flex';
    divPai.style.justifyContent = 'space-between';
    divPai.style.padding = '2px';
    divPai.style.border = '1px solid rgb(180, 179, 179)'; // A borda será de 2px, cor escura (pode ser ajustada conforme necessário)
    divPai.style.borderRadius = '2px'; // Opcional: bordas arredondadas
    
    // Função para criar uma div com label e input
    function criarDivComLabelInput(labelText, inputId, onChangeCallback) {
        let div = document.createElement('div');
        div.style.flex = '1';
        div.style.padding = '5px';
    
        let label = document.createElement('label');
        label.setAttribute('for', inputId);
        label.textContent = labelText;
        label.style.marginTop = '5px';
        label.style.marginBottom = '5px';
        label.style.fontFamily = 'Arial, sans-serif';
        label.style.fontSize = fontSize;
        label.style.color = '#333';
    
        let input = document.createElement('input');
        input.type = 'text';
        input.id = inputId;
        input.name = inputId;
        input.style.width = '90%';
        input.style.padding = '5px';
        input.style.fontFamily = 'Arial, sans-serif';
        input.style.fontSize = fontSize;
    
        // Adiciona o evento que chama a função passada como callback
        if (typeof onChangeCallback === 'function') {
            input.addEventListener('input', (event) => onChangeCallback(event.target.value));
        }
    
        div.appendChild(label);
        div.appendChild(input);
    
        return div;
    }

    // Adicionando as divs internas à div pai
    divPai.appendChild(criarDivComLabelInput('Latitude:', 'latitude',AlterouPntInicial));
    divPai.appendChild(criarDivComLabelInput('Longitude:', 'longitude',AlterouPntInicial));
    divPai.appendChild(criarDivComLabelInput('Descrição:', 'descricao'));    
    iDlg.appendChild(divPai);
 
    function AlterouPntInicial()
    {
        lat = document.getElementById('latitude');
        lon = document.getElementById('longitude');
        lat.value = lat.value.replace(/[^\d.,]/g, '');
        lon.value = lon.value.replace(/[^\d.,]/g, '');
        if(selectRotas.value!="nova")
        {
            ativaElementoHtml('listaPontos', false);
            adicionarItemAoSelect(selectRotas,`Nova Rota`, `nova`);
            selectRotas.value = "nova";
        }    

    }

    document.getElementById('latitude').value =  ListaRotasCalculadas[selectRotas.selectedIndex].pontoinicial[0];
    document.getElementById('longitude').value = ListaRotasCalculadas[selectRotas.selectedIndex].pontoinicial[1];
    document.getElementById('descricao').value = ListaRotasCalculadas[selectRotas.selectedIndex].pontoinicial[2];
    //----------------------------------------------------------------------------------- 
    // Label Ordem dos Pontos e os controles ao seu lado
    // novo label com div
    // Cria uma div para envolver o label e outros elementos
    div = document.createElement('div');
    div.style.display = 'flex'; // Habilita o Flexbox
    div.style.justifyContent = 'space-between'; // Espaça os itens entre si
    div.style.alignItems = 'center'; // Centraliza os itens verticalmente (opcional)
    div.style.marginBottom = '5px'; // Espaçamento externo inferior
    div.style.marginTop = '5px'; // Espaçamento externo inferior
    // Faz o div ocupar 100% do espaço disponível
    div.style.width = '100%'; // Largura total
    div.style.boxSizing = 'border-box'; // Garante que padding e borda sejam incluídos na largura total

    // Cria o label (alinhado à esquerda)
    label = document.createElement('label');
    label.htmlFor = 'listaPontos';
    label.textContent = 'Ordem dos pontos:';
    label.style.fontFamily = 'Arial, sans-serif';
    label.style.fontSize = fontSize;
    label.style.color = '#333';


    // Cria um wrapper para os elementos alinhados à direita
    const rightWrapper = document.createElement('div');
    rightWrapper.style.display = 'flex'; // Flexbox para os elementos da direita
    rightWrapper.style.justifyContent = 'flex-end'; // Garante o alinhamento à direita dentro do wrapper
    rightWrapper.style.gap = '5px'; // Espaçamento entre os itens da direita
    rightWrapper.style.flexGrow = '1'; // Faz o wrapper ocupar todo o espaço restante na linha

    // Exemplo de ícones clicáveis para as setas
    const upArrow = document.createElement('span');
    upArrow.textContent = '▲'; // Seta para cima
    upArrow.style.cursor = 'pointer'; // Define como clicável
    upArrow.style.fontSize = '14px'; // Ajusta o tamanho da seta
    upArrow.style.color = '#333'; // Cor da seta
    upArrow.style.marginRight = '0px'; // Espaçamento à direita (opcional)

    // Adiciona um evento de clique na seta para cima
    upArrow.addEventListener('click', () => {
        console.log('Seta acima clicada!');
        moveOption(-1)
    });

    const downArrow = document.createElement('span');
    downArrow.textContent = '▼'; // Seta para baixo
    downArrow.style.cursor = 'pointer'; // Define como clicável
    downArrow.style.fontSize = '14px'; // Ajusta o tamanho da seta
    downArrow.style.color = '#333'; // Cor da seta

    // Adiciona um evento de clique na seta para baixo
    downArrow.addEventListener('click', () => {
        console.log('Seta abaixo clicada!');
        moveOption(1)
    });

    // Adiciona os elementos ao wrapper da direita
    rightWrapper.appendChild(upArrow);
    rightWrapper.appendChild(downArrow);

    // Adiciona o label (esquerda) e o wrapper (direita) à div principal
    div.appendChild(label);
    div.appendChild(rightWrapper);

    // Adiciona a div ao elemento pai (iDlg)
    iDlg.appendChild(div);
    // Fim novo label com div
    //-----------------------------------------------------------------------------------
    // Lista Pontos  - Cria o controle de seleção múltipla
    const select = document.createElement('select');
    select.id = 'listaPontos';
    select.multiple = true;
    select.size = 10000; // Define o número de itens visíveis
    select.style.width = '100%';
    select.style.height = 'calc(100% - 250px)'; // Ocupa o espaço restante e retira os espaços para outros controles
    select.style.fontSize = fontSize;
    iDlg.appendChild(select);

    // Adiciona opções ao select dos pontos
    function LoadSelectPontos(value)
    {
        /*
            ListaRotasCalculadas[0].id
            ListaRotasCalculadas[0].time
            ListaRotasCalculadas[0].polylineRotaDat
            ListaRotasCalculadas[0].pontosvisitaDados
            ListaRotasCalculadas[0].pontosVisitaOrdenados
            ListaRotasCalculadas[0].pontoinicial
            ListaRotasCalculadas[0].DistanceTotal
        */   
        selId = parseInt(value); // Converte para número, se necessário
        if(selId==NaN)
        {
            console.log(`Valor selId selecionado: ${selId} sem carregar rotas`);
            return;
        }
        console.log(`Valor selId selecionado: ${selId}`);

        const rotaSelecionada = ListaRotasCalculadas.find(rota => rota.id === selId);
        rotaSel = structuredClone(rotaSelecionada);

        console.log(`LoadSelectPontos: rotaSel.pontoinicial ${rotaSel.pontoinicial[0]}, ${rotaSel.pontoinicial[1]}, ${rotaSel.pontoinicial[2]}`);
        select.innerHTML = '';
        rotaSel.pontosVisitaOrdenados.forEach((ponto, index) => {
            const [latitude, longitude] = ponto;
            const option = document.createElement('option');
            option.value = `${latitude},${longitude}`;
            //  [2.803887, -60.691666,"P0","Local", "Hospital Materno Infantil – Bairro 13 de Setembro","0","Ativo"],
            //ponto = EncontrarDado(rotaSel.pontosvisitaDados, latitude, longitude,2);
            ponto = `P${index}`;
            desc = EncontrarDado(rotaSel.pontosvisitaDados, latitude, longitude,4);
            if(desc == "")
                option.textContent = ponto;
            else 
                option.textContent = ponto+"  - "+desc;            
            select.appendChild(option);
        });    
        // Atualiza dados ponto inicial
        document.getElementById('latitude').value =  rotaSel.pontoinicial[0];
        document.getElementById('longitude').value = rotaSel.pontoinicial[1];
        document.getElementById('descricao').value = rotaSel.pontoinicial[2];
        ReordenaPontosTela(rotaSel);
        poly_lineRota = RedesenhaRota(rotaSel.polylineRotaDat,rotaSel);

    }
    LoadSelectPontos(0);

    // Cria os botões
    const buttonsContainer = document.createElement('div');
    buttonsContainer.style.position = 'absolute';
    buttonsContainer.style.bottom = '10px';
    buttonsContainer.style.left = '10px';
    buttonsContainer.style.right = '10px';
    buttonsContainer.style.display = 'flex'; // Flex para alinhar os botões horizontalmente
    buttonsContainer.style.justifyContent = 'flex-end'; // Alinha os itens ao lado direito
    buttonsContainer.style.gap = '5px'; // Espaçamento entre os botões

    const reordenaBtn = createButton('Recalcula Rota', () => reordenaOption());
    buttonsContainer.appendChild(reordenaBtn);
    iDlg.appendChild(buttonsContainer);

    // Função auxiliar para criar botões
    function createButton(text, onClick) {
        const button = document.createElement('button');
        button.textContent = text;
        button.style.padding = '4px 16px';
        button.style.cursor = 'pointer';
        button.style.fontSize = fontSize;
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
            //Pn = option.textContent.split(" ")[0]; // Pega o texto antes do primeiro espaço;
            [lat, lon] = option.value.split(',').map(Number); // Converte de volta para números
            // lat = EncontrarDadoPn(pontosvisitaDados, Pn,0)
            // lon = EncontrarDadoPn(pontosvisitaDados, Pn,1)
            pontosVisitaNew.push([lat, lon]);
        });
        pontosVisitaOrdenados = pontosVisitaNew;
        //  Pegar algoritmo de ordenação selecionado
        // selecionado = selectAlgoOrdenacao.value; // Obtém o valor selecionado
        // console.log("Algoritmo de ordenação selecionado:", selecionado);
        rotaSel.pontoinicial[0] = document.getElementById('latitude').value;
        rotaSel.pontoinicial[1] = document.getElementById('longitude').value;
        rotaSel.pontoinicial[2] = document.getElementById('descricao').value;

        ListaRotasCalculadas.forEach((rota, index) => {
            console.log(`🔹 Rota ${index}:`);
            console.log(`   ID: ${rota.id}`);
            console.log(`   Tempo: ${rota.time}`);
            console.log(`   Polyline: ${rota.polylineRotaDat}`);
            console.log(`   Pontos de Visita:`, rota.pontosvisitaDados);
            console.log(`   Ponto Inicial: ${rota.pontoinicial}`);
            console.log(`   Distância Total: ${rota.DistanceTotal} km`);
        });

        ReordenaPontosTela(rotaSel);
        // data = await RefazRotaNoServidor(pontosVisitaOrdenados);
        // usar aqui rotaSel 
        // RefazRotaNoServidor(pontosVisitaOrdenados).then(data => 
        RefazRotaNoServidor(pontosVisitaOrdenados,rotaSel).then(data =>     
        {
            console.log("Rota refeita com sucesso!", data);
            /*
            ListaRotasCalculadas[0].id
            ListaRotasCalculadas[0].time
            ListaRotasCalculadas[0].polylineRotaDat
            ListaRotasCalculadas[0].pontosvisitaDados
            ListaRotasCalculadas[0].pontosVisitaOrdenados
            ListaRotasCalculadas[0].pontoinicial
            ListaRotasCalculadas[0].DistanceTotal
            */

            pntinicialBuf = [];
            pntinicialBuf[0] = document.getElementById('latitude').value;
            pntinicialBuf[1] = document.getElementById('longitude').value;
            pntinicialBuf[2] = document.getElementById('descricao').value;

            maiorId = ListaRotasCalculadas.reduce((max, item) => {return item.id > max ? item.id : max;}, 0);
            bufdados = {};
            bufdados.id = maiorId+1; // ID da nova rota
            bufdados.time = getFormattedTimestamp();
            bufdados.polylineRotaDat = polylineRotaDat;
            bufdados.pontosvisitaDados = pontosvisitaDados;
            bufdados.pontosVisitaOrdenados = pontosVisitaOrdenados;
            bufdados.pontoinicial = pntinicialBuf;
            bufdados.DistanceTotal = data.DistanceTotal/1000;
            ListaRotasCalculadas.push(bufdados);
            rotaSel=bufdados;
            CarregaRotasCalculadas(bufdados.id);
            LoadSelectPontos(bufdados.id);    
        }).catch(error => {
            console.error("Erro ao refazer rota:", error);
        });
    }
    ////////////////////////////////
    function GetServerUrl()
    {
        if ( window.location.hostname=="127.0.0.1")
        {
                //  sem ngrock
                serverUrl = `${window.location.protocol}//${window.location.hostname}`;
                url = `${serverUrl}:5001`
        }
        else
        {
                //  no ngrock
                serverUrl = `${window.location.protocol}//${window.location.hostname}`;
                url = `${serverUrl}`
        }
        return(url);
    }
    ////////////////////////////////
    async function RefazRotaNoServidor(pontosVisita,rotaSel)
    {
        IhandleMsg=exibirMensagem('Servidor calculando a nova rota');

        const payload = {
            TipoRequisicao: "RoteamentoOSMR",
            PortaOSRMServer: OSRMPort,
            pontosvisita: pontosVisita,
            pontoinicial: rotaSel.pontoinicial
        };
         
        url = GetServerUrl()+ "/webrotas";

        try {
            // Espera a resposta da função enviarJson
            data = await enviarJson(payload, url);
            // Manipula a resposta
            console.log("Resposta recebida:", data);
            if(data==undefined)
            {
                console.error("Erro ao processar a requisição:", data);
                exibirMensagemComTimeout('Erro ao processar a requisição', 5000);
                document.body.removeChild(IhandleMsg);
                return;
            }
        } catch (error) {
            console.error("Erro ao processar a requisição:", error);
            document.body.removeChild(IhandleMsg);
            return;
        }

        polylineRotaDat = data.polylineRota;
        DistanceTotal = data.DistanceTotal;
        poly_lineRota = RedesenhaRota(polylineRotaDat,rotaSel);
        
        document.body.removeChild(IhandleMsg);
        return data;
    }
    ////////////////////////////////
    function RedesenhaRota(polylineRotaDat,rotaSel)
    {
        lat=rotaSel.pontoinicial[0];
        lon=rotaSel.pontoinicial[1];
        desc=rotaSel.pontoinicial[2];
        console.log(`RedesenhaRota - Ponto - Inicial lat ${lat}, lon ${lon}, desc - ${desc}`);

        if(mrkPtInicial)
        {
            mrkPtInicial.remove();
            mrkPtInicial = null;
        }

        mrkPtInicial = L.marker([lat, lon]).addTo(map).setIcon(createSvgIconColorAltitude('i',10000));     
        mrkPtInicial.bindTooltip(desc, {permanent: false,direction: 'top',offset: [0, -60],className:'custom-tooltip'});  
        
        if(poly_lineRota)
        {
            poly_lineRota.remove();
            poly_lineRota = null;
        }  
        console.log(`Redesenhando  poly_lineRota`);
        poly_lineRota = L.polyline(polylineRotaDat, {
            "bubblingMouseEvents": true,"color": "blue","dashArray": null,"dashOffset": null,
            "fill": false,"fillColor": "blue","fillOpacity": 0.2,"fillRule": "evenodd","lineCap": "round",
            "lineJoin": "round","noClip": false,"opacity": 0.7,"smoothFactor": 1.0,"stroke": true,
            "weight": 3}).addTo(map);    
        return poly_lineRota;     
    }
    ////////////////////////////////
    // Função para mover opções na lista
    /*
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
    */
    function moveOption(direction) {
        const options = Array.from(select.options);
        const selectedOptions = options.filter(option => option.selected);
    
        if (selectedOptions.length === 0) return; // Nenhuma opção selecionada
    
        const increment = direction > 0 ? 1 : -1;
    
        // Para mover para baixo, iteramos do final para o início
        // Para mover para cima, iteramos do início para o final
        const sortedOptions = direction > 0 ? selectedOptions.reverse() : selectedOptions;
    
        sortedOptions.forEach(option => {
            const index = options.indexOf(option);
            const newIndex = index + increment;
    
            // Verificar limites
            if (newIndex < 0 || newIndex >= options.length) return;
    
            // Trocar posição dos elementos
            [options[index], options[newIndex]] = [options[newIndex], options[index]];
        });
    
        // Reaplica a ordem na lista
        select.innerHTML = "";
        options.forEach(option => select.appendChild(option));
    
        // Re-seleciona os itens movidos
        selectedOptions.forEach(option => option.selected = true);
    }
}
// Fim Dialogo de ordenação de pontos
//////////////////////////////////////////////////////////////////////////////////////////////////////
