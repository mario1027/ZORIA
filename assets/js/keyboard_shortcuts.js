/**
 * Keyboard Shortcuts Handler
 * 
 * Maneja atajos de teclado globales para la aplicación ZORIA.
 * Incluye Alt+T para abrir/cerrar terminal y otros atajos futuros.
 * 
 * @author Mario Ricardo Montero
 * @license MIT
 */

(function() {
    'use strict';
    
    // Bandera para evitar múltiples inicializaciones
    let initialized = false;
    
    /**
     * Toggle del terminal CLI
     */
    function toggleTerminal() {
        const terminal = document.getElementById('command-modal');
        const floatingBtn = document.getElementById('floating-terminal-btn');
        const sidebarBtn = document.getElementById('sidebar-terminal-btn');
        
        if (!terminal) {
            console.warn('[KeyboardShortcuts] Terminal modal no encontrado');
            return;
        }
        
        const isVisible = terminal.style.display === 'flex';
        
        if (isVisible) {
            // Cerrar terminal
            terminal.style.display = 'none';
            console.log('[KeyboardShortcuts] Terminal cerrado con Alt+T');
        } else {
            // Abrir terminal - simular clic en el botón flotante para activar callbacks de Dash
            if (floatingBtn) {
                floatingBtn.click();
                console.log('[KeyboardShortcuts] Terminal abierto con Alt+T (vía floating button)');
            } else if (sidebarBtn) {
                sidebarBtn.click();
                console.log('[KeyboardShortcuts] Terminal abierto con Alt+T (vía sidebar button)');
            } else {
                // Fallback: abrir directamente
                terminal.style.display = 'flex';
                console.log('[KeyboardShortcuts] Terminal abierto con Alt+T (directo)');
                
                // Enfocar input si existe
                setTimeout(() => {
                    const input = document.getElementById('command-input');
                    if (input) {
                        input.focus();
                    }
                }, 100);
            }
        }
    }
    
    /**
     * Manejador principal de eventos de teclado
     */
    function handleKeydown(event) {
        // Alt+T: Toggle Terminal
        if (event.altKey && (event.key === 't' || event.key === 'T')) {
            // Prevenir comportamientos por defecto
            event.preventDefault();
            event.stopPropagation();
            
            toggleTerminal();
            return false;
        }
        
        // Aquí se pueden agregar más atajos en el futuro
        // Ejemplo: Ctrl+K para búsqueda, Ctrl+B para sidebar, etc.
    }
    
    /**
     * Función de inicialización
     */
    function init() {
        if (initialized) {
            console.log('[KeyboardShortcuts] Ya inicializado - skipping');
            return;
        }
        
        console.log('[KeyboardShortcuts] Inicializando atajos de teclado...');
        
        // Registrar event listener global
        document.addEventListener('keydown', handleKeydown, true);
        
        initialized = true;
        console.log('[KeyboardShortcuts] ✅ Atajos de teclado inicializados');
        console.log('[KeyboardShortcuts] Disponibles:');
        console.log('  - Alt+T: Abrir/Cerrar Terminal CLI');
    }
    
    /**
     * Función de limpieza (por si se necesita desregistrar)
     */
    function cleanup() {
        if (!initialized) {
            return;
        }
        
        document.removeEventListener('keydown', handleKeydown, true);
        initialized = false;
        console.log('[KeyboardShortcuts] ⚠️ Atajos de teclado desregistrados');
    }
    
    // Exportar a window para acceso global
    window.KeyboardShortcuts = {
        init: init,
        cleanup: cleanup,
        toggleTerminal: toggleTerminal
    };
    
    // Auto-inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // DOM ya está listo
        init();
    }
    
    // Reinicializar en cada carga (útil para Dash SPA con navegación)
    window.addEventListener('load', () => {
        if (!initialized) {
            setTimeout(init, 500);
        }
    });
    
})();
