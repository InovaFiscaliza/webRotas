//////////////////////////////////////////////////////////////////////////////////////////////////////
// Dialogo de ordenação de pontos
fontSize = '10px';   // Tamanho da fonte
clicouPipetaPontoInicial=false; // Flag para indicar que clicou na pipeta
var arrayPnts = null;
var arrayLinhas = null;
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
    /*
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
    */
    // Adiciona os elementos ao contêiner
    container.appendChild(label);
    // container.appendChild(trashButton);

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
        selectRotas.innerHTML = ""; // Limpa todo o conteúdo do select
        for (let i = 0; i < ListaRotasCalculadas.length; i++) {
            let item = ListaRotasCalculadas[i];
            fmtDist = item.DistanceTotal.toFixed(2);  
            if(item.rotaCalculada==0) // Rota não calculada, proposta pelo usuário
                adicionarItemAoSelect(selectRotas,`Rota #${item.id} - ${item.time} - ${fmtDist} km`, `${item.id}`);
            else
                adicionarItemAoSelect(selectRotas,`Rota #${item.id} - ${item.time} - ${fmtDist} km - Calculada`, `${item.id}`);    
            
            console.log(`Item ${i}:`);
            console.log(`ID: ${item.id}`);
            console.log(`Polyline: ${item.polylineRotaDat}`);
            console.log(`Pontos de Visita: ${item.pontosvisitaDados}`);
            console.log(`Ponto Inicial: ${item.pontoinicial}`);
            console.log(`Distância Total: ${item.DistanceTotal}`);
        }
        selectRotas.selectedIndex = selIndex;
        AtivaControles();
        ativaElementoHtml('idPontoInicial', true); 
        ativaElementoHtml('listaRotas', true); 
    }

    CarregaRotasCalculadas(0);
    // rotaSel = ListaRotasCalculadas[0];
    rotaSel = structuredClone(ListaRotasCalculadas[0]); // Clona o objeto para evitar alterações indesejadas
    //-----------------------------------------------------------------------------------
    // Ponto Inicial
    // Criando o contêiner principal
    container = document.createElement('div');
    container.style.display = 'flex';
    container.style.alignItems = 'center';
    container.style.justifyContent = 'space-between';
    container.style.width = '100%'; // Largura ajustável
    container.style.padding = '0px';
    container.style.paddingTop = '5px'; // Adiciona espaçamento no topo
    container.style.marginBottom = '5px'; // Adiciona espaçamento na parte inferior
    container.style.fontFamily = 'Arial, sans-serif';

    // Criando o label
    label = document.createElement('label');
    label.htmlFor = 'listaRotas';
    label.textContent = 'Ponto Inicial:';
    label.style.fontSize = fontSize;
    label.style.color = '#333';

    // Criando a letra "P"
    letterP = document.createElement('span');
    letterP.textContent = '🧪';
    letterP.id = 'idPipetaLatLon';
    letterP.style.fontSize = '16px';
    letterP.style.color = '#555';
    letterP.style.fontWeight = 'bold';
    letterP.style.marginLeft = '10px';
    letterP.style.cursor = 'pointer'; // Transforma em clicável
    // Adicionando evento de clique
    letterP.addEventListener('click', function() {
        // alert('Você clicou na pipeta! 🧪');
        clicouPipetaPontoInicial=true;
        ativaElementoHtml('idPipetaLatLon', false); 
    });

    // Adicionando elementos ao contêiner
    container.appendChild(label);
    container.appendChild(letterP);

    // Adicionando o contêiner ao corpo do documento
    iDlg.appendChild(container);

    /*
    label = document.createElement('label');
    label.htmlFor = 'listaRotas';
    label.textContent = 'Ponto Inicial:';
    label.style.marginTop = '5px';
    label.style.marginBottom = '5px';
    label.style.fontFamily = 'Arial, sans-serif';
    label.style.fontSize = fontSize;
    label.style.color = '#333';
    iDlg.appendChild(label);
    */ 
    //-----------------------------------------------------------------------------------
    // Div ponto inicial com lat, lon e descrição 
    let divPai = document.createElement('div');
    divPai.style.width = '98%';
    divPai.id = 'idPontoInicial';
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
    //-----------------------------------------------------------------------------------
    // Alterou ponto inicial
    recalcularRotaPontoInicial = false;

    function AlterouPntInicial()
    {
        recalcularRotaPontoInicial = true;
        lat = document.getElementById('latitude');
        lon = document.getElementById('longitude');
        lat.value = lat.value.replace(/[^\d.,-]/g, '');
        lon.value = lon.value.replace(/[^\d.,-]/g, '');
        if(selectRotas.value!="nova")
        {
            DesativaControles()
            adicionarItemAoSelect(selectRotas,`Nova Rota`, `nova`);
            selectRotas.value = "nova";
        }    
    }
    function DesativaControles()     
    {
        ativaElementoHtml('listaRotas', false); 
        ativaElementoHtml('divOrdemPontos', false);
        ativaElementoHtml('listaPontos', false);
    }
    function AtivaControles()
    {
        ativaElementoHtml('listaRotas', true); 
        ativaElementoHtml('divOrdemPontos', true);
        ativaElementoHtml('listaPontos', true);
    }
    //-----------------------------------------------------------------------------------
    document.getElementById('latitude').value =  ListaRotasCalculadas[selectRotas.selectedIndex].pontoinicial[0];
    document.getElementById('longitude').value = ListaRotasCalculadas[selectRotas.selectedIndex].pontoinicial[1];
    document.getElementById('descricao').value = ListaRotasCalculadas[selectRotas.selectedIndex].pontoinicial[2];
    //----------------------------------------------------------------------------------- 
    // Label Ordem dos Pontos e os controles ao seu lado
    // novo label com div
    // Cria uma div para envolver o label e outros elementos
    div = document.createElement('div');
    div.style.display = 'flex'; // Habilita o Flexbox
    div.id = 'divOrdemPontos';
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
    upArrow.id = 'idSetaParaCima';  
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
    downArrow.id = 'idSetaParaBaixo';  
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
    select.style.height = 'calc(100% - 260px)'; // Ocupa o espaço restante e retira os espaços para outros controles
    select.style.fontSize = fontSize;
    iDlg.appendChild(select);
    bMudouOrdemPontos = false;
    // Adiciona um event listener para monitorar mudanças
    select.addEventListener("change", function () {
        bMudouOrdemPontos = true;
        recalcularRotaPontoInicial = false;
        ativaElementoHtml('idPontoInicial', false); 
        if(selectRotas.value!="nova")
        {
            ativaElementoHtml('listaRotas', false); 
            adicionarItemAoSelect(selectRotas,`Nova Rota`, `nova`);
            selectRotas.value = "nova";
        }    
    });    

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
            ListaRotasCalculadas[0].rotaCalculada
        */   
        selId = parseInt(value); // Converte para número, se necessário
        if(selId==NaN)
        {
            console.log(`Valor selId selecionado: ${selId} sem carregar rotas`);
            return;
        }
        console.log(`Valor selId selecionado: ${selId}`);

        const rotaSelecionada = ListaRotasCalculadas.find(rota => rota.id === selId);
        rotaSel = [];
        rotaSel = structuredClone(rotaSelecionada);
        
        pontosvisitaDados = rotaSel.pontosvisitaDados;
        pontosVisitaOrdenados = rotaSel.pontosVisitaOrdenados;
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
    // buttonsContainer.style.justifyContent = 'flex-end'; // Alinha os itens ao lado direito
    buttonsContainer.style.justifyContent = 'space-between'; // Alinha os botões nas extremidades
    buttonsContainer.style.gap = '5px'; // Espaçamento entre os botões

    const apagaRotaBtn = createButton('Apaga Rota', () => BtnApagaRota());
    buttonsContainer.appendChild(apagaRotaBtn);

    const reordenaBtn = createButton('Recalcula Rota', () => reordenaOption());
    buttonsContainer.appendChild(reordenaBtn);
    iDlg.appendChild(buttonsContainer);

    // Adiciona um evento para limpar a lista ao clicar no botão de lixeira
    function BtnApagaRota()
    {
        // document.getElementById('listaRotas').innerHTML = ''; // Limpa o select de rotas
        // LoadSelectPontos(selectRotas.value)
        if (selectRotas.options.length <= 1) {
            return; // Sai da função se houver apenas 1 ou nenhum item
        }

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
    }


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
            console.log(`   rotaCalculada: ${rota.rotaCalculada} `);
        });

        ReordenaPontosTela(rotaSel);
        // data = await RefazRotaNoServidor(pontosVisitaOrdenados);
        // usar aqui rotaSel 
        // RefazRotaNoServidor(pontosVisitaOrdenados).then(data => 
         
        // Faz de forma sincrona a função assincrona    
        tornarElementosReadonly()
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
            ListaRotasCalculadas[0].rotaCalculada
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
            if(bMudouOrdemPontos)
                bufdados.rotaCalculada = 0; // Rota proposta pelo usuário
            else
                bufdados.rotaCalculada = 1; // Rota calculada pelo servidor      
            ListaRotasCalculadas.push(bufdados);
            rotaSel=bufdados;

            
            CarregaRotasCalculadas(bufdados.id);
            LoadSelectPontos(bufdados.id);  
            AtivaControles();  
            ativaElementoHtml('idPontoInicial', true); 
            ativaElementoHtml('listaRotas', true); 
            bMudouOrdemPontos = false;
            desfazerReadonly();
        }).catch(error => {
            console.error("Erro ao refazer rota:", error);
        });
    }
    ////////////////////////////////
    function tornarElementosReadonly() {
        ativaElementoHtml('idSetaParaBaixo', false); 
        ativaElementoHtml('idSetaParaCima', false); 
        const divOrdenaPontos = document.getElementById('divOrdenaPontos');
        
        if (divOrdenaPontos) {
            // Percorre todos os inputs e selects dentro da div e os torna readonly ou desativados
            divOrdenaPontos.querySelectorAll('input, textarea, select, button').forEach(elemento => {
                if (elemento.tagName === 'INPUT' || elemento.tagName === 'TEXTAREA') {
                    elemento.readOnly = true; // Torna o campo de texto somente leitura
                } else {
                    elemento.disabled = true; // Desabilita outros elementos como selects e botões
                }
            });
        } else {
            console.warn("Elemento 'divOrdenaPontos' não encontrado.");
        }
    }
    ////////////////////////////////
    function desfazerReadonly() {
        ativaElementoHtml('idSetaParaBaixo', true); 
        ativaElementoHtml('idSetaParaCima', true); 
        const divOrdenaPontos = document.getElementById('divOrdenaPontos');
    
        if (divOrdenaPontos) {
            divOrdenaPontos.querySelectorAll('input, textarea, select, button').forEach(elemento => {
                if (elemento.tagName === 'INPUT' || elemento.tagName === 'TEXTAREA') {
                    elemento.readOnly = false; // Permite edição
                } else {
                    elemento.disabled = false; // Reativa selects e botões
                }
            });
        } else {
            console.warn("Elemento 'divOrdenaPontos' não encontrado.");
        }
    }
    ////////////////////////////////
    // Atualiza váriável global do JS, onde estão várias informações dos pontos, com a nova ordenação dos pontos
    function SincOrdenadosPontosVisitaDados(pontosVisitaOrdenados,pontosvisitaDados)
    {
        i=0;
        pontosVisitaOrdenados.forEach(([lat, lon]) => {
            sPn = `P${i}`; 
            // AtualizaPontosvisitaDados(pontosvisitaDados,lat, lon,ColunaAtualizar,NovoDado)
            AtualizaPontosvisitaDados(pontosvisitaDados,lat, lon,2,sPn); // Atualiza Pn
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
    rotaRecalculada=0;  // Flag deste diálogo que indica se ondem de pontos foi recalculada no servidor
    async function RefazRotaNoServidor(pontosVisita,rotaSel)
    {
        IhandleMsg=exibirMensagem('Servidor calculando a nova rota');
        if(recalcularRotaPontoInicial)
            recalcularrota=1;
        else
            recalcularrota=0;
        
        const payload = {
            TipoRequisicao: "RoteamentoOSMR",
            PortaOSRMServer: OSRMPort,
            pontosvisita: pontosVisita,
            pontoinicial: rotaSel.pontoinicial,
            recalcularrota: recalcularrota
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
        // Guardando dados para uso posterior e atualizando as variáveis globais da rota
        polylineRotaDat = data.polylineRota;
        DistanceTotal = data.DistanceTotal;
        poly_lineRota = RedesenhaRota(polylineRotaDat,rotaSel);
        rotaRecalculada = data.RotaRecalculada; 
        pontosVisitaOrdenados = data.pontosVisita
        SincOrdenadosPontosVisitaDados(pontosVisitaOrdenados,pontosvisitaDados);
        
        document.body.removeChild(IhandleMsg);
        return data;
    }
    ////////////////////////////////
    function haversine(lat1, lon1, lat2, lon2) {
        const R = 6371e3; // Raio da Terra em metros
        const toRad = Math.PI / 180;
        const dLat = (lat2 - lat1) * toRad;
        const dLon = (lon2 - lon1) * toRad;
    
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                  Math.cos(lat1 * toRad) * Math.cos(lat2 * toRad) *
                  Math.sin(dLon / 2) * Math.sin(dLon / 2);
    
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c; // Distância em metros
    }
    ////////////////////////////////
    function filtrarTrechosMenoresQue5km(polylineRotaDat) {
        if (polylineRotaDat.length < 2) return polylineRotaDat; // Se tiver menos de 2 pontos, retorna como está
    
        let novaRota = [polylineRotaDat[0]]; // Sempre mantemos o primeiro ponto
    
        for (let i = 1; i < polylineRotaDat.length; i++) {
            const [lat1, lon1] = novaRota[novaRota.length - 1];
            const [lat2, lon2] = polylineRotaDat[i];
    
            if (haversine(lat1, lon1, lat2, lon2) <= 5000) {
                novaRota.push([lat2, lon2]);
            }
        }
        return novaRota;
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
        
        for (let i = 0; i < poly_lineRota.length; i++) 
        {
            poly_lineRota[i].remove();
        }  
        poly_lineRota = [];

        // console.log(`Redesenhando  poly_lineRota`);
        // console.log(polylineRotaDat);
        // Remove o último ponto da polyline, se houver pontos suficientes
        const numeroDePontos = polylineRotaDat.length;
        console.log(`Número de pontos na polyline: ${numeroDePontos}`);
        console.log(`polylineRotaDat[0]: ${polylineRotaDat[0]}`);

        // polylineRotaDat = filtrarTrechosMenoresQue5km(polylineRotaDat);
        if(polylineRotaDat[0].length==2)
            return  poly_lineRota;  

        for (let i = 0; i < polylineRotaDat.length; i++) 
        {    
            tempBuf = L.polyline(polylineRotaDat[i], {
                "bubblingMouseEvents": true,"color": "blue","dashArray": null,"dashOffset": null,
                "fill": false,"fillColor": "blue","fillOpacity": 0.2,"fillRule": "evenodd","lineCap": "round",
                "lineJoin": "round","noClip": false,"opacity": 0.7,"smoothFactor": 1.0,"stroke": true,
                "weight": 3}).addTo(map);

            poly_lineRota.push(tempBuf);    
        }
     
        // Exibir Lat/Lon ao clicar na Polyline
        /*
        poly_lineRota.on('click', function () {
            let coords = poly_lineRota.getLatLngs(); // Obtém as coordenadas
            let coordText = coords.map(c => `${c.lat},${c.lng}`).join('\n');
            
            alert("Coordenadas da Polyline:\n" + coordText);
            console.log(coords); // Exibe no console também
        });   
        */ 
        // clearPlottedPoints(arrayPnts, map); 
        // removLines(arrayLinhas);
        // arrayPnts = plotPolylineAsPoints(map, polylineRotaDat, color = 'red')
        return poly_lineRota;     
    }

    function plotPolylineAsPoints(map, polylineCoords, color = 'blue') {
        // Inicializar o array para armazenar os pontos e as linhas
        let ind = 0;
        let arrayPnts = [];
        let arrayLinhas = [];

        // Percorrer os pontos e criar uma linha entre cada dupla de pontos consecutivos
        for (let i = 0; i < polylineCoords.length - 1; i++) {
            // Criar uma linha azul entre os pontos consecutivos
            let line = L.polyline([polylineCoords[i], polylineCoords[i + 1]], {
                color: color,   // Cor da linha
                weight: 2,      // Espessura da linha
                opacity: 0.7    // Opacidade da linha
            }).addTo(map);
            
            // Criar um marcador circular no ponto atual
            let point = L.circleMarker(polylineCoords[i], {
                radius: 5, // Tamanho do ponto
                color: 'red', // Cor da borda
                fillColor: 'yellow', // Cor interna
                fillOpacity: 0.8
            })
            .bindTooltip(`Ind: ${ind} Lat: ${polylineCoords[i][0]}, Lng: ${polylineCoords[i][1]}`, {
                permanent: false,  // Apenas ao passar o mouse
                direction: 'top',  // Posição do tooltip
                offset: [0, -5]    // Ajuste fino da posição
            })
            .addTo(map);
            
            arrayLinhas.push(line);
            arrayPnts.push(point);
            ind++;
        }
        
        return arrayPnts;
    }
    

    function plotPolylineAsPointsOld(map, polylineCoords, color = 'blue') {
        // Criar a polyline no mapa

        // Percorrer cada ponto da polyline e criar um marcador circular com tooltip
        ind = 0;
        arrayPnts = [];
        polylineCoords.forEach(coord => {

            let line = L.polyline([polylineCoords[i], polylineCoords[i + 1]], {
                color: color,   // Cor da linha
                weight: 2,      // Espessura da linha
                opacity: 0.7    // Opacidade da linha
            }).addTo(map);

            point = L.circleMarker(coord, {
                radius: 5, // Tamanho do ponto
                color: 'red', // Cor da borda
                fillColor: 'yellow', // Cor interna
                fillOpacity: 0.8
            })
            .bindTooltip(`Ind: ${ind} Lat: ${coord[0]}, Lng: ${coord[1]}`, {
                permanent: false,  // Apenas ao passar o mouse
                direction: 'top',  // Posição do tooltip
                offset: [0, -5]    // Ajuste fino da posição
            })
            .addTo(map);
            arrayPnts.push(point);
            ind++;
        });
        return arrayPnts;
    }
  
    function removLines(linesArray) 
    {
        if(linesArray==null)
            return;
        // Percorrer o array de linhas e remover cada linha do mapa
        linesArray.forEach(line => {
            line.remove();  // Remove a linha do mapa
        });
    }

    function clearPlottedPoints(arrayPnts, map) {
        if (arrayPnts) {
            arrayPnts.forEach(point => map.removeLayer(point)); // Remove cada ponto do mapa
            arrayPnts.length = 0; // Limpa o array
        }
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
