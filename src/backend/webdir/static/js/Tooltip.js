/*
    ToDo:
    - Implementar menu de contexto no tooltip do mapa, possibilitando coleta das coordenadas
      do target relacionado ao "stickyTooltip" selecionado, a exclusão desse "stickyTooltip",
      ou de todos os "stickyTooltip", dentre outras.
      - ...
*/


class Tooltip {
    static basicTooltipClasses   = ['tooltip-container', 'tooltip-arrow']
    static leafletTooltipClasses = ['leaflet-tooltip-bottom', 'leaflet-container', 'tooltip-container', 'tooltip-on-grabbing']

    /*-----------------------------------------------------------------------------------
        ## TOOLTIP BÁSICO ##
        (não instanciável)

        Para uso em imagens, botões, caixas de texto etc. Possui um único método estático 
        bindBasicTooltip(target, text), o qual possui três funções com escopo local:
        - basicTooltipShow(tooltip, target, id, text)
        - basicTooltipHide(tooltip, target)
        - basicTooltipRender(target, id, text)
    -----------------------------------------------------------------------------------*/
    static bindBasicTooltip(target, text, defaultPosition = "top") {
        let tooltip;

        if (!target.dataset.tooltipId) {
            target.dataset.tooltipId    = Tooltip.uuid();
            target.dataset.tooltipState = 'hidden';
            target.dataset.tooltipText  = text;
        }

        target.addEventListener('mouseenter', () => tooltip = basicTooltipShow(tooltip, target, defaultPosition));
        target.addEventListener('mouseleave', () => basicTooltipHide(tooltip, target));

        /*-----------------------------------------------------------------------------*/
        function basicTooltipShow(tooltip, target, defaultPosition) {
            if (!tooltip || target.dataset.tooltipState === 'hidden') {
                tooltip = basicTooltipRender(target, defaultPosition);
                target.dataset.tooltipState = 'hover';
            }

            return tooltip;
        }

        /*-----------------------------------------------------------------------------*/
        function basicTooltipHide(tooltip, target) {
            if (tooltip && target.dataset.tooltipState === 'hover') {
                tooltip.remove();
                tooltip = null;

                target.dataset.tooltipState = 'hidden';
            }
        }

        /*-----------------------------------------------------------------------------*/
        function basicTooltipRender(target, defaultPosition) {
            let tooltip, tooltipArrow;
    
            tooltip = window.document.createElement('div');
            tooltip.id = target.dataset.tooltipId;
            tooltip.className = Tooltip.basicTooltipClasses[0];
            tooltip.innerHTML = target.dataset.tooltipText;;
    
            tooltipArrow = window.document.createElement('div');
            tooltipArrow.className = Tooltip.basicTooltipClasses[1];
    
            tooltip.appendChild(tooltipArrow);
            window.document.body.appendChild(tooltip);
    
            const rect = target.getBoundingClientRect();
            const scrollX  = window.scrollX;
            const scrollY  = window.scrollY;
            const centerX  = rect.left + scrollX + rect.width / 2;
            const maxRight = scrollX + window.innerWidth - 4;
    
            const tooltipWidth  = tooltip.offsetWidth;
            const tooltipHeight = tooltip.offsetHeight;    
            
            let left = centerX - tooltipWidth / 2;
            if (left < 4) { left = 4; }
            if (left + tooltipWidth > maxRight) { left = maxRight - tooltipWidth; }
    
            let top, showAbove;
            
            if (defaultPosition === 'bottom') {
                top = rect.bottom + scrollY + 8;
                showAbove = false;

                if (top + tooltipHeight > scrollY + window.innerHeight - 4) {
                    top = rect.top + scrollY - tooltipHeight - 8;
                    showAbove = true;
                }
            } else {
                top = rect.top + scrollY - tooltipHeight - 8
                showAbove = true;

                if (top < scrollY + 4) {
                    top = rect.bottom + scrollY + 8;
                    showAbove = false;
                }
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


    /*-----------------------------------------------------------------------------------
        ## TOOLTIP LEAFLET CUSTOMIZADO ##
        (instanciável pelo próprio app)
        
        Uma vez instanciado, usa-se o método "bindLeafletTooltip" para criar os tooltips
        e os listeners (mousedown, mouseover, mouseup etc).       
    -----------------------------------------------------------------------------------*/
    mapEventRegistry = false
    dragContext = this.#initialDragState()

    bindLeafletTooltip(map, target, coords, text, direction, offsetResolver = (direction) => { return (direction === "top") ? [0, -41] : [0, 0] }) {
        /*
            Cria atributo no target (L.Marker), registrando o modo de operação ("hover" ou "sticky"), 
            handles para os tooltips e os parâmetros de configuração.

            O handle para o "hoverTooltip", apesar de previsto nesse atributo, não será usado 
            porque o Leaflet já o retorna por meio de target._tooltip.
        */
        const offset = offsetResolver(direction);

        target._tooltipContext = {
            mode: 'TOOLTIP_MODE.HOVER',
            handle: {
              hover: null, // "hoverTooltip" (target._tooltip)
              sticky: null // "stickyTooltip"
            },
            config: {
              coords,
              text,
              direction,
              offset,
              offsetResolver // handle para função
            }
          };

        this.#bindLeafletHoverTooltip(target);
        // target._tooltipContext.handle.hover = target._tooltip;

        target.on('mouseover', () => {
            if (!!target._tooltipContext.handle.sticky || this.dragContext.status === 'MOVING') {
                target.closeTooltip(); // não exclui "hoverTooltip"
            }
        });

        target.on('click', () => {
            if (!target._tooltipContext.handle.sticky) {
                target._tooltipContext.handle.sticky = this.#bindLeafletStickyTooltip(map, target);
            } else {
                target._tooltipContext.handle.sticky.remove();
                target._tooltipContext.handle.sticky = null;                
            }

            target._tooltipContext.mode = (target._tooltipContext.handle.sticky) ? 'TOOLTIP_MODE.STICKY' : 'TOOLTIP_MODE.HOVER';
        })

        window.L.DomEvent.on(target, 'mouseover', window.L.DomEvent.stopPropagation);
        window.L.DomEvent.on(target, 'click',     window.L.DomEvent.stopPropagation);

        if (!this.mapEventRegistry) {
            this.mapEventRegistry = true;

            map.on('mousemove', (event) => {
                if (this.dragContext.handle.shadow) {
                    const { clientX, clientY } = event.originalEvent;

                    const dx = clientX - this.dragContext.shadowCurrentPos[0];
                    const dy = clientY - this.dragContext.shadowCurrentPos[1];

                    const newScreenX = parseInt(this.dragContext.handle.shadow.style.left) + dx;
                    const newScreenY = parseInt(this.dragContext.handle.shadow.style.top)  + dy;

                    this.dragContext.shadowCurrentPos = [clientX, clientY];
                    this.dragContext.updateShadowPosition(newScreenX, newScreenY);

                    this.dragContext.status = 'MOVING';
                }
            })

            map.on('mouseup', (event) => {
                if (this.dragContext.handle.shadow) {
                    const { clientX, clientY } = event.originalEvent;
                    const currentDirection = this.dragContext.handle.sticky.options.direction;
                    const dragDirection    = this.#dragDirection([clientX, clientY]);
        
                    if (!!dragDirection && currentDirection !== dragDirection) {
                        this.#recreateLeafletTooltip(map, this.dragContext.handle.sticky._target, dragDirection);
                    }
        
                    this.#resetDragState(map);
                }
            });

            window.L.DomEvent.on(map, 'mousemove', window.L.DomEvent.stopPropagation);
            window.L.DomEvent.on(map, 'mouseup',   window.L.DomEvent.stopPropagation);

            const mapContainer = window.document.getElementById("document");
            window.addEventListener('mouseup', (event) => {
                if (this.dragContext.status === 'MOVING' && !mapContainer.contains(event.target)) {
                    this.#resetDragState(map);
                }
            });
        }
    }

    /*---------------------------------------------------------------------------------*/
    #bindLeafletHoverTooltip(target) {
        const { text, direction, offset } = target._tooltipContext.config;

        target.bindTooltip(text, { 
            className: Tooltip.basicTooltipClasses[0], 
            direction: direction,
            offset: offset
        });
    }

    #bindLeafletStickyTooltip(map, target) {
        const { coords, text, direction, offset } = target._tooltipContext.config;

        const tooltip = window.L.tooltip({
            className: Tooltip.basicTooltipClasses[0], 
            direction: direction,
            offset: offset,
            permanent: true,
            interactive: true
        })
        .setContent(text)
        .setLatLng(coords)
        .addTo(map);

        /*
            Cria atributo no "stickyTooltip", registrando handle para o target (L.Marker).
        */
        tooltip._target = target;

        tooltip.on('mousedown', (event) => {
            map.dragging.disable();

            if (this.dragContext.handle.sticky !== tooltip) {
                const { clientX, clientY } = event.originalEvent;
                const boundingBox = tooltip._container.getBoundingClientRect();
                const shadowTooltip = this.#dragPreviewTooltipRender(text, boundingBox)

                this.dragContext.handle = {
                    sticky: tooltip,
                    shadow: shadowTooltip
                };
                this.dragContext.shadowCurrentPos = [clientX, clientY];
                this.dragContext.updateShadowPosition = (left, top) => {
                    Object.assign(shadowTooltip.style, {
                        left: `${left}px`,
                        top: `${top}px`
                    });
                }

                map._container.classList.add('tooltip-on-grabbing');
            }
        })

        tooltip.on('mouseup', () => {
            this.#resetDragState(map);
        });

        window.L.DomEvent.on(tooltip, 'mousedown', window.L.DomEvent.stopPropagation);
        window.L.DomEvent.on(tooltip, 'mouseup',   window.L.DomEvent.stopPropagation);

        return tooltip;
    }

    /*---------------------------------------------------------------------------------*/
    #initialDragState() {
        return {
            handle: {
                sticky: null,
                shadow: null
            },
            shadowCurrentPos: null,
            updateShadowPosition: null,
            status: 'NONE'
        }
    }

    /*---------------------------------------------------------------------------------*/
    #resetDragState(map) {
        if (!map.dragging.enabled()) {
            map.dragging.enable();
        }
    
        if (this.dragContext.handle.shadow) {      
            this.dragContext.handle.shadow.remove()
            this.dragContext = this.#initialDragState();

            map._container.classList.remove('tooltip-on-grabbing');
        }
    }

    /*---------------------------------------------------------------------------------*/
    #dragDirection(finalMousePos) {
        let angle;

        const target = this.dragContext.handle.sticky._target;
        const { left, top } = target._icon.getBoundingClientRect();     

        const dx = finalMousePos[0] - left;
        const dy = top - finalMousePos[1];

        angle = Math.atan2(dx, dy) * (180 / Math.PI);                
        if (angle < 0) angle += 360;

        if (angle >=  45 && angle < 135) return 'right';
        if (angle >= 135 && angle < 225) return 'bottom';
        if (angle >= 225 && angle < 315) return 'left';
        return 'top';
    }

    /*---------------------------------------------------------------------------------*/
    #dragPreviewTooltipRender(text, boundingBox) {
        const { left, top, width, height } = boundingBox;
        const dragPreviewTooltip = window.document.createElement('div');

        Tooltip.leafletTooltipClasses.forEach(className => {
            dragPreviewTooltip.classList.add(className);
        });
        dragPreviewTooltip.innerHTML = text;

        Object.assign(dragPreviewTooltip.style, {
            left: `${left}px`,
            top: `${top}px`,
            width: `${width}px`,
            height: `${height}px`,
            margin: '10px',
            opacity: '0.25'
        });
        window.document.body.appendChild(dragPreviewTooltip);

        return dragPreviewTooltip;
    }

    /*---------------------------------------------------------------------------------*/
    #recreateLeafletTooltip(map, target, newDirection) {        
        const newOffset = target._tooltipContext.config.offsetResolver(newDirection);

        target._tooltipContext.config.direction = newDirection;
        target._tooltipContext.config.offset = newOffset;
        
        target._tooltip.remove();
        this.#bindLeafletHoverTooltip(target);
        
        target._tooltipContext.handle.sticky.remove();
        target._tooltipContext.handle.sticky = this.#bindLeafletStickyTooltip(map, target);
    }
}