class DialogBox {
    /*---------------------------------------------------------------------------------*/
    uuid   = null;
    handle = null;    
    static icon   = { 
        info:     'images/info.svg', 
        warning:  'images/warning.svg', 
        question: 'images/question.svg', 
        error:    'images/error.svg' 
    };

    /*---------------------------------------------------------------------------------*/
    constructor(dialogContent, dialogType, dialogButtonList = [{ text: 'OK', callback: () => {}, focus: true }], dialogZIndex = 1000) {
        this.uuid   = DialogBox.uuid();
        this.handle = window.top.document.createElement("div");
        this.handle.className = "dialog-box-overlay";        
        this.handle.id = this.uuid;
        this.handle.style.zIndex = dialogZIndex;

        this.handle.innerHTML = `
            <div class="dialog-box-popup">
                <div class="dialog-box-popup-header">
                    <span></span>
                    <button class="dialog-box-popup-close-btn">
                        <svg viewBox="0 0 12 12">
                            <g>
                                <rect width="12" height="12" fill="none"></rect>
                                <path
                                    d="M9.09,1.5L6,4.59,2.91,1.5,1.5,2.91,4.59,6,1.5,9.08,2.91,10.5,6,7.41,9.09,10.5,10.5,9.08,7.41,6,10.5,2.91,9.09,1.5h0Z"
                                    fill=" #616161">
                                </path>
                            </g>
                        </svg>
                    </button>
                </div>

                <div class="dialog-box-popup-content">
                    <div class="dialog-box-icon">
                        <img class="dialog-box-popup-icon no-select" width=32 height=32/>
                    </div>

                    <span class="dialog-box-popup-text">
                    </span>
                </div>

                <div class="dialog-box-popup-footer">
                </div>
            </div>
        `;

        this.handle.querySelector(".dialog-box-popup-close-btn").onclick = () => this.close();
        this.handle.querySelector(".dialog-box-popup-text").innerHTML = dialogContent;
        this.handle.querySelector(".dialog-box-popup-icon").src = Object.keys(DialogBox.icon).includes(dialogType) ? DialogBox.icon[dialogType] : DialogBox.icon.info;
        this.makeDraggable()

        let focusBtn = null;
        if (dialogButtonList.length) {
            this.handle.querySelector(".dialog-box-popup-footer").style.height = '42px';
            this.handle.querySelector(".dialog-box-popup-footer").innerHTML = dialogButtonList.map((button) => {
                return `<button class="dialog-box-popup-btn no-select">${button.text}</button>`;
            }).join('\n');

            for (let ii = 0; ii < dialogButtonList.length; ii++) {
                this.handle.querySelector(".dialog-box-popup-footer").children[ii].onclick = () => this.executeCallback(dialogButtonList[ii].callback);

                if (dialogButtonList[ii].focus) {
                    focusBtn = this.handle.querySelector(".dialog-box-popup-footer").children[ii];
                }
            }
        }

        window.top.document.body.appendChild(this.handle);
        if (focusBtn) {
            focusBtn.focus();
            this.trapFocus()
        }
    }

    /*---------------------------------------------------------------------------------*/
    close() {
        this.handle.remove();
    }

    /*---------------------------------------------------------------------------------*/
    executeCallback(callbackFunction) {
        callbackFunction();
        this.close();
    }

    /*---------------------------------------------------------------------------------*/
    makeDraggable() {
        let popup    = this.handle.querySelector(".dialog-box-popup");
        let dragArea = this.handle.querySelector(".dialog-box-popup-header");

        let mousePosX, mousePosY;
        let objNormLeft, objNormTop;

        dragArea.addEventListener("mousedown", function(event) {
            event.preventDefault();

            mousePosX    = event.clientX;
            mousePosY    = event.clientY;

            objNormLeft  = popup.offsetLeft;
            objNormTop   = popup.offsetTop;

            function mouseMoveCallback(event) {        
                let minLeft  = popup.offsetWidth/2;
                let maxLeft  = window.top.innerWidth  - popup.offsetWidth/2;
                let minTop   = popup.offsetHeight/2;
                let maxTop   = window.top.innerHeight - popup.offsetHeight/2;

                objNormLeft += event.clientX - mousePosX;
                objNormTop  += event.clientY - mousePosY;
        
                if (objNormLeft < minLeft) objNormLeft = minLeft;
                if (objNormLeft > maxLeft) objNormLeft = maxLeft;
        
                if (objNormTop  < minTop)  objNormTop  = minTop;
                if (objNormTop  > maxTop)  objNormTop  = maxTop;
                
                popup.style.left = 100 * objNormLeft/window.top.innerWidth + "%";
                popup.style.top  = 100 * objNormTop/window.top.innerHeight + "%";
        
                mousePosX    = event.clientX;
                mousePosY    = event.clientY;
            }

            function mouseUpCallback(event) {            
                window.top.document.removeEventListener("mousemove", mouseMoveCallback);
                window.top.document.removeEventListener("mouseup",   mouseUpCallback);
            }

            window.top.document.addEventListener("mousemove", mouseMoveCallback);
            window.top.document.addEventListener("mouseup",   mouseUpCallback);
        });
    }

    /*---------------------------------------------------------------------------------*/
    trapFocus() {
        const focusElements = Array.from(this.handle.querySelectorAll('button, input, select, [contenteditable]'))
            .filter(el => !el.disabled && el.tabIndex !== -1);
    
        if (focusElements.length === 0) return;
    
        const handleKeyDown = (event) => {
            if (event.key === 'Tab') {
                const activeElement = window.top.document.activeElement;
                let currentIndex = focusElements.indexOf(activeElement);
                currentIndex = (currentIndex === -1) ? 0 : currentIndex;
    
                event.preventDefault();
    
                let nextIndex;
                if (event.shiftKey) {
                    nextIndex = (currentIndex - 1 + focusElements.length) % focusElements.length;
                } else {
                    nextIndex = (currentIndex + 1) % focusElements.length;
                }
    
                focusElements[nextIndex].focus();
            }
        };
    
        this.handle.addEventListener('keydown', handleKeyDown);
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