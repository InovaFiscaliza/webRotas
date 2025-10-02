/*
    ## webRotas Components ##
    - BARRA DE NAVEGAÇÃO
      └── createNavBar
    - MAPA
      ├── createMap
      ├── createContextMenu
      ├── createColorbar
      ├── createSvgElement
      └── updateColorbar
    - PAINEL À ESQUERDA DO MAPA
      └── createPanel
    - TOOLBAR
      └── createToolbar
    - *.*
      ├── getDOMElements
      ├── createElement
      ├── createTitle
      ├── createTextList
      └── createBasemapSelector
*/
(function() {
    class Components {
        /*-----------------------------------------------------------------------------------
            ## BARRA DE NAVEGAÇÃO ##
        -----------------------------------------------------------------------------------*/
        static createNavBar() {
            const container = window.document.getElementById('app');
            const navbar = this.createElement('nav', {
                id: 'navbar',
                classList: ['grid']                
            }, container);

            Object.assign(navbar.style, { 
                gridTemplateRows: 'minmax(0px, 1fr)',
                gridTemplateColumns: 'minmax(0px, 1fr) 22px 22px'
            });

            // TÍTULO
            this.createTitle('icon+text', {
                gridArea: '1 / 1 / 2 / 2',
                iconPath: 'images/route_white.svg', 
                innerHTML: `${window.app.name} v. ${window.app.version}<br><font style="font-size: 9px;">${window.app.released}</font>`
            }, navbar)

            this.createElement('button', {
                id: 'serverStatusBtn',
                classList: ['btn-input'],                
                style: { 
                    gridArea: '1 / 2 / 2 / 3',
                    display: (window.location.protocol === "file:") ? 'block' : 'none',
                    width: '18px', 
                    height: '18px', 
                    backgroundImage: 'url(images/red-circle-blink.gif)',
                    backgroundSize: 'contain'
                },
                eventListeners: {
                    click: (event) => window.app.modules.Callbacks.onNavBarButtonClicked(event)
                },
                dataset: { tooltip: 'Servidor offline', tooltipDefaultPosition: 'bottom' }
            }, navbar);

            this.createElement('button', {
                id: 'appInfoBtn',
                classList: ['btn-input'],                
                textContent: '⋮',
                style: { 
                    gridArea: '1 / 3 / 2 / 4',
                    color: 'rgb(255, 255, 255)',
                    fontSize: '19px'
                },
                eventListeners: {
                    click: (event) => window.app.modules.Callbacks.onNavBarButtonClicked(event)
                },
                dataset: { tooltip: 'Informações gerais', tooltipDefaultPosition: 'bottom' }
            }, navbar);
        }

        /*-----------------------------------------------------------------------------------
            ## MAPA ##
            O mapa estará relacionado a alguns eventos: mousemove e mouseup (ambos definidos 
            em "Tooltip.js"), além de contextmenu (definido em "Callback.js"). Além disso, 
            quando o menu de contexto estiver visível, disparam-se os eventos mousedown e 
            zoomstart, que removem o menu caso exista interação com o mapa.
        -----------------------------------------------------------------------------------*/
        static createMap() {
            const container = window.document.getElementById('app');
            this.createElement('div', {
                id: 'document'
            }, container);

            const { center, zoom } = window.app.mapContext.settings.position.default;
            const basemapList      = window.app.mapContext.layers.basemap;
            const basemapSelection = window.app.mapContext.settings.basemap;

            const map = window.L.map('document', { 
                zoomControl: false,
            }).setView(center, zoom);

            basemapList[basemapSelection].addTo(map);
            window.L.control.scale().addTo(map);            
            map.on('contextmenu', (event) => window.app.modules.Callbacks.onContextMenuCreation(event));

            window.app.map = map;
        }

        /*---------------------------------------------------------------------------------*/
        static createContextMenu() {
            const document = window.document.getElementById('document');
            const context  = this.createElement('div', {
                id: 'contextMenu',
                classList: ['context-menu']                
            }, document);

            this.createElement('div', {
                id: 'contextMenuCoords',
                classList: ['context-menu-item'],                
                textContent: 'Coordenadas: -1, -1',
                eventListeners: {
                    click: (event) => window.app.modules.Callbacks.onContextMenuItemSelected(event)
                },
            }, context);

            this.createElement('div', {
                id: 'contextMenuStreetView',
                classList: ['context-menu-item'],                
                textContent: 'Visualizar no StreetView',
                eventListeners: {
                    click: (event) => window.app.modules.Callbacks.onContextMenuItemSelected(event)
                },
            }, context);

            this.createElement('div', {
                id: 'contextMenuUpdateVehicle',
                classList: ['context-menu-item'],                
                textContent: 'Atualizar posição do veículo (offline)',
                eventListeners: {
                    click: (event) => window.app.modules.Callbacks.onContextMenuItemSelected(event)
                },
            }, context);

            return context;
        }

        /*---------------------------------------------------------------------------------*/
        static createColorbar() {
            let mainContainer = window.document.querySelector('.colorbar');
            if (mainContainer) {
                mainContainer.remove();
            }

            window.app.mapContext.settings.colorbar = (window.app.mapContext.settings.colorbar === "hidden") ? "visible" : "hidden";
            if (window.app.mapContext.settings.colorbar === "hidden") {
                return;
            }

            mainContainer = document.createElement("div");
            mainContainer.className = "colorbar";

            const svgContainer = document.createElement("div");
            svgContainer.id = "svgContainer";
            Object.assign(svgContainer.style, {
                width: "100%",
                height: "100%",
                position: "absolute",
                top: "0",
                left: "0"
            });

            mainContainer.appendChild(svgContainer);
            window.document.body.appendChild(mainContainer);

            this.updateColorbar();
        }

        /*---------------------------------------------------------------------------------*/
        static createSvgElement(tagName, attributes = {}) {
            const el = document.createElementNS("http://www.w3.org/2000/svg", tagName);
            Object.entries(attributes).forEach(([k, v]) => el.setAttribute(k, v));
            return el;
        }


        /*---------------------------------------------------------------------------------*/
        static updateColorbar() {
            const svgContainer = window.document.getElementById("svgContainer");
            if (!svgContainer) return;
            svgContainer.innerHTML = "";

            const svg = window.app.modules.Utils.Image.colorbar();
            svgContainer.appendChild(svg);
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
        static createPanel() {
            // <GRID PRINCIPAL>
            const container = window.document.getElementById('app');
            
            const panel = this.createElement('div', {
                id: 'panel',
                classList: ['grid']                
            }, container);

            Object.assign(panel.style, { 
                gridTemplateRows: '17px minmax(0px, 1fr) 22px 115px 22px minmax(0px, 0.5fr) 22px 52px', 
                gridTemplateColumns: 'minmax(0px, 1fr)'
            });

            // ROTAS - LABEL E CONTROLES
            const routeListTitleGrid = this.createElement('div', {
                classList: ['grid'],
                style: { 
                    gridArea: '1 / 1 / 2 / 2', 
                    gridTemplateRows: '17px', 
                    gridTemplateColumns: 'minmax(0px, 1fr) 18px 18px 18px', 
                    padding: '0px', 
                    columnGap: '5px', 
                    overflow: 'visible' 
                }
            }, panel);

                // <SUB-GRID>
                this.createElement('label', {
                    classList: ['label-text-list'],
                    style: { 
                        gridArea: '1 / 1 / 2 / 2' 
                    },
                    textContent: 'Rotas:'
                }, routeListTitleGrid);

                this.createElement('button', {
                    id: 'routeListAddBtn',        
                    classList: ['btn-top-right', 'disabled'],
                    style: { 
                        gridArea: '1 / 2 / 2 / 3', 
                        width: '100%', 
                        height: '100%', 
                        backgroundImage: 'url(images/addFiles_32.png)',
                        backgroundSize: 'contain'
                    },
                    eventListeners: {
                        click: (event) => window.app.modules.Callbacks.onPanelButtonClicked(event)
                    },
                    dataset: { 
                        tooltip: 'Duplica rota' 
                    }
                }, routeListTitleGrid);

                this.createElement('button', {
                    id: 'routeListDelBtn',
                    classList: ['btn-top-right', 'disabled'],
                    style: { 
                        gridArea: '1 / 3 / 2 / 4', 
                        width: '18px', 
                        height: '18px', 
                        backgroundImage: 'url(images/Trash_32.png)' ,
                        backgroundSize: 'contain'
                    },
                    eventListeners: {
                        click: (event) => window.app.modules.Callbacks.onPanelButtonClicked(event)
                    },
                    disabled: true,
                    dataset: { 
                        tooltip: 'Exclui rota' 
                    }
                }, routeListTitleGrid);

                this.createElement('button', {
                    id: 'routeListEditModeBtn',
                    classList: ['btn-top-right', 'disabled'],
                    style: { 
                        gridArea: '1 / 4 / 2 / 5', 
                        width: '18px', 
                        height: '18px', 
                        backgroundImage: 'url(images/Edit_32.png)',
                        backgroundSize: 'contain'
                    },
                    eventListeners: {
                        click: (event) => window.app.modules.Callbacks.onPanelButtonClicked(event)
                    },
                    dataset: { 
                        tooltip: 'Habilita modo de edição da rota', 
                        value: 'off' 
                    }
                }, routeListTitleGrid);

                this.createElement('button', {
                    id: 'routeListConfirmBtn',
                    classList: ['btn-top-right'],
                    style: { 
                        gridArea: '1 / 5 / 2 / 6', 
                        display: 'none', 
                        width: '18px', 
                        height: '18px', 
                        backgroundImage: 'url(images/Ok_32Green.png)',
                        backgroundSize: 'contain'
                    },
                    eventListeners: {
                        click: (event) => window.app.modules.Callbacks.onPanelButtonClicked(event)
                    },
                    dataset: { 
                        tooltip: 'Confirma edição' 
                    }
                }, routeListTitleGrid);

                this.createElement('button', {
                    id: 'routeListCancelBtn',
                    classList: ['btn-top-right'],
                    style: { 
                        gridArea: '1 / 6 / 2 / 7', 
                        display: 'none', 
                        width: '18px', 
                        height: '18px', 
                        backgroundImage: 'url(images/Delete_32Red.png)',
                        backgroundSize: 'contain'
                    },
                    eventListeners: {
                        click: (event) => window.app.modules.Callbacks.onPanelButtonClicked(event)
                    },
                    dataset: { 
                        tooltip: 'Cancela edição' 
                    }
                }, routeListTitleGrid);
                // </SUB-GRID>
        
            // ROTAS - ÁRVORE
            this.createElement('ul', {
                id: 'routeList',
                classList: ['text-list'],
                style: { 
                    gridArea: '2 / 1 / 3 / 2' 
                }
            }, panel);
        
            // PONTO INICIAL - LABEL E CONTROLES
            const initialPointTitleGrid = this.createElement('div', {
                classList: ['grid'],
                style: { 
                    gridArea: '3 / 1 / 4 / 2', 
                    gridTemplateRows: '22px', 
                    gridTemplateColumns: 'minmax(0px, 1fr) 18px', 
                    padding: '0px', 
                    overflow: 'visible' 
                }
            }, panel);

                // <SUB-GRID>
                this.createElement('label', {
                    classList: ['label-panel'],
                    style: { 
                        gridArea: '1 / 1 / 2 / 2' 
                    },
                    textContent: 'Ponto inicial:'
                }, initialPointTitleGrid);
            
                this.createElement('button', {
                    id: 'initialPointBtn',
                    classList: ['btn-top-right', 'disabled'],
                    style: { 
                        gridArea: '1 / 2 / 2 / 3', 
                        width: '18px', 
                        height: '18px', 
                        backgroundImage: 'url(images/pin_18.png)' 
                    },
                    eventListeners: {
                        click: (event) => window.app.modules.Callbacks.onPanelButtonClicked(event)
                    },
                    disabled: true,
                    dataset: { 
                        tooltip: 'Altera ponto inicial diretamente no mapa' 
                    }
                }, initialPointTitleGrid);
                // </SUB-GRID>
        
            // PONTO INICIAL - LATITUDE, LONGITUDE E DESCRIÇÃO
            const initialPointGrid = this.createElement('div', {
                id: 'initialPointGrid',
                classList: ['grid', 'grid-border'],
                style: { 
                    gridArea: '4 / 1 / 5 / 2', 
                    gridTemplateRows: '17px 22px 17px 22px', 
                    gridTemplateColumns: 'minmax(0px, 1fr) minmax(0px, 1fr) minmax(0px, 1fr)', 
                    padding: '10px',
                    borderRadius: '0px'
                }
            });
            panel.appendChild(initialPointGrid);

                // <SUB-GRID>
                this.createElement('label', {
                    classList: ['label-form-field'],
                    htmlFor: 'initialPointLatitude',
                    style: { 
                        gridArea: '1 / 1 / 2 / 2' 
                    },
                    textContent: 'Latitude:'
                }, initialPointGrid);
            
                this.createElement('input', {
                    id: 'initialPointLatitude',
                    type: 'number',
                    step: 'any',
                    style: { 
                        gridArea: '2 / 1 / 3 / 2' 
                    },
                    eventListeners: {
                        change: (event) => window.app.modules.Callbacks.onPanelButtonClicked(event, { min: -90, max: 90 })
                    },
                    disabled: true,
                    dataset: { 
                        tooltip: 'Limites: [-90, 90]', 
                        tooltipDefaultPosition: 'bottom' 
                    }
                }, initialPointGrid);
            
                this.createElement('label', {
                    classList: ['label-form-field'],
                    htmlFor: 'initialPointLongitude',
                    style: { 
                        gridArea: '1 / 2 / 2 / 3' 
                    },
                    textContent: 'Longitude:'
                }, initialPointGrid);
            
                this.createElement('input', {
                    id: 'initialPointLongitude',
                    type: 'number',
                    step: 'any',
                    style: { 
                        gridArea: '2 / 2 / 3 / 3' 
                    },
                    eventListeners: {
                        change: (event) => window.app.modules.Callbacks.onPanelButtonClicked(event, { min: -180, max: 180 })
                    },
                    disabled: true,
                    dataset: { 
                        tooltip: 'Limites: [-180, 180]', 
                        tooltipDefaultPosition: 'bottom' 
                    }
                }, initialPointGrid);

                this.createElement('label', {
                    classList: ['label-form-field'],
                    htmlFor: 'initialPointElevation',
                    style: { 
                        gridArea: '1 / 3 / 2 / 4' 
                    },
                    textContent: 'Elevação:'
                }, initialPointGrid);
            
                this.createElement('input', {
                    id: 'initialPointElevation',
                    type: 'number',
                    step: 'any',
                    style: { 
                        gridArea: '2 / 3 / 3 / 4' 
                    },
                    disabled: true,
                }, initialPointGrid);
            
                this.createElement('label', {
                    classList: ['label-form-field'],
                    htmlFor: 'initialPointDescription',
                    style: { 
                        gridArea: '3 / 1 / 4 / 4' 
                    },
                    textContent: 'Descrição:'
                }, initialPointGrid);
            
                this.createElement('input', {
                    id: 'initialPointDescription',
                    type: 'text',
                    style: { 
                        gridArea: '4 / 1 / 5 / 4' 
                    },
                    disabled: true
                }, initialPointGrid);
                // </SUB-GRID>

            // PONTO A VISITAR - LABEL E CONTROLES
            const pointsToVisitTitleGrid = this.createElement('div', {
                classList: ['grid'],
                style: { 
                    gridArea: '5 / 1 / 6 / 2', 
                    display: 'grid', 
                    gridTemplateRows: '22px', 
                    gridTemplateColumns: 'minmax(0px, 1fr) 18px 18px', 
                    padding: '0px', 
                    columnGap: '5px', 
                    overflow: 'visible' 
                }
            }, panel);

                // <SUB-GRID>        
                this.createElement('label', {
                    classList: ['label-text-list'],
                    style: { 
                        gridArea: '1 / 1 / 2 / 2' 
                    },
                    textContent: 'Pontos a visitar:'
                }, pointsToVisitTitleGrid);
            
                this.createElement('button', {
                    id: 'routeListMoveUpBtn',
                    classList: ['btn-top-right', 'disabled'],
                    textContent: '▲',
                    style: { 
                        gridArea: '1 / 2 / 2 / 3' 
                    },
                    eventListeners: {
                        click: (event) => window.app.modules.Callbacks.onPanelButtonClicked(event)
                    },
                    disabled: true,
                    dataset: { 
                        tooltip: 'Altera ordem do ponto selecionado' 
                    }
                }, pointsToVisitTitleGrid);
            
                this.createElement('button', {
                    id: 'routeListMoveDownBtn',
                    classList: ['btn-top-right', 'disabled'],
                    textContent: '▼',
                    style: { 
                        gridArea: '1 / 3 / 2 / 4' 
                    },
                    eventListeners: {
                        click: (event) => window.app.modules.Callbacks.onPanelButtonClicked(event)
                    },
                    disabled: true,
                    dataset: { 
                        tooltip: 'Altera ordem do ponto selecionado' 
                    }
                }, pointsToVisitTitleGrid);
                // </SUB-GRID>
        
            this.createElement('ul', {
                id: 'pointsToVisit',
                classList: ['text-list'],                
                style: { 
                    gridArea: '6 / 1 / 7 / 2' 
                }
            }, panel);

            this.createElement('label', {
                classList: ['label-text-list'],
                style: { 
                    gridArea: '7 / 1 / 8 / 2' 
                },
                textContent: 'Outras informações:'
            }, panel);

            this.createElement('div', {
                id: 'routeIds',
                classList: ['text-area'],                
                style: { 
                    gridArea: '8 / 1 / 9 / 2' 
                }
            }, panel);
            // </GRID PRINCIPAL>
        }


        /*-----------------------------------------------------------------------------------
            ## TOOLBAR ##
        -----------------------------------------------------------------------------------*/
        static createToolbar() {
            const container = window.document.getElementById('app');
            
            const toolbar = this.createElement('footer', {
                id: 'toolbar',
                classList: ['grid-toolbar']                
            }, container);

            Object.assign(toolbar.style, { 
                gridTemplateRows: '1fr', 
                gridTemplateColumns: '22px 22px 22px 5px 218px minmax(0px, 1fr) 22px 22px 22px 22px 22px' 
            });

            this.createElement('button', {
                id: 'toolbarPanelVisibilityBtn',
                classList: ['btn-panel-on'],                
                style: { 
                    gridArea: '1 / 1 / 2 / 2', 
                    height: '100%',
                    backgroundSize: '17px'
                },
                eventListeners: {
                    click: (event) => window.app.modules.Callbacks.onToolbarButtonClicked(event)
                },
                dataset: { 
                    tooltip: 'Visibilidade do painel de controle' 
                }
            }, toolbar);

            const btn = this.createElement('label', {
                id: 'toolbarImportBtn',
                classList: ['btn-input'],
                htmlFor: 'toolbarImportInput',
                style: { 
                    gridArea: '1 / 2 / 2 / 3', 
                    height: '100%', 
                    backgroundImage: 'url(images/import.png)'
                },
                dataset: { 
                    tooltip: 'Importa arquivo de configuração (.json)' 
                },
            }, toolbar);

            const input = this.createElement('input', {
                id: 'toolbarImportInput',
                type: 'file',
                accept: window.app.mapContext.settings.importFile.format,
                style: { 
                    display: 'none'
                },
                eventListeners: {
                    change: (event) => {
                        window.app.modules.Callbacks.onToolbarButtonClicked(event);
                        event.target.value = '';
                    }
                },
            }, btn);
            // input.multiple = true;

            this.createElement('button', {
                id: 'toolbarExportBtn',
                classList: ['disabled'],
                style: { 
                    gridArea: '1 / 3 / 2 / 4', 
                    height: '100%', 
                    backgroundImage: 'url(images/export.png)'
                },
                eventListeners: {
                    click: (event) => window.app.modules.Callbacks.onToolbarButtonClicked(event)
                },
                dataset: { 
                    tooltip: 'Exporta arquivos (.json | .kml | .html)' 
                }
            }, toolbar);

            this.createElement('separator', {
                style: { 
                    gridArea: '1 / 4 / 2 / 5',
                    borderLeft: '1px solid #7d7d7d',
                    height: '85%',
                    transform: 'translateX(2px)'
                },
            }, toolbar);

            this.createElement('label', {
                id: 'toolbarPositionSliderValue',
                classList: ['no-drag'],
                textContent: '0%',
                style: { 
                    gridArea: '1 / 5 / 2 / 6',
                    textAlign: 'right',
                    color: '#4caf50',
                    transform: 'translateY(-8px)'
                },
                eventListeners: {
                    input: (event) => window.app.modules.Callbacks.onToolbarButtonClicked(event)
                }
            }, toolbar);

            this.createElement('input', {
                id: 'toolbarPositionSlider',
                classList: ['disabled'],
                style: { 
                    gridArea: '1 / 5 / 2 / 6'
                },
                eventListeners: {
                    input: (event) => window.app.modules.Callbacks.onToolbarButtonClicked(event)
                },
                type: 'range',
                min: 0,
                max: 100,
                value: 0
            }, toolbar);

            this.createElement('button', {
                id: 'toolbarLocationBtn',
                classList: ['disabled'],
                style: { 
                    gridArea: '1 / 7 / 2 / 8', 
                    height: '100%', 
                    backgroundImage: 'url(images/gps-off.png)' 
                },
                eventListeners: {
                    click: (event) => window.app.modules.Callbacks.onToolbarButtonClicked(event)
                },
                dataset: { 
                    tooltip: 'Compartilhar localização' 
                }
            }, toolbar);

            this.createElement('button', {
                id: 'toolbarOrientationBtn',
                classList: ['disabled'],
                style: { 
                    gridArea: '1 / 8 / 2 / 9', 
                    height: '100%', 
                    backgroundImage: 'url(images/north.png)' 
                },
                eventListeners: {
                    click: (event) => window.app.modules.Callbacks.onToolbarButtonClicked(event)
                },
                dataset: { 
                    tooltip: 'Orientação do mapa' 
                }
            }, toolbar);

            this.createElement('button', {
                id: 'toolbarInitialZoomBtn',
                style: { 
                    gridArea: '1 / 9 / 2 / 10', 
                    height: '100%', 
                    backgroundImage: 'url(images/restore-initial-zoom.png)' 
                },
                eventListeners: {
                    click: (event) => window.app.modules.Callbacks.onToolbarButtonClicked(event)
                },
                dataset: { 
                    tooltip: 'Zoom inicial' 
                }
            }, toolbar);

            this.createElement('button', {
                id: 'toolbarColorbarBtn',
                style: { 
                    gridArea: '1 / 10 / 2 / 11', 
                    height: '100%', 
                    backgroundImage: 'url(images/colorbar.svg)' 
                },
                eventListeners: {
                    click: (event) => window.app.modules.Callbacks.onToolbarButtonClicked(event)
                },
                dataset: { 
                    tooltip: 'Barra de cores' 
                }
            }, toolbar);

            this.createElement('button', {
                id: 'toolbarBasemapsBtn',
                style: { 
                    gridArea: '1 / 11 / 2 / 12', 
                    height: '100%', 
                    backgroundImage: 'url(images/layers.png)' 
                },
                eventListeners: {
                    click: (event) => window.app.modules.Callbacks.onToolbarButtonClicked(event)
                },
                dataset: { 
                    tooltip: 'Basemap' 
                }
            }, toolbar);
        }


        /*-----------------------------------------------------------------------------------
            ## *.* ##
        -----------------------------------------------------------------------------------*/
        static getDOMElements(ids) {
            const elements = {};
            ids.forEach(id => {
                elements[id] = window.document.getElementById(id);
            });

            return elements;
        }

        /*---------------------------------------------------------------------------------*/
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
                                let tooltipDefaultPosition = [];
                                if (options.dataset.tooltipDefaultPosition) {
                                    tooltipDefaultPosition.push(options.dataset.tooltipDefaultPosition);
                                }
                                Tooltip.bindBasicTooltip(el, options.dataset.tooltip, ...tooltipDefaultPosition);
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
                case 'icon+text': {
                    const { gridArea, iconPath, innerHTML } = options;
                    
                    const title = this.createElement('div',  { 
                        classList: ['topdiv-container'], 
                        style: { 
                            gridArea: gridArea, 
                            display: 'flex', 
                            margin: '0', 
                            padding: '0', 
                            color: 'white' 
                        } 
                    }, parentElement);

                    const content = this.createElement('div',  { 
                        style: { 
                            display: 'flex', 
                            alignItems: 'center', 
                            paddingLeft: '4px', 
                            gap: '12px' 
                        } 
                    }, title);

                    const img = this.createElement('img',  { 
                        width: 18, 
                        height: 18, 
                        src: iconPath
                    }, content);

                    const txt = this.createElement('span', { 
                        innerHTML: innerHTML 
                    }, content);

                    return title;
                }

                case 'icon+text+line': {
                    const { gridArea, iconPath, textContent } = options;
                    
                    const title = this.createElement('div',  { 
                        classList: ['topdiv-container'], 
                        style: { 
                            gridArea: gridArea, 
                            display: 'flex', 
                            flexDirection: 'column', 
                            height: '26px', 
                            margin: '0', 
                            padding: '0', 
                            backgroundColor: 'rgb(191, 191, 191)' 
                        } 
                    }, parentElement);

                    const content = this.createElement('div',  { 
                        style: { 
                            display: 'flex', 
                            alignItems: 'center', 
                            height: '23px', 
                            paddingLeft: '4px', 
                            gap: '6px' 
                        } 
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
                        style: { 
                            height: '3px', 
                            width: '100%', 
                            backgroundColor: 'rgb(0,0,0)' 
                        } 
                    }, title);

                    return title;
                }

                default:
                    // IMPLEMENTAR OUTROS ESTILOS À MEDIDA QUE FOR NECESSÁRIO
                    throw Error('Unexpected title style')
            }
        }

        /*---------------------------------------------------------------------------------*/
        static createRouteList(parentElement, routing, textResolver, eventListeners, selectedIndex) {     
            parentElement.innerHTML = '';

            routing.forEach((routingEl, index1) => {
                routingEl.response.routes.forEach((routeEl, index2) => {
                    const htmlEl = this.createElement('li', {
                        innerHTML: textResolver(routeEl, index1, index2),
                        eventListeners: eventListeners,
                        dataset: { index: JSON.stringify([index1, index2]) }
                    }, parentElement);

                    if (index1 === selectedIndex[0] && index2 === selectedIndex[1]) {
                        htmlEl.classList.add('selected');
                    }
                })
            });
        }

        /*---------------------------------------------------------------------------------*/
        static createTextList(parentElement, textList, textResolver, eventListeners, selectedIndex=-1) {
            parentElement.innerHTML = '';

            textList.forEach((element, index) => {
                const el = this.createElement('li', {
                    innerHTML: textResolver(element, index),
                    value: index,
                    eventListeners: eventListeners
                }, parentElement);

                if (index === selectedIndex) {
                    el.classList.add('selected');
                }
            })
        }
        
        /*---------------------------------------------------------------------------------*/
        static createBasicSelector(type) {
            const options  = window.app.mapContext.settings[type].options;
            const selected = window.app.mapContext.settings[type].selected;

            let popup = window.document.querySelector('.selector-popup');
            if (popup) popup.remove();

            popup = window.document.createElement('div');
            popup.className = 'selector-popup';
    
            // Rádios
            options.forEach((option) => {
                const label = window.document.createElement('label');
                Object.assign(label.style, {
                    display: 'flex',
                    alignItems: 'center',
                    cursor: 'pointer',
                });
    
                const radio = window.document.createElement('input');
                Object.assign(radio, {
                    type: 'radio',
                    name: 'exportFile',
                    value: option,
                    checked: option === selected
                });
                radio.style.marginRight = '5px';

                radio.addEventListener('change', () => {
                    window.app.mapContext.settings.exportFile.selected = option;
                });
    
                label.appendChild(radio);
                label.appendChild(window.document.createTextNode(option));
                popup.appendChild(label);
            });

            return popup;
        }

        /*---------------------------------------------------------------------------------*/
        static createBasemapSelector() {
            const options  = window.app.mapContext.layers.basemap;
            const selected = window.app.mapContext.settings.basemap;

            let popup = window.document.querySelector('.selector-popup');
            if (popup) popup.remove();

            popup = window.document.createElement('div');
            popup.className = 'selector-popup';
    
            // Rádios
            Object.entries(options).forEach(([key, layer]) => {
                const label = window.document.createElement('label');
                Object.assign(label.style, {
                    display: 'flex',
                    alignItems: 'center',
                    cursor: 'pointer',
                });
    
                const radio = window.document.createElement('input');
                Object.assign(radio, {
                    type: 'radio',
                    name: 'basemap',
                    value: key,
                    checked: key === selected
                });
                radio.style.marginRight = '5px';
    
                radio.addEventListener('change', () => {
                    const { map } = window.app;
                    const oldKey  = window.app.mapContext.settings.basemap;
                    map.removeLayer(options[oldKey]);
                    
                    window.app.mapContext.settings.basemap = key;
                    map.addLayer(layer);
                });
    
                label.appendChild(radio);
                label.appendChild(window.document.createTextNode(key));
                popup.appendChild(label);
            });

            return popup;
        }
    }

    window.app.modules.Components = Components;
})()