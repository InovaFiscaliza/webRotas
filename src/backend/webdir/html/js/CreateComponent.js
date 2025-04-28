(function() {
    class CreateComponent {
        /*-----------------------------------------------------------------------------------
            ## MAPA ##
        -----------------------------------------------------------------------------------*/
        static document() {
            const { center, zoom } = window.app.mapContext.settings.position;
            const basemapList      = window.app.mapContext.layers.basemap;
            const basemapSelection = window.app.mapContext.settings.basemap;

            const map = window.L.map('document', { 
                zoomControl: false 
            }).setView(center, zoom);

            basemapList[basemapSelection].addTo(map);
            window.L.control.scale().addTo(map);

            window.app.map = map;
        }

        /*-----------------------------------------------------------------------------------
            ## PAINEL À ESQUERDA DO MAPA ##

            A organização do estilo dos componentes é agrupado nas categorias:
            - Layout pai    : gridArea
            - Layout interno: display, flexDirection, alignItems, justifyContent, gridTemplateRows, gridTemplateColumns, overflow etc;
            - Dimensão      : width, height, minWidth, minHeight etc;
            - Espaçamento   : margin, padding, gap etc; e
            - Visual        : backgroundColor, border, boxShadow, color, fontSize etc.
        -----------------------------------------------------------------------------------*/
        static leftPanel() {
            // <GRID PRINCIPAL>
            const panel = window.document.getElementById('left-panel');
            ['left-panel-on', 'grid'].forEach(className => {
                panel.classList.add(className);
            });
            Object.assign(panel.style, { gridTemplateRows: '26px 22px minmax(0px, 1fr) 22px 115px 22px minmax(0px, 1fr)', gridTemplateColumns: 'minmax(0px, 1fr)'
            });

            // TÍTULO
            this.createTitle('icon+text+line', {
                gridArea: '1 / 1 / 2 / 2',
                iconPath: 'images/route.svg', 
                textContent: 'webRotas'                
            }, panel)

            // ROTAS - LABEL E CONTROLES
            const routeListTitleGrid = this.createElement('div', {
                classList: ['grid'],
                style: { gridArea: '2 / 1 / 3 / 2', gridTemplateRows: '22px', gridTemplateColumns: 'minmax(0px, 1fr) 18px 18px 18px', padding: '0px', columnGap: '5px', overflow: 'visible' }
            }, panel);

                // <SUB-GRID>
                this.createElement('label', {
                    classList: ['title-label'],
                    style: { gridArea: '1 / 1 / 2 / 2' },
                    textContent: 'Rotas:'
                }, routeListTitleGrid);

                this.createElement('img', {
                    classList: ['title-button'],
                    id: 'routeListEditModeBtn',
                    src: 'images/Edit_32.png',
                    style: { gridArea: '1 / 2 / 2 / 3', width: '18px', height: '18px' },
                    eventListeners: {
                        click: (event) => onRouteListChange(event)
                    },
                    disabled: true,
                    dataset: { value: 'off', tooltip: 'Habilita modo de edição' }
                }, routeListTitleGrid);

                this.createElement('img', {
                    classList: ['title-button', 'disabled'],
                    id: 'routeListConfirmBtn',
                    src: 'images/Ok_32Green.png',
                    style: { gridArea: '1 / 3 / 2 / 4', width: '18px', height: '18px' },
                    eventListeners: {
                        click: (event) => onRouteListChange(event)
                    },
                    dataset: { tooltip: 'Habilita modo de edição' }
                }, routeListTitleGrid);

                this.createElement('img', {
                    classList: ['title-button', 'disabled'],
                    id: 'routeListCancelBtn',
                    src: 'images/Delete_32Red.png',
                    style: { gridArea: '1 / 4 / 2 / 5', width: '18px', height: '18px' },
                    eventListeners: {
                        click: (event) => onRouteListChange(event)
                    },
                    dataset: { tooltip: 'Habilita modo de edição' }
                }, routeListTitleGrid);
                // </SUB-GRID>
        
            // ROTAS - ÁRVORE
            this.createElement('ul', {
                classList: ['text-list'],
                id: 'routeList',
                style: { gridArea: '3 / 1 / 4 / 2' }
            }, panel);
        
            // PONTO INICIAL - LABEL E CONTROLES
            const initialPointTitleGrid = this.createElement('div', {
                classList: ['grid'],
                style: { gridArea: '4 / 1 / 5 / 2', gridTemplateRows: '22px', gridTemplateColumns: 'minmax(0px, 1fr) 18px', padding: '0px', overflow: 'visible' }
            }, panel);

                // <SUB-GRID>
                this.createElement('label', {
                    classList: ['title-label'],
                    style: { gridArea: '1 / 1 / 2 / 2' },
                    textContent: 'Ponto inicial:'
                }, initialPointTitleGrid);
            
                this.createElement('img', {
                    classList: ['title-button', 'disabled'],
                    id: 'initialPointButton',
                    src: 'images/pin_18.png',
                    style: { gridArea: '1 / 2 / 2 / 3' }
                }, initialPointTitleGrid);
                // </SUB-GRID>
        
            // PONTO INICIAL - LATITUDE, LONGITUDE E DESCRIÇÃO
            const initialPointGrid = this.createElement('div', {
                classList: ['grid', 'grid-border'],
                style: { gridArea: '5 / 1 / 6 / 2', gridTemplateRows: '17px 22px 17px 22px', gridTemplateColumns: 'minmax(0px, 1fr) minmax(0px, 1fr)', padding: '10px' }
            });
            panel.appendChild(initialPointGrid);

                // <SUB-GRID>
                this.createElement('label', {
                    classList: ['sublabel'],
                    htmlFor: 'initialPointLatitude',
                    style: { gridArea: '1 / 1 / 2 / 2' },
                    textContent: 'Latitude:'
                }, initialPointGrid);
            
                const initialPointLatitude = this.createElement('input', {
                    classList: ['no-spinner'],
                    id: 'initialPointLatitude',
                    type: 'number',
                    min: '-90',
                    max: '90',
                    style: { gridArea: '2 / 1 / 3 / 2' },
                    eventListeners: {
                        input: () => window.app.modules.Callback.addEventListener(initialPointLatitude, 'input:numeric:range-validation')
                    },
                    disabled: true
                }, initialPointGrid);
            
                this.createElement('label', {
                    classList: ['sublabel'],
                    htmlFor: 'initialPointLongitude',
                    style: { gridArea: '1 / 2 / 2 / 3' },
                    textContent: 'Longitude:'
                }, initialPointGrid);
            
                const initialPointLongitude = this.createElement('input', {
                    classList: ['no-spinner'],
                    id: 'initialPointLongitude',
                    type: 'number',
                    min: '-180',
                    max: '180',
                    style: { gridArea: '2 / 2 / 3 / 3' },
                    eventListeners: {
                        input: () => window.app.modules.Callback.addEventListener(initialPointLongitude, 'input:numeric:range-validation')
                    },
                    disabled: true
                }, initialPointGrid);
            
                this.createElement('label', {
                    classList: ['sublabel'],
                    htmlFor: 'initialPointDescription',
                    style: { gridArea: '3 / 1 / 4 / 2' },
                    textContent: 'Descrição:'
                }, initialPointGrid);
            
                this.createElement('input', {
                    id: 'initialPointDescription',
                    type: 'text',
                    style: { gridArea: '4 / 1 / 5 / 3' },
                    disabled: true
                }, initialPointGrid);
                // </SUB-GRID>

            // PONTO A VISITAR - LABEL E CONTROLES
            const pointsToVisitTitleGrid = this.createElement('div', {
                classList: ['grid'],
                style: { gridArea: '6 / 1 / 7 / 2', display: 'grid', gridTemplateRows: '22px', gridTemplateColumns: 'minmax(0px, 1fr) 18px 18px', padding: '0px', columnGap: '5px', overflow: 'visible' }
            }, panel);

                // <SUB-GRID>        
                this.createElement('label', {
                    classList: ['title-label'],
                    style: { gridArea: '1 / 1 / 2 / 2' },
                    textContent: 'Pontos a visitar:'
                }, pointsToVisitTitleGrid);
            
                this.createElement('button', {
                    classList: ['title-button', 'disabled'],
                    id: 'routeListMoveUpBtn',
                    textContent: '▲',
                    style: { gridArea: '1 / 2 / 2 / 3' },
                    eventListeners: {
                        click: (event) => onRouteListChange(event)
                    }
                }, pointsToVisitTitleGrid);
            
                this.createElement('button', {
                    classList: ['title-button', 'disabled'],
                    id: 'routeListMoveDownBtn',
                    textContent: '▼',
                    style: { gridArea: '1 / 3 / 2 / 4' },
                    eventListeners: {
                        click: (event) => onRouteListChange(event)
                    }
                }, pointsToVisitTitleGrid);
                // </SUB-GRID>
        
            this.createElement('ul', {
                classList: ['text-list'],
                id: 'pointsToVisit',
                style: { gridArea: '7 / 1 / 8 / 2' }
            }, panel);
            // </GRID PRINCIPAL>
        }        

        /*-----------------------------------------------------------------------------------
            ## TOOLBAR ##
        -----------------------------------------------------------------------------------*/
        static toolbar() {
            let footerContainer = document.getElementById('toolbar');
            footerContainer.style.position = 'absolute';
            footerContainer.style.bottom = '0';
            footerContainer.style.left = '0px';
            footerContainer.style.paddingLeft = '5px';
            footerContainer.style.paddingRight = '5px';
            footerContainer.style.alignItems = 'center';
            footerContainer.style.height = '34px';
            footerContainer.style.backgroundColor = 'rgb(240, 240, 240)';
            footerContainer.style.display = 'grid';
            footerContainer.style.width = '100%';
            footerContainer.style.gridTemplateColumns = '22px 22px 22px minmax(0, 1fr) 22px 22px 22px 22px';
            footerContainer.style.gridTemplateRows = '1fr';
            footerContainer.style.columnGap = '5px';

            // Lado esquerdo
            const img1 = document.createElement('img');
            img1.id = 'footer: logo';
            img1.style.gridArea = '1 / 1 / 2 / 2';
            img1.src = 'images/ArrowLeft_32.png';
            img1.style.width = '17px';
            img1.style.height = '17px';
            img1.style.cursor = 'pointer';
            Tooltip.bindBasicTooltip(img1, 'Visibilidade do painel de controle');
            img1.onclick = window.app.modules.Callback.toolbar_routeButtonClick;

            const img3 = document.createElement('img');
            img3.id = 'footer: logo';
            img3.style.gridArea = '1 / 2 / 2 / 3';
            img3.src = 'images/Connect_18.png';
            img3.style.cursor = 'pointer';
            Tooltip.bindBasicTooltip(img3, 'Conexão servidor');

            const img2 = document.createElement('img');
            img2.id = 'footer: logo';
            img2.style.gridArea = '1 / 3 / 2 / 4';
            img2.src = 'images/export.png';
            img2.style.cursor = 'pointer';
            Tooltip.bindBasicTooltip(img2, 'Exporta a rota em KML');

            const img3a = document.createElement('img');
            img3a.style.gridArea = '1 / 5 / 2 / 6';
            img3a.src = 'images/gps-off.png';
            img3a.style.width = '18px';
            img3a.style.height = '18px';
            img3a.style.cursor = 'pointer';
            Tooltip.bindBasicTooltip(img3a, 'Compartilhar localização');
            img3a.onclick = () => { 
                const currentStatus = window.app.mapContext.settings.geolocation.status;
                if (currentStatus === 'on') {
                    window.app.mapContext.settings.geolocation.status = 'off';
                    img3a.src = window.app.mapContext.settings.geolocation.icon.off;
                } else {
                    window.app.mapContext.settings.geolocation.status = 'on';
                    img3a.src = window.app.mapContext.settings.geolocation.icon.on;
                }

                new DialogBox('<h1>Título</h1><p>Parágrafo</p>', 'warning', []); 
            };

            const img3b = document.createElement('img');
            img3b.style.gridArea = '1 / 6 / 2 / 7';
            img3b.src = 'images/north.png';
            img3b.style.width = '18px';
            img3b.style.height = '18px';
            img3b.style.cursor = 'pointer';
            Tooltip.bindBasicTooltip(img3b, 'Orientação do mapa');
            img3b.onclick = () => { 
                const currentStatus = window.app.mapContext.settings.orientation.status;
                if (currentStatus === 'north') {
                    window.app.mapContext.settings.orientation.status = 'car-heading';
                    img3b.src = window.app.mapContext.settings.orientation.icon.off;
                } else {
                    window.app.mapContext.settings.orientation.status = 'north';
                    img3b.src = window.app.mapContext.settings.orientation.icon.on;
                }

                new DialogBox('<h1>Título</h1><p>Parágrafo</p>', 'error', [], 800); 
            };

            const img4 = document.createElement('img');
            img4.id = 'footer: logo';
            img4.style.gridArea = '1 / 7 / 2 / 8';
            img4.src = 'images/colorbar.svg';
            img4.style.width = '18px';
            img4.style.height = '18px';
            img4.style.cursor = 'pointer';
            Tooltip.bindBasicTooltip(img4, 'Barra de cores');
            img4.onclick = () => { 
                new DialogBox('Uma informação qualquer... Uma informação qualquer... <b>Uma informação qualquer...</b> <br><br> Uma informação qualquer... Uma informação qualquer... <p>Uma informação qualquer...</p> Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer...  Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer... Uma informação qualquer...', '', [{ text: 'OK', callback: () => console.log('OK'), focus: true }, { text: 'Cancel', callback: () => console.error('Cancel'), focus: false }]) 
            };

            const img5 = document.createElement('img');
            img5.id = 'footer: logo';
            img5.style.gridArea = '1 / 8 / 2 / 9';
            img5.src = 'images/layers.png';
            img5.style.width = '18px';
            img5.style.height = '18px';
            img5.style.cursor = 'pointer';
            Tooltip.bindBasicTooltip(img5, 'Basemap');
            img5.onclick = () => { 
                window.app.map.setView(window.app.mapContext.settings.position.center, window.app.mapContext.settings.position.zoom);
                // this.createBasemapSelector() 
            };


            // Monta o footer
            footerContainer.appendChild(img1);
            footerContainer.appendChild(img2);
            footerContainer.appendChild(img3);
            footerContainer.appendChild(img3a);
            footerContainer.appendChild(img3b);
            footerContainer.appendChild(img4);
            footerContainer.appendChild(img5);
        }

        /*-----------------------------------------------------------------------------------
            ## OUTROS ELEMENTOS CRIADOS SOB DEMANDA ##
        -----------------------------------------------------------------------------------*/
        static createElement(tag, options = {}, parentElement = null) {
            const el = document.createElement(tag);
          
            Object.keys(options).forEach(key => {
              switch (key) {
                case 'classList':
                    options.classList.forEach(cls => el.classList.add(cls));
                    break;

                case 'style':
                    Object.assign(el.style, options.style);
                    break;

                case 'dataset':
                    Object.keys(options.dataset).forEach(dataKey => {
                        switch (dataKey) {
                            case 'tooltip':
                                Tooltip.bindBasicTooltip(el, options.dataset.tooltip);
                                break;

                            default:
                                el.dataset[dataKey] = options.dataset[dataKey];
                        }                        
                    });
                    break;

                case 'eventListeners':
                    Object.keys(options.eventListeners).forEach(eventType => {
                        el.addEventListener(eventType, options.eventListeners[eventType]);
                    });
                    break;

                default:
                    el[key] = options[key];
              }
            });

            if (parentElement) {
                parentElement.appendChild(el);
            }
          
            return el;
        }

        /*---------------------------------------------------------------------------------*/
        static createTitle(style, options, parentElement = null) {
            switch (style) {
                case 'icon+text+line':
                    const { gridArea, iconPath, textContent } = options;
                    
                    const title = this.createElement('div',  { 
                        classList: ['topdiv-container'], 
                        style: { gridArea: gridArea, display: 'flex', flexDirection: 'column', height: '26px', margin: '0', padding: '0', backgroundColor: 'rgb(191, 191, 191)' } 
                    }, parentElement);

                    const content = this.createElement('div',  { 
                        style: { display: 'flex', alignItems: 'center', height: '23px', paddingLeft: '4px', gap: '6px' } 
                    }, title);

                    const img = this.createElement('img',  { 
                        width: 18, 
                        height: 18, 
                        src: iconPath
                    }, content);

                    const txt = this.createElement('span', { 
                        textContent: textContent 
                    }, content);

                    const line = this.createElement('div',  { 
                        style: { height: '3px', width: '100%', backgroundColor: 'rgb(0,0,0)' } 
                    }, title);

                    return title;

                default:
                    // IMPLEMENTAR OUTROS ESTILOS À MEDIDA QUE FOR NECESSÁRIO
                    throw Error('Unexpected title style')
            }
        }

        /*---------------------------------------------------------------------------------*/
        static createTextList(textList, textResolver, eventListeners, parentElement) {
            parentElement.childNodes.forEach(element => element.remove())

            textList.forEach((element, index) => {
                this.createElement('li', {
                    textContent: textResolver(element, index),
                    style: { height: '22px' },
                    eventListeners: eventListeners
                }, parentElement);
            })
        }

        /*---------------------------------------------------------------------------------*/
        static createBasemapSelector() {
            let tooltip = document.querySelector('.tooltip');
            if (tooltip) {
                tooltip.remove();
                tooltip = null;
            }

            let popup = document.querySelector('.basemap-popup');

            if (popup) {
                popup.remove();
                popup = null;
            } else {
                const map = window.app.map;
                const basemaps = window.L.dataSet.Basemap.items;
        
                popup = document.createElement('div');
                popup.className = 'basemap-popup';
        
                Object.assign(popup.style, {
                    position: 'fixed',
                    right: '10px',
                    bottom: '56px',
                    background: 'rgba(255, 255, 255, 0.8)',
                    padding: '10px 10px 10px 5px',
                    borderRadius: '3px',
                    fontFamily: 'Helvetica, Arial, sans-serif',
                    fontSize: '11px',
                    color: '#333',
                    whiteSpace: 'nowrap',
                    boxShadow: '0 2px 6px rgba(0,0,0,0.3)',
                    transition: 'opacity 0.2s ease',
                });
        
                // Rádios
                const current = window.L.dataSet.Basemap.value;
                Object.entries(basemaps).forEach(([key, layer]) => {
                    const label = document.createElement('label');
                    label.style.display = 'flex';
                    label.style.alignItems = 'center';
                    label.style.cursor = 'pointer';
        
                    const radio = document.createElement('input');
                    radio.type = 'radio';
                    radio.name = 'basemap';
                    radio.value = key;
                    radio.checked = (key === current);
                    radio.style.marginRight = '5px';
        
                    radio.addEventListener('change', () => {
                        const oldKey = window.L.dataSet.Basemap.value;
                        map.removeLayer(basemaps[oldKey]);
                        window.L.dataSet.Basemap.value = key;
                        map.addLayer(basemaps[key]);
                    });
        
                    label.appendChild(radio);
                    label.appendChild(document.createTextNode(key));
                    popup.appendChild(label);
                });    
                document.body.appendChild(popup);
            }
        }

        /*---------------------------------------------------------------------------------*/
        static colorbar() {
            const svgContainer = window.document.getElementById("colorbar");
            if (!svgContainer) return;
        
            // Limpa o conteúdo anterior
            svgContainer.innerHTML = "";
            
            // Insere o novo SVG
            svgContainer.appendChild(generateScaleSVG(globalMinElevation, globalMaxElevation));
        }

        /*---------------------------------------------------------------------------------*/
        static uuid() {
            return (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') 
                ? crypto.randomUUID()
                : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
                    const r = Math.random() * 16 | 0;
                    const v = c === 'x' ? r : (r & 0x3 | 0x8);
                    return v.toString(16);
                });
        }
    }

    window.app.modules.CreateComponent = CreateComponent;
})()