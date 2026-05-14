"""
ZORIA Dashboard - Aplicación principal

Dashboard web interactivo para análisis de impedancia y caracterización de circuitos.
Utiliza Dash/Plotly para visualización y se comunica con dispositivos ADMX2001 vía serial.

Author: Mario Ricardo Montero, Juan Carlos Alvarez, Francisco J. Racedo N.
Email: mariomontero942@gmail.com 
License: MIT
"""

# =============================================================================
# IMPORTS ESTÁNDAR
# =============================================================================
import os
import logging
import sys
from pathlib import Path
from typing import Optional

# =============================================================================
# IMPORTS DE TERCEROS
# =============================================================================
from dash_spa import DashSPA, page_container
from dash import html, dcc

# =============================================================================
# IMPORTS LOCALES
# =============================================================================
from themes import VOLT


# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================
def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    """
    Configura el sistema de logging de la aplicación.
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR). 
                  Si es None, usa la variable de entorno LOG_LEVEL o INFO por defecto.
    
    Returns:
        Logger configurado para la aplicación.
    """
    level = (log_level or os.environ.get("LOG_LEVEL", "INFO")).upper()
    
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    return logging.getLogger(__name__)


# =============================================================================
# CONFIGURACIÓN DE RECURSOS (SOPORTE OFFLINE)
# =============================================================================
# Estas dependencias están descargadas localmente en assets/vendor/
# para permitir el funcionamiento sin conexión a internet.

EXTERNAL_STYLESHEETS = [
    # Los CSS se sirven automáticamente desde assets/ por Dash.
    # No se duplican aquí para evitar cargas redundantes.
    # El orden de carga es alphabético: vendor/ < css/ (volt → zoria-tokens → resto)
]

EXTERNAL_SCRIPTS = [
    # Bootstrap 5 JS (local)
    "/assets/vendor/js/bootstrap.bundle.min.js",
    # SweetAlert2 para modales mejorados (local)
    "/assets/vendor/js/sweetalert2.all.min.js",
    # Notyf para notificaciones (local)
    "/assets/vendor/js/notyf.min.js",
    # Sistema de ventanas arrastrables (local)
    "/assets/js/draggable_windows.js",
    # Atajos de teclado globales (local)
    "/assets/js/keyboard_shortcuts.js",
    # Mermaid.js para diagramas (UMD build local — expone window.mermaid)
    "/assets/vendor/js/mermaid.min.js",
]

# =============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# =============================================================================
DEFAULT_CONFIG = {
    "title": "ZORIA Dashboard",
    "assets_folder": "assets",
    "favicon": "logo.png",
    "port": 8050,
    "host": "localhost",
    "debug": True,
    "use_reloader": False,
}


def register_global_connection_callbacks(app):
    """
    Registra los callbacks globales de conexión del sidebar.
    Estos callbacks controlan la conexión/desconexión del dispositivo ADMX2001
    desde el sidebar, disponible en todas las páginas.
    """
    from dash import Input, Output, State, ctx
    from dash.exceptions import PreventUpdate
    import serial.tools.list_ports
    import time
    from lib.device_state import device_state
    from lib import ADMX2001
    from lib.utils import get_preferred_usb_serial_ports, is_likely_admx_port
    
    logger = logging.getLogger(__name__)
    
    # Variable para rastrear si ya se intentó la auto-conexión
    auto_connect_attempted = {'flag': False}

    # =========================================================================
    # CALLBACK ÚNICO DE CONEXIÓN - Sidebar (disponible en todas las páginas)
    # =========================================================================
    @app.callback(
        [Output('sidebar-connection-text', 'children', allow_duplicate=True),
         Output('sidebar-connection-dot', 'className', allow_duplicate=True),
         Output('sidebar-device-port', 'children', allow_duplicate=True),
         Output('sidebar-disconnect-btn', 'disabled', allow_duplicate=True),
         Output('connection-error-trigger', 'data', allow_duplicate=True),
         Output('connection-success-trigger', 'data', allow_duplicate=True)],
        [Input('sidebar-quick-connect-btn', 'n_clicks'),
         Input('sidebar-disconnect-btn', 'n_clicks'),
         Input('auto-connect-on-start', 'data')],
        State('autoconn-store', 'data'),
        prevent_initial_call=True
    )
    def sidebar_connection_handler(sidebar_quick_clicks, sidebar_disconnect_clicks, auto_start, autoconn_pref):
        """
        Callback de conexión desde el sidebar (disponible globalmente):
        - Conexión rápida sidebar (sidebar-quick-connect-btn) 
        - Auto-conexión al inicio (auto-connect-on-start)
        - Desconexión (sidebar-disconnect-btn)
        """
        triggered = ctx.triggered_id
        logger.info(f"Sidebar connection handler triggered by: {triggered}, auto_start={auto_start}")
        
        # Ignorar auto-connect si ya se intentó anteriormente
        if triggered == 'auto-connect-on-start' and auto_connect_attempted['flag']:
            logger.info("Auto-connect ya fue intentado, ignorando ejecución duplicada")
            raise PreventUpdate
        
        # Respetar preferencia: si autoconn-store es False, no auto-conectar
        if triggered == 'auto-connect-on-start' and autoconn_pref is False:
            logger.info("Auto-connect omitido: preferencia del usuario desactivada")
            raise PreventUpdate

        # Marcar que se intentó auto-connect
        if triggered == 'auto-connect-on-start':
            auto_connect_attempted['flag'] = True
        
        # Ignorar si auto_start es True pero no fue el trigger activo
        # Esto evita re-ejecuciones cuando otros botones se presionan
        # EXCEPCIÓN: permitir que la desconexión siempre proceda
        if triggered != 'auto-connect-on-start' and triggered != 'sidebar-disconnect-btn' and auto_start is True:
            # auto-connect-on-start está en True pero no fue quien disparó este callback
            # Solo actualizar estado sin intentar conectar de nuevo
            if device_state.is_connected and device_state.device is not None:
                is_conn, status_msg, port_info = device_state.verify_connection()
                if is_conn:
                    return ("Conectado", "connection-pulse connected",
                            port_info if port_info else "ADMX2001",
                            False, False, False)
            return ("Desconectado", "connection-pulse disconnected",
                    "ADMX2001", True, False, False)
        
        # Si ya está conectado y no es desconexión, mostrar estado
        if triggered != 'sidebar-disconnect-btn':
            if device_state.is_connected and device_state.device is not None:
                is_conn, status_msg, port_info = device_state.verify_connection()
                if is_conn:
                    return ("Conectado", "connection-pulse connected",
                            port_info if port_info else "ADMX2001",
                            False, False, False)
        
        # ===== DESCONEXIÓN =====
        if triggered == 'sidebar-disconnect-btn':
            try:
                if device_state.device:
                    device_state.device.close()
                device_state.set_device(None, False)
                logger.info("Dispositivo desconectado")
                return ("Desconectado", "connection-pulse disconnected",
                        "ADMX2001", True, False, False)
            except Exception as e:
                logger.error(f"Error desconectando: {e}")
                # NO activar error modal - desconexión fallida no es crítica
                return ("Error", "connection-pulse error",
                        "ADMX2001", True, False, False)
        
        # ===== CONEXIÓN RÁPIDA / AUTO =====
        if triggered in ['sidebar-quick-connect-btn', 'auto-connect-on-start']:
            # Mostrar error modal solo si hubo un intento real sobre un adaptador detectado.
            # Si no hay dispositivo/adaptador conectado, solo actualizar el estado visual.
            is_manual_quick_connect = (triggered == 'sidebar-quick-connect-btn')
            logger.info(
                f"Iniciando conexión, is_manual_quick_connect={is_manual_quick_connect}"
            )
            
            # Adquirir lock para evitar conexiones simultáneas
            if not device_state._operation_lock.acquire(blocking=False):
                logger.warning("Otra operación en curso, saltando intento de conexión")
                return ("Ocupado", "connection-pulse disconnected",
                        "ADMX2001", True, False, False)
            
            try:
                logger.info("Iniciando conexión automática...")
                all_ports = list(serial.tools.list_ports.comports())
                usb_ports = get_preferred_usb_serial_ports(all_ports)
                
                if not usb_ports:
                    logger.warning("No hay puertos USB disponibles")
                    return ("Sin puertos USB", "connection-pulse disconnected",
                            "ADMX2001", True, False, False)
                
                logger.info(f"Puertos USB detectados: {[p.device for p in usb_ports]}")
                
                ports_to_try = [p for p in usb_ports if is_likely_admx_port(p)]
                if not ports_to_try and usb_ports:
                    ports_to_try = usb_ports[:1]

                if not ports_to_try:
                    logger.warning("No se encontró adaptador USB TTL232R-3V3")
                    return ("No detectado", "connection-pulse disconnected",
                            "TTL232R-3V3", True, False, False)

                logger.info(
                    f"Probando {len(ports_to_try)} puerto(s) USB TTL232R-3V3: "
                    f"{[p.device for p in ports_to_try[:8]]}"
                )

                attempted_candidate_connection = False

                # Probar primero el adaptador TTL preferido; si no aparece exacto, usar el mejor USB.
                for p in ports_to_try[:2]:
                    attempted_candidate_connection = True
                    try:
                        logger.info(f"Probando {p.device}...")
                        dev = ADMX2001(p.device, baudrate=115200, timeout=1.2)
                        
                        resp = dev.send_command('*idn')
                        logger.info(f"Respuesta: {resp}")
                        
                        if resp and any(x in str(resp).upper() for x in ['ADMX', '2001', 'ANALOG']):
                            dev.set_mdelay(1)
                            dev.set_tdelay(0)
                            device_state.set_device(dev, True)
                            logger.info(f"Conectado a {p.device}")
                            return ("Conectado", "connection-pulse connected",
                                    p.device, False, False, True)
                        else:
                            dev.close()
                    except Exception as e:
                        logger.warning(f"Falló {p.device}: {e}")
                        continue
                
                logger.warning("No se encontró dispositivo ADMX2001")
                return ("No detectado", "connection-pulse disconnected",
                        "ADMX2001", True,
                        is_manual_quick_connect and attempted_candidate_connection,
                        False)
                
            except Exception as e:
                logger.error(f"Error autoconnect: {e}")
                return ("Error", "connection-pulse error",
                        "ADMX2001", True, False, False)
            
            finally:
                # Liberar lock de operación
                device_state._operation_lock.release()
        
        return ("Desconectado", "connection-pulse disconnected",
                "ADMX2001", True, False, False)

    # =========================================================================
    # MONITOR ACTIVO DE CONEXIÓN - Verifica estado real periódicamente
    # =========================================================================
    @app.callback(
        [Output('sidebar-connection-text', 'children', allow_duplicate=True),
         Output('sidebar-connection-dot', 'className', allow_duplicate=True),
         Output('sidebar-device-port', 'children', allow_duplicate=True),
         Output('sidebar-disconnect-btn', 'disabled', allow_duplicate=True)],
        Input('connection-monitor-interval', 'n_intervals'),
        prevent_initial_call=True
    )
    def monitor_connection_health(n_intervals):
        """
        Monitorea activamente la salud de la conexión cada 5 segundos.
        Verifica que el dispositivo siga respondiendo y actualiza el badge y sidebar.
        """
        if n_intervals is None or n_intervals == 0:
            raise PreventUpdate
        
        try:
            # Verificar estado real del dispositivo
            is_conn, status_msg, port = device_state.verify_connection()
            
            if is_conn:
                # Dispositivo conectado y respondiendo
                return ("Conectado", "connection-pulse connected",
                        port if port else "ADMX2001", False)
            else:
                # Dispositivo no responde, actualizar estado
                if status_msg == "Puerto cerrado":
                    return ("Error", "connection-pulse error",
                            "Puerto cerrado", True)
                elif status_msg == "Sin respuesta":
                    return ("Sin respuesta", "connection-pulse error",
                            "Sin respuesta", True)
                else:
                    return ("Desconectado", "connection-pulse disconnected",
                            "ADMX2001", True)
        
        except Exception as e:
            logger.error(f"Error en monitor de conexión: {e}")
            raise PreventUpdate

    # =========================================================================
    # AUTO-CONNECT TRIGGER - Activa auto-conexión al iniciar
    # =========================================================================
    @app.callback(
        Output('auto-connect-on-start', 'data'),
        Input('ports-interval', 'n_intervals'),
        State('autoconn-store', 'data'),
        prevent_initial_call=True
    )
    def trigger_auto_connect(n_intervals, autoconn_pref):
        """Trigger para auto-conexión al iniciar (solo una vez)"""
        if n_intervals == 1 and not device_state.is_connected:
            # Respetar preferencia del usuario; si el store nunca fue configurado
            # (None o False por defecto), igualmente intentar conectar
            if autoconn_pref is False:
                logger.info("Auto-connect desactivado por preferencia del usuario")
                raise PreventUpdate
            logger.info("Activando auto-connect al inicio (n_intervals=1)")
            return True
        raise PreventUpdate


def register_global_terminal_callbacks(app):
    """
    Registra los callbacks globales del terminal CLI.
    Estos callbacks están disponibles en todas las páginas.
    """
    from dash import Input, Output, State, ctx, html
    from dash.exceptions import PreventUpdate
    from datetime import datetime
    from lib.device_state import device_state
    
    # Clientside callback para inicializar terminal (teclado + arrastre)
    app.clientside_callback(
        """
        function(style) {
            console.log('[Terminal] Callback ejecutado, style:', style);
            
            // Solo ejecutar cuando está visible
            if (!style || style.display !== 'flex') {
                return window.dash_clientside.no_update;
            }
            
            console.log('[Terminal] Ventana mostrada, inicializando...');
            
            setTimeout(function() {
                var input = document.getElementById('command-input');
                var terminal = document.getElementById('command-modal');
                
                if (!input || !terminal) {
                    console.warn('[Terminal] Elementos no encontrados');
                    return;
                }
                
                // === INICIALIZAR TECLADO ===
                // Dash 3.x almacena dcc.Store(storage_type='session') en sessionStorage directamente
                function readHistory() {
                    try {
                        var raw = sessionStorage.getItem('command-history-store');
                        return raw ? JSON.parse(raw) : {'commands': [], 'index': -1};
                    } catch(err) {
                        return {'commands': [], 'index': -1};
                    }
                }
                function writeHistory(commands, index) {
                    try {
                        sessionStorage.setItem('command-history-store', JSON.stringify({'commands': commands, 'index': index}));
                        sessionStorage.setItem('command-history-store-timestamp', Date.now().toString());
                    } catch(err) {}
                }
                
                // Setear valor en input React (controlled component): requiere el native setter
                // para que React detecte el cambio y el callback n_submit reciba el valor correcto.
                function setReactInputValue(inputEl, val) {
                    var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeSetter.call(inputEl, val);
                    inputEl.dispatchEvent(new Event('input', { bubbles: true }));
                }
                
                input.onkeydown = function(e) {
                    var historyData = readHistory();
                    var commands = historyData.commands || [];
                    var currentIndex = historyData.index;
                    if (currentIndex === undefined || currentIndex < 0) currentIndex = commands.length;
                    
                    if (e.key === 'Enter') {
                        return;
                    }
                    
                    if (e.key === 'ArrowUp') {
                        e.preventDefault();
                        if (commands.length > 0 && currentIndex > 0) {
                            currentIndex--;
                            setReactInputValue(input, commands[currentIndex]);
                            writeHistory(commands, currentIndex);
                        }
                        return false;
                    }
                    
                    if (e.key === 'ArrowDown') {
                        e.preventDefault();
                        if (currentIndex < commands.length - 1) {
                            currentIndex++;
                            setReactInputValue(input, commands[currentIndex]);
                            writeHistory(commands, currentIndex);
                        } else if (currentIndex === commands.length - 1) {
                            currentIndex = commands.length;
                            setReactInputValue(input, '');
                            writeHistory(commands, currentIndex);
                        }
                        return false;
                    }
                    
                    if (e.key === 'Escape') {
                        if (input.value === '') {
                            terminal.style.display = 'none';
                        } else {
                            input.value = '';
                        }
                        return false;
                    }
                    
                    if (e.key === 'l' && e.ctrlKey) {
                        e.preventDefault();
                        var clearBtn = document.getElementById('clear-terminal-btn');
                        if (clearBtn) clearBtn.click();
                        return false;
                    }
                };
                
                // === INICIALIZAR SISTEMA DE ARRASTRE ===
                terminal.classList.remove('terminal-hidden-initial');
                
                if (!window.DraggableWindows) {
                    console.error('[Terminal] DraggableWindows no disponible');
                    return;
                }
                
                if (window.DraggableWindows.isInitialized('command-modal')) {
                    console.log('[Terminal] Ya inicializado - traer al frente');
                    window.DraggableWindows.bringToFront('command-modal');
                } else {
                    console.log('[Terminal] Inicializando sistema de arrastre...');
                    var success = window.DraggableWindows.init('command-modal', 'terminal-header-drag', {
                        width: 700,
                        height: 500
                    });
                    
                    if (success) {
                        console.log('[Terminal] Sistema inicializado');
                    }
                }
                
                // Enfocar input
                setTimeout(function() {
                    if (input) {
                        input.focus();
                    }
                }, 100);
                
            }, 250);
            
            return window.dash_clientside.no_update;
        }
        """,
        Output('terminal-drag-init', 'data'),
        Input('command-modal', 'style')
    )
    
    # Callback para abrir/cerrar terminal desde cualquier página
    @app.callback(
        Output('command-modal', 'style', allow_duplicate=True),
        Output('command-modal', 'className', allow_duplicate=True),
        Input('sidebar-terminal-btn', 'n_clicks'),
        Input('floating-terminal-btn', 'n_clicks'),
        Input('terminal-close-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def toggle_terminal_sidebar(sidebar_clicks, floating_clicks, close_clicks):
        """Abre o cierra el terminal desde cualquier botón"""
        if not ctx.triggered:
            raise PreventUpdate
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Solo abrir cuando se hace clic específicamente en los botones de abrir
        if triggered_id in ['sidebar-terminal-btn', 'floating-terminal-btn']:
            if (triggered_id == 'sidebar-terminal-btn' and sidebar_clicks and sidebar_clicks > 0) or \
               (triggered_id == 'floating-terminal-btn' and floating_clicks and floating_clicks > 0):
                return {'display': 'flex'}, 'draggable-window terminal-window'
        # Cerrar por botón de cerrar
        elif triggered_id == 'terminal-close-btn' and close_clicks and close_clicks > 0:
            return {'display': 'none'}, 'draggable-window terminal-window'
        
        raise PreventUpdate
    
    # Callback clientside para inicializar ventana arrastrable del Terminal cuando se muestra
    app.clientside_callback(
        """
        function(style) {
            if (style && (style.display === 'flex' || style.display === 'block')) {
                // Dar tiempo a que el DOM se actualice
                setTimeout(function() {
                    if (window.DraggableWindows && !window.DraggableWindows.isInitialized('command-modal')) {
                        window.DraggableWindows.init('command-modal', 'terminal-header-drag', {width: 700, height: 500});
                        window.DraggableWindows.show('command-modal');
                    } else if (window.DraggableWindows) {
                        window.DraggableWindows.show('command-modal');
                    }
                }, 100);
            }
            return 1;
        }
        """,
        Output('terminal-initialized', 'data'),
        Input('command-modal', 'style'),
        prevent_initial_call=True
    )
    
    # Clientside callback: sync data-system-state from badge-connection data-state
    app.clientside_callback(
        """
        function(conState) {
            var terminal = document.getElementById('command-modal');
            if (terminal) {
                terminal.setAttribute('data-system-state', conState || 'idle');
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output('terminal-drag-init', 'data', allow_duplicate=True),
        Input('badge-connection', 'data-state'),
        prevent_initial_call=True
    )
    
    # Callback clientside para auto-scroll del terminal cuando se actualiza el output
    app.clientside_callback(
        """
        function(children) {
            if (!children || children.length === 0) {
                return window.dash_clientside.no_update;
            }
            
            // Hacer scroll suave hacia abajo después de un pequeño delay
            setTimeout(function() {
                var terminalScreen = document.querySelector('.terminal-float-screen');
                if (terminalScreen) {
                    terminalScreen.scrollTo({
                        top: terminalScreen.scrollHeight,
                        behavior: 'smooth'
                    });
                }
            }, 50);
            
            return window.dash_clientside.no_update;
        }
        """,
        Output('terminal-scroll-trigger', 'data'),
        Input('command-output', 'children')
    )
    
    # Callback para actualizar indicador de estado del terminal + badges + system-state
    @app.callback(
        [Output('terminal-status-text', 'children'),
         Output('terminal-port-label', 'children'),
         Output('badge-connection-value', 'children'),
         Output('badge-connection', 'data-state'),
         Output('badge-port-value', 'children'),
         Output('badge-port', 'data-state'),
         Output('badge-baud-value', 'children'),
         Output('badge-baud', 'data-state'),
         Output('badge-sweep-value', 'children'),
         Output('badge-sweep', 'data-state')],
        Input('command-modal', 'style'),
        prevent_initial_call=True
    )
    def update_terminal_status(style):
        """Actualiza indicador de conexion, badges de telemetria y system-state"""
        if style and style.get('display') == 'flex':
            is_conn, status_msg, port = device_state.verify_connection(force=False)
            is_streaming = device_state.is_streaming_in_progress()
            is_sweep = device_state.is_sweep_in_progress()
            
            if is_streaming or is_sweep:
                status_text = "streaming"
                port_text = port or "\u2014"
                con_state = "streaming"
                port_state = "connected" if port else "idle"
                sweep_val = "active" if is_sweep else "\u2014"
                sweep_state = "streaming" if is_sweep else "idle"
                baud_val = "115200" if is_conn else "\u2014"
                baud_state = "connected" if is_conn else "idle"
            elif is_conn:
                status_text = "connected"
                port_text = port or "ADMX2001"
                con_state = "connected"
                port_state = "connected" if port else "idle"
                sweep_val = "\u2014"
                sweep_state = "idle"
                baud_val = "115200"
                baud_state = "connected"
            else:
                status_text = "disconnected"
                port_text = "\u2014"
                con_state = "disconnected"
                port_state = "disconnected"
                sweep_val = "\u2014"
                sweep_state = "disconnected"
                baud_val = "\u2014"
                baud_state = "disconnected"
            
            return (status_text, port_text,
                    status_text, con_state,
                    port_text, port_state,
                    baud_val, baud_state,
                    sweep_val, sweep_state)
        
        return ("", "\u2014",
                "\u2014", "idle",
                "\u2014", "idle",
                "\u2014", "idle",
                "\u2014", "idle")
    
    # Periodic update of terminal status bar badges
    @app.callback(
        [Output('terminal-status-text', 'children', allow_duplicate=True),
         Output('terminal-port-label', 'children', allow_duplicate=True),
         Output('badge-connection-value', 'children', allow_duplicate=True),
         Output('badge-connection', 'data-state', allow_duplicate=True),
         Output('badge-port-value', 'children', allow_duplicate=True),
         Output('badge-port', 'data-state', allow_duplicate=True),
         Output('badge-baud-value', 'children', allow_duplicate=True),
         Output('badge-baud', 'data-state', allow_duplicate=True),
         Output('badge-sweep-value', 'children', allow_duplicate=True),
         Output('badge-sweep', 'data-state', allow_duplicate=True)],
        Input('connection-monitor-interval', 'n_intervals'),
        prevent_initial_call=True
    )
    def update_terminal_badges_periodic(n_intervals):
        """Actualiza badges de telemetria del terminal periodicamente"""
        is_conn, status_msg, port = device_state.verify_connection(force=False)
        is_streaming = device_state.is_streaming_in_progress()
        is_sweep = device_state.is_sweep_in_progress()
        
        if is_streaming or is_sweep:
            status_text = "streaming"
            port_text = port or "\u2014"
            con_state = "streaming"
            port_state = "connected" if port else "idle"
            sweep_val = "active" if is_sweep else "\u2014"
            sweep_state = "streaming" if is_sweep else "idle"
            baud_val = "115200" if is_conn else "\u2014"
            baud_state = "connected" if is_conn else "idle"
        elif is_conn:
            status_text = "connected"
            port_text = port or "ADMX2001"
            con_state = "connected"
            port_state = "connected" if port else "idle"
            sweep_val = "\u2014"
            sweep_state = "idle"
            baud_val = "115200"
            baud_state = "connected"
        else:
            status_text = "disconnected"
            port_text = "\u2014"
            con_state = "disconnected"
            port_state = "disconnected"
            sweep_val = "\u2014"
            sweep_state = "disconnected"
            baud_val = "\u2014"
            baud_state = "disconnected"
        
        return (status_text, port_text,
                status_text, con_state,
                port_text, port_state,
                baud_val, baud_state,
                sweep_val, sweep_state)
    
    # Callback de streaming - Poll de nuevas líneas cada 100ms
    @app.callback(
        [Output('command-output', 'children', allow_duplicate=True),
         Output('terminal-streaming-interval', 'disabled'),
         Output('terminal-streaming-state', 'data', allow_duplicate=True)],
        Input('terminal-streaming-interval', 'n_intervals'),
        [State('command-output', 'children'),
         State('terminal-streaming-state', 'data')],
        prevent_initial_call=True
    )
    def poll_streaming_lines(n_intervals, current_output, streaming_state):
        """
        Consulta nuevas líneas del streaming cada 100ms y las agrega al terminal.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Log para debugging del polling
        logger.info(f"[Terminal Poll] n_intervals={n_intervals}, streaming_active={streaming_state.get('active') if streaming_state else False}")
        
        if not streaming_state or not streaming_state.get('active'):
            raise PreventUpdate
        
        # Obtener nuevas líneas
        new_lines = device_state.get_streaming_lines()
        logger.info(f"[Terminal Poll] Recibidas {len(new_lines)} líneas nuevas")
        
        if not new_lines and not device_state.is_streaming_complete():
            # No hay nuevas líneas pero el comando sigue en progreso
            raise PreventUpdate
        
        # Normalizar output
        if current_output is None:
            current_output = []
        elif not isinstance(current_output, list):
            current_output = [current_output]
        
        # Procesar nuevas líneas
        appended_count = 0
        for line_data in new_lines:
            line_type = line_data.get('type')
            line_text = line_data.get('line', '')
            
            logger.info(f"[Terminal Poll] Procesando línea tipo={line_type}, texto='{line_text[:60]}'")
            
            if line_type == 'error':
                current_output.append(
                    html.Div([
                        html.Span("", className="terminal-error-icon"),
                        html.Span(f"Error: {line_text}", className="terminal-error-text")
                    ], className="terminal-line terminal-error-line")
                )
                appended_count += 1
            elif line_type == 'data' and line_text:
                # Filtrar eco del comando (doble check por si acaso)
                cmd = streaming_state.get('command', '').strip().lower()
                if line_text.strip().lower() == cmd:
                    logger.info(f"[Terminal Poll] Eco del comando filtrado: '{line_text}'")
                    continue
                
                # Determinar clase CSS
                line_lower = line_text.lower()
                if any(err in line_lower for err in ['error', 'fail', 'invalid', 'unknown']):
                    css_class = "terminal-response-line terminal-response-error"
                    prefix = html.Span("", className="terminal-error-icon")
                elif any(ok in line_lower for ok in ['ok', 'success', 'done', 'ready', 'pass']):
                    css_class = "terminal-response-line terminal-response-success"
                    prefix = html.Span("", className="terminal-success-icon")
                elif any(warn in line_lower for warn in ['warning', 'warn', 'caution']):
                    css_class = "terminal-response-line terminal-response-warning"
                    prefix = html.Span("", className="terminal-warning-icon")
                else:
                    css_class = "terminal-response-line"
                    prefix = html.Span("  ", className="terminal-indent")
                
                current_output.append(
                    html.Div([prefix, html.Span(line_text, className=css_class)], className="terminal-line")
                )
                appended_count += 1

        # Acumular cantidad de líneas realmente mostradas durante el streaming
        streaming_state['received'] = streaming_state.get('received', 0) + appended_count
        
        # Verificar si el comando terminó
        if device_state.is_streaming_complete():
            logger.info("[Terminal] Streaming completado, desactivando polling")

            # Si no se recibió ninguna línea útil, mostrar feedback explícito
            if streaming_state.get('received', 0) == 0:
                current_output.append(
                    html.Div([
                        html.Span("  ", className="terminal-indent"),
                        html.Span("(sin respuesta del dispositivo)", className="terminal-empty-response text-muted")
                    ], className="terminal-line")
                )
                current_output.append(
                    html.Div([
                        html.Span("", className="text-info"),
                        html.Span("Verifique que el comando sea correcto. Use ", className="text-muted"),
                        html.Code("help", className="terminal-code"),
                        html.Span(" para ver comandos disponibles.", className="text-muted")
                    ], className="terminal-line")
                )
            
            # Agregar separador
            current_output.append(html.Div(className="terminal-separator"))
            
            # Limitar output
            if len(current_output) > 500:
                current_output = current_output[-500:]
            
            # Desactivar streaming
            streaming_state['active'] = False
            return current_output, True, streaming_state  # True = deshabilitar Interval
        
        # Limitar output mientras va creciendo
        if len(current_output) > 500:
            current_output = current_output[-500:]
        
        # Continuar polling
        return current_output, False, streaming_state  # False = mantener Interval activo
    
    # Callback principal para manejar comandos del terminal
    @app.callback(
        [Output('command-output', 'children', allow_duplicate=True),
         Output('command-input', 'value', allow_duplicate=True),
         Output('command-history-store', 'data', allow_duplicate=True),
         Output('terminal-streaming-state', 'data', allow_duplicate=True),
         Output('terminal-streaming-interval', 'disabled', allow_duplicate=True),
         Output('terminal-password-state', 'data', allow_duplicate=True)],
        [Input('command-input', 'n_submit'),
         Input('quick-measure-btn', 'n_clicks'),
         Input('quick-help-btn', 'n_clicks'),
         Input('quick-status-btn', 'n_clicks'),
         Input('quick-version-btn', 'n_clicks'),
         Input('clear-terminal-btn', 'n_clicks')],
        [State('command-input', 'value'),
         State('command-output', 'children'),
         State('command-history-store', 'data'),
         State('terminal-password-state', 'data')],
        prevent_initial_call=True
    )
    def handle_terminal_command_global(
        n_submit, measure_clicks, help_clicks, status_clicks, version_clicks,
        clear_clicks, command_text, current_output, history_store, password_state
    ):
        """
        Maneja todos los comandos del terminal CLI globalmente.
        Versión optimizada con procesamiento rápido.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Inicializar historial
        if history_store is None:
            history_store = {'commands': [], 'index': -1}
        
        # Inicializar password_state
        if password_state is None:
            password_state = {'waiting': False, 'original_command': ''}
        
        if not ctx.triggered:
            return current_output or [], "", history_store, {'active': False, 'command': ''}, True, password_state
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Normalizar output
        if current_output is None:
            current_output = []
        elif not isinstance(current_output, list):
            current_output = [current_output]
        
        # Timestamp para todas las operaciones del terminal
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # ===== LIMPIAR TERMINAL =====
        if triggered_id == 'clear-terminal-btn':
            welcome = html.Div([
                html.Div([
                    html.Span("$ ", className="text-success fw-bold"),
                    html.Span("clear", className="text-light")
                ], className="terminal-line"),
                html.Div([
                    html.Span("→ Terminal limpiada", className="text-muted")
                ], className="terminal-line mb-2")
            ])
            return [welcome], "", history_store, {'active': False, 'command': ''}, True, password_state
        
        # ===== DETERMINAR COMANDO =====
        quick_commands = {
            'quick-measure-btn': 'z',
            'quick-help-btn': 'help',
            'quick-status-btn': 'status',
            'quick-version-btn': 'version'
        }
        
        if triggered_id in quick_commands:
            command = quick_commands[triggered_id]
        elif triggered_id == 'command-input' and n_submit and n_submit > 0:
            command = (command_text or "").strip()
            if not command:
                return current_output, "", history_store, {'active': False, 'command': ''}, True, password_state
            # Log para debug
            logger.info(f"[Terminal] Comando recibido: '{command}'")
        else:
            return current_output, "", history_store, {'active': False, 'command': ''}, True, password_state

        # ===== AUTO-STOP STREAMING SI HAY COMANDO NUEVO =====
        if not password_state.get('waiting', False):
            try:
                if device_state.is_streaming_in_progress() and command.lower() != 'stop':
                    current_output.append(
                        html.Div([
                            html.Span("⏹ ", className="text-warning"),
                            html.Span("Deteniendo streaming activo...", className="text-muted fst-italic")
                        ], className="terminal-line")
                    )
                    device_state.stop_streaming_command(wait_timeout=3.0)
            except Exception as e:
                logger.warning(f"[Terminal] No se pudo detener streaming automáticamente: {e}")
        
        # ===== MANEJO DE PASSWORD: Si estamos esperando una contraseña =====
        if password_state.get('waiting', False):
            logger.info(f"[Terminal] PASSWORD MODE: Enviando '{command}' como contraseña (TeraTerm style)")
            
            # El comando actual es la contraseña
            password = command
            if password.lower() == 'analog123':
                password = 'Analog123'
            original_command = password_state.get('original_command', 'calibrate commit')
            keep_password_mode = False
            
            # Mostrar en terminal que se envió la contraseña (oculta)
            current_output.append(
                html.Div([
                    html.Span(f"[{timestamp}] ", className="terminal-prompt"),
                    html.Span("*" * len(password), className="text-muted"),  # Ocultar contraseña
                    html.Span(" (password)", className="text-muted fst-italic ms-2")
                ], className="terminal-line")
            )
            
            # Obtener dispositivo
            device = device_state.device
            is_device_connected = device_state.is_connected
            
            if is_device_connected and device is not None:
                try:
                    # Enviar contraseña directamente al serial (SIN esperar prompt ADMX2001>)
                    device.serial.write((password + '\n').encode('utf-8'))
                    device.serial.flush()
                    logger.info(f"[Terminal] Contraseña enviada")
                    
                    # DETECCIÓN ACTIVA de respuesta (TeraTerm style)
                    import time
                    response_buffer = bytearray()
                    timeout = 5.0
                    start_time = time.time()
                    success_detected = False
                    
                    while (time.time() - start_time) < timeout:
                        if device.serial.in_waiting:
                            chunk = device.serial.read(device.serial.in_waiting)
                            response_buffer.extend(chunk)
                            
                            # Buscar confirmación de éxito o prompt
                            buffer_str = response_buffer.decode('utf-8', errors='ignore')
                            if 'success' in buffer_str.lower() or 'ADMX2001>' in buffer_str:
                                success_detected = True
                                logger.info(f"[Terminal] Respuesta recibida (success o prompt detectado)")
                                # Pequeña pausa para datos finales
                                time.sleep(0.05)
                                if device.serial.in_waiting:
                                    response_buffer.extend(device.serial.read(device.serial.in_waiting))
                                break
                        else:
                            # No hay datos, breve pausa
                            time.sleep(0.05)
                    
                    # Decodificar buffer
                    response_text = response_buffer.decode('utf-8', errors='ignore')
                    logger.info(f"[Terminal] Respuesta completa: {repr(response_text[:200])}")
                    
                    # Procesar respuesta con limpieza robusta (ANSI/VT100)
                    from lib.utils import clean_response_line
                    cleaned_lines = []
                    password_as_command_detected = False
                    for raw_line in response_text.split('\n'):
                        line = clean_response_line(raw_line)
                        if not line:
                            continue
                        if line == password:
                            continue
                        if line.lower().startswith("password>"):
                            keep_password_mode = True
                            continue
                        if "command" in line.lower() and "not found" in line.lower() and password.lower() in line.lower():
                            password_as_command_detected = True
                        cleaned_lines.append(line)

                    # Fallback: si la contraseña se interpretó como comando, reintentar flujo completo automáticamente
                    if password_as_command_detected and original_command.lower().startswith('calibrate '):
                        logger.warning(f"[Terminal] Password interpretada como comando. Reintentando flujo: {original_command}")
                        try:
                            # 1) Re-enviar comando original
                            device.serial.reset_input_buffer()
                            device.serial.reset_output_buffer()
                            device.serial.write((original_command + '\n').encode('utf-8'))
                            device.serial.flush()

                            # 2) Esperar prompt PASSWORD>
                            retry_buffer = bytearray()
                            retry_start = time.time()
                            retry_timeout = 3.0
                            got_password_prompt = False

                            while (time.time() - retry_start) < retry_timeout:
                                if device.serial.in_waiting:
                                    retry_buffer.extend(device.serial.read(device.serial.in_waiting))
                                    retry_text = retry_buffer.decode('utf-8', errors='ignore')
                                    if 'PASSWORD>' in retry_text.upper():
                                        got_password_prompt = True
                                        break
                                else:
                                    time.sleep(0.05)

                            if got_password_prompt:
                                # 3) Enviar contraseña inmediatamente
                                device.serial.write((password + '\n').encode('utf-8'))
                                device.serial.flush()

                                # 4) Leer respuesta final
                                final_buffer = bytearray()
                                final_start = time.time()
                                final_timeout = 6.0
                                while (time.time() - final_start) < final_timeout:
                                    if device.serial.in_waiting:
                                        final_buffer.extend(device.serial.read(device.serial.in_waiting))
                                        final_text = final_buffer.decode('utf-8', errors='ignore')
                                        if 'success' in final_text.lower() or 'done' in final_text.lower() or 'ADMX2001>' in final_text:
                                            time.sleep(0.05)
                                            if device.serial.in_waiting:
                                                final_buffer.extend(device.serial.read(device.serial.in_waiting))
                                            break
                                    else:
                                        time.sleep(0.05)

                                # Re-procesar líneas con resultado final
                                cleaned_lines = []
                                keep_password_mode = False
                                for raw_line in final_buffer.decode('utf-8', errors='ignore').split('\n'):
                                    line = clean_response_line(raw_line)
                                    if not line:
                                        continue
                                    if line == password:
                                        continue
                                    if line.lower().startswith("password>"):
                                        keep_password_mode = True
                                        continue
                                    cleaned_lines.append(line)
                            else:
                                keep_password_mode = True
                                cleaned_lines = ["No se pudo reabrir prompt PASSWORD>. Intente nuevamente."]
                        except Exception as retry_error:
                            logger.warning(f"[Terminal] Reintento automático de password falló: {retry_error}")
                            keep_password_mode = True
                            cleaned_lines = ["No se pudo completar reintento automático. Reingrese la contraseña."]
                    
                    if cleaned_lines:
                        for line in cleaned_lines:
                            # Determinar clase CSS
                            line_lower = line.lower()
                            if 'success' in line_lower or 'done' in line_lower:
                                css_class = "terminal-response-success"
                                prefix = html.Span("", className="terminal-success-icon")
                            elif "command" in line_lower and "not found" in line_lower and password.lower() in line_lower:
                                css_class = "terminal-response-warning"
                                prefix = html.Span("", className="terminal-warning-icon")
                                line = "Contraseña incorrecta o prompt expirado. Intente nuevamente."
                                keep_password_mode = True
                            elif 'error' in line_lower or 'fail' in line_lower:
                                css_class = "terminal-response-error"
                                prefix = html.Span("", className="terminal-error-icon")
                            else:
                                css_class = "terminal-response-line"
                                prefix = html.Span("  ", className="terminal-indent")
                            
                            current_output.append(
                                html.Div([prefix, html.Span(line, className=css_class)], className="terminal-line")
                            )
                    else:
                        current_output.append(
                            html.Div([
                                html.Span("", className="text-warning"),
                                html.Span("Sin respuesta del dispositivo", className="text-muted")
                            ], className="terminal-line")
                        )
                    
                except Exception as e:
                    logger.error(f"[Terminal] Error enviando contraseña: {e}")
                    current_output.append(
                        html.Div([
                            html.Span("", className="terminal-error-icon"),
                            html.Span(f"Error: {str(e)}", className="terminal-response-error")
                        ], className="terminal-line")
                    )
            else:
                current_output.append(
                    html.Div([
                        html.Span("", className="terminal-error-icon"),
                        html.Span("Error: Dispositivo no conectado", className="terminal-response-error")
                    ], className="terminal-line")
                )
            
            # Mantener modo password si el dispositivo aún lo requiere
            if keep_password_mode:
                password_state = {'waiting': True, 'original_command': original_command}
                current_output.append(
                    html.Div([
                        html.Span("", className="text-warning"),
                        html.Span("PASSWORD> ", className="terminal-response-warning fw-bold"),
                        html.Span("Reingrese la contraseña.", className="text-muted fst-italic")
                    ], className="terminal-line")
                )
            else:
                password_state = {'waiting': False, 'original_command': ''}
            
            # Agregar separador
            current_output.append(html.Div(className="terminal-separator"))
            if len(current_output) > 500:
                current_output = current_output[-500:]
            
            return current_output, "", history_store, {'active': False, 'command': ''}, True, password_state
        
        # ===== AGREGAR AL HISTORIAL =====
        if triggered_id == 'command-input':
            if command and (not history_store['commands'] or history_store['commands'][-1] != command):
                history_store['commands'].append(command)
                if len(history_store['commands']) > 100:
                    history_store['commands'] = history_store['commands'][-100:]
            history_store['index'] = len(history_store['commands'])
        
        # Obtener referencia al dispositivo desde el estado global
        device = device_state.device
        is_device_connected = device_state.is_connected
        
        # ===== PROCESAR COMANDO =====
        # Línea del comando
        cmd_block = html.Div([
            html.Div([
                html.Span(f"[{timestamp}] ", className="terminal-timestamp"),
                html.Span("", className="terminal-prompt-symbol"),
                html.Span(command, className="terminal-cmd-text")
            ], className="terminal-line")
        ])
        current_output.append(cmd_block)
        
        # ===== CORRECCIÓN DE COMANDOS COMUNES =====
        cmd_lower = command.lower()
        
        # Detectar "calibration" y sugerir "calibrate"
        if cmd_lower.startswith('calibration '):
            current_output.append(
                html.Div([
                    html.Span("Warn: ", className="text-warning fw-bold"),
                    html.Span("Command 'calibration' not found", className="terminal-response-line")
                ], className="terminal-line")
            )
            current_output.append(
                html.Div([
                    html.Span("", className="text-info"),
                    html.Span("Did you mean: ", className="text-muted"),
                    html.Code(f"calibrate {' '.join(command.split()[1:])}", className="terminal-code text-info")
                ], className="terminal-line")
            )
            current_output.append(html.Div(className="terminal-separator"))
            if len(current_output) > 500:
                current_output = current_output[-500:]
            return current_output, "", history_store, {'active': False, 'command': ''}, True, password_state
        
        # ===== COMANDOS LOCALES (funcionan siempre, con o sin hardware) =====
        
        # Comando debug: cambiar nivel de logging en tiempo de ejecución
        if cmd_lower in ['debug on', 'debug off', 'debug info']:
            if cmd_lower == 'debug on':
                logging.getLogger().setLevel(logging.DEBUG)
                logging.getLogger('lib.admx2001').setLevel(logging.DEBUG)
                logging.getLogger('lib.device_state').setLevel(logging.DEBUG)
                msg = "Logging detallado ACTIVADO (DEBUG)"
                css_class = "terminal-response-success"
            elif cmd_lower == 'debug off':
                logging.getLogger().setLevel(logging.WARNING)
                logging.getLogger('lib.admx2001').setLevel(logging.WARNING)
                logging.getLogger('lib.device_state').setLevel(logging.WARNING)
                msg = "Logging detallado DESACTIVADO (WARNING)"
                css_class = "terminal-response-warning"
            elif cmd_lower == 'debug info':
                logging.getLogger().setLevel(logging.INFO)
                logging.getLogger('lib.admx2001').setLevel(logging.INFO)
                logging.getLogger('lib.device_state').setLevel(logging.INFO)
                msg = "Logging nivel INFO (normal)"
                css_class = "terminal-response-line"
            
            current_output.append(
                html.Div([
                    html.Span("  ", className="terminal-indent"),
                    html.Span(msg, className=css_class)
                ], className="terminal-line")
            )
            current_output.append(
                html.Div([
                    html.Span("", className="text-info"),
                    html.Span("Los logs se muestran en la consola donde se ejecutó app.py", className="text-muted small")
                ], className="terminal-line")
            )
            current_output.append(html.Div(className="terminal-separator"))
            if len(current_output) > 500:
                current_output = current_output[-500:]
            return current_output, "", history_store, {'active': False, 'command': ''}, True, password_state
        
        if cmd_lower == 'version':
            # Comando version: mostrar información local y del hardware
            response_children = [
                html.Div([
                    html.Span("  ", className="terminal-indent"),
                    html.Span("SOFTWARE:", className="terminal-response-line text-info fw-bold")
                ], className="terminal-line"),
                html.Div([
                    html.Span("    ", className="terminal-indent"),
                    html.Span("ZORIA Dashboard v1.0.0", className="terminal-response-line terminal-response-success")
                ], className="terminal-line"),
                html.Div([
                    html.Span("    ", className="terminal-indent"),
                    html.Span("Python Dashboard for ADMX2001 Impedance Analyzer", className="terminal-response-line")
                ], className="terminal-line"),
                html.Div([
                    html.Span("    ", className="terminal-indent"),
                    html.Span("Authors: Mario R. Montero, Juan C. Alvarez, Francisco J. Racedo N.", className="terminal-response-line")
                ], className="terminal-line"),
                html.Div([
                    html.Span("  ", className="terminal-indent"),
                    html.Span("", className="terminal-response-line")
                ], className="terminal-line"),
            ]
            
            # Intentar obtener información del hardware
            if is_device_connected and device is not None:
                try:
                    hw_response = device_state.send_command('*idn')
                    response_children.append(
                        html.Div([
                            html.Span("  ", className="terminal-indent"),
                            html.Span("HARDWARE:", className="terminal-response-line text-warning fw-bold")
                        ], className="terminal-line")
                    )
                    if hw_response:
                        for line in hw_response:
                            if line.strip():
                                response_children.append(
                                    html.Div([
                                        html.Span("    ", className="terminal-indent"),
                                        html.Span(line.strip(), className="terminal-response-line terminal-response-success")
                                    ], className="terminal-line")
                                )
                    else:
                        response_children.append(
                            html.Div([
                                html.Span("    ", className="terminal-indent"),
                                html.Span("(sin respuesta del hardware)", className="terminal-response-line text-muted")
                            ], className="terminal-line")
                        )
                except Exception as e:
                    response_children.append(
                        html.Div([
                            html.Span("  ", className="terminal-indent"),
                            html.Span("HARDWARE:", className="terminal-response-line text-warning fw-bold")
                        ], className="terminal-line")
                    )
                    response_children.append(
                        html.Div([
                            html.Span("    ", className="terminal-indent"),
                            html.Span(f"Error al consultar hardware: {str(e)}", className="terminal-response-line terminal-response-error")
                        ], className="terminal-line")
                    )
            else:
                response_children.append(
                    html.Div([
                        html.Span("  ", className="terminal-indent"),
                        html.Span("HARDWARE:", className="terminal-response-line text-warning fw-bold")
                    ], className="terminal-line")
                )
                response_children.append(
                    html.Div([
                        html.Span("    ", className="terminal-indent"),
                        html.Span("No conectado (modo simulación)", className="terminal-response-line text-muted")
                    ], className="terminal-line")
                )
            
            current_output.append(html.Div(response_children))
            current_output.append(html.Div(className="terminal-separator"))
            if len(current_output) > 500:
                current_output = current_output[-500:]
            return current_output, "", history_store, {'active': False, 'command': ''}, True, password_state
        
        # Verificar si hay dispositivo conectado
        if is_device_connected and device is not None:
            # ===== MODO REAL: Usar dispositivo ADMX2001 =====

            # ===== COMANDOS LOCALES EN MODO REAL =====
            if cmd_lower == 'help' or cmd_lower.startswith('help '):
                # Mostrar help formateado localmente (el blob del firmware no es legible en web)
                help_lines = [
                    "════════════════════════════════════════════════════",
                    "ADMX2001B CLI · HELP",
                    "Referencia rápida alineada a DOCUMENTACION_OFICIAL",
                    "════════════════════════════════════════════════════",
                    "",
                    "USO:",
                    "  help                      Lista de comandos",
                    "  help <comando>            Ayuda detallada",
                    "",
                    "MEDICIÓN:",
                    "  z                         Ejecutar medición/sweep",
                    "  frequency <valor_kHz>     Ej: 100 => 100 kHz, 0 => modo DC",
                    "  magnitude <V>             0.01 a 2 V",
                    "  offset <V>                -5 V a +5 V",
                    "  average <1-256>           Promediado de muestras",
                    "  count <n>                 Cantidad de puntos del sweep",
                    "  mdelay <ms>               Retardo previo a medición",
                    "  tdelay <ms>               Retardo post-trigger",
                    "",
                    "DISPLAY:",
                    "  display <0-18>            Modo de salida",
                    "  display 6                 R/X (default)",
                    "  display 7                 |Z|/deg",
                    "  display 15                G/B",
                    "",
                    "GANANCIA / RANGO:",
                    "  setgain                   Ver configuración actual",
                    "  setgain auto              Activar auto-ranging",
                    "  setgain ch0 <0-3>         Ganancia de voltaje",
                    "  setgain ch1 <0-3>         Ganancia de corriente",
                    "",
                    "BARRIDOS:",
                    "  sweep_type frequency <inicio> <fin>",
                    "  sweep_scale <log|linear>",
                    "",
                    "CALIBRACIÓN:",
                    "  calibrate open",
                    "  calibrate short",
                    "  calibrate rt <R> xt <X>",
                    "  calibrate commit <pass> [ts]",
                    "  calibrate list",
                    "",
                    "SISTEMA:",
                    "  *idn | status | reset | version | debug on|off|info",
                    "",
                    "TIP: usa 'help <comando>' para ver sintaxis exacta del firmware.",
                ]
                import re as _re
                response_children = []
                for line in help_lines:
                    if line.startswith('═') or line.startswith('─'):
                        response_children.append(html.Div(html.Span(line, style={'color': 'var(--t-accent)', 'fontWeight': '600'}), className="terminal-line"))
                    elif line and not line.startswith(' ') and line[0].isupper() and ':' in line:
                        response_children.append(html.Div(html.Span(line, style={'color': 'var(--t-text-secondary)', 'fontWeight': '700', 'marginTop': '4px', 'display': 'block'}), className="terminal-line"))
                    elif line == '':
                        response_children.append(html.Div(style={'height': '4px'}, className="terminal-line"))
                    elif line.startswith('  '):
                        m = _re.match(r'^(  \S[^\s]*)(\s{2,})(.*)', line)
                        if m:
                            response_children.append(html.Div([html.Span(m.group(1), style={'color': 'var(--t-text-primary)'}), html.Span(m.group(3), style={'color': 'var(--t-text-muted)', 'marginLeft': '1ch'})], className="terminal-line", style={'paddingLeft': '1rem'}))
                        else:
                            response_children.append(html.Div(html.Span(line, style={'color': 'var(--t-text-primary)'}), className="terminal-line", style={'paddingLeft': '1rem'}))
                    else:
                        response_children.append(html.Div(html.Span(line, style={'color': 'var(--t-text-muted)', 'fontStyle': 'italic'}), className="terminal-line"))
                current_output.append(html.Div(response_children))
                current_output.append(html.Div(className="terminal-separator"))
                if len(current_output) > 500:
                    current_output = current_output[-500:]
                return current_output, "", history_store, {'active': False, 'command': ''}, True, password_state

            if cmd_lower == 'status':
                status_lines = [
                    f"Conexión: {'Conectado' if device_state.is_connected else 'Desconectado'}",
                    f"Puerto: {device_state.port_info or 'N/A'}",
                    f"Streaming activo: {'Sí' if device_state.is_streaming_in_progress() else 'No'}"
                ]
                response_lines = status_lines
                response_children = []
                for line in response_lines:
                    response_children.append(
                        html.Div([
                            html.Span("  ", className="terminal-indent"),
                            html.Span(line, className="terminal-response-line")
                        ], className="terminal-line")
                    )
                current_output.append(html.Div(response_children))
                current_output.append(html.Div(className="terminal-separator"))
                if len(current_output) > 500:
                    current_output = current_output[-500:]
                return current_output, "", history_store, {'active': False, 'command': ''}, True, password_state

            if cmd_lower == 'stop':
                try:
                    device_state.stop_streaming_command(wait_timeout=3.0)
                except Exception as e:
                    logger.warning(f"[Terminal] Error en stop: {e}")

                current_output.append(
                    html.Div([
                        html.Span("", className="terminal-success-icon"),
                        html.Span("Streaming detenido", className="terminal-response-success")
                    ], className="terminal-line")
                )
                current_output.append(html.Div(className="terminal-separator"))
                if len(current_output) > 500:
                    current_output = current_output[-500:]
                return current_output, "", history_store, {'active': False, 'command': ''}, True, password_state
            
            # Detectar comandos que deben usar STREAMING (respuestas en tiempo real)
            cmd_lower_check = cmd_lower if 'cmd_lower' in locals() else command.lower()
            use_streaming = cmd_lower_check in ['sweep', 'z']
            
            if use_streaming:
                # ===== MODO STREAMING: Mostrar datos en tiempo real =====
                logger.info(f"[Terminal] Iniciando streaming para: '{command}'")
                
                # Agregar mensaje de ejecución
                current_output.append(
                    html.Div([
                        html.Span("", className="text-warning"),
                        html.Span(f"Ejecutando: {command}...", className="text-muted fst-italic")
                    ], className="terminal-line")
                )
                
                # Iniciar streaming en thread separado
                stream_timeout = 45.0 if cmd_lower_check == 'z' else 30.0
                device_state.start_streaming_command(command, timeout=stream_timeout)
                
                # Activar polling interval
                streaming_state = {'active': True, 'command': command, 'received': 0}
                return current_output, "", history_store, streaming_state, False, password_state  # False = activar Interval
            
            # ===== MODO NORMAL: Esperar respuesta completa =====
            try:
                logger.info(f"[Terminal] ▶ Enviando: '{command}'")

                # ===== MANEJO ESPECIAL: calibrate erase (requiere contraseña) =====
                if cmd_lower_check.startswith('calibrate erase'):
                    parts = command.split()
                    erase_password = parts[2] if len(parts) >= 3 else None

                    import time
                    erase_cmd = "calibrate erase"
                    from lib.utils import clean_response_line

                    try:
                        device = device_state.device
                        device.serial.reset_input_buffer()
                        device.serial.reset_output_buffer()

                        # Enviar comando erase
                        device.serial.write((erase_cmd + '\n').encode('utf-8'))
                        device.serial.flush()

                        # Esperar prompt PASSWORD>
                        first_buffer = bytearray()
                        timeout = 5.0
                        start_time = time.time()
                        password_prompt_received = False

                        while (time.time() - start_time) < timeout:
                            if device.serial.in_waiting:
                                first_buffer.extend(device.serial.read(device.serial.in_waiting))
                                first_text = first_buffer.decode('utf-8', errors='ignore')
                                if 'PASSWORD>' in first_text.upper():
                                    password_prompt_received = True
                                    time.sleep(0.05)
                                    if device.serial.in_waiting:
                                        first_buffer.extend(device.serial.read(device.serial.in_waiting))
                                    break
                            else:
                                time.sleep(0.05)

                        first_text = first_buffer.decode('utf-8', errors='ignore')

                        # Si no vino password inline, entrar a modo interactivo
                        if not erase_password:
                            response = []
                            for line in first_text.split('\n'):
                                clean_line = clean_response_line(line)
                                if clean_line and clean_line.lower() != erase_cmd:
                                    response.append(clean_line)

                            if password_prompt_received:
                                password_state = {'waiting': True, 'original_command': erase_cmd}
                                current_output.append(
                                    html.Div([
                                        html.Span("", className="text-warning"),
                                        html.Span("PASSWORD> ", className="terminal-response-warning fw-bold"),
                                        html.Span("Ingrese la contraseña:", className="text-muted fst-italic")
                                    ], className="terminal-line")
                                )
                                current_output.append(
                                    html.Div([
                                        html.Span("", className="text-info"),
                                        html.Span("Contraseña predeterminada: ", className="text-muted"),
                                        html.Code("Analog123", className="terminal-code text-success")
                                    ], className="terminal-line")
                                )
                                current_output.append(html.Div(className="terminal-separator"))
                                if len(current_output) > 500:
                                    current_output = current_output[-500:]
                                return current_output, "", history_store, {'active': False, 'command': ''}, True, password_state

                            # Si no detecta PASSWORD>, mostrar lo que haya
                            response = response or ["No se recibió prompt PASSWORD> para calibrate erase"]

                        else:
                            # Password inline: enviar contraseña y leer respuesta final
                            device.serial.write((erase_password + '\n').encode('utf-8'))
                            device.serial.flush()

                            final_buffer = bytearray()
                            timeout = 6.0
                            start_time = time.time()
                            while (time.time() - start_time) < timeout:
                                if device.serial.in_waiting:
                                    final_buffer.extend(device.serial.read(device.serial.in_waiting))
                                    final_text = final_buffer.decode('utf-8', errors='ignore')
                                    if 'ADMX2001>' in final_text or 'success' in final_text.lower() or 'invalid' in final_text.lower() or 'done' in final_text.lower():
                                        time.sleep(0.05)
                                        if device.serial.in_waiting:
                                            final_buffer.extend(device.serial.read(device.serial.in_waiting))
                                        break
                                else:
                                    time.sleep(0.05)

                            response = []
                            for line in (first_text + final_buffer.decode('utf-8', errors='ignore')).split('\n'):
                                clean_line = clean_response_line(line)
                                if not clean_line:
                                    continue
                                if clean_line.lower() == erase_cmd:
                                    continue
                                if clean_line == erase_password:
                                    continue
                                response.append(clean_line)

                    except Exception as e:
                        logger.error(f"[Terminal] Error en erase: {e}")
                        import traceback
                        traceback.print_exc()
                        response = [f"Error: {e}"]
                
                # ===== MANEJO ESPECIAL: calibrate commit (requiere contraseña) =====
                elif cmd_lower_check.startswith('calibrate commit'):
                    # Parsear argumentos: calibrate commit [password] [timestamp]
                    parts = command.split()
                    password = None
                    timestamp = None
                    
                    if len(parts) >= 3:  # calibrate commit <password>
                        password = parts[2]
                    if len(parts) >= 4:  # calibrate commit <password> <timestamp>
                        timestamp = parts[3]
                    
                    if password:
                        # Usuario proporcionó contraseña - enviar todo el flujo (TeraTerm style)
                        logger.info(f"[Terminal] Calibrate commit con contraseña proporcionada: '{password}' (TeraTerm style)")
                        
                        # Construir comando commit
                        import time
                        if timestamp:
                            commit_cmd = f"calibrate commit {timestamp}"
                        else:
                            commit_cmd = f"calibrate commit {int(time.time())}"
                        
                        logger.info(f"[Terminal] Enviando: {commit_cmd}")
                        
                        try:
                            device = device_state.device
                            
                            # Limpiar buffers antes de comenzar
                            device.serial.reset_input_buffer()
                            device.serial.reset_output_buffer()
                            
                            # Enviar comando commit
                            device.serial.write((commit_cmd + '\n').encode('utf-8'))
                            device.serial.flush()
                            
                            # DETECCIÓN ACTIVA del prompt PASSWORD>
                            response_buffer = bytearray()
                            timeout = 5.0
                            start_time = time.time()
                            password_prompt_received = False
                            
                            while (time.time() - start_time) < timeout:
                                if device.serial.in_waiting:
                                    chunk = device.serial.read(device.serial.in_waiting)
                                    response_buffer.extend(chunk)
                                    
                                    # Buscar el prompt de contraseña
                                    buffer_str = response_buffer.decode('utf-8', errors='ignore')
                                    if 'PASSWORD>' in buffer_str.upper():
                                        password_prompt_received = True
                                        logger.info(f"[Terminal] PASSWORD> detectado activamente")
                                        # Pequeña pausa para datos finales
                                        time.sleep(0.05)
                                        if device.serial.in_waiting:
                                            response_buffer.extend(device.serial.read(device.serial.in_waiting))
                                        break
                                else:
                                    time.sleep(0.05)
                            
                            first_response = response_buffer.decode('utf-8', errors='ignore')
                            logger.info(f"[Terminal] Respuesta después de commit: {repr(first_response[:200])}")
                            
                            # Verificar que recibimos PASSWORD>
                            if not password_prompt_received:
                                logger.warning(f"[Terminal] No se recibió PASSWORD>, respuesta: {first_response}")
                            
                            # Enviar contraseña (sin esperar prompt ADMX2001>)
                            logger.info(f"[Terminal] Enviando contraseña...")
                            device.serial.write((password + '\n').encode('utf-8'))
                            device.serial.flush()
                            
                            # DETECCIÓN ACTIVA de respuesta final
                            commit_response_buffer = bytearray()
                            timeout = 5.0
                            start_time = time.time()
                            success_detected = False
                            
                            while (time.time() - start_time) < timeout:
                                if device.serial.in_waiting:
                                    chunk = device.serial.read(device.serial.in_waiting)
                                    commit_response_buffer.extend(chunk)
                                    
                                    # Buscar confirmación
                                    buffer_str = commit_response_buffer.decode('utf-8', errors='ignore')
                                    if 'success' in buffer_str.lower() or 'ADMX2001>' in buffer_str or 'invalid' in buffer_str.lower():
                                        success_detected = True
                                        logger.info(f"[Terminal] Respuesta final recibida")
                                        # Pequeña pausa para datos finales
                                        time.sleep(0.05)
                                        if device.serial.in_waiting:
                                            commit_response_buffer.extend(device.serial.read(device.serial.in_waiting))
                                        break
                                else:
                                    time.sleep(0.05)
                            
                            commit_response = commit_response_buffer.decode('utf-8', errors='ignore')
                            logger.info(f"[Terminal] Respuesta completa del commit: {repr(commit_response[:200])}")
                            
                            # Procesar respuesta
                            from lib.utils import clean_response_line
                            response = []
                            for line in (first_response + commit_response).split('\n'):
                                clean_line = clean_response_line(line)
                                if clean_line:
                                    # Filtrar eco del comando y timestamp
                                    if clean_line.lower() != commit_cmd.lower() and not clean_line.isdigit():
                                        response.append(clean_line)
                            
                            logger.info(f"[Terminal] Respuesta procesada: {len(response)} líneas")
                            
                        except Exception as e:
                            logger.error(f"[Terminal] Error en commit: {e}")
                            import traceback
                            traceback.print_exc()
                            response = [f"Error: {e}"]
                    else:
                        # Sin contraseña - flujo interactivo: generar timestamp y enviar
                        logger.info(f"[Terminal] calibrate commit sin contraseña - modo interactivo (TeraTerm style)")
                        
                        import time
                        timestamp = int(time.time())
                        commit_cmd = f"calibrate commit {timestamp}"
                        
                        logger.info(f"[Terminal] Enviando comando con timestamp Unix: {commit_cmd}")
                        
                        try:
                            device = device_state.device
                            
                            # Limpiar buffers antes de comenzar (TeraTerm style)
                            device.serial.reset_input_buffer()
                            device.serial.reset_output_buffer()
                            
                            # Enviar comando commit
                            device.serial.write((commit_cmd + '\n').encode('utf-8'))
                            device.serial.flush()
                            logger.debug(f"[Terminal] Comando enviado: {commit_cmd}")
                            
                            # DETECCIÓN ACTIVA del prompt PASSWORD> (similar a TeraTerm)
                            response_buffer = bytearray()
                            timeout = 5.0
                            start_time = time.time()
                            password_prompt_received = False
                            
                            while (time.time() - start_time) < timeout:
                                if device.serial.in_waiting:
                                    chunk = device.serial.read(device.serial.in_waiting)
                                    response_buffer.extend(chunk)
                                    
                                    # Buscar el prompt de contraseña (case-insensitive)
                                    buffer_str = response_buffer.decode('utf-8', errors='ignore')
                                    if 'PASSWORD>' in buffer_str.upper():
                                        password_prompt_received = True
                                        logger.info(f"[Terminal] PASSWORD> detectado activamente")
                                        # Pequeña pausa para datos finales
                                        time.sleep(0.05)
                                        # Leer cualquier dato adicional
                                        if device.serial.in_waiting:
                                            response_buffer.extend(device.serial.read(device.serial.in_waiting))
                                        break
                                else:
                                    # No hay datos, breve pausa
                                    time.sleep(0.05)
                            
                            # Decodificar buffer
                            response_text = response_buffer.decode('utf-8', errors='ignore')
                            
                            if not password_prompt_received:
                                logger.warning(f"[Terminal] No se recibió PASSWORD> en {timeout}s")
                                logger.warning(f"[Terminal] Respuesta recibida: {repr(response_text)}")
                            
                            # Separar en líneas para mostrar
                            response = [line.strip() for line in response_text.split('\n') if line.strip()]
                            logger.info(f"[Terminal] Respuesta recibida: {len(response)} líneas (prompt detectado: {password_prompt_received})")
                            
                        except Exception as e:
                            logger.error(f"[Terminal] Error en commit interactivo: {e}")
                            import traceback
                            traceback.print_exc()
                            response = [f"Error: {e}"]
                
                # Determinar timeout según el comando
                elif cmd_lower_check.startswith('calibrate') or cmd_lower_check == '*idn' or cmd_lower_check == 'z':
                    timeout = 30.0
                    logger.info(f"[Terminal] ⏱ Usando timeout extendido: {timeout}s")
                    response = device_state.send_command(command, timeout=timeout, lock_timeout=5.0)
                else:
                    # Comandos rápidos, usar timeout default
                    response = device_state.send_command(command, lock_timeout=5.0)
                
                logger.info(f"[Terminal] ◀ Recibido: {len(response) if response else 0} líneas")

                # Reintento automático para calibración si llegó vacío (evita falsos 'sin respuesta')
                if (not response) and cmd_lower_check.startswith('calibrate') and (not cmd_lower_check.startswith('calibrate commit')) and (not cmd_lower_check.startswith('calibrate erase')):
                    logger.warning(f"[Terminal] Respuesta vacía en calibración. Reintentando: '{command}'")
                    try:
                        import time
                        time.sleep(0.15)
                        response = device_state.send_command(command, timeout=45.0, lock_timeout=8.0)
                        logger.info(f"[Terminal] ◀ Reintento calibración: {len(response) if response else 0} líneas")
                    except Exception as retry_error:
                        logger.warning(f"[Terminal] Reintento de calibración falló: {retry_error}")
                
                # Log completo de la respuesta para comandos de calibración
                if cmd_lower_check.startswith('calibrate'):
                    logger.info(f"[Terminal] DEBUG CALIBRATE - Command: '{command}'")
                    logger.info(f"[Terminal] DEBUG CALIBRATE - Response type: {type(response)}")
                    logger.info(f"[Terminal] DEBUG CALIBRATE - Response is None: {response is None}")
                    if response:
                        logger.info(f"[Terminal] DEBUG CALIBRATE - Response length: {len(response)}")
                        logger.info(f"[Terminal] DEBUG CALIBRATE - Todas las líneas:")
                        for idx, line in enumerate(response):
                            logger.info(f"[Terminal]    [{idx}] {repr(line)}")
                    else:
                        logger.error(f"[Terminal] DEBUG CALIBRATE - Respuesta es None o vacía!")
                        logger.error(f"[Terminal] DEBUG - Probablemente el dispositivo tardó mucho en responder")
                
                # Log de respuesta cruda para debug (primeras 10 líneas)
                if response:
                    for idx, line in enumerate(response[:10]):
                        logger.info(f"[Terminal] RAW[{idx}]: '{line}'")
                    if len(response) > 10:
                        logger.info(f"[Terminal] ... y {len(response)-10} líneas más")
                
                if response:
                    # Procesar líneas de respuesta de forma optimizada
                    # Para comandos de calibración, usar filtrado menos agresivo
                    is_calibrate_cmd = cmd_lower_check.startswith('calibrate')
                    
                    # Detectar si hay prompt de PASSWORD (indica que necesita contraseña)
                    has_password_prompt = any('PASSWORD>' in line or 'password>' in line.lower() for line in response)
                    
                    if has_password_prompt:
                        logger.warning(f"[Terminal] PASSWORD> detectado - esperando contraseña del usuario")
                        
                        # Establecer estado: esperando contraseña
                        password_state = {'waiting': True, 'original_command': command}
                        
                        # Mostrar prompt de contraseña al usuario
                        current_output.append(
                            html.Div([
                                html.Span("", className="text-warning"),
                                html.Span("PASSWORD> ", className="terminal-response-warning fw-bold"),
                                html.Span("Ingrese la contraseña:", className="text-muted fst-italic")
                            ], className="terminal-line")
                        )
                        current_output.append(
                            html.Div([
                                html.Span("", className="text-info"),
                                html.Span("Contraseña predeterminada: ", className="text-muted"),
                                html.Code("Analog123", className="terminal-code text-success")
                            ], className="terminal-line")
                        )
                        current_output.append( html.Div(className="terminal-separator"))
                        if len(current_output) > 500:
                            current_output = current_output[-500:]
                        
                        # NO limpiar el input, retornar con password_state activo
                        return current_output, "", history_store, {'active': False, 'command': ''}, True, password_state
                    
                    # Filtrar eco del comando que puede aparecer al inicio O al final
                    cleaned_lines = []
                    
                    for idx, line in enumerate(response):
                        line_stripped = line.strip()
                        
                        # Saltar líneas completamente vacías
                        if not line_stripped:
                            # Para comandos de calibración, mantener como separadores si ya hay contenido
                            if is_calibrate_cmd and cleaned_lines:
                                cleaned_lines.append("")
                            continue
                        
                        # Filtrar eco: SOLO si es exactamente igual al comando
                        # Para comandos de calibración, ser muy estricto ya que la salida es importante
                        is_first_line = idx == 0
                        is_last_line = idx == len(response) - 1
                        
                        # Filtrar eco solo si es la primera o última línea Y es exactamente igual (case-insensitive)
                        is_echo = line_stripped.lower() == command.lower()
                        if is_echo and (is_first_line or is_last_line):
                            logger.info(f"[Terminal]  Filtrando eco en línea {idx}: '{line_stripped}'")
                            continue
                        
                        # Para calibración, ser más permisivo - agregar casi todo
                        if is_calibrate_cmd:
                            logger.info(f"[Terminal] [CALIBRATE] Agregando línea {idx}: '{line_stripped}'")
                            cleaned_lines.append(line_stripped)
                        else:
                            # Para otros comandos, filtrado normal
                            logger.info(f"[Terminal] Agregando línea {idx}: '{line_stripped}'")
                            cleaned_lines.append(line_stripped)
                    
                    logger.info(f"[Terminal]  Líneas procesadas: {len(cleaned_lines)} (de {len(response)} originales)")
                    
                    # FILTRADO ESPECIAL: Para comando 'z', mostrar solo la última línea de medición
                    if cmd_lower_check == 'z' and len(cleaned_lines) > 0:
                        # Buscar la última línea que parece una medición (empieza con número)
                        measurement_lines = [line for line in cleaned_lines if line and line[0].isdigit()]
                        if measurement_lines:
                            logger.info(f"[Terminal]  Comando 'z': Filtrando {len(measurement_lines)} mediciones, mostrando solo la última")
                            # Mantener la última medición y cualquier mensaje/advertencia
                            last_measurement = measurement_lines[-1]
                            warnings = [line for line in cleaned_lines if not (line and line[0].isdigit())]
                            cleaned_lines = [last_measurement] + warnings
                    
                    # FILTRADO ESPECIAL: Para comando 'display', no debería haber mediciones
                    if cmd_lower_check.startswith('display') and len(cleaned_lines) > 0:
                        # Filtrar líneas que parecen mediciones (empiezan con número)
                        non_measurement_lines = [line for line in cleaned_lines if not (line and line[0].isdigit())]
                        if len(non_measurement_lines) < len(cleaned_lines):
                            logger.warning(f"[Terminal]  Comando 'display': Filtrando {len(cleaned_lines) - len(non_measurement_lines)} líneas de medición no deseadas")
                            cleaned_lines = non_measurement_lines if non_measurement_lines else cleaned_lines[:1]
                    
                    if cleaned_lines:
                        response_children = []
                        for line in cleaned_lines:
                            # Mantener líneas vacías como separadores visuales
                            if not line:
                                response_children.append(html.Div(style={'height': '0.5em'}))
                                continue
                            
                            line_lower = line.lower()
                            
                            # Determinar clase CSS basada en contenido
                            if any(err in line_lower for err in ['error', 'fail', 'invalid', 'unknown']):
                                css_class = "terminal-response-line terminal-response-error"
                                prefix = html.Span("", className="terminal-error-icon")
                            elif any(ok in line_lower for ok in ['ok', 'success', 'done', 'ready', 'pass']):
                                css_class = "terminal-response-line terminal-response-success"
                                prefix = html.Span("", className="terminal-success-icon")
                            elif any(warn in line_lower for warn in ['warning', 'warn', 'caution']):
                                css_class = "terminal-response-line terminal-response-warning"
                                prefix = html.Span("", className="terminal-warning-icon")
                            # Detectar líneas de calibración (empiezan con números o contienen "ch0" "ch1")
                            elif cmd_lower_check.startswith('calibrate') and (line[0].isdigit() or 'ch0' in line_lower or 'ch1' in line_lower or 'gain' in line_lower):
                                css_class = "terminal-response-line text-info"
                                prefix = html.Span("  ", className="terminal-indent")
                            else:
                                css_class = "terminal-response-line"
                                prefix = html.Span("  ", className="terminal-indent")
                            
                            response_children.append(
                                html.Div([prefix, html.Span(line, className=css_class)], className="terminal-line")
                            )
                        current_output.append(html.Div(response_children))
                    else:
                        # No hay líneas después del filtrado - mostrar info de debug
                        logger.warning(f"[Terminal] Sin líneas después de filtrar - respuesta original tenía {len(response)} líneas")
                        
                        # Para comandos de calibración, mostrar las líneas sin filtrar directamente
                        if cmd_lower_check.startswith('calibrate'):
                            logger.info(f"[Terminal]  Comando de calibración - mostrando respuesta sin filtrar")
                            current_output.append(
                                html.Div([
                                    html.Span("", className="text-warning"),
                                    html.Span("Respuesta sin formato (debug):", className="text-warning fst-italic")
                                ], className="terminal-line")
                            )
                            
                            response_children = []
                            for idx, line in enumerate(response):
                                line_stripped = line.strip()
                                if line_stripped:
                                    # Mostrar todas las líneas sin filtrar para calibración
                                    response_children.append(
                                        html.Div([
                                            html.Span(f"[{idx}] ", className="text-muted small"),
                                            html.Span(line_stripped, className="terminal-response-line")
                                        ], className="terminal-line")
                                    )
                            
                            if response_children:
                                current_output.append(html.Div(response_children))
                            else:
                                current_output.append(
                                    html.Div([
                                        html.Span("  ", className="terminal-indent"),
                                        html.Span("(todas las líneas están vacías)", className="terminal-empty-response text-muted")
                                    ], className="terminal-line")
                                )
                        else:
                            # Para otros comandos, mostrar mensaje estándar
                            current_output.append(
                                html.Div([
                                    html.Span("  ", className="terminal-indent"),
                                    html.Span("(sin salida del comando)", className="terminal-empty-response text-muted")
                                ], className="terminal-line")
                            )
                        
                        # Mostrar detalles de debug expandibles con las líneas originales
                        raw_lines_preview = []
                        for idx, line in enumerate(response[:10]):
                            raw_lines_preview.append(
                                html.Div([
                                    html.Span(f"    [{idx}] ", className="text-muted small"),
                                    html.Code(repr(line), className="text-warning small")
                                ], className="terminal-line")
                            )
                        
                        if len(response) > 10:
                            raw_lines_preview.append(
                                html.Div([
                                    html.Span(f"    ... y {len(response)-10} líneas más", className="text-muted small fst-italic")
                                ], className="terminal-line")
                            )
                        
                        current_output.append(
                            html.Details([
                                html.Summary([
                                    html.Span(" ", className="text-warning"),
                                    html.Span(f"Debug: Ver {len(response)} líneas originales", className="text-muted small")
                                ], style={'cursor': 'pointer', 'userSelect': 'none'}),
                                html.Div(raw_lines_preview, className="ms-3 mt-2")
                            ], className="terminal-debug-details")
                        )
                else:
                    # Respuesta None o vacía desde el dispositivo
                    logger.warning(f"[Terminal] Dispositivo retornó respuesta vacía o None para comando: '{command}'")
                    current_output.append(
                        html.Div([
                            html.Span("  ", className="terminal-indent"),
                            html.Span("(sin respuesta del dispositivo)", className="terminal-empty-response text-muted")
                        ], className="terminal-line")
                    )
                    current_output.append(
                        html.Div([
                            html.Span("", className="text-info"),
                            html.Span("Verifique que el comando sea correcto. Use ", className="text-muted"),
                            html.Code("help", className="terminal-code"),
                            html.Span(" para ver comandos disponibles.", className="text-muted")
                        ], className="terminal-line")
                    )
                
                # Agregar separador
                current_output.append(html.Div(className="terminal-separator"))
                
                # Limitar output
                if len(current_output) > 500:
                    current_output = current_output[-500:]
                
                return current_output, "", history_store, {'active': False, 'command': ''}, True, password_state
                    
            except Exception as e:
                error_msg = str(e)
                # Mensaje más amigable si es error de conexión
                if "not connected" in error_msg.lower() or "no conectado" in error_msg.lower():
                    error_msg = "Dispositivo desconectado. Reconecte desde el Dashboard."
                current_output.append(
                    html.Div([
                        html.Span("", className="terminal-error-icon"),
                        html.Span(f"Error: {error_msg}", className="terminal-error-text")
                    ], className="terminal-line terminal-error-line")
                )
                
                # Agregar separador
                current_output.append(html.Div(className="terminal-separator"))
                
                # Limitar output  
                if len(current_output) > 500:
                    current_output = current_output[-500:]
                
                return current_output, "", history_store, {'active': False, 'command': ''}, True, password_state
        
        # ===== MODO SIMULACIÓN: Respuestas simuladas =====
        cmd_lower = command.lower()
        
        if cmd_lower == 'help':
            response_lines = [
                "════════════════════════════════════════════════════",
                "ADMX2001B CLI · HELP",
                "Referencia rápida alineada a DOCUMENTACION_OFICIAL",
                "════════════════════════════════════════════════════",
                "",
                "USO:",
                "  help                      Lista de comandos",
                "  help <comando>            Ayuda detallada",
                "",
                "MEDICIÓN:",
                "  z                         Ejecutar medición/sweep",
                "  frequency <valor_kHz>     Ej: 100 => 100 kHz, 0 => modo DC",
                "  magnitude <V>             0.01 a 2 V",
                "  offset <V>                -5 V a +5 V",
                "  average <1-256>           Promediado de muestras",
                "  count <n>                 Cantidad de puntos del sweep",
                "  mdelay <ms>               Retardo previo a medición",
                "  tdelay <ms>               Retardo post-trigger",
                "",
                "DISPLAY:",
                "  display <0-18>            Modo de salida",
                "  display 6                 R/X (default)",
                "  display 7                 |Z|/deg",
                "  display 15                G/B",
                "",
                "GANANCIA / RANGO:",
                "  setgain                   Ver configuración actual",
                "  setgain auto              Activar auto-ranging",
                "  setgain ch0 <0-3>         Ganancia de voltaje",
                "  setgain ch1 <0-3>         Ganancia de corriente",
                "",
                "BARRIDOS:",
                "  sweep_type frequency <inicio> <fin>",
                "  sweep_scale <log|linear>",
                "",
                "CALIBRACIÓN:",
                "  calibrate open",
                "  calibrate short",
                "  calibrate rt <R> xt <X>",
                "  calibrate commit <pass> [ts]",
                "  calibrate list",
                "",
                "SISTEMA:",
                "  *idn | status | reset | version | debug on|off|info",
                "",
                "TIP: usa 'help <comando>' para ver sintaxis exacta del firmware.",
                "Modo SIMULACIÓN: conecta hardware desde Dashboard para ejecutar."
            ]
        elif cmd_lower == 'z':
            response_lines = [
                "0,1.000021e+03,8.220137e-01",
                "[SIMULADO] Z = 1.000kΩ + 0.822jΩ"
            ]
        elif cmd_lower == '*idn':
            response_lines = [
                "ADMX2001B,FW=1.3.2,HW=Rev.A (SIMULADO)",
            ]
        elif cmd_lower == 'status':
            response_lines = [
                "Sistema: Listo (modo simulación)",
                "Conexión: No conectado a hardware",
                "Para conectar: vaya al Dashboard principal"
            ]
        elif cmd_lower.startswith('frequency'):
            parts = command.split()
            freq_val = parts[1] if len(parts) > 1 else '1000'
            response_lines = [f"frequency = {freq_val}.0000Hz"]
        elif cmd_lower.startswith('setgain'):
            response_lines = ["setgain: configuración actualizada (simulado)"]
        elif cmd_lower.startswith('display'):
            response_lines = ["display: modo actualizado (simulado)"]
        elif cmd_lower.startswith('average'):
            response_lines = [f"average = {command.split()[1] if len(command.split()) > 1 else '1'}"]
        elif cmd_lower.startswith('calibrate'):
            # Detectar subcomandos específicos de calibración
            parts = command.split()
            if len(parts) > 1:
                subcmd = parts[1].lower()
                if subcmd == 'list':
                    response_lines = [
                        "═══════════════════════════════════════",
                        "CALIBRACIONES (Modo Simulación)",
                        "═══════════════════════════════════════",
                        "No hay calibraciones disponibles en modo simulación.",
                        "",
                        "Conecte el dispositivo para:",
                        "  • Ver calibraciones guardadas",
                        "  • Ejecutar wizard de calibración",
                        "  • Gestionar calibraciones existentes"
                    ]
                elif subcmd in ['open', 'short', 'load']:
                    response_lines = [
                        f"calibrate {subcmd}: requiere hardware conectado",
                        "",
                        "Use el Wizard de Calibración en la interfaz:",
                        "   Dashboard > Calibración > Iniciar Wizard"
                    ]
                else:
                    response_lines = [
                        "calibrate: use el Dashboard para calibración completa",
                        "Wizard disponible en: Calibración > Iniciar Wizard",
                        "",
                        "Comandos de calibración disponibles:",
                        "  • calibrate list - Listar calibraciones",
                        "  • calibrate open - Medición open",
                        "  • calibrate short - Medición short",
                        "  • calibrate load - Medición con carga conocida"
                    ]
            else:
                response_lines = [
                    "calibrate: use el Dashboard para calibración completa",
                    "Wizard disponible en: Calibración > Iniciar Wizard"
                ]
        else:
            response_lines = [
                f"Comando: {command}",
                "",
                "Nota: Conecte el dispositivo en el Dashboard",
                "para obtener respuestas reales del hardware."
            ]
        
        # Renderizar respuesta simulada
        response_children = []
        is_help_cmd = (cmd_lower == 'help' or cmd_lower.startswith('help '))
        for line in response_lines:
            if is_help_cmd:
                # Cabecera separadora (═══)
                if line.startswith('═') or line.startswith('─'):
                    response_children.append(
                        html.Div(
                            html.Span(line, style={'color': 'var(--t-accent)', 'fontWeight': '600', 'letterSpacing': '0'}),
                            className="terminal-line"
                        )
                    )
                # Título de sección (mayúsculas, sin indentación)
                elif line and not line.startswith(' ') and line[0].isupper() and ':' in line:
                    response_children.append(
                        html.Div(
                            html.Span(line, style={'color': 'var(--t-text-secondary)', 'fontWeight': '700', 'marginTop': '4px', 'display': 'block'}),
                            className="terminal-line"
                        )
                    )
                # Línea vacía
                elif line == '':
                    response_children.append(html.Div(style={'height': '4px'}, className="terminal-line"))
                # Línea de comando (indentada con dos espacios)
                elif line.startswith('  '):
                    # Separar comando de descripción por espacios múltiples
                    import re as _re
                    m = _re.match(r'^(  \S[^\s]*)(\s{2,})(.*)', line)
                    if m:
                        response_children.append(
                            html.Div([
                                html.Span(m.group(1), style={'color': 'var(--t-text-primary)', 'fontFamily': 'inherit'}),
                                html.Span(m.group(3), style={'color': 'var(--t-text-muted)', 'marginLeft': '1ch'}),
                            ], className="terminal-line", style={'paddingLeft': '1rem'})
                        )
                    else:
                        response_children.append(
                            html.Div(
                                html.Span(line, style={'color': 'var(--t-text-primary)'}),
                                className="terminal-line", style={'paddingLeft': '1rem'}
                            )
                        )
                # Línea de tip/nota
                else:
                    response_children.append(
                        html.Div(
                            html.Span(line, style={'color': 'var(--t-text-muted)', 'fontStyle': 'italic'}),
                            className="terminal-line"
                        )
                    )
            else:
                response_children.append(
                    html.Div([
                        html.Span("  ", className="terminal-indent"),
                        html.Span(line, className="terminal-response-line")
                    ], className="terminal-line")
                )
        current_output.append(html.Div(response_children))
        
        # Línea separadora
        current_output.append(html.Div(className="terminal-separator"))
        
        # Limitar output
        if len(current_output) > 500:
            current_output = current_output[-500:]
        
        return current_output, "", history_store, {'active': False, 'command': ''}, True, password_state



# =============================================================================
# CALLBACKS GLOBALES DE INTERNACIONALIZACIÓN (i18n)
# =============================================================================

def register_global_i18n_callbacks(app):
    """
    Registra los callbacks de internacionalización.

    Flujo:
      1. El usuario hace clic en un botón del language_picker → actualiza 'lang-store'.
      2. El callback server-side 'serve_translations' convierte el código de idioma
         en el diccionario completo y lo guarda en 'lang-translations-store'.
      3. El clientside_callback 'apply_i18n' invoca window.ZORIA_I18N.apply()
         con el dict, que actualiza todos los [data-i18n] en el DOM.
    """
    from dash import Input, Output, ALL, ctx
    from dash.exceptions import PreventUpdate
    from lib.i18n import get_all_for_lang, LANGUAGES, DEFAULT_LANG

    # ── 1. Botones de idioma → actualizar lang-store ────────────────────────────
    @app.callback(
        Output('lang-store', 'data'),
        Input({'type': 'lang-btn', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True,
    )
    def update_lang_store(n_clicks_list):
        if not ctx.triggered or not ctx.triggered_id:
            raise PreventUpdate
        triggered = ctx.triggered_id
        if isinstance(triggered, dict) and triggered.get('type') == 'lang-btn':
            lang = triggered['index']
            if lang in LANGUAGES:
                return lang
        raise PreventUpdate

    # ── 2. lang-store → construir dict de traducciones (server-side) ────────────
    # El idioma se incluye como '_lang' dentro del propio dict para que el clientside
    # callback nunca tenga un lang desincronizado de sus traducciones.
    @app.callback(
        Output('lang-translations-store', 'data'),
        Input('lang-store', 'data'),
    )
    def serve_translations(lang):
        lang = lang or DEFAULT_LANG
        result = get_all_for_lang(lang)
        result['_lang'] = lang   # paquete atómico: traducciones + su idioma juntos
        return result

    # ── 3. Translations store → aplicar en el DOM (clientside) ─────────────────
    # Usa ClientsideFunction para registrar la función desde i18n_client.js, evitando
    # problemas de Dash 3 con callbacks inline que colisionan con nombres JS reservados.
    # La función window.dash_clientside.zoria.applyI18n está definida en assets/js/i18n_client.js.
    from dash import ClientsideFunction
    app.clientside_callback(
        ClientsideFunction(namespace='zoria', function_name='applyI18n'),
        Output('lang-apply-done', 'data'),
        Input('lang-translations-store', 'data'),
        prevent_initial_call=False,
    )

    # ── 4. Theme store → aplicar data-theme en <html> (clientside) ─────────────
    # Sincroniza theme-store con el atributo data-theme del elemento <html>
    # para activar los CSS custom properties del design system.
    # Función definida en assets/js/i18n_client.js como window.dash_clientside.zoria.applyTheme
    app.clientside_callback(
        ClientsideFunction(namespace='zoria', function_name='applyTheme'),
        Output('theme-dom-sync', 'data'),
        Input('theme-store', 'data'),
        prevent_initial_call=False,
    )


def set_global_device(device, is_connected=False):
    """
    Establece el dispositivo global para el terminal CLI.
    Llamado desde dashboard_page cuando se conecta/desconecta.
    """
    from lib.device_state import device_state
    device_state.set_device(device, is_connected)


def get_secret_key() -> str:
    """
    Obtiene la SECRET_KEY para Flask.
    
    Prioridad:
    1. Variable de entorno SECRET_KEY
    2. Variable de entorno FLASK_SECRET_KEY
    3. Fallback seguro para desarrollo (con advertencia)
    
    Returns:
        String con la secret key.
    """
    secret = os.environ.get("SECRET_KEY") or os.environ.get("FLASK_SECRET_KEY")
    
    if not secret:
        # Fallback para desarrollo - NO USAR EN PRODUCCIÓN
        secret = "zoria-dev-secret-key-change-in-production"
        logging.getLogger(__name__).warning(
            " Usando SECRET_KEY de desarrollo. "
            "Para producción, configure la variable de entorno SECRET_KEY"
        )
    
    return secret


def get_app_config() -> dict:
    """
    Obtiene la configuración de la aplicación desde variables de entorno.
    
    Returns:
        Diccionario con la configuración completa.
    """
    return {
        "title": os.environ.get("APP_TITLE", DEFAULT_CONFIG["title"]),
        "port": int(os.environ.get("PORT", DEFAULT_CONFIG["port"])),
        "host": os.environ.get("HOSTNAME", DEFAULT_CONFIG["host"]),
        "debug": os.environ.get("DEBUG", "true").lower() == "true",
        "use_reloader": os.environ.get("USE_RELOADER", "false").lower() == "true",
        "secret_key": get_secret_key(),
    }


# =============================================================================
# CREACIÓN DE LA APLICACIÓN
# =============================================================================
def create_app() -> DashSPA:
    """
    Crea y configura la aplicación DashSPA.
    
    Esta función inicializa la aplicación Dash con todas las configuraciones
    necesarias, registra las páginas y configura el servidor Flask subyacente.
    
    Returns:
        Instancia configurada de DashSPA.
    
    Raises:
        RuntimeError: Si hay un error crítico en la creación de la app.
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(" Inicializando ZORIA Dashboard...")
        
        # Crear instancia de DashSPA
        app = DashSPA(
            __name__,
            prevent_initial_callbacks=True,
            suppress_callback_exceptions=True,
            external_scripts=EXTERNAL_SCRIPTS,
            external_stylesheets=EXTERNAL_STYLESHEETS,
            url_base_pathname="/",
            assets_folder=DEFAULT_CONFIG["assets_folder"],
            title=DEFAULT_CONFIG["title"],
            update_title=None,
        )
        
        # Configurar favicon
        app._favicon = DEFAULT_CONFIG["favicon"]
        
        # Obtener configuración
        config = get_app_config()
        
        # Configurar servidor Flask
        app.server.config["SECRET_KEY"] = config["secret_key"]
        
        # Configurar modo debug
        if config["debug"]:
            logger.info(" Modo DEBUG activado")
        
        logger.info(" Registrando páginas...")
        
        # Importar y registrar páginas
        # Nota: Los imports se hacen aquí para evitar problemas de circular import
        try:
            from pages.dashboard.dashboard_page import register_dashboard_page
            from pages.simulator.simulator_page import register_simulator_page
            from pages.calibration.calibration_page import register_calibration_page
            from pages.about.about_page import register_about_page
            from pages.config.config_page import register_config_page
            from pages.common.terminal_component import global_terminal_component
            from dash import html
            
            register_dashboard_page(app)
            logger.info("  Dashboard registrado")
            
            register_simulator_page(app)
            logger.info("  Simulator registrado")
            
            register_calibration_page(app)
            logger.info("  Calibration registrado")
            
            register_about_page(app)
            logger.info("  About registrado")
            
            register_config_page(app)
            logger.info("  Config registrado")
            
            # Registrar callbacks globales de conexión
            register_global_connection_callbacks(app)
            logger.info("  Conexión sidebar global registrada")
            
            # Registrar callbacks globales del terminal
            register_global_terminal_callbacks(app)
            logger.info("  Terminal global registrado")

            # Registrar callbacks globales de i18n (multilenguaje)
            register_global_i18n_callbacks(app)
            logger.info("  i18n multilenguaje registrado")
            
        except ImportError as e:
            logger.error(f"Error registrando páginas: {e}")
            raise RuntimeError(f"No se pudieron registrar las páginas: {e}") from e
        
        # Establecer layout principal con terminal global
        # El terminal se inyecta en el layout para estar disponible en todas las páginas
        # NOTA: page_container de DashSPA ya incluye SPA_ALERT y SPA_NOTIFY internamente
        original_layout = page_container
        app.layout = html.Div([
            # Stores globales
            dcc.Store(id='auto-connect-on-start', data=False),  # Trigger para auto-conexión al iniciar
            dcc.Store(id='connection-error-trigger', data=False),  # Store para activar alerta de error de conexión
            dcc.Store(id='connection-success-trigger', data=False),  # Store para activar notificación de conexión exitosa
            # i18n stores
            dcc.Store(id='lang-store', storage_type='local', data='es'),          # Idioma activo (persiste en localStorage)
            dcc.Store(id='lang-translations-store', storage_type='memory', data={}),  # Dict de traducciones listo para el cliente
            dcc.Store(id='lang-apply-done', data=0),  # Output dummy del clientside i18n callback
            # Theme store (global – usado por dashboard, config y simulador)
            dcc.Store(id='theme-store', storage_type='local', data='dark'),
            dcc.Store(id='theme-dom-sync', data='dark'),  # Output del callback que sincroniza data-theme al <html>
            # Config preferences (persisten en localStorage)
            dcc.Store(id='autoconn-store', storage_type='local', data=True),
            # Intervals globales
            dcc.Interval(id='ports-interval', interval=2000, n_intervals=0),  # Detección de puertos
            dcc.Interval(id='connection-monitor-interval', interval=5000, n_intervals=0),  # Monitor activo de conexión (cada 5s)
            # Terminal global
            global_terminal_component(),
            original_layout
        ])
        
        logger.info("Aplicación inicializada correctamente")
        return app
        
    except Exception as e:
        logger.error(f"Error crítico al crear la aplicación: {e}")
        raise RuntimeError(f"Error al inicializar la aplicación: {e}") from e


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================
def main():
    """
    Punto de entrada principal de la aplicación.
    
    Configura logging, crea la aplicación y la ejecuta.
    """
    # Configurar logging primero
    logger = setup_logging()
    
    try:
        # Reusar la instancia global ya creada al importar el módulo.
        # No llamar create_app() de nuevo: registraría callbacks duplicados
        # lo que provoca KeyError en SPA_NOTIFY (callback_map del 2.º app vacío).
        global app
        if app is None:
            app = create_app()
        
        # Obtener configuración
        config = get_app_config()
        
        logger.info(f" Iniciando servidor en http://{config['host']}:{config['port']}")
        logger.info(f"⏹  Para detener presione Ctrl+C")
        
        # Ejecutar aplicación
        app.run(
            host=config["host"],
            port=config["port"],
            debug=config["debug"],
            use_reloader=config["use_reloader"]
        )
        
    except KeyboardInterrupt:
        logger.info("\n Servidor detenido por el usuario")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)


# =============================================================================
# INSTANCIA GLOBAL (para compatibilidad con server.py y despliegues)
# =============================================================================
# Configurar logging básico para imports
logger = setup_logging()

# Crear instancia global
try:
    app = create_app()
except Exception as e:
    logger.error(f"No se pudo crear la aplicación global: {e}")
    app = None  # type: ignore

# =============================================================================
# EJECUCIÓN DIRECTA
# =============================================================================
if __name__ == "__main__":
    main()
