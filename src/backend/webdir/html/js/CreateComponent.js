(function() {
    /*
        Inventário dos métodos estáticos da classe "CreateComponent":
        - navBar()
        - leftPanel()
        - rightPanel()
        - document()
        - toolbar()
    */
    class CreateComponent {
        static navBar() {
        }


        static leftPanel() {
            const panel = document.getElementById('left-panel');
            ['left-panel-on', 'grid'].forEach(className => {
                panel.classList.add(className);
            });
            panel.style.gridTemplateRows = '26px 22px minmax(0px, 1fr) 22px 115px 22px minmax(0px, 1fr) 1px 22px';
            panel.style.gridTemplateColumns = '110px 1fr 74px 18px 18px';
            panel.style.columnGap = '0px';

            // título
            const topdivContainer = document.createElement('div');
            topdivContainer.style.gridArea = '1 / 1 / 2 / 6';
            topdivContainer.style.backgroundColor = 'rgb(191, 191, 191)';
            topdivContainer.style.height = '26px';
            topdivContainer.style.display = 'flex';
            topdivContainer.style.flexDirection = 'column';
            topdivContainer.style.padding = '0';
            topdivContainer.style.margin = '0';

            // linha com ícone e texto
            const contentRow = document.createElement('div');
            contentRow.style.height = '23px';
            contentRow.style.display = 'flex';
            contentRow.style.alignItems = 'center';
            contentRow.style.gap = '6px';
            contentRow.style.paddingLeft = '4px';

            const img = document.createElement('img');
            img.src = 'images/route.svg';
            img.width = 18;
            img.height = 18;
            img.alt = 'Ícone';

            const span = document.createElement('span');
            span.textContent = 'webRotas';

            // faixa preta inferior
            const bottomDiv = document.createElement('div');
            bottomDiv.style.backgroundColor = 'black';
            bottomDiv.style.height = '3px';
            bottomDiv.style.width = '100%';

            // montar estrutura
            contentRow.appendChild(img);
            contentRow.appendChild(span);
            topdivContainer.appendChild(contentRow);
            topdivContainer.appendChild(bottomDiv);
            panel.appendChild(topdivContainer);

            // item 1
            const label1 = document.createElement('label');
            label1.classList.add('label');
            label1.id = 'panel: routeListLabel';
            label1.style.gridArea = '2 / 1 / 3 / 6';
            label1.textContent = 'Rotas:';
            panel.appendChild(label1);

            const treeView1 = document.createElement('ul');
            treeView1.classList.add('text-list');
            treeView1.id = 'panel: routeList';
            treeView1.style.gridArea = '3 / 1 / 4 / 6';
            panel.appendChild(treeView1);

            const label2 = document.createElement('label');
            label2.classList.add('label');
            label2.id = 'panel: initialPointLabel';
            label2.style.gridArea = '4 / 1 / 5 / 5';
            label2.textContent = 'Ponto inicial:';
            panel.appendChild(label2);

            const btn1 = document.createElement('img');
            btn1.id = 'panel: initialPointButton';
            btn1.src = 'images/pin_18.png';
            btn1.style.gridArea = '4 / 5 / 5 / 6';
            btn1.style.textAlign = 'right';
            btn1.style.alignSelf = 'end';
            btn1.style.transform = 'translateY(3px)'
            btn1.style.cursor = 'pointer';
            panel.appendChild(btn1);

            const grid1 = document.createElement('div');
            grid1.id = 'panel: initialPointGrid';
            grid1.style.gridArea = '5 / 1 / 6 / 6';
            ['grid', 'grid-border'].forEach(className => {
                grid1.classList.add(className);
            });
            grid1.style.gridTemplateRows = '17px 22px 17px 22px';
            panel.appendChild(grid1);

            const label3 = document.createElement('label');
            label3.classList.add('sublabel');
            label3.id = 'panel: latitudeLabel';
            label3.htmlFor = 'panel: latitude';
            label3.style.gridArea = '1 / 1 / 2 / 2';
            label3.textContent = 'Latitude:';
            grid1.appendChild(label3);

            const input1 = document.createElement('input');
            input1.classList.add('no-spinner');
            input1.id = 'panel: latitude';
            input1.type = 'number';
            input1.min = '-90';
            input1.max = '90';
            input1.style.gridArea = '2 / 1 / 3 / 2';
            window.app.module.Callback.addEventListener(input1, 'input:numeric:range-validation');
            grid1.appendChild(input1);

            const label4 = document.createElement('label');
            label4.classList.add('sublabel');
            label4.id = 'panel: longitudeLabel';
            label4.htmlFor = 'panel: longitude';
            label4.style.gridArea = '1 / 2 / 2 / 3';
            label4.textContent = 'Longitude:';
            grid1.appendChild(label4);

            const input2 = document.createElement('input');
            input2.classList.add('no-spinner');
            input2.id = 'panel: longitude';
            input2.type = 'number';
            input2.min = '-180';
            input2.max = '180';
            window.app.module.Callback.addEventListener(input2, 'input:numeric:range-validation');
            input2.style.gridArea = '2 / 2 / 3 / 3';
            grid1.appendChild(input2);

            const label5 = document.createElement('label');
            label5.classList.add('sublabel');
            label5.id = 'panel: descriptionLabel';
            label5.htmlFor = 'panel: description';
            label5.style.gridArea = '3 / 1 / 4 / 2';
            label5.textContent = 'Descrição:';
            grid1.appendChild(label5);

            const input3 = document.createElement('input');
            input3.id = 'panel: description';
            input3.type = 'text';
            input3.style.gridArea = '4 / 1 / 5 / 3';
            grid1.appendChild(input3);

            const label6 = document.createElement('label');
            label6.classList.add('label');
            label6.id = 'panel: pointsToVisitLabel';
            label6.style.gridArea = '6 / 1 / 7 / 6';
            label6.textContent = 'Pontos a visitar:';
            panel.appendChild(label6);

            const upArrow = document.createElement('button');
            upArrow.id = 'panel: upArrow';
            upArrow.textContent = '▲';
            upArrow.style.gridArea = '6 / 4 / 7 / 5';
            upArrow.style.background = 'none';
            upArrow.style.border = 'none';
            upArrow.style.fontSize = '12px';
            upArrow.style.cursor = 'pointer';
            upArrow.style.alignSelf = 'end';
            upArrow.style.textAlign = 'right';
            upArrow.style.transform = 'translateY(3px)';
            panel.appendChild(upArrow);

            const downArrow = document.createElement('button');
            downArrow.id = 'panel: downArrow';
            downArrow.textContent = '▼';
            downArrow.style.gridArea = '6 / 5 / 7 / 6';
            downArrow.style.background = 'none';
            downArrow.style.border = 'none';
            downArrow.style.fontSize = '12px';
            downArrow.style.cursor = 'pointer';
            downArrow.style.alignSelf = 'end';
            downArrow.style.textAlign = 'right';
            downArrow.style.transform = 'translateY(3px)'
            panel.appendChild(downArrow);

            const treeView2 = document.createElement('ul');
            treeView2.classList.add('text-list');
            treeView2.id = 'panel: pointsToVisitList';
            treeView2.style.gridArea = '7 / 1 / 10 / 6';
            panel.appendChild(treeView2);
        }


        static rightPanel() {
        }


        static document() {
            /*
                O documento é composto unicamente pelo mapa provido pela lib Leaflet.
            */
            if (!window.L.dataSet) {
                window.L.dataSet = {};
            }

            window.L.dataSet.basemaps = {
                "street-light": window.L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
                    maxZoom: 19,
                    attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
                    subdomains: 'abcd'
                }),
                "street-dark": window.L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                    maxZoom: 19,
                    attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
                    subdomains: 'abcd'
                }),
                "open-street": window.L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                }),
                "satellite": window.L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                    maxZoom: 19,
                    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
                })
            };

            const map = window.L.map('document', { 
                zoomControl: false 
            }).setView(window.app.mapView.center, window.app.mapView.zoom);

            map.on('mousedown', (event) => {
                if (!!window.app.plot.tooltip.mouseDownTarget.handle) {
                    window.app.plot.tooltip.mouseDownTarget.handle = null;
                }                
            });

            map.on('mouseup', (event) => {
                window.app.module.Plot.checkDragging();

                if (!!window.app.plot.tooltip.mouseDownTarget.handle) {
                    const { screenX, screenY } = event.originalEvent;

                    const tooltip = window.app.plot.tooltip.mouseDownTarget.handle;
                    const direction = tooltip.options.direction;                    
                    const mouseDirection = window.app.module.Util.Tooltip.detectMouseDirection(window.app.plot.tooltip.mouseDownTarget.position, [screenX, screenY]);                    
                    const newDirection   = window.app.module.Util.Tooltip.suggestNewTooltipDirection(direction, mouseDirection);

                    if (!!newDirection && direction !== newDirection) {
                        window.app.module.Util.Tooltip.recreateLeafletTooltip(tooltip, newDirection);
                    }

                    window.app.plot.tooltip.mouseDownTarget.handle = null;
                }                
            });

            window.L.dataSet.basemaps[window.app.mapView.basemap].addTo(map);
            window.L.control.scale().addTo(map);

            window.app.map = map;
        }

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
            footerContainer.style.width = 'calc(100% - 10px)';
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
            window.app.module.Util.Tooltip.controller(img1, 'add-hover-listener', 'Visibilidade do painel de controle', 'tooltip-button');
            img1.onclick = window.app.module.Callback.toolbar_routeButtonClick;

            const img3 = document.createElement('img');
            img3.id = 'footer: logo';
            img3.style.gridArea = '1 / 2 / 2 / 3';
            img3.src = 'images/Connect_18.png';
            img3.style.cursor = 'pointer';
            window.app.module.Util.Tooltip.controller(img3, 'add-hover-listener', 'Conexão servidor', 'tooltip-button');

            const img2 = document.createElement('img');
            img2.id = 'footer: logo';
            img2.style.gridArea = '1 / 3 / 2 / 4';
            img2.src = 'images/export.png';
            img2.style.cursor = 'pointer';
            window.app.module.Util.Tooltip.controller(img2, 'add-hover-listener', 'Exporta a rota em KML', 'tooltip-button');

            const img3a = document.createElement('img');
            img3a.style.gridArea = '1 / 5 / 2 / 6';
            img3a.src = 'images/gps-off.png';
            img3a.style.width = '18px';
            img3a.style.height = '18px';
            img3a.style.cursor = 'pointer';
            window.app.module.Util.Tooltip.controller(img3a, 'add-hover-listener', 'Compartilhar localização', 'tooltip-button');
            img3a.onclick = () => { 
                window.app.location.status = !window.app.location.status; 
                new DialogBox('<h1>Título</h1><p>Parágrafo</p>', 'warning', []); 
            };

            const img3b = document.createElement('img');
            img3b.style.gridArea = '1 / 6 / 2 / 7';
            img3b.src = 'images/north.png';
            img3b.style.width = '18px';
            img3b.style.height = '18px';
            img3b.style.cursor = 'pointer';
            window.app.module.Util.Tooltip.controller(img3b, 'add-hover-listener', 'Orientação do mapa', 'tooltip-button');
            img3b.onclick = () => { 
                window.app.orientation.status = !window.app.orientation.status; 
                new DialogBox('<h1>Título</h1><p>Parágrafo</p>', 'error', [], 800); 
            };

            const img4 = document.createElement('img');
            img4.id = 'footer: logo';
            img4.style.gridArea = '1 / 7 / 2 / 8';
            img4.src = 'images/colorbar.svg';
            img4.style.width = '18px';
            img4.style.height = '18px';
            img4.style.cursor = 'pointer';
            window.app.module.Util.Tooltip.controller(img4, 'add-hover-listener', 'Barra de cores', 'tooltip-button');
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
            window.app.module.Util.Tooltip.controller(img5, 'add-hover-listener', 'Basemap', 'tooltip-button');
            img5.onclick = () => { 
                window.app.map.setView(window.app.mapView.center, window.app.mapView.zoom);
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


        static colorbar() {
            const svgContainer = window.document.getElementById("colorbar");
            if (!svgContainer) return;
        
            // Limpa o conteúdo anterior
            svgContainer.innerHTML = "";
            
            // Insere o novo SVG
            svgContainer.appendChild(generateScaleSVG(globalMinElevation, globalMaxElevation));
        }


        /*---------------------------------------------------------------------------------*/
        static tooltip(targetElement, tooltipId, tooltipText, tooltipRole) {
            let tooltip, tooltipArrow;

            tooltip = window.document.createElement('div');
            tooltip.id = tooltipId;
            tooltip.className = 'tooltip-panel';
            tooltip.role = tooltipRole;
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

            return tooltip;
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

    window.app.module.CreateComponent = CreateComponent;
})()