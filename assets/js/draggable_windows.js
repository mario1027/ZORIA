/**
 * Sistema de ventanas arrastrables tipo escritorio
 * Para Terminal CLI y Wizard de Calibración
 */

(function() {
    'use strict';
    
    // Estado global de las ventanas
    const windows = new Map();
    let zIndexCounter = 10000;
    let activeWindow = null;
    
    /**
     * Inicializa el sistema cuando el DOM está listo
     * Permite re-inicialización para páginas SPA
     */
    function initSystem() {
        console.log('[DraggableWindows] Sistema listo (sin auto-inicialización)');
        // NO auto-inicializar ventanas
        // Las ventanas se inicializarán SOLO cuando Dash las muestre (display: flex)
    }
    
    /**
     * Inicializa una ventana arrastrable
     * @param {string} windowId - ID del contenedor de la ventana
     * @param {string} headerId - ID del header arrastrable
     * @param {Object} options - Opciones adicionales
     */
    function initDraggableWindow(windowId, headerId, options = {}) {
        const win = document.getElementById(windowId);
        const header = document.getElementById(headerId);
        
        if (!win || !header) {
            console.warn(`[DraggableWindows] Ventana no encontrada: ${windowId} o ${headerId}`);
            return false;
        }
        
        // Si ya está inicializada, no hacer nada
        if (windows.has(windowId)) {
            console.log(`[DraggableWindows] Ventana ya inicializada (skipping): ${windowId}`);
            return true;
        }
        
        console.log(`[DraggableWindows] Inicializando ventana: ${windowId}`);
        
        // Obtener dimensiones reales del elemento
        const computedStyle = window.getComputedStyle(win);
        const currentWidth = win.offsetWidth || parseInt(computedStyle.width) || options.width || 700;
        const currentHeight = win.offsetHeight || parseInt(computedStyle.height) || options.height || 500;
        
        console.log(`[DraggableWindows] Dimensiones detectadas para ${windowId}: ${currentWidth}x${currentHeight}`);
        
        // Estado de la ventana
        const state = {
            isDragging: false,
            isMinimized: false,
            isMaximized: false,
            x: options.x || (window.innerWidth - currentWidth) / 2,
            y: options.y || (window.innerHeight - currentHeight) / 2,
            width: currentWidth,
            height: currentHeight,
            prevWidth: currentWidth,
            prevHeight: currentHeight,
            prevX: null,
            prevY: null,
            dragStartX: 0,
            dragStartY: 0,
            dragStartMouseX: 0,
            dragStartMouseY: 0
        };
        
        windows.set(windowId, { element: win, header: header, state: state, options: options });
        
        // Posición inicial (centrada)
        updateWindowPosition(win, state);
        
        // Eventos del header para arrastre
        header.addEventListener('mousedown', (e) => handleDragStart(e, windowId));
        header.addEventListener('touchstart', (e) => handleDragStart(e, windowId), { passive: false });
        header.addEventListener('selectstart', (e) => e.preventDefault());
        
        // Traer al frente al hacer clic
        win.addEventListener('mousedown', () => bringToFront(windowId));
        win.addEventListener('touchstart', () => bringToFront(windowId), { passive: true });
        
        // Configurar controles de ventana
        setupWindowControls(windowId);
        
        console.log(`[DraggableWindows] ✅ Ventana ${windowId} inicializada correctamente`);
        
        return true;
    }
    
    /**
     * Inicia el arrastre
     */
    function handleDragStart(e, windowId) {
        const winData = windows.get(windowId);
        if (!winData) return;
        
        const { element, header, state } = winData;
        
        // No arrastrar si está maximizado
        if (state.isMaximized) return;
        
        // No arrastrar si se hizo clic en un botón
        if (e.target.closest('button')) return;
        
        e.preventDefault();
        
        state.isDragging = true;
        state.dragStartX = state.x;
        state.dragStartY = state.y;
        
        const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
        const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY;
        
        state.dragStartMouseX = clientX;
        state.dragStartMouseY = clientY;
        
        // Agregar clase de arrastre
        element.classList.add('window-dragging');
        document.body.classList.add('window-dragging-active');
        
        // Traer al frente
        bringToFront(windowId);
        
        // Agregar eventos globales
        document.addEventListener('mousemove', handleDragMove);
        document.addEventListener('mouseup', handleDragEnd);
        document.addEventListener('touchmove', handleDragMove, { passive: false });
        document.addEventListener('touchend', handleDragEnd);
        
        // Guardar referencia a la ventana activa
        activeWindow = windowId;
    }
    
    /**
     * Durante el arrastre
     */
    function handleDragMove(e) {
        if (!activeWindow) return;
        
        const winData = windows.get(activeWindow);
        if (!winData || !winData.state.isDragging) return;
        
        e.preventDefault();
        
        const { element, state } = winData;
        
        const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
        const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY;
        
        // Calcular nueva posición
        let newX = state.dragStartX + (clientX - state.dragStartMouseX);
        let newY = state.dragStartY + (clientY - state.dragStartMouseY);
        
        // Limites de la ventana (permitir parcialmente fuera)
        const maxX = window.innerWidth - 50;
        const maxY = window.innerHeight - 50;
        
        newX = Math.max(-element.offsetWidth + 150, Math.min(newX, maxX));
        newY = Math.max(0, Math.min(newY, maxY));
        
        state.x = newX;
        state.y = newY;
        
        updateWindowPosition(element, state);
    }
    
    /**
     * Termina el arrastre
     */
    function handleDragEnd(e) {
        if (!activeWindow) return;
        
        const winData = windows.get(activeWindow);
        if (winData) {
            winData.state.isDragging = false;
            winData.element.classList.remove('window-dragging');
        }
        
        document.body.classList.remove('window-dragging-active');
        
        // Remover eventos globales
        document.removeEventListener('mousemove', handleDragMove);
        document.removeEventListener('mouseup', handleDragEnd);
        document.removeEventListener('touchmove', handleDragMove);
        document.removeEventListener('touchend', handleDragEnd);
        
        activeWindow = null;
    }
    
    /**
     * Actualiza la posición visual de la ventana
     */
    function updateWindowPosition(element, state) {
        element.style.position = 'fixed';
        element.style.left = `${state.x}px`;
        element.style.top = `${state.y}px`;
        element.style.right = 'auto';
        element.style.bottom = 'auto';
        element.style.margin = '0';
        element.style.transform = 'none';
    }
    
    /**
     * Trae la ventana al frente
     */
    function bringToFront(windowId) {
        const winData = windows.get(windowId);
        if (!winData) return;
        
        zIndexCounter++;
        winData.element.style.zIndex = zIndexCounter;
        
        // Actualizar clase activa
        windows.forEach((data, id) => {
            data.element.classList.toggle('window-active', id === windowId);
        });
    }
    
    /**
     * Configura los controles de la ventana (minimizar, maximizar, cerrar)
     */
    function setupWindowControls(windowId) {
        const winData = windows.get(windowId);
        if (!winData) return;
        
        const { element, state } = winData;
        
        // Si ya se configuraron los controles, salir
        if (element.dataset.controlsConfigured === 'true') {
            console.log(`[DraggableWindows] Controles ya configurados: ${windowId}`);
            return;
        }
        
        console.log(`[DraggableWindows] Configurando controles para: ${windowId}`);
        
        // Botón minimizar
        const minimizeBtn = element.querySelector('.window-btn-minimize');
        if (minimizeBtn) {
            minimizeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                console.log(`[DraggableWindows] Minimizar: ${windowId}`);
                minimizeWindow(windowId);
            });
        }
        
        // Botón maximizar
        const maximizeBtn = element.querySelector('.window-btn-maximize');
        if (maximizeBtn) {
            maximizeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                console.log(`[DraggableWindows] Maximizar/Restaurar: ${windowId}`);
                toggleMaximize(windowId);
            });
        }
        
        // Botón cerrar
        const closeBtn = element.querySelector('.window-btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                console.log(`[DraggableWindows] Cerrar: ${windowId}`);
                closeWindow(windowId);
            });
        }
        
        // Marcar como configurado
        element.dataset.controlsConfigured = 'true';
        console.log(`[DraggableWindows] ✅ Controles configurados para: ${windowId}`);
    }
    
    /**
     * Minimiza la ventana
     */
    function minimizeWindow(windowId) {
        const winData = windows.get(windowId);
        if (!winData) return;
        
        const { element, state } = winData;
        state.isMinimized = !state.isMinimized;
        
        if (state.isMinimized) {
            element.classList.add('window-minimized');
            console.log(`[DraggableWindows] Ventana minimizada: ${windowId}`);
        } else {
            element.classList.remove('window-minimized');
            console.log(`[DraggableWindows] Ventana restaurada: ${windowId}`);
        }
        
        // Actualizar icono del botón
        const minimizeBtn = element.querySelector('.window-btn-minimize');
        if (minimizeBtn) {
            const icon = minimizeBtn.querySelector('i');
            if (icon) {
                icon.className = state.isMinimized ? 'fas fa-window-restore' : 'fas fa-minus';
            }
        }
    }
    
    /**
     * Maximiza/restaura la ventana
     */
    function toggleMaximize(windowId) {
        const winData = windows.get(windowId);
        if (!winData) {
            console.warn(`[DraggableWindows] No encontrado: ${windowId}`);
            return;
        }
        
        const { element, state } = winData;
        state.isMaximized = !state.isMaximized;
        
        if (state.isMaximized) {
            // Guardar estado actual
            state.prevX = state.x;
            state.prevY = state.y;
            state.prevWidth = element.offsetWidth;
            state.prevHeight = element.offsetHeight;
            
            console.log(`[DraggableWindows] Maximizando: ${state.prevWidth}x${state.prevHeight}`);
            
            // Maximizar
            element.classList.add('window-maximized');
            element.style.left = '0';
            element.style.top = '0';
            element.style.width = '100vw';
            element.style.height = '100vh';
            element.style.borderRadius = '0';
        } else {
            // Restaurar
            element.classList.remove('window-maximized');
            
            state.x = state.prevX || state.x;
            state.y = state.prevY || state.y;
            
            console.log(`[DraggableWindows] Restaurando: ${state.prevWidth}x${state.prevHeight}`);
            
            updateWindowPosition(element, state);
            element.style.width = (state.prevWidth || state.width) + 'px';
            element.style.height = (state.prevHeight || state.height) + 'px';
            element.style.borderRadius = '12px';
        }
        
        // Actualizar icono
        const maximizeBtn = element.querySelector('.window-btn-maximize');
        if (maximizeBtn) {
            const icon = maximizeBtn.querySelector('i');
            if (icon) {
                icon.className = state.isMaximized ? 'fas fa-compress' : 'fas fa-expand';
            }
        }
    }
    
    /**
     * Cierra la ventana
     */
    function closeWindow(windowId) {
        const winData = windows.get(windowId);
        if (!winData) return;
        
        winData.element.style.display = 'none';
        console.log(`[DraggableWindows] Ventana cerrada: ${windowId}`);
    }
    
    /**
     * Muestra una ventana
     */
    function showWindow(windowId) {
        const winData = windows.get(windowId);
        if (!winData) {
            // Intentar inicializar si existe en DOM
            const autoInitMap = {
                'command-modal': { headerId: 'terminal-header-drag', width: 700, height: 500 },
                'cal-wizard-modal': { headerId: 'cal-wizard-header', width: 750, height: 580 },
                'connect-modal': { headerId: 'connect-modal-header', width: 380, height: 420 },
                'chart-modal': { headerId: 'chart-modal-header-drag', width: 900, height: 650 }
            };
            
            if (autoInitMap[windowId]) {
                const { headerId, width, height } = autoInitMap[windowId];
                const win = document.getElementById(windowId);
                const header = document.getElementById(headerId);
                if (win && header) {
                    initDraggableWindow(windowId, headerId, { width, height });
                    return showWindow(windowId);
                }
            }
            
            // Si no está en autoInitMap pero existe en DOM, intentar auto-detectar header
            const win = document.getElementById(windowId);
            if (win) {
                const header = win.querySelector('[id*="header"]') || win.firstElementChild;
                if (header && header.id) {
                    initDraggableWindow(windowId, header.id, { width: 900, height: 650 });
                    return showWindow(windowId);
                }
            }
            return;
        }
        
        const { element, state } = winData;
        element.style.display = 'flex';
        bringToFront(windowId);
        
        // Centrar si es la primera vez
        if (state.x === 0 && state.y === 0) {
            state.x = (window.innerWidth - element.offsetWidth) / 2;
            state.y = (window.innerHeight - element.offsetHeight) / 2;
            updateWindowPosition(element, state);
        }
        
        console.log(`[DraggableWindows] Ventana mostrada: ${windowId}`);
    }
    
    /**
     * Verifica si una ventana ya está inicializada
     */
    function isInitialized(windowId) {
        return windows.has(windowId);
    }
    
    // Exponer API global
    window.DraggableWindows = {
        init: initDraggableWindow,
        show: showWindow,
        close: closeWindow,
        minimize: minimizeWindow,
        maximize: toggleMaximize,
        bringToFront: bringToFront,
        isInitialized: isInitialized,
        reinit: initSystem  // Permitir re-inicialización manual
    };
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSystem);
    } else {
        // DOM ya está listo, inicializar con delay
        setTimeout(initSystem, 100);
    }
    
    // También intentar inicializar en window.load
    window.addEventListener('load', () => {
        setTimeout(initSystem, 500);
    });
    
    // Observar cambios en el DOM para re-inicializar ventanas cuando Dash renderiza páginas
    // DESHABILITADO TEMPORALMENTE PARA DEBUG
    /*
    let reinitTimeout = null;
    const observer = new MutationObserver((mutations) => {
        // Verificar si se agregaron elementos relevantes
        let needsReinit = false;
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) {  // Element node
                    // Si se agregó una ventana modal específica
                    if (node.id && (node.id === 'command-modal' || node.id === 'cal-wizard-modal' || node.id === 'chart-modal')) {
                        needsReinit = true;
                        console.log(`[DraggableWindows] Detectada nueva ventana en DOM: ${node.id}`);
                    }
                    // O si contiene ventanas modales específicas
                    if (node.querySelector) {
                        const modals = node.querySelectorAll('#command-modal, #cal-wizard-modal, #chart-modal');
                        if (modals.length > 0) {
                            needsReinit = true;
                            console.log(`[DraggableWindows] Detectadas ${modals.length} ventanas en nuevo contenedor`);
                        }
                    }
                }
            });
        });
        
        if (needsReinit) {
            // Usar debounce para evitar múltiples re-inicializaciones
            if (reinitTimeout) clearTimeout(reinitTimeout);
            reinitTimeout = setTimeout(() => {
                console.log('[DraggableWindows] DOM cambió, re-inicializando...');
                initSystem();
            }, 300);
        }
    });
    
    // Observar cambios en el body
    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    */
   console.log('[DraggableWindows] MutationObserver deshabilitado para debug');
    
})();
